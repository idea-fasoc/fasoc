# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 12:14:17 2019

@author: SumanthKamineni
"""

import os
import sys
import time

from optparse import OptionParser
from decimal import *
from SRAM.sram_model import sram_6t_ed_model
from deo.auxcell_char import AuxcellChar

getcontext().prec = 20


class SRAMChar(AuxcellChar):

    def __init__(self):
        super(SRAMChar, self).__init__()
        self.sram_specs = None
        self.auxcells = {}

    @staticmethod
    def str_class(classname):
        return getattr(sys.modules[classname], classname)

    def sram_gen(self, voltage, freq, word_size, bank, NR, NC):
        file_dir = os.path.abspath(__file__)
        top_dir = os.path.dirname(file_dir)
        comp_lib_dir = os.path.join(top_dir, '../comp_lib')
        SRAM_dir = os.path.join(comp_lib_dir, 'components/SRAM')

        deoDir = os.path.dirname(os.path.abspath(__file__))  # Generator Directory: Deo
        genDir = os.path.split(deoDir)[0]  # MemGen path
        genName = os.path.split(deoDir)[1]  # MemGen Name
        genParentDir = os.path.split(genDir)[0]  # generators directory
        Fasocdir = os.path.split(genParentDir)[0]
        deodir = os.path.join(Fasocdir, 'private', 'generators', genName, 'deo')

        self.sram_libdir = os.path.join(deodir, 'SRAM')
        # fh_r=open('SRAM_Criticalpath.sp', 'r')
        fh = open('%s/SRAM_Criticalpath_B%d_NR%d_NC%d.sp' % (SRAM_dir, bank, NR, NC), 'w')
        fh.write(".inc '%s/ColMux.sp'\n" % SRAM_dir)
        fh.write(".inc '%s/BL_Load.sp'\n" % SRAM_dir)
        fh.write(".inc '%s/PreCharge.sp'\n" % SRAM_dir)
        fh.write(".inc '%s/SenseAmp_VLSA.sp'\n" % SRAM_dir)
        fh.write(".inc '%s/WriteDriver.sp'\n" % SRAM_dir)
        Colmux = int(NC / word_size)
        print('ColMux is %d' % Colmux)
        En_Str = ' '.join(['En<%d>' % r for r in range(Colmux)])
        EnB_Str = ' '.join(['En_B<%d>' % r for r in range(Colmux)])
        BL_Str = ' '.join(['BL<%d>' % r for r in range(Colmux)])
        BLB_Str = ' '.join(['BLB<%d>' % r for r in range(Colmux)])
        ColMux_Pins = '%s %s %s %s' % (En_Str, EnB_Str, BL_Str, BLB_Str)
        ColMux_Name = 'ColMux_%dx1' % Colmux
        fh.write("** Cell Name: %s\n\n" % ColMux_Name)
        fh.write(".subckt %s %s DL DLB VDD VSS\n" % (ColMux_Name, ColMux_Pins))
        for i in range(Colmux):
            fh.write("xi0<%d> BL<%d> BLB<%d> DL DLB En<%d> EnB<%d> VDD VSS ColMux\n" % (i, i, i, i, i))
        fh.write(".ends %s\n" % ColMux_Name)
        fh.write("** Cell Name: SRAM_ColPeriphery\n\n")
        fh.write(
            ".subckt SRAM_ColPeriphery PCH %s SAEn SAEnB DIN WE WEB DOUT DOUT_DFF_EN VDDPCH VDDCM VDDWD VDDSA VDDOD VSS\n" % ColMux_Pins)
        fh.write("xi8 BL<0> BLB<0> PCH VDDPCH PreCharge\n")
        fh.write("xi7 %s  DL DLB VDDCM VSS %s\n" % (ColMux_Pins, ColMux_Name))
        fh.write("xi4 DIN DL DLB WE WEB VDDWD VSS WriteDriver\n")
        fh.write("xi6 DL DLB SAEn SAEnB VDDSA VSS SenseAmp_VLSA\n")
        fh.write("xi14 DOUT_DFF_EN net030 DOUT VDDOD VDDOD VSS VSS DFFQ_X2N_A10P5PP84TR_C14\n")
        fh.write("xi5 DL VDDOD VDDOD VSS VSS net030 BUFH_X1N_A10P5PP84TR_C14\n")
        for i in range(Colmux):
            fh.write("xi10<%d> BLB<%d> BL_Load\n" % (i, i))
            fh.write("xi9<%d> BL<%d> BL_Load\n" % (i, i))
        fh.write(".ends SRAM_ColPeriphery \n")
        fh.close()

    def get_sram_ed(self, tech_config_dic, sram_config, sram_bank_arch, sram_specs):
        """
            - Estimates the SRAM Energy and Delay value for the given architecture, auxcells and specifications.
            - Runs the simulation and gathers the component Energy and delay values for each architecture point.
                - Creates the SRAM cirtical path circuit using auxcells for each architecture point.
                - Estimates the auxcells E and D value and plugs-in on to the top-level SRAM model.
        """
        self.sram_config = sram_config  # List -> [#b, #r, #c]
        self.sram_specs = sram_specs  # Dic

        start = time.time()

        auxcells_ed_output_file = f"auxcells_ed_{self.sram_specs['no_words']:d}_{self.sram_specs['word_size']:d}" \
                                  f"_{self.sram_specs['target_vdd']:f}_{self.sram_specs['target_delay']:f}.txt"

        self.fh_comp = self.get_auxcell_ed_handler(auxcells_ed_output_file)  # Which dir?

        # Collect the list of the auxcells in the given sram_architecture
        for comp, comp_ac in sram_bank_arch.items():  # comp -> row_periphery, col_periphery or bitcell_array.
            for ax in comp_ac.keys():  # auxcell keys from the sram architecture definition.
                self.auxcells[ax] = comp_ac[ax]

        # Characterize each auxcell and obtain the energy and delay values.
        for auxcell in self.auxcells.keys():
            auxcell_props = self.auxcells[auxcell]
            auxcell_delay, auxcell_active_power, auxcell_leak_power = self.ed_char(tech_config_dic, auxcell,
                                                                                   auxcell_props,
                                                                                   self.sram_specs, self.sram_config)

            # Update the Energy and delay values of the Auxcell properties.
            auxcell_props.update_delay(auxcell_delay)
            auxcell_props.update_active_power(auxcell_active_power)
            auxcell_props.update_leak_power(auxcell_leak_power)

            self.fh_comp.write(f"{self.auxcells[auxcell].get_cellname():s}, {self.sram_specs['no_words']:d},"
                               f"{self.sram_specs['word_size']:d}, {self.sram_specs['target_vdd']:f}, "
                               f"{self.sram_specs['target_delay']:f}, {self.sram_config[0]:d}, {self.sram_config[1]:d},"
                               f" {self.sram_config[2]:d}, {Decimal(auxcell_active_power * 1e9):f}, "
                               f"{Decimal(auxcell_leak_power * 1e9):f}, {Decimal(auxcell_delay * 1e9):f}")

        SRAM_ED: list = sram_6t_ed_model(self.auxcells, self.sram_specs['no_words'], self.sram_config[0],
                                         self.sram_config[1], self.sram_config[2])

        self.fh_comp.close()
        end = time.time()

        print(f"Runtime of the program is {end - start}")

        return SRAM_ED

    def get_auxcell_ed_handler(self, auxcell_ed_file):
        fh = open(auxcell_ed_file, 'w')
        fh.write("auxcell, no_words, word_wize, target_VDD, target_delay, no_banks, no_rows, no_columns, "
                 "auxcell_active_power, auxcell_leak_power, auxcell_delay \n")

        return fh

    @staticmethod
    def str_class(classname):
        return getattr(sys.modules[classname], classname)


def main():
    parser = OptionParser()
    parser.add_option('-s', '--sram_specs',
                      type='string',
                      dest='mem_specs',
                      help='''Configuration file in Json format with Specifications of the memory to be generated.
                         Ex: -c sram_config.json or --mem_specs= sram_config.json ''',
                      default='')
    parser.add_option('-p', '--pdk',
                      type='string',
                      dest='pdk',
                      help='''Process Design Kit: The pdk process info in which the memory to be generated. 
                         Ex: -pdk tsmc65  or --pdk= tsmc65 ''',
                      default='')
    parser.add_option('-a', '--auxcells',
                      type='dic',
                      dest='pdk_char',
                      help='''PDK Characterization: Enabling this will characterize the given PDK before the sram ED estimation. 
                         Ex: --pdk_char= 1 ''',
                      default=0)

    (options, argv) = parser.parse_args()
    global p_options
    p_options = {}
    p_options['mem_size'] = options.mem_size
    p_options['word_size'] = options.word_size
    p_options['voltage'] = options.voltage
    p_options['frequency'] = options.frequency
    p_options['pdk'] = options.pdk
    p_options['mem_specs'] = options.mem_specs
    p_options['pdk_char'] = options.pdk_char
    p_options['bc_char'] = options.bc_char
    global rundir
    rundir = os.getcwd()
    global components
    global pdk_char_comp
    pdk_char_comp = ["Bank_2inputDecoder", "Bank_4inputDecoder",
                     "Bank_2outputMux", "Bank_4outputMux",
                     "Bitcell_read_leakage", "Bitcell_write_leakage", "Bitcell_hold_leakage"]
    components = ["RowDecoder", "ColDecoder", "WLDriver", "SenseAmp_VLSA", "PreCharge", "WriteDriver", "Read_Tcrit",
                  "Write_Tcrit"]

    sram_ed = SRAMChar.get_sram_ed(components, pdk_char_comp)
    print(sram_ed)


if __name__ == '__main__':
    # For bank_verilog_gen.py testing purpose only.
    os.environ['memgen_path'] = ''
    os.environ['auxcell_lib_path'] = ''

    from SRAM import sram_arch

    arch = sram_arch.SRAM6TArch()

    row = arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col = arch.bank_top["col_periphery"]
    bca = arch.bank_top["bitcell_array"]

    sram_bank_arch = dict(row_periphery=row, col_periphery=col, bitcell_array=bca)
    sram_config = [1, 128, 128]
    sram_specs = {'word_size': 16, 'target_vdd': 0.8, 'target_delay': 200e-9}
    tech_config = ''
    import yaml

    with open(tech_config, 'r') as th:
        dic = yaml_config_dic = yaml.safe_load(th)
    auxcell = list(sram_bank_arch['col_periphery'].keys())[0]
    auxcell_props = sram_bank_arch['col_periphery'][auxcell]

    SRAM_ED = SRAMChar.get_sram_ed(dic, sram_config, sram_bank_arch, sram_specs)
    print("SRAM_Delay", SRAM_ED[0], '\n', "SRAM_Energy", SRAM_ED[1])
