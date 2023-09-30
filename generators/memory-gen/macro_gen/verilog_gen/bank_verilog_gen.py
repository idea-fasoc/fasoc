#!/usr/bin/env python3.7
import logging
import math
import sys

# Importing Component modules
from bitcell_array_verilog import BitcellArrayVerilogGen
from col_periphery_verilog import ColPeriVerilogGen
from row_periphery_verilog import RowPeriVerilogGen
from contol_unit_verilog import ControlUnitVerilogGen

log = logging.getLogger(__name__)


class BankVerilogGen:

    def __init__(self, sram_bank_config, sram_bank_arch, sram_specs, bank_module_name, tech_config_dic):
        """
        Generates the bank verilog file hiearachically for the Synthesis
        """
        self.word_size = sram_specs['word_size']
        self.bank_rows = sram_bank_config[0]
        self.bank_cols = sram_bank_config[1]
        self.tech_config_dic = tech_config_dic
        self.bank_module_name = bank_module_name

        # Determine the bank column muxing
        self.bank_col_mux = self.bank_cols / self.word_size

        # Determining the address Size:
        # no_addr_bits = no_addr_for128rows + no_addr_forcolmux
        self.addr_bits = math.log2(self.bank_rows) + math.log2(self.bank_col_mux)

        # Obtaining the top-level modules pin info from the defined SRAM Architecure.
        # This helps to let the users define their own pininfo instead of hard-coding it.
        # However, currently, updating the module pin_info similar to auxcell pin is not enabled. If needed,
        # the comp pin_info can be updated as part of a new architecture.
        from SRAM import sram_arch

        sram_arch = sram_arch.SRAM6TArch()

        # Collect the bank and the components pin ipininfo
        self.bank_top_pininfo = sram_arch.bank_top_pininfo
        # self.col_periphery_top_pininfo = sram_arch.col_periphery_top_pininfo
        # self.row_periphery_top_pininfo = sram_arch.row_periphery_top_pininfo
        # self.bitcell_array_top_pininfo = sram_arch.bitcell_array_top_pininfo
        self.control_unit_top_pininfo = sram_arch.control_unit_top_pininfo

        # Bank verilog file.
        self.bank_vlog = ".".join([self.bank_module_name, 'v'])

        self.bank_fh = open(self.bank_vlog, 'w')
        self.bank_fh.write("`timescale 1ns / 1ns\n")

        # Dic to collect all the components pins info.
        self.component_pin_collection = {}

        # Generate the bank verilog modules including each of the component modules.
        self.generate_bank_top_module(sram_bank_arch, sram_bank_config, sram_specs)

        # Close the file:
        self.bank_fh.close()

    def generate_component_modules(self, sram_bank_arch, sram_bank_config, sram_specs):
        print(sram_bank_arch)

        self.row_periphery = sram_bank_arch['row_periphery']
        self.col_periphery = sram_bank_arch['col_periphery']
        self.bitcell_array = sram_bank_arch['bitcell_array']

        # Initialize each component Generation class.
        cp = ColPeriVerilogGen(sram_bank_config, sram_specs, self.tech_config_dic)
        rp = RowPeriVerilogGen(sram_bank_config, sram_specs, self.tech_config_dic)
        bca = BitcellArrayVerilogGen(sram_bank_config, sram_specs, self.tech_config_dic)
        cu = ControlUnitVerilogGen(sram_bank_config, sram_specs, self.tech_config_dic)

        # Generate each component.
        # self.cp_pin_info = cp.generate_col_peri_top_module(self.col_periphery_top_pininfo, self.col_periphery)
        # self.rp_pin_info = rp.generate_row_peri_top_module(self.row_periphery_top_pininfo, self.row_periphery)
        # self.bca_pin_info = bca.generate_bitcell_array_top_module(self.bitcell_array_top_pininfo, self.bitcell_array)
        self.cu_pin_info = cu.generate_control_unit_top_module(self.control_unit_top_pininfo)

        # Collect each component pin info
        # self.component_pin_collection.update(self.cp_pin_info)
        # self.component_pin_collection.update(self.rp_pin_info)
        # self.component_pin_collection.update(self.bca_pin_info)
        self.component_pin_collection.update(self.cu_pin_info)

    def generate_bank_top_module(self, sram_bank_arch, sram_bank_config, sram_specs):
        """
        Generates the bank top verilog module along with the respective components verilog module instances.
        """

        # Generate the component modules and collect the pin info.
        self.generate_component_modules(sram_bank_arch, sram_bank_config, sram_specs)

        # Extract the pin types from the definition.
        module_input_pins = []
        module_output_pins = []
        module_inout_pins = []
        module_wires = []

        for keys, values in self.bank_top_pininfo.items():
            if values[1] == 'input':
                module_input_pins.append(keys)
            elif values[1] == 'output':
                module_output_pins.append(keys)
            elif values[1] == 'inout':
                module_inout_pins.append(keys)
            elif values[1] == 'wire':
                module_wires.append(keys)

        # ########################################################################
        # ########## Determine the variables for row and col periphery ###########
        # ########################################################################

        ########################
        # # For Row Periphery ##
        ########################
        # Divide the rows into bottom half and top half.
        if math.floor(math.log2(self.bank_rows)) != math.ceil(math.log2(self.bank_rows)):
            print("The number of bank rows are not a power of 2 and so can not be divided into top and bottom halves."
                  " Can not proceed with row periphery. Please check the no of rows are power of 2 and can be divided "
                  "into two halves.")
            sys.exit(1)

        # The entire row periphery is divided into two halves

        self.no_rp_bottom_rows = int(self.bank_rows / 2)
        self.no_rp_top_rows = int(self.bank_rows / 2)

        # The bottom row periphery variables
        self.no_rp_bottom_addr_bits = int(math.log2(self.no_rp_bottom_rows))

        self.no_rp_bottom_pre_decoded_bits = int(2 ** int(math.floor(self.no_rp_bottom_addr_bits / 2)) + \
                                          2 ** int(math.ceil(self.no_rp_bottom_addr_bits / 2)))

        # The top row periphery variables
        self.no_rp_top_addr_bits = int(math.log2(self.no_rp_top_rows))

        self.no_rp_top_pre_decoded_bits = int(2 ** int(math.floor(self.no_rp_top_addr_bits / 2)) + \
                                                 2 ** int(math.ceil(self.no_rp_top_addr_bits / 2)))

        self.no_rp_addr_bits = int(self.no_rp_bottom_addr_bits + 1) # Because we need one addr between to choose top and
        # bottom rows.

        ########################
        # # For Col Periphery ##
        ########################

        if math.floor(math.log2(self.bank_col_mux)) != math.ceil(math.log2(self.bank_col_mux)):
            print(f"The col mux {self.bank_col_mux} is not a power of 2. Can not proceed with "
                  "generation of colum periphery pre-decoders.")
            sys.exit(1)

        self.no_cp_addr_bits = int(math.log2(self.bank_col_mux))
        self.cp_decoder_name = f'decoder_{self.no_cp_addr_bits}_to_{self.bank_col_mux}'

        # Determine the bank address bits
        self.no_bank_addr_bits = int(self.no_rp_addr_bits + self.no_cp_addr_bits)

        # Top-level module defintion.
        bank_module_pin_list = module_input_pins + module_output_pins + module_inout_pins
        bank_module_pin_str = ', '.join(bank_module_pin_list)

        # Include the component verilog files on bank top
        # The naming convention is standardized between the component verilog generation and here.
        col_periphery_file_include = f'col_periphery_{self.bank_rows}rows_{self.bank_cols}cols.v'
        row_periphery_file_include = f'row_periphery_{self.bank_rows}rows_{self.bank_cols}cols.v'
        bitcell_array_file_include = f'bitcell_array_{self.bank_rows}rows_{self.bank_cols}cols.v'
        control_unit_file_include = f'control_unit_{self.bank_rows}rows_{self.bank_cols}cols.v'

        self.bank_fh.write('\n\n')
        self.bank_fh.write(f'`include "{col_periphery_file_include}"\n')
        self.bank_fh.write(f'`include "{row_periphery_file_include}"\n')
        self.bank_fh.write(f'`include "{bitcell_array_file_include}"\n')
        self.bank_fh.write(f'`include "{control_unit_file_include}"\n')
        self.bank_fh.write('\n\n')
        self.bank_fh.write('\n\n')

        # Define the bank top module
        self.bank_fh.write(f"module {self.bank_module_name} ({bank_module_pin_str});\n")
        self.bank_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.bank_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.bank_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.bank_fh.write("   parameter word_size    = %d;\n" % self.word_size)
        self.bank_fh.write("   parameter pre_dec_b    = %d;\n" % self.no_rp_bottom_pre_decoded_bits)
        self.bank_fh.write("   parameter pre_dec_t    = %d;\n" % self.no_rp_top_pre_decoded_bits)
        self.bank_fh.write("   parameter addr_width    = %d;\n" % self.no_bank_addr_bits)

        for in_pin in module_input_pins:
            print(self.bank_top_pininfo[in_pin])
            if list(self.bank_top_pininfo[in_pin][2].keys())[0] == 'bus':
                self.bank_fh.write("   input [%s-1:0] %s;\n" % (self.bank_top_pininfo[in_pin][2]['bus'], in_pin))
            else:
                self.bank_fh.write("   input  %s;\n" % in_pin)

        for inout_pin in module_inout_pins:
            if list(self.bank_top_pininfo[inout_pin][2].keys())[0] == 'bus':
                self.bank_fh.write("   inout [%s-1:0] %s;\n" % (self.bank_top_pininfo[inout_pin][2]['bus'], inout_pin))
            else:
                self.bank_fh.write("   inout  %s;\n" % inout_pin)

        for out_pin in module_output_pins:
            if list(self.bank_top_pininfo[out_pin][2].keys())[0] == 'bus':
                self.bank_fh.write("   output [%s-1:0] %s;\n" % (self.bank_top_pininfo[out_pin][2]['bus'], out_pin))
            else:
                self.bank_fh.write("   input  %s;\n" % out_pin)

        for wire in module_wires:
            if list(self.component_pin_collection[wire][2].keys())[0] == 'bus':
                self.bank_fh.write("   wire [%s-1:0] %s;\n" % (self.component_pin_collection[wire][2]['bus'], wire))
            else:
                self.bank_fh.write("   wire  %s;\n" % wire)

        i = 0

        bca_module_inst_pins = {}
        for k, v in self.bitcell_array_top_pininfo.items():
            if not v[1] in ['power', 'ground', 'wire']:
                bca_module_inst_pins[k] = v

        bca_module_inst_pins_list = []

        # Pin Connection by name. values = pin from auxcells. So, the pin connection is '.value(key)'
        for k in bca_module_inst_pins:
            bca_module_inst_pins_list.append('.%s(%s)' % (bca_module_inst_pins[k][0], k))

        cp_module_inst_pins = {}
        for k, v in self.col_periphery_top_pininfo.items():
            if not v[1] in ['power', 'ground', 'wire']:
                cp_module_inst_pins[k] = v

        cp_module_inst_pins_list = []
        for k in cp_module_inst_pins:
            cp_module_inst_pins_list.append('.%s(%s)' % (cp_module_inst_pins[k][0], k))

        rp_module_inst_pins = {}
        for k, v in self.row_periphery_top_pininfo.items():
            if not v[1] in ['power', 'ground', 'wire']:
                rp_module_inst_pins[k] = v

        rp_module_inst_pins_list = []
        for k in rp_module_inst_pins:
            rp_module_inst_pins_list.append('.%s(%s)' % (rp_module_inst_pins[k][0], k))

        cu_module_inst_pins = {}
        for k, v in self.control_unit_top_pininfo.items():
            if not v[1] in ['power', 'ground', 'wire']:
                 cu_module_inst_pins[k] = v

        cu_module_inst_pins_list = []
        for k in cu_module_inst_pins:
            cu_module_inst_pins_list.append('.%s(%s)' % (cu_module_inst_pins[k][0], k))

        self.bank_fh.write(
            f"   bitcell_array_{self.bank_rows}rows_{self.bank_cols}cols bca ({', '.join(bca_module_inst_pins_list)});\n")
        self.bank_fh.write(
            f"   col_periphery_{self.bank_rows}rows_{self.bank_cols}cols cp ({', '.join(cp_module_inst_pins_list)});\n")
        self.bank_fh.write(
            f"   row_periphery_{self.bank_rows}rows_{self.bank_cols}cols rp ({', '.join(rp_module_inst_pins_list)});\n")
        self.bank_fh.write(
            f"   control_unit_{self.bank_rows}rows_{self.bank_cols}cols cu ({', '.join(cu_module_inst_pins_list)});\n")

        self.bank_fh.write("endmodule\n\n\n\n")


if __name__ == "__main__":
    # For bank_verilog_gen.py testing purpose only.
    sys.path.append('')
    from SRAM import sram_arch

    arch = sram_arch.SRAM6TArch()

    row = arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col = arch.bank_top["col_periphery"]
    bca = arch.bank_top["bitcell_array"]

    sram_bank_arch = dict(row_periphery=row, col_periphery=col, bitcell_array=bca)
    print("SRAM Arch here is ", sram_arch)
    sram_bank_config = [512, 512]
    sram_specs = {'word_size': 128}

    tech_config = ''
    # tech_config = 'collateral--12nm--gf--lp.yaml'
    import yaml
    with open(tech_config, 'r') as th:
        dic = yaml_config_dic = yaml.safe_load(th)
    # dic = {}
    # dic['auxcells'] = {}
    # dic['auxcells']['bitcell_array'] = {}
    # dic['auxcells']['bitcell_array']['bitcell'] = {}
    # dic['auxcells']['bitcell_array']['bitcell']['no_rows'] = 2
    # dic['auxcells']['bitcell_array']['bitcell']['no_cols'] = 1
    # dic['auxcells']['bitcell_array']['bitcell_end_cell'] = {}
    # dic['auxcells']['bitcell_array']['bitcell_end_cell']['no_rows'] = 2
    # dic['auxcells']['bitcell_array']['bitcell_end_cell']['no_cols'] = 1
    # dic['auxcells']['bitcell_array']['edge_cell'] = {}
    # dic['auxcells']['bitcell_array']['edge_cell']['no_rows'] = 1
    # dic['auxcells']['bitcell_array']['edge_cell']['no_cols'] = 2
    # dic['auxcells']['bitcell_array']['edge_end_cell'] = {}
    # dic['auxcells']['bitcell_array']['edge_end_cell']['no_rows'] = 1
    # dic['auxcells']['bitcell_array']['edge_end_cell']['no_cols'] = 1
    # dic['auxcells']['bitcell_array']['strap_cell'] = {}
    # dic['auxcells']['bitcell_array']['strap_cell']['no_rows'] = 1
    # dic['auxcells']['bitcell_array']['strap_cell']['no_cols'] = 2
    # dic['auxcells']['bitcell_array']['strap_end_cell'] = {}
    # dic['auxcells']['bitcell_array']['strap_end_cell']['no_rows'] = 1
    # dic['auxcells']['bitcell_array']['strap_end_cell']['no_cols'] = 1

    BankVerilogGen(sram_bank_config, sram_bank_arch, sram_specs,
                   f'sram_bank_{sram_bank_config[0]}rows_{sram_bank_config[1]}cols', dic)
