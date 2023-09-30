#!/usr/bin/env python3.7.3

import os
import subprocess as sp
import re
import shutil
import sys
import pandas as pd

import logging

global log
log = logging.getLogger(__name__)


class AuxcellChar:

    def __init__(self):
        self.auxcell_name = ''
        self.auxcell_pininfo = ''

        self.memgendir = os.getenv('memgen_path')
        self.auxcelllibdir = os.getenv('auxcell_lib_path')

        #self.memgendir = ''
        #self.auxcelllibdir = ''
        
        self.genName = os.path.split(self.memgendir)[1]
        self.genParentdir = os.path.split(self.memgendir)[0]
        self.genParentdirName = os.path.split(self.genParentdir)[1]

        print("Name of Gen", self.genName)
        self.Fasocdir = os.path.split(self.genParentdir)[0]
        # self.genPrivatedir = os.path.join(self.Fasocdir, 'private', self.genParentdirName, self.genName)
        self.genPrivatedir = os.path.join(self.Fasocdir, 'private', self.genParentdirName, 'memory-gen')
        # Check if the MemGen private directory is present and accessible.
        if not os.path.isdir(self.genPrivatedir):
            log.error(
                f"The  {self.genPrivatedir} dir does not exists, which is required to access the auxcell "
                f"characterization files. Exiting MemGen")
            sys.exit(1)
        elif os.path.isdir(self.genPrivatedir):
            # append the apr_pymodules path to pythonpath to access all the apr modules.
            sys.path.append(os.path.join(self.genPrivatedir, 'deo'))

        self.deo_private_dir = os.path.join(self.genPrivatedir, 'deo')
        self.auxcells_lib_char = os.path.join(self.deo_private_dir, 'auxcells_lib_char')

    def ed_char(self, tech_config_dic, auxcell, auxcell_props, sram_specs, sram_config):

        self.target_vdd = sram_specs["target_vdd"]
        self.target_delay = sram_specs["target_delay"]
        self.word_size = sram_specs["word_size"]
        self.no_banks = sram_config[0]
        self.no_bank_rows = sram_config[1]
        self.no_bank_cols = sram_config[2]

        self.auxcell_name = auxcell_props.get_cellname()
        self.auxcell_pininfo = auxcell_props.get_pininfo()

        # Get the required path variables.
        self.auxcell_char_dir = os.path.join(self.auxcells_lib_char, f"{auxcell:s}")  # Auxcell name as per the
        # sram definition.
        print("Directory of characterization", self.auxcell_char_dir)

        exec_dir = os.getcwd()  # Current working directory to be returned after auxcell characterization.

        # Obtain the required libraries from the technology collateral file.
        mos_lib = tech_config_dic['spice_lib']['hspice_lib']['default']
        stdcell_lib_netlist = tech_config_dic['stdcell_lib']['default']
        auxcell_netlist = '%s/CDL/%s.cdl' % (self.auxcelllibdir, self.auxcell_name)

        # Create the auxcell characterization spice file.
        self.auxcell_char_sp = '%s_%d_%db_%dr_%dc.sp' % (self.auxcell_name, self.word_size, self.no_banks,
                                                         self.no_bank_rows, self.no_bank_cols)

        # Changign the directory to the respective auxcell directory for the cell characterization.
        os.chdir(self.auxcell_char_dir)

        fhand_r = open('%s.sp' % auxcell, 'r')  # Open the default spice characterization file provided.
        fhand_w = open(self.auxcell_char_sp, 'w')  # Open the new auxcell char spice file for the current sram specs.

        # Adding the
        # PDK mos lib
        fhand_w.write("*** Char Script *** \n .lib %s\n" % mos_lib)
        # STD Cell library
        fhand_w.write(".inc %s\n" % stdcell_lib_netlist)
        # PDK Specific Auxcell netlist
        fhand_w.write(".inc %s\n" % auxcell_netlist)

        fhand_auxcellcdl = open(auxcell_netlist, 'r')  # Open the PDK sepcific Auxcell netlist to get the port-order.

        # Extract the pin info and the order from the auxcell cdl netlist.
        pins_str = ''
        for line in fhand_auxcellcdl:
            line = line.strip()  # Using rstrip to remove the new line
            if line.startswith('.SUBCKT %s ' % self.auxcell_name):  # Spacing in the definition has to be exact for the
                # condition to pass.
                pins_str = re.split(".SUBCKT\s+%s\s+" % self.auxcell_name, line)[1]  # Auxcell all pins as string.

        auxcell_pin_list = re.split("\s+", pins_str)  # Convert the string to list

        # Update the pin order of the CUT instance based on the pin order of the auxcell subckt definition and pininfo.
        auxcell_pininfo_keys = list(self.auxcell_pininfo.keys()) # Obtain the standardized pin names
        auxcell_pininfo_values = list(self.auxcell_pininfo.values()) # PDK-specific pin values as per SRAM definition.
        auxcell_pininfo_values_names_only = [i[0] for i in auxcell_pininfo_values] # PDK specific pin names only.

        # Determine the auxcell under test (aut) pin order for Xtop instance based on the PDK auxcell pin order.
        aut_pin_order = []
        for i in auxcell_pin_list:
            pin_index = auxcell_pininfo_values_names_only.index(i)
            aut_pin_order.append(auxcell_pininfo_keys[pin_index])
        cut_pin_str = ' '.join(aut_pin_order)

        # fhand_w.write("**SRAM**\n.inc '%s'\n"%SRAM_sp)
        # ColMux = int(self.no_bank_cols / self.word_size)

        # Replace the default parameters
        for line in fhand_r:
            line = line.strip()  # Using rstrip to remove the new line
            if line.startswith('.param pvdd='):
                line = re.sub('.param pvdd=.+', '.param pvdd=' + str(self.target_vdd), line)
                fhand_w.write(line + '\n')
            elif line.startswith('.param tper='):
                line = re.sub('.param tper=.+', '.param tper=' + str(self.target_delay), line)
                fhand_w.write(line + '\n')
            elif line.startswith('.param WS='):
                line = re.sub('.param WS=.+', '.param WS=' + str(self.word_size), line)
                fhand_w.write(line + '\n')
            elif line.startswith('.param NR='):
                line = re.sub('.param NR=.+', '.param NR=' + str(self.no_bank_rows), line)
                fhand_w.write(line + '\n')
            elif line.startswith('.param NC='):
                line = re.sub('.param NC=.+', '.param NC=' + str(self.no_bank_cols), line)
                fhand_w.write(line + '\n')
            elif line.startswith('XTOP '):
                line = re.sub('XTOP.+', 'XTOP %s / %s' % (cut_pin_str, self.auxcell_name), line)
                fhand_w.write(line + '\n')
            else:
                fhand_w.write(line + '\n')

        # close the file stream
        fhand_r.close()
        fhand_w.close()
        fhand_auxcellcdl.close()

        # # Run HSPICE # #
        # auxcell_lis = 'outputdir/%s_%dB_%dR_%dC' % (auxcell, self.no_banks, self.no_bank_rows, self.no_bank_cols)
        auxcell_lis = os.path.join('outputdir', self.auxcell_char_sp.split('.sp')[0])
        tp = sp.Popen(['hspice', '-i', self.auxcell_char_sp, '-o', auxcell_lis, '-mt', '16'])  # execute a new process
        tp.wait()

        # Extract the delay, active and leakage powers
        # delay and active power from auxcell_lis.mt0.csv, and leakage from auxcell_lis.mt1.csv
        df_mt0 = pd.read_table(auxcell_lis+'.mt0.csv', sep=',', skiprows=3) # skipping 3 rows to remove the mt0 header.
        delay = df_mt0['delay'][0]
        active_power = df_mt0['active_power'][0]
        df_mt1 = pd.read_table(auxcell_lis+'.mt1.csv', sep=',', skiprows=3) # skipping 3 rows to remove the mt0 header.
        leak_power = df_mt1['leak_power'][0]

        # Remove the current run related files
        os.chdir('outputdir')
        
        output_file_list = os.listdir(os.getcwd())  # list the files in the directory
        
        auxcell_lis = auxcell_lis.split('outputdir/')[1]
        
        for file_name in output_file_list:
            z = re.match(auxcell_lis, file_name)
            # z = file_name.startswith(auxcell_lis)
            if z is not None:
                try:
                    os.remove(file_name)
                except:
                    shutil.rmtree(file_name)

        os.chdir(self.auxcell_char_dir)
        os.remove(self.auxcell_char_sp)
        os.chdir(exec_dir)

        return [delay, active_power, leak_power]


if __name__ == '__main__':
    # For bank_verilog_gen.py testing purpose only.
    os.environ['memgen_path'] = ''
    os.environ['auxcell_lib_path'] = ''
    sys.path.append('')
    from SRAM import sram_arch

    arch = sram_arch.SRAM6TArch()

    row = arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col = arch.bank_top["col_periphery"]
    bca = arch.bank_top["bitcell_array"]

    sram_bank_arch = dict(row_periphery=row, col_periphery=col, bitcell_array=bca)
    print("SRAM Arch here is ", sram_arch)
    sram_config = [1, 128, 128]
    sram_specs = {'word_size': 16, 'target_vdd' : 0.8, 'target_delay': 200e-9}
    tech_config = ''
    import yaml
    with open(tech_config, 'r') as th:
        dic = yaml_config_dic = yaml.safe_load(th)
    auxcell = list(sram_bank_arch['col_periphery'].keys())[1]
    auxcell_props = sram_bank_arch['col_periphery'][auxcell]

    ac_char = AuxcellChar()
    tdly, active_power, leak_power = ac_char.ed_char(dic, auxcell, auxcell_props, sram_specs, sram_config)
    print("Delay", tdly, '\n', "active_power", active_power, "leak_power", leak_power)
