#!/usr/bin/env python3.7.3
###################################################################################
# Version : Beta                                                                  #
# Date    : Jan 31, 2022                                                          #
# Author  : Sumanth Kamineni                                                      #
# Contact : SumanthKamineni@virginia.edu                                          #
###################################################################################
# What's in the release?                                                          #
# Updated MemGen to support FinFET process and with-in bank optimization          #
# with auxcells.                                                                  #
# Current Version supports TSMC 65nm planar and GF 12nm FinFET processes.         #
# This version generates the multi-bank memory and its associated                 #
# (GDS, LEF, LIB, DB)  files for the given user specifications with design-space  #
# exploration and optimization                                                    #
# This release includes verilog generation, synthesis and auto place & route       #
###################################################################################

import os
import sys
# import re
import logging
from optparse import OptionParser
# import shutil
# import subprocess as sp
# import matplotlib.pyplot as p
import numpy as np
# from itertools import izip
# import json
# from typing import Any, Union

# Memory modules
from deo.deo import DEO
from macro_gen.macro_gen import MacroGen

global log
log = logging.getLogger(__name__)


class PDKError(Exception):
    """
        Raised when all the required variables for PDK is not set
    """
    pass


class MemGen(MacroGen, DEO):
    """
        Wrapper Class on the memory macro generation. It takes the user spec and generates the memory macro.
        Inputs  : User spec in Yaml format.
        Outputs : Memory macro and its associated views for top-level SoC.
    """

    def __init__(self, **kwargs):
        """
            Initializes MemGen with the required attributes and generates memory.
        """
        print("Entered above")
        super(MemGen, self).__init__()
        # Initialize the parent classes.
        MacroGen.__init__(self)
        DEO.__init__(self)

        # Required Variables Initialization
        self.sram_name = ''
        self.mem_config_options = {}
        self.sram_specs = {}

        # Variables to hold the final SRAM parameters
        self.final_sram_config_point = []  # List: [banks, rows, cols]
        self.final_sram_ed_point = []  # List: [delay, energy]
        self.final_sram_arch = {}  # dic: {'row_periphery':{auxcells}, 'col_periphery':{auxcells},
        # 'bitcell_array': {auxcells}

        self.mem_spec = kwargs['mem_spec']
        self.node = kwargs['node']
        self.foundry = kwargs['foundry']
        self.sub_process = kwargs['sub_process']

        # Process
        self.genDir = os.path.dirname(os.path.abspath(__file__))  # Generator Directory
        self.genName = os.path.split(self.genDir)[1]

        # Setting the MemGen path as env variable
        os.environ['memgen_path'] = self.genDir

        # Setting the technology process information variables
        os.environ['node'] = self.node
        os.environ['foundry'] = self.foundry
        os.environ['sub_process'] = self.sub_process

        # Parse the tech collateral:
        self.tech_config_dic = self.get_tech_collaterals()

        # Setting the Auxcell library path as env variable
        os.environ['auxcell_lib_path'] = self.tech_config_dic['auxcells']['auxcells_lib_dir']

        # Obtain the technology specific auxcells from technology collateral file.
        self.auxcells_dic = self.tech_config_dic["auxcells"]

        # Generated files dir.
        self.runfilesdir = os.path.join(self.genDir, 'generated')

        try:
            os.mkdir(self.runfilesdir)
        except OSError:
            if os.path.exists(self.runfilesdir):
                log.debug("Directory already exists")
            else:
                log.error(f"Unable to create the dir, check the permissions of the run dir {self.runfilesdir}")
                sys.exit(1)

        # Check the environment to verify the required tools.
        self.check_toolenv()

        if kwargs['mode'] == 'verilog':
            self.make_sram_verilog()
        elif kwargs['mode'] == 'macro':
            self.make_sram_macro()
            # self.filemanage()
            log.info("Successfully generated the syntehsizable SRAM. Refer the outputs dir for all the outputs")

    def make_sram_macro(self):
        """
        Generates the SRAM macro by collecting the tech collaterals, updating the default auxcells with PDK specific
        info, exploring the design-space and running the macro generation.
        """
        # Parse the tech collateral:
        # self.tech_config_dic = self.get_tech_collaterals()
        # Obtain the memory specifications to be generated.
        self.sram_specs = self.get_mem_specs(self.mem_spec)
        # Obtain the SRAM architecture from defined SRAM class.
        self.sram_arch = self.get_sram_arch()
        # Update the default SRAM auxcells with the technology specific auxcells.
        self.updated_sram_arch = self.update_sram_auxcells(self.auxcells_dic, self.sram_arch)
        # Obtain the range of column-muxing supported by the PDK.
        self.tech_colmux_range = self.tech_config_dic["auxcells"]["col_mux_range"]
        # Obtain the architecture options for design space exploration
        self.no_words = self.sram_specs['no_words']
        self.word_size = self.sram_specs['word_size']
        self.mem_config_options = self.get_mem_config_options(self.no_words, self.word_size, self.tech_colmux_range)
        # Explore the design space, optimize the design and obtain the SRAM design point satisfying the Specs.
        self.final_sram_config_point, self.final_sram_ed_point, self.final_sram_arch = self._deo()
        # Generate the SRAM macro
        self._macro_gen(self.final_sram_config_point, self.final_sram_arch)

    def make_sram_verilog(self):
        """
        Generates only the SRAM verilog file in the verilog mode.
        :return:
        """
        # Parse the tech collateral:
        # self.tech_config_dic = self.get_tech_collaterals()
        # Obtain the memory specifications to be generated.
        self.sram_specs = self.get_mem_specs(self.mem_spec)
        # Obtain the SRAM architecture from defined SRAM class.
        self.sram_arch = self.get_sram_arch()  # Dic of Dic
        # Update the default SRAM auxcells with the technology specific auxcells.
        self.updated_sram_arch = self.update_sram_auxcells(self.auxcells_dic, self.sram_arch)
        # Obtain the range of column-muxing supported by the PDK.
        self.tech_colmux_range = self.tech_config_dic["auxcells"]["col_mux_range"]
        # Obtain the architecture options for design space exploration
        self.no_words = self.sram_specs['no_words']
        self.word_size = self.sram_specs['word_size']
        self.mem_config_options = self.get_mem_config_options(self.no_words, self.word_size, self.tech_colmux_range)

    # noinspection PyAttributeOutsideInit
    @staticmethod
    def get_mem_specs(mem_spec):
        """
        Parses the input spec file and creates the necessary variables.
        spec format = Yaml file.  Replacing Json --> Yaml for user flexibility
        """
        log.info(" Loading the memory specifications from the file %s" % mem_spec)
        from globals.global_utils import yaml_config_parser

        config = yaml_config_parser(mem_spec)
        sram_specs = {"sram_name": config["module_name"], "no_words": config["mem_specs"]["no_words"],
                      "word_size": config["mem_specs"]["word_size"],
                      "target_vdd": config["mem_specs"]["target_voltage"],
                      "target_freq": config["mem_specs"]["target_frequency"], "process_info": config["process_info"]}

        return sram_specs

    @staticmethod
    def get_sram_arch() -> dict:

        # Create the instance of the specificed architecture in the spec file.
        # access the bank architecture from that instance.

        from SRAM import sram_arch

        arch = sram_arch.SRAM6TArch()

        row_periphery = arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
        col_periphery = arch.bank_top["col_periphery"]
        bitcell_array = arch.bank_top["bitcell_array"]

        sram_components = dict(row_periphery=row_periphery, col_periphery=col_periphery, bitcell_array=bitcell_array)

        return sram_components

    def update_sram_auxcells(self, auxcells_dic, sram_default_components) -> dict:
        """
        Grabs the pdk specific auxcells from techonlogy collaterals, and
        updates the properties of MemGen SRAM defualt auxcells
        """
        row_periphery = sram_default_components[
            "row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
        col_periphery = sram_default_components["col_periphery"]
        bitcell_array = sram_default_components["bitcell_array"]

        def update_col_periphery_auxcells(col_periphery_to_be_updated: dict):
            for col_auxcell in col_periphery_to_be_updated.keys():
                col_periphery_to_be_updated[col_auxcell].update_cellname(
                    auxcells_dic["col_periphery"][col_auxcell]["name"])
                if auxcells_dic["col_periphery"][col_auxcell]["pin_info"] != {}:
                    col_periphery_to_be_updated[col_auxcell].update_pininfo(
                        auxcells_dic["col_periphery"][col_auxcell]["pin_info"])
                col_periphery_to_be_updated[col_auxcell].update_orientations(
                    auxcells_dic["col_periphery"][col_auxcell]["orientations"])

            return col_periphery

        def update_row_periphery_auxcells(row_periphery_to_be_updated):
            for row_auxcell in row_periphery_to_be_updated.keys():
                row_periphery_to_be_updated[row_auxcell].update_cellname(
                    auxcells_dic["row_periphery"][row_auxcell]["name"])
                if auxcells_dic["row_periphery"][row_auxcell]["pin_info"] != {}:
                    row_periphery_to_be_updated[row_auxcell].update_pininfo(
                        auxcells_dic["row_periphery"][row_auxcell]["pin_info"])
                row_periphery_to_be_updated[row_auxcell].update_orientations(
                    auxcells_dic["row_periphery"][row_auxcell]["orientations"])

            return row_periphery

        def update_bitcell_array_auxcells(bitcell_array_to_be_updated):
            for bca_auxcell in bitcell_array_to_be_updated.keys():
                bitcell_array_to_be_updated[bca_auxcell].update_cellname(
                    auxcells_dic["bitcell_array"][bca_auxcell]["name"])
                if auxcells_dic["bitcell_array"][bca_auxcell]["pin_info"] != {}:
                    bitcell_array_to_be_updated[bca_auxcell].update_pininfo(
                        auxcells_dic["bitcell_array"][bca_auxcell]["pin_info"])
                bitcell_array_to_be_updated[bca_auxcell].update_orientations(
                    auxcells_dic["bitcell_array"][bca_auxcell]["orientations"])

            return bitcell_array

        col = update_col_periphery_auxcells(col_periphery)
        row = update_row_periphery_auxcells(row_periphery)
        bca = update_bitcell_array_auxcells(bitcell_array)

        return dict(row_periphery=row, col_periphery=col, bitcell_array=bca)

    def _deo(self) -> [list, list, dict]:
        """
        Explores the design space of SRAM and determines the components satisfying the user specifications.
        Returns the design decisions and the corresponding auxcells, which will be passed to macro generator.
        """
        print("Entered, DEO")
        # Explore the design space and obtain the pareto points for the given architecture and the user specificaitons.
        self.ppo_sram_ed, self.ppo_arch_points = self.get_sram_pareto(self.tech_config_dic,
                                                                      self.mem_config_options,
                                                                      self.updated_sram_arch,
                                                                      self.sram_specs)
        # Check if any of the pareto point satisfy the user specs.
        self.spec_satisfied_bool = self.check_pareto_points(self.sram_specs, self.ppo_sram_ed)  # List with Bool values.

        if np.any(self.spec_satisfied_bool):
            self.spec_satisfied_config_points = self.ppo_arch_points[self.spec_satisfied_bool]
            self.spec_satisfied_ed_points = self.ppo_sram_ed[self.spec_satisfied_bool]
            # Finding a minimum energy point, iff there are multiple points satisfying the user delay requirements.
            min_energy_point_index = np.where(min(self.spec_satisfied_ed_points[:][0]))

            spec_satisfied_mem_config_point_ = self.spec_satisfied_config_points[min_energy_point_index]
            spec_satisfied_mem_ed_point_ = self.spec_satisfied_config_points[min_energy_point_index]
            spec_satisfied_mem_arch = self.updated_sram_arch  # As the base case architecutre itself satisfied the
            # specs.

        else:  # Optimize the pareto points to satisfy the user specifications.
            spec_satisfied_mem_config_point_ = []
            spec_satisfied_mem_ed_point_ = []
            spec_satisfied_mem_arch = {}

            # Optimize the pareto points to satisfy the user specifications.
            # if not final_sram_point
            # self.final_sram_arch = self.optimization()

        return spec_satisfied_mem_config_point_, spec_satisfied_mem_ed_point_, spec_satisfied_mem_arch

    def _macro_gen(self, final_sram_config_point, final_sram_arch):
        """
               Generates the macro layout starting with bank generation followed by the multi-bank generation.
               :return:
        """
        self.banks = final_sram_config_point[0]
        self.sram_bank_config = [final_sram_config_point[1], final_sram_config_point[2]] # [Rows, cols]

        # Determine the number of hierarchies
        if self.banks == 1:
            self.no_generation_hierarchies = 1  # Only one bank memory
        if self.banks in [2, 4]:
            self.no_generation_hierarchies = 2  # 1 for bank generation and 2 for either 2 or 4 bank generation.
        elif self.banks > 4:
            self.no_generation_hierarchies = 3  # 1 for bank, 2 for 4 bank memory and the 3 for top multi-bank memory.

        # generation.

        if self.no_generation_hierarchies == 1:
            self.generate_bank(self.tech_config_dic, self.sram_bank_config, final_sram_arch, self.sram_specs)
        else:
            self.generate_multi_bank(self.tech_config_dic, self.no_generation_hierarchies, self.banks, self.sram_bank_config, final_sram_arch, self.sram_specs)

        # Get the cell area estimate from synthesis report to check if synthesis is done.
        # with open(self.digitalflowdir + '/reports/dc/' + self.sram_name + '.mapped.area.rpt', 'r')as file:
        #     filedata = file.read()
        # m = re.search('Total cell area: *([0-9.]*)', filedata)
        # if m:
        #     self.coreCellArea = float(m.group(1))
        #     log.info("Completed the synthesis for the design %s" % self.sram_name)
        # else:
        #     log.error('Synthesis Failed')
        #     sys.exit(1)
        # os.chdir(rundir)

        # Check if the APR is done.
        # with open(self.digitalflowdir + '/reports/innovus/' + self.sram_name + '.main.htm.ascii', 'r') as file:
        #     filedata = file.read()
        # m = re.search('Total area of Chip: ([0-9.]*)', filedata)
        # if m:
        #     self.designArea = float(m.group(1))
        #     log.info("Completed the APR for the design %s" % self.sram_name)
        # else:
        #     log.error('APR Failed')
        #     sys.exit(1)
        # os.chdir(rundir)

    def get_tech_collaterals(self):
        from globals.global_utils import yaml_config_parser
        config_file = f'collateral--{self.node}nm--{self.foundry}--{self.sub_process}.yaml'
        tech_collateral_config = os.path.join(self.genDir, 'tech_collaterals', config_file)

        tech_config_dic = yaml_config_parser(tech_collateral_config)

        return tech_config_dic

    @staticmethod
    def check_toolenv():

        from globals import toolenv_check

        toolenv_check.toolenv()


def main():
    parser = OptionParser()
    parser.add_option('-m', '--mode',
                      type='string',
                      dest='mode',
                      help='''Mode in which MemGen has to run. Supported options are "verilog" and "macro". 
                      "verilog" is default mode.
                         Ex: -m macro or --Mode= verilog''',
                      default='verilog')
    parser.add_option('-s', '--specfile',
                      type='string',
                      dest='mem_spec',
                      help='''Configuration file in Json format with Specifications of the memory to be generated.
                         Ex: -c memgen_config.json or --Config= memgen_config.json ''',
                      default='')
    parser.add_option('-o', '--outputDir',
                      type='string',
                      dest='opdir',
                      help='''Output directory: A place holder for all the memory output.
                         Ex: -output ./output/SRAM  or --Output= ./output/SRAM ''',
                      default='')
    parser.add_option('-f', '--foundry',
                      type='string',
                      dest='foundry',
                      help='''Foundry process info the memory to be generated.
                         Ex: -f tsmc  or --foundry= tsmc ''',
                      default='')
    parser.add_option('-n', '--node',
                      type='string',
                      dest='node',
                      help='''Technology node info the SRAM has to be generated
                      Ex: -n "65" or --Node="65" ''',
                      default='')
    parser.add_option('-p', '--sub_process',
                      type='string',
                      dest='sub_process',
                      help='''Flavors of the process such as lp, gp.
                      Ex: -p "lp" or --sub_process="gp" ''',
                      default='')
    parser.add_option("--debug",
                      action="store_true",
                      dest='log_debug',
                      help="Setting this value to True enables logging in Debug mode",
                      default=False)

    (options, argv) = parser.parse_args()

    p_options = {'mode': options.mode, 'mem_spec': options.mem_spec, 'op_dir': options.opdir,
                 'foundry': options.foundry, 'node': options.node, 'sub_process': options.sub_process}

    # Gets the directory structure absoulte paths
    # global rundir  # , tdir, ViProdir
    rundir = os.getcwd()  # Top level directory where MemGen is triggered.

    #######################
    # ##### LOGGING ##### #
    #######################

    logFile = os.path.join(rundir, 'MemGen.log')
    if options.log_debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(filename=logFile, filemode='w',
                        format='%(filename)s:%(lineno)d - %(asctime)s - %(levelname)s -> %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S')
    log.setLevel(loglevel)
    stdouth = logging.StreamHandler(sys.stdout)  # Used to direct the logging into log file as well as stdout.
    log.addHandler(stdouth)

    #####################################
    # Checking the command line options #
    #####################################

    if not os.access(rundir, os.W_OK):
        log.error(
            f'Do not have the write permissions of the run directory {rundir}. Can not run the tool. Hence Exiting...')
        log.error('Ensure the %s directory has the write permissions and re-run the tool.' % rundir)
        sys.exit(1)
    if p_options['mem_spec'] in ['', ' ']:
        log.error(
            'Memory specification file is not specified. Can not determine the specifications to generate the SRAM. '
            'Exting MemGen.')
        log.error('Please specify the configuration file using the command line option -s and re-run the tool.')
    if not os.path.isfile(p_options['mem_spec']):
        log.error(f"{p_options['mem_spec']} file does not exist. Can not proceed further. Exiting...")
        log.error('Provide a valid config file and re-run the MemGen')
        sys.exit(1)
    if p_options['op_dir'] in ['', ' ']:
        log.info('The output directory is not specified.')
        p_options['op_dir'] = os.path.join(rundir, 'outputs')
        log.info(f"Using the {p_options['op_dir']} output directory for storing all the outputs")
        try:
            os.mkdir(p_options['op_dir'])
        except OSError:
            if os.path.exists(p_options['op_dir']):
                log.debug("Directory already exists")
            else:
                log.error(f"Unable to create the dir, check the permissions of the run dir {self.runfilesdir}")
                sys.exit(1)
    else:
        if not os.path.isdir(p_options['op_dir']):
            log.warning(f'The specified output dir: {p_options["op_dir"]} does not exists.')
            if os.access(os.path.dirname(p_options['op_dir']), os.W_OK):
                log.info(f"Creating {p_options['op_dir']} output dir to store all the inputs.")
                os.mkdir(p_options['op_dir'])
            else:
                log.error('Unable to create an specified output directory.Can not store the outputs. Exiting... ')
                sys.exit(1)
    if p_options['node'] in ['', ' ']:
        log.error('The process node information required to determine the technology kit is not provided. Can not '
                  'generate the tool. Exting....')
        log.error('Please specify the process node info and re-run the tool.')
        sys.exit(1)

    if p_options['foundry'] in ['', ' ']:
        log.error('The process foundry information required to determine the technology kit is not provided. Can not '
                  'generate the tool. Exting....')
        log.error('Please specify the process foundry info and re-run the tool.')
        sys.exit(1)

    if p_options['sub_process'] in ['', ' ']:
        log.error(
            'The sub_process information required to determine the technology kit is not provided. Can not generate '
            'the tool. Exting....')
        log.error('Please specify the process node info and re-run the tool.')
        sys.exit(1)

    # MemGen(p_options)
    MemGen(mode=options.mode, mem_spec=options.mem_spec, op_dir=options.opdir, foundry=options.foundry,
           node=options.node, sub_process=options.sub_process)


if __name__ == '__main__':
    main()
