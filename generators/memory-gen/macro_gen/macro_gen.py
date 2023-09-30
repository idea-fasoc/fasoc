import os
import sys
import subprocess as sp
import shutil
import logging
import re
import glob

global log
log = logging.getLogger(__name__)


class MacroGen:
    """ Wrapper for the SRAM macro layout generation
        -  Generate the bank:
            - Generate the verilog file.
            - Perform the Synthesis.
            - Perform the layout generation.

        - Hierarchical multi-bank layout.
            - Manage the files: Prepare for the mult-bank layout.
            - Generate the multi-bank verilog file.
            - Perform the Synthesis.
            - Perform the layout generation.
        - Separate the common modules between the bank generation and hierarchical multi-bank generation, and use the
        in-heritance.
    """

    def __init__(self):

        self.memgendir = os.getenv('memgen_path')
        self.auxcelllibdir = os.getenv('auxcell_lib_path')
        
        self.genName = os.path.split(self.memgendir)[1]
        self.genParentdir = os.path.split(self.memgendir)[0]
        self.genParentdirName = os.path.split(self.genParentdir)[1]

        self.runfilesdir = os.path.join(self.memgendir, 'generated')

        self.Fasocdir = os.path.split(self.genParentdir)[0]
        self.genPrivatedir = os.path.join(self.Fasocdir, 'private', self.genParentdirName, self.genName)

        self.aprPymodulesdir = os.path.join(self.genPrivatedir, 'apr_pymodules')
        self.aprscriptsdir = os.path.join(self.genPrivatedir, 'apr_scripts')
        self.bank_default_aprscriptsdir = os.path.join(self.aprscriptsdir, 'bank_scripts')
        self.multibank_default_aprscriptsdir = os.path.join(self.aprscriptsdir, 'multibank_scripts')

    def generate_bank(self, tech_config_dic, sram_bank_config: list, sram_auxcell_updated_bank_arch, sram_specs):
        """
            Generates the bank by creating the verilog, prepares and updates the files for the next steps,
            runs synthesis and apr to generate the SRAM bank layout.
        """
        self.tech_config_dic = tech_config_dic
        self.sram_bank_config = sram_bank_config
        self.sram_bank_arch = sram_auxcell_updated_bank_arch
        self.sram_specs = sram_specs

        self.bank_top_module_name = f'sram_bank_{self.sram_bank_config[0]}rows_{self.sram_bank_config[1]}cols'

        self.bank_vlog_dir = os.path.join(self.runfilesdir, f'verilog/{self.bank_top_module_name}')

        self.bank_gen_dir = os.path.join(self.genPrivatedir, self.bank_top_module_name)
        self.bank_gen_auxcells_dir = os.path.join(self.bank_gen_dir, 'blocks/auxcells/export')
        self.bank_gen_scripts_dir = os.path.join(self.bank_gen_dir, 'scripts')
        self.bank_gen_src_dir = os.path.join(self.bank_gen_dir, 'src')

        def bank_verilog_gen():
            """
                Generates the bank verilog file hierarchically for the Synthesis
            """
            log.info(
                f"Generating the bank verilog file {self.bank_top_module_name}.v in {self.bank_vlog_dir} directory")

            try:
                os.mkdir(self.bank_vlog_dir)
                try:
                    os.chdir(self.bank_vlog_dir)
                except OSError as err:
                    log.info("Can not enter the %s directory" % self.bank_vlog_dir, err)
                    log.info("Exiting MemGen")
                    sys.exit(1)
            except FileExistsError:
                log.info(f"{self.bank_vlog_dir} exists. Cleaning up the directory from previous runs")
                shutil.rmtree(self.bank_vlog_dir)
                os.mkdir(self.bank_vlog_dir)
                try:
                    os.chdir(self.bank_vlog_dir)
                except OSError as err:
                    log.info("Can not enter the %s directiory" % self.bank_vlog_dir, err)
                    log.info("Exiting MemGen")
                    sys.exit(1)
            except PermissionError as pr_err:
                log.info("Can not create the %s directory" % self.bank_vlog_dir, pr_err)
                log.info("Exiting MemGen")
                sys.exit(1)

            # Import the Bank verilog generation and generate all the required files.
            from .verilog_gen.bank_verilog_gen import BankVerilogGen

            BankVerilogGen(self.sram_bank_config, self.sram_bank_arch, self.sram_specs, self.bank_top_module_name,
                           self.tech_config_dic)

            # Change to memgen dir
            os.chdir(self.memgendir)

        def bank_layout_data_prep():
            """
            Prepares all the required data for running the synthesis and apr.
            """
            log.info("Preparing the Data for running the synthesis and PNR")

            # Check if the MemGen private directory is present and accessible.
            if not os.path.isdir(self.genPrivatedir):
                log.error(
                    "The  %s dir does not exists, which is required for generating the SRAM macro" % self.genPrivatedir)
                log.error("Make sure access to private repo is obtained. Can not proceed to synthesis and PNR. "
                          "Exiting.....")
                sys.exit(1)
            elif os.path.isdir(self.genPrivatedir):
                # append the apr_pymodules path to pythonpath to access all the apr modules.
                sys.path.append(os.path.join(self.genPrivatedir, 'apr_pymodules'))

            # Create a BankGeneration directory for the bank apr, where the bank layout generation occurs.

            if not os.path.isdir(self.bank_gen_dir):
                log.info("The dir %s  does not exists" % self.bank_gen_dir)
                try:
                    log.info("Creating the directory %s" % self.bank_gen_dir)
                    os.mkdir(self.bank_gen_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Create a bank apr scripts dir, where the default bank scripts are copied & updated for bank under design.

            if not os.path.isdir(self.bank_gen_scripts_dir):
                log.info("The dir %s  does not exists" % self.bank_gen_scripts_dir)
                try:
                    log.info("Creating the directory %s" % self.bank_gen_scripts_dir)
                    os.mkdir(self.bank_gen_scripts_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_scripts_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Copy the apr scripts to the bank_apr
            try:
                shutil.copytree(self.bank_default_aprscriptsdir, self.bank_gen_scripts_dir)
            except IOError as e:
                log.error(
                    f"Unable to copy apr scripts under {self.bank_default_aprscriptsdir} dir to {self.bank_gen_dir}", e)
                if not os.path.exists(self.bank_default_aprscriptsdir):
                    log.error(
                        f"MemGen default CADRE apr scripts directory {self.bank_default_aprscriptsdir} is not found")
                    log.error(f"Make sure user has access to {self.genPrivatedir} and all the required files are "
                              f"cloned properly from Git")
                    log.info(f"Can not proceed with bank generation due to the above reported errors.")
                    sys.exit(1)

            # create the bank source directory
            if os.path.isdir(self.bank_gen_dir):
                try:
                    log.info("Creating the directory %s" % self.bank_gen_src_dir)
                    os.mkdir(self.bank_gen_src_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_src_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Copy all the bank related Verilog files.
            try:
                shutil.copytree(self.bank_vlog_dir, self.bank_gen_src_dir)
            except IOError as e:
                log.error(f"Unable to copy bank verilog files to {self.bank_gen_src_dir} from {self.bank_vlog_dir}", e)
                if not os.path.exists(os.path.join(self.bank_vlog_dir, self.bank_top_module_name, '.v')):
                    log.error(f" {self.bank_top_module_name} verilog module is not created. Check the run log for the "
                              f"errors")
                    log.error("SRAM generation failed. Check the log file for more information.")
                    sys.exit(1)

            # Create the auxcells place holder for the bank generation.
            if os.path.isdir(self.bank_gen_dir):
                try:
                    log.info("Creating the directory %s" % self.bank_gen_auxcells_dir)
                    os.mkdir(self.bank_gen_auxcells_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_auxcells_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Copy all the auxcells under blocks/auxcells/export
            auxcell_lib_files = glob.glob(os.path.join(self.auxcelllibdir, '*', '*'))
            for file in auxcell_lib_files:
                if os.path.isfile(file):
                    shutil.copy(file, self.bank_gen_auxcells_dir)

            # Copy all the required make files from default apr_scripts dir to the bankgen dir.
            # shutil.copy(os.path.join(self.aprscriptsdir, 'include.mk'), self.bank_gen_dir)
            shutil.copy(os.path.join(self.aprscriptsdir, 'Makefile'), self.bank_gen_dir)

            # Update the design name and platfrom of the include file and write to the bank gen dir
            log.info("Updating the include.mk file")
            with open(self.aprscriptsdir + '/include.mk', 'r') as file:
                filedata = file.read()
                filedata = re.sub(r'export DESIGN_NAME :=.*', r'export DESIGN_NAME := ' +
                                  self.bank_top_module_name, filedata)

                platform = f'{os.getenv("foundry")}{os.getenv("node")}{os.getenv("sub_process")}'
                filedata = re.sub(r'export PLATFORM *:=.*', r'export PLATFORM    := ' +
                                  platform, filedata)
                # update the standard cell track and metal number information as well.

            with open(self.bank_gen_dir + '/include.mk', 'w') as file:
                file.write(filedata)

        def bank_synthesis():
            # Generate the constraints.py
            # Update the dc file list.
            # run make synth command.
            # Check if the synthesis is successful

            # Update the files with design specific information.
            with open(self.bank_gen_scripts_dir + '/dc/dc.filelist.tcl', 'r') as file:
                filedata = file.read()
                sourcefile = "./src/" + self.bank_top_module_name + '.v'
                filedata = re.sub(r'set SVERILOG_SOURCE_FILES ".*"', r'set SVERILOG_SOURCE_FILES "' + sourcefile + '\"',
                                  filedata)
            with open(self.bank_gen_scripts_dir + '//dc/dc.filelist.tcl', 'w') as file:
                file.write(filedata)

            # Generate the constraints.py
            # Add clock information
            # Add set_do_not_touch
            # Need to obtain the clock information etc, but for bank without timer clock needs to be defined.  For
            # now, on set_do_not_touch information is added.
            with open(os.path.join(self.bank_gen_scripts_dir, 'dc', 'constraints.tcl'), 'w') as ctcl:
                from macro_gen.synthesis.synth_constraints import constraints_gen
                constraints_gen(ctcl)

            # Run the synthesis
            log.info("Running the synthesis for the design %s" % self.bank_top_module_name)
            os.chdir(self.bank_gen_dir)
            p1 = sp.Popen("make synth", shell=True)
            p1.wait()

            # Check if the Synthesis is successful.
            # Get the cell area estimate from synthesis report
            with open(self.bank_gen_dir + '/reports/dc/' + self.bank_top_module_name + '.mapped.area.rpt', 'r')as file:
                filedata = file.read()
            m = re.search('Total cell area: *([0-9.]*)', filedata)
            if m:
                self.coreCellArea = float(m.group(1))
                log.info("Completed the synthesis for the design %s" % self.bank_top_module_name)
            else:
                log.error('Synthesis Failed, exiting the run. Please check the reports')
                sys.exit(1)
            os.chdir(self.memgendir)

        def bank_apr():

            # from .apr import setup
            from .apr.floorplan import FloorPlan
            from .apr.power_plan import create_bank_power_plan as bank_pp

            self.bank_apr_dir = os.path.join(self.bank_gen_scripts_dir, 'inv')
            # Generate the apr setup files
            # The bank apr and multi-bank apr scripts are maintained separately. So, no need to generate the setup and
            # always source files on the go, unless there needs some pdk dependent updates

            # setup.setup_tcl(self.bank_apr_dir)
            # setup.always_source_tcl(self.bank_apr_dir)

            # Generate the floorplan.tcl
            fp = FloorPlan()
            rp_cu_power_route_area = fp.create_bank_floorplan(self.bank_apr_dir, self.bank_top_module_name, self.tech_config_dic,
                                     self.sram_bank_arch, self.sram_bank_config, self.sram_specs)

            # Generate the power intent and the power planning tcl files.
            bank_pp(self.bank_apr_dir, self.tech_config_dic, rp_cu_power_route_area)

            # Create the bus guides for routing.
            # Will add it after testing the flow for few bank configurations including on the fly CU generation.

            # Run the APR flow
            p2 = sp.Popen("make design", shell=True)
            p2.wait()

            p3 = sp.Popen(['make', 'drc'], shell=True)
            p3.wait()

            p4 = sp.Popen(['make', 'lvs'], shell=True)
            p4.wait()

            p5 = sp.Popen("make export", shell=True)
            p5.wait()

            with (open(self.bank_gen_dir + '/reports/innovus/' + self.bank_top_module_name + '.mapped.htm.ascii', 'r')
                  as file):
                filedata = file.read()
            m = re.search('Total cell area: *([0-9.]*)', filedata)
            if m:
                self.designArea = float(m.group(1))
                log.info("Completed the APR for the design successfully %s" % self.bank_top_module_name)
            else:
                log.error('APR Failed, exiting the run. Please check the reports')
                sys.exit(1)
            os.chdir(self.memgendir)

        # Generate the Bank verilog module for the given architecture and sram specifications.
        bank_verilog_gen()
        # Create a check if the bank verilog generation is successful or not. Will add later.
        bank_layout_data_prep()
        bank_synthesis()
        bank_apr()

    def generate_multi_bank(self, tech_config_dic, no_generation_hierarchies, no_banks, sram_bank_config: list, sram_auxcell_updated_bank_arch, sram_specs):
        """
            Generates the multi-bank for the specified banks by taking the SRAM bank as a macro.
            Created the multi-bank verilog, prepares and updates the files for the next steps,
            runs synthesis and apr to generate the multi-bank SRAM layout.
            Depending on the number of hierarchies, generate_multi-bank will be called twice at the top-level.
        """
        self.tech_config_dic = tech_config_dic
        self.no_banks = no_banks
        self.sram_bank_config = sram_bank_config
        self.sram_bank_arch = sram_auxcell_updated_bank_arch
        self.sram_specs = sram_specs
        self.no_hir = no_generation_hierarchies

        def mb_verilog_gen(vlog_dir, top_module_name, no_banks ):
            # mb --> multi_bank
            """
                Generates the multi-bank verilog file for the Synthesis
            """

            log.info(
                f"Generating the multi-bank verilog file {top_module_name}.v in {vlog_dir} directory")

            try:
                os.mkdir(vlog_dir)
                try:
                    os.chdir(vlog_dir)
                except OSError as err:
                    log.info("Can not enter the %s directory" % vlog_dir, err)
                    log.info("Exiting MemGen")
                    sys.exit(1)
            except FileExistsError:
                log.info(f"{vlog_dir} exists. Cleaning up the directory from previous runs")
                shutil.rmtree(vlog_dir)
                os.mkdir(vlog_dir)
                try:
                    os.chdir(vlog_dir)
                except OSError as err:
                    log.info("Can not enter the %s directiory" % vlog_dir, err)
                    log.info("Exiting MemGen")
                    sys.exit(1)
            except PermissionError as pr_err:
                log.info("Can not create the %s directory" % vlog_dir, pr_err)
                log.info("Exiting MemGen")
                sys.exit(1)

            # Import the Bank verilog generation and generate all the required files.
            from .verilog_gen.multi_bank_verilog_gen import MultibankVerilogGen

            MultibankVerilogGen(self.sram_bank_config, self.sram_bank_arch, no_banks, self.sram_specs, top_module_name,
                           self.tech_config_dic)

            # Change to memgen dir
            os.chdir(self.memgendir)


        def mb_layout_data_prep():
            """
            Prepares all the required data for running the synthesis and apr.
            """
            log.info("Preparing the Data for running the synthesis and PNR")

            # Check if the MemGen private directory is present and accessible.
            if not os.path.isdir(self.genPrivatedir):
                log.error(
                    "The  %s dir does not exists, which is required for generating the SRAM macro" % self.genPrivatedir)
                log.error("Make sure access to private repo is obtained. Can not proceed to synthesis and PNR. "
                          "Exiting.....")
                sys.exit(1)
            elif os.path.isdir(self.genPrivatedir):
                # append the apr_pymodules path to pythonpath to access all the apr modules.
                sys.path.append(os.path.join(self.genPrivatedir, 'apr_pymodules'))

            # Create a BankGeneration directory for the bank apr, where the bank layout generation occurs.

            if not os.path.isdir(self.bank_gen_dir):
                log.info("The dir %s  does not exists" % self.bank_gen_dir)
                try:
                    log.info("Creating the directory %s" % self.bank_gen_dir)
                    os.mkdir(self.bank_gen_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Create a bank apr scripts dir, where the default bank scripts are copied & updated for bank under design.

            if not os.path.isdir(self.bank_gen_scripts_dir):
                log.info("The dir %s  does not exists" % self.bank_gen_scripts_dir)
                try:
                    log.info("Creating the directory %s" % self.bank_gen_scripts_dir)
                    os.mkdir(self.bank_gen_scripts_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_scripts_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Copy the apr scripts to the bank_apr
            try:
                shutil.copytree(self.bank_default_aprscriptsdir, self.bank_gen_scripts_dir)
            except IOError as e:
                log.error(
                    f"Unable to copy apr scripts under {self.bank_default_aprscriptsdir} dir to {self.bank_gen_dir}", e)
                if not os.path.exists(self.bank_default_aprscriptsdir):
                    log.error(
                        f"MemGen default CADRE apr scripts directory {self.bank_default_aprscriptsdir} is not found")
                    log.error(f"Make sure user has access to {self.genPrivatedir} and all the required files are "
                              f"cloned properly from Git")
                    log.info(f"Can not proceed with bank generation due to the above reported errors.")
                    sys.exit(1)

            # create the bank source directory
            if os.path.isdir(self.bank_gen_dir):
                try:
                    log.info("Creating the directory %s" % self.bank_gen_src_dir)
                    os.mkdir(self.bank_gen_src_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_src_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Copy all the bank related Verilog files.
            try:
                shutil.copytree(self.bank_vlog_dir, self.bank_gen_src_dir)
            except IOError as e:
                log.error(f"Unable to copy bank verilog files to {self.bank_gen_src_dir} from {self.bank_vlog_dir}", e)
                if not os.path.exists(os.path.join(self.bank_vlog_dir, self.bank_top_module_name, '.v')):
                    log.error(f" {self.bank_top_module_name} verilog module is not created. Check the run log for the "
                              f"errors")
                    log.error("SRAM generation failed. Check the log file for more information.")
                    sys.exit(1)

            # Create the auxcells place holder for the bank generation.
            if os.path.isdir(self.bank_gen_dir):
                try:
                    log.info("Creating the directory %s" % self.bank_gen_auxcells_dir)
                    os.mkdir(self.bank_gen_auxcells_dir)
                except OSError:
                    log.error("Unable to create the %s directory" % self.bank_gen_auxcells_dir)
                    log.error("Can not proceed with bank layout generation. Exiting MemGen .....")
                    sys.exit(1)

            # Copy all the auxcells under blocks/auxcells/export
            auxcell_lib_files = glob.glob(os.path.join(self.auxcelllibdir, '*', '*'))
            for file in auxcell_lib_files:
                if os.path.isfile(file):
                    shutil.copy(file, self.bank_gen_auxcells_dir)

            # Copy all the required make files from default apr_scripts dir to the bankgen dir.
            # shutil.copy(os.path.join(self.aprscriptsdir, 'include.mk'), self.bank_gen_dir)
            shutil.copy(os.path.join(self.aprscriptsdir, 'Makefile'), self.bank_gen_dir)

            # Update the design name and platfrom of the include file and write to the bank gen dir
            log.info("Updating the include.mk file")
            with open(self.aprscriptsdir + '/include.mk', 'r') as file:
                filedata = file.read()
                filedata = re.sub(r'export DESIGN_NAME :=.*', r'export DESIGN_NAME := ' +
                                  self.bank_top_module_name, filedata)

                platform = f'{os.getenv("foundry")}{os.getenv("node")}{os.getenv("sub_process")}'
                filedata = re.sub(r'export PLATFORM *:=.*', r'export PLATFORM    := ' +
                                  platform, filedata)
                # update the standard cell track and metal number information as well.

            with open(self.bank_gen_dir + '/include.mk', 'w') as file:
                file.write(filedata)

        def mb_synthesis():
            # Update the files with design specific information.
            with open(self.bank_gen_scripts_dir + '/dc/dc.filelist.tcl', 'r') as file:
                filedata = file.read()
                sourcefile = "./src/" + self.bank_top_module_name + '.v'
                filedata = re.sub(r'set SVERILOG_SOURCE_FILES ".*"', r'set SVERILOG_SOURCE_FILES "' + sourcefile + '\"',
                                  filedata)
            with open(self.bank_gen_scripts_dir + '//dc/dc.filelist.tcl', 'w') as file:
                file.write(filedata)

            # Generate the constraints.py
            # Add clock information
            # Add set_do_not_touch
            # Need to obtain the clock information etc, but for bank without timer clock needs to be defined.  For
            # now, on set_do_not_touch information is added.
            with open(os.path.join(self.bank_gen_scripts_dir, 'dc', 'constraints.tcl'), 'w') as ctcl:
                from macro_gen.synthesis.synth_constraints import constraints_gen
                constraints_gen(ctcl)

            # Run the synthesis
            log.info("Running the synthesis for the design %s" % self.bank_top_module_name)
            os.chdir(self.bank_gen_dir)
            p1 = sp.Popen("make synth", shell=True)
            p1.wait()

            # Check if the Synthesis is successful.
            # Get the cell area estimate from synthesis report
            with open(self.bank_gen_dir + '/reports/dc/' + self.bank_top_module_name + '.mapped.area.rpt', 'r') as file:
                filedata = file.read()
            m = re.search('Total cell area: *([0-9.]*)', filedata)
            if m:
                self.coreCellArea = float(m.group(1))
                log.info("Completed the synthesis for the design %s" % self.bank_top_module_name)
            else:
                log.error('Synthesis Failed, exiting the run. Please check the reports')
                sys.exit(1)
            os.chdir(self.memgendir)

        def mb_apr():
            # from .apr import setup
            from .apr.floorplan import FloorPlan
            from .apr.power_plan import create_bank_power_plan as bank_pp

            self.bank_apr_dir = os.path.join(self.bank_gen_scripts_dir, 'inv')
            # Generate the apr setup files
            # The bank apr and multi-bank apr scripts are maintained separately. So, no need to generate the setup and
            # always source files on the go, unless there needs some pdk dependent updates

            # setup.setup_tcl(self.bank_apr_dir)
            # setup.always_source_tcl(self.bank_apr_dir)

            # Generate the floorplan.tcl
            fp = FloorPlan()
            rp_cu_power_route_area = fp.create_bank_floorplan(self.bank_apr_dir, self.bank_top_module_name,
                                                              self.tech_config_dic,
                                                              self.sram_bank_arch, self.sram_bank_config,
                                                              self.sram_specs)

            # Generate the power intent and the power planning tcl files.
            bank_pp(self.bank_apr_dir, self.tech_config_dic, rp_cu_power_route_area)

            # Create the bus guides for routing.
            # Will add it after testing the flow for few bank configurations including on the fly CU generation.

            # Run the APR flow
            p2 = sp.Popen("make design", shell=True)
            p2.wait()

            p3 = sp.Popen(['make', 'drc'], shell=True)
            p3.wait()

            p4 = sp.Popen(['make', 'lvs'], shell=True)
            p4.wait()

            p5 = sp.Popen("make export", shell=True)
            p5.wait()

            with (open(self.bank_gen_dir + '/reports/innovus/' + self.bank_top_module_name + '.mapped.htm.ascii', 'r')
                  as file):
                filedata = file.read()
            m = re.search('Total cell area: *([0-9.]*)', filedata)
            if m:
                self.designArea = float(m.group(1))
                log.info("Completed the APR for the design successfully %s" % self.bank_top_module_name)
            else:
                log.error('APR Failed, exiting the run. Please check the reports')
                sys.exit(1)
            os.chdir(self.memgendir)

        def gen_two_or_four_mb():

            self.mb_hir2_top_module_name = f'sram_hir2_mb_bank_{self.no_banks}{self.sram_bank_config[0]}rows_{self.sram_bank_config[1]}cols'

            self.mb_hir2_vlog_dir = os.path.join(self.runfilesdir, f'verilog/{self.mb_hir2_top_module_name}')

            self.mb_hir2_gen_dir = os.path.join(self.genPrivatedir, self.mb_hir2_top_module_name)

            self.mb_hir2_macro_dir = os.path.join(self.mb_hir2_gen_dir, f'blocks/{self.bank_top_module_name}/export')
            self.mb2_hir2_macro_gen_scripts_dir = os.path.join(self.mb_hir2_gen_dir, 'scripts')
            self.mb2_hir2_macro_src_dir = os.path.join(self.mb_hir2_gen_dir, 'src')

            mb_verilog_gen()
            # Create a check if the bank verilog generation is successful or not. Will add later.
            mb_layout_data_prep()
            mb_synthesis()
            mb_apr()

        if self.no_hir in [2, 4]:
            self.generate_bank(self.tech_config_dic, self.sram_bank_config, self.sram_bank_arch, self.sram_specs)

            gen_two_or_four_mb()

        else:
            self.generate_bank(self.tech_config_dic, self.sram_bank_config, self.sram_bank_arch, self.sram_specs)
            gen_two_or_four_mb()

            self.mb_hir3_top_module_name = f'sram_hir2_mb_bank_{self.no_banks}{self.sram_bank_config[0]}rows_{self.sram_bank_config[1]}cols'

            self.mb_hir3_vlog_dir = os.path.join(self.runfilesdir, f'verilog/{self.mb_hir3_top_module_name}')

            self.mb_hir3_gen_dir = os.path.join(self.genPrivatedir, self.mb_hir3_top_module_name)

            self.mb_hir3_macro_dir = os.path.join(self.mb_hir3_gen_dir, f'blocks/{self.bank_top_module_name}/export')
            self.mb_hir3_macro_gen_scripts_dir = os.path.join(self.mb_hir3_gen_dir, 'scripts')
            self.mb_hir3_macro_src_dir = os.path.join(self.mb_hir3_gen_dir, 'src')

            # Generate the level-3 hierarchy multi-bank memory, where four-bank memory is
            mb_verilog_gen()
            # Create a check if the bank verilog generation is successful or not. Will add later.
            mb_layout_data_prep()
            mb_synthesis()
            mb_apr()






