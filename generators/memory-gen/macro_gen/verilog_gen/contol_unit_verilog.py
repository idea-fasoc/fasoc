import math
import sys


class ControlUnitVerilogGen:
    """
    Generates the row-periphery module along with auxcell modules for the given architecture and specifications.
    """

    def __init__(self, sram_bank_config, sram_specs, tech_config_dic):

        self.word_size = sram_specs['word_size']
        self.bank_rows = sram_bank_config[0]
        self.bank_cols = sram_bank_config[1]
        self.tech_config_dic = tech_config_dic

        # Colmux ratio from the architecture point.
        self.bank_col_mux = int(self.bank_cols / self.word_size)

        # # Module Name
        self.cu_module_name = f'control_unit_{self.bank_rows}rows_{self.bank_cols}cols'
        self.cu_fh = open(f"{self.cu_module_name}.v", 'w')
        self.cu_fh.write("`timescale 1ns / 1ns\n")

        # Collects all the pins of all auxcells to compare with the row_periphery module
        self.auxcell_pin_collection = {}

    def generate_decoder_modules(self, decoder_name, no_input_bits, no_output_bits):
        """
        Generates the single row (1 dimension) and multi-columns (as specified by sram_arch) auxcells verilog module.
        """
        self.dec_fh = open(f'{decoder_name}.v', 'w')

        # #####################################
        # ##### Write the verilog module. #####
        # #####################################

        self.dec_fh.write('`timescale 1ns / 1ns\n\n')
        self.dec_fh.write(f"module  {decoder_name} ( Out, In, En);\n")
        self.dec_fh.write(f"   input  En;\n\n")
        self.dec_fh.write(f"   output reg [{no_output_bits - 1}:0]  Out;\n\n")
        self.dec_fh.write(f"   input [{no_input_bits - 1}:0]  In;\n\n")

        self.dec_fh.write(f"   always @(In, En) begin\n")
        self.dec_fh.write(f"    if (En) begin\n")
        self.dec_fh.write(f"         case(In)\n")
        # Converting decimal to binary and making the bitlength as per the requirement.
        # bin(num)[2:].zfill(lengthofbitstring]
        for c in range(no_output_bits):
            self.dec_fh.write(
                f"            {no_input_bits}'b{bin(c)[2:].zfill(no_input_bits)}: "
                f"Out={no_output_bits}'b{bin(int(math.pow(2, c)))[2:].zfill(no_output_bits)};\n")
        self.dec_fh.write("         endcase\n")
        self.dec_fh.write("    end\n")
        self.dec_fh.write(f"    else begin\n")
        self.dec_fh.write(f"         Out={no_output_bits}'b{bin(0)[2:].zfill(no_output_bits)};\n")
        self.dec_fh.write(f"    end\n")
        self.dec_fh.write(f"   end\n")
        self.dec_fh.write("endmodule\n")

        self.dec_fh.close()

    def generate_delay_modules(self):
        pass

    def generate_control_unit_top_module(self, cu_module_pininfo: dict):
        """
        Generates the row-periphery array verilog module along with the respective auxcell verilog module instances
        generated through  generate_auxcell_module

        :param cu_module_pininfo: Pin information of control unit top module defined in the SRAM architecture.
        :return: None
        """
        self.cu_module_pininfo = cu_module_pininfo

        # Generate the decoder and delay modules for the given architecture point and the specified auxcells.

        #############################################################################################
        # ########## Determine the pre-decoder variables for the row and column-periphery ###########
        #############################################################################################

        ########################
        # # For Col Periphery ##
        ########################

        if math.floor(math.log2(self.bank_col_mux)) != math.ceil(math.log2(self.bank_col_mux)):
            print(f"The col mux {self.bank_col_mux} is not a power of 2. Can not proceed with "
                  "generation of colum periphery pre-decoders.")
            sys.exit(1)

        self.no_cp_addr_bits = int(math.log2(self.bank_col_mux))
        self.cp_decoder_name = f'decoder_{self.no_cp_addr_bits}_to_{self.bank_col_mux}'

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

        # The row periphery is implemented such that no_bottom_rows = self.no_bottom_LSB_pre_decoded_bits *
        # self.no_bottom_MSB_pre_decoded_bits to reduce the gate count

        self.no_rp_bottom_LSB_addr_bits = int(math.ceil(self.no_rp_bottom_addr_bits / 2))
        self.no_rp_bottom_MSB_addr_bits = int(math.floor(self.no_rp_bottom_addr_bits / 2))

        self.no_rp_bottom_LSB_pre_decoded_bits = int(2 ** self.no_rp_bottom_LSB_addr_bits)
        self.no_rp_bottom_MSB_pre_decoded_bits = int(2 ** self.no_rp_bottom_MSB_addr_bits)

        self.no_rp_bottom_pre_decoded_bits = int(self.no_rp_bottom_LSB_pre_decoded_bits + \
                                             self.no_rp_bottom_MSB_pre_decoded_bits)

        # The top row periphery variables
        self.no_rp_top_addr_bits = int(math.log2(self.no_rp_top_rows))

        self.no_rp_top_LSB_addr_bits = int(math.ceil(self.no_rp_top_addr_bits / 2))
        self.no_rp_top_MSB_addr_bits = int(math.floor(self.no_rp_top_addr_bits / 2))

        self.no_rp_top_LSB_pre_decoded_bits = int(2 ** self.no_rp_top_LSB_addr_bits)
        self.no_rp_top_MSB_pre_decoded_bits = int(2 ** self.no_rp_top_MSB_addr_bits)

        self.no_rp_top_pre_decoded_bits = int(self.no_rp_top_LSB_pre_decoded_bits + self.no_rp_top_MSB_pre_decoded_bits)

        # Note:
        # With the way row periphery is implemented, the bottom and top row periphery variables would be same. So, will
        # use only the bottom variables for the remainder of the code.

        # self.no_rp_addr_bits = int(self.no_rp_bottom_addr_bits + self.no_rp_top_addr_bits)
        self.no_rp_addr_bits = int(self.no_rp_bottom_addr_bits + 1) # Because we need one addr between to choose top and
        # bottom rows.
        print("rp_bottom_addr_bits", self.no_rp_bottom_addr_bits)
        print("rp_top_addr_bits", self.no_rp_top_addr_bits)
        print("rp_addr_bits", self.no_rp_addr_bits)

        ###############################################################################
        # ########## Generate the pre-decoder modules for the row-periphery ###########
        ###############################################################################

        self.rp_lsb_decoder_name = f"decoder_{self.no_rp_bottom_LSB_addr_bits}_to_" \
                              f"{self.no_rp_bottom_LSB_pre_decoded_bits}"
        self.rp_msb_decoder_name = f"decoder_{self.no_rp_bottom_MSB_addr_bits}_to_" \
                              f"{self.no_rp_bottom_MSB_pre_decoded_bits}"
        if self.rp_lsb_decoder_name != self.rp_msb_decoder_name:
            # If the bottom LSB and MSB address bits are not same, generate two different types of decoders
            # Generate the decoders:
            # LSB decoder
            self.generate_decoder_modules(self.rp_lsb_decoder_name, int(self.no_rp_bottom_LSB_addr_bits),
                                          int(self.no_rp_bottom_LSB_pre_decoded_bits))
            # MSB decoder
            self.generate_decoder_modules(self.rp_msb_decoder_name, int(self.no_rp_bottom_MSB_addr_bits),
                                          int(self.no_rp_bottom_MSB_pre_decoded_bits))

        else:
            self.generate_decoder_modules(self.rp_lsb_decoder_name, int(self.no_rp_bottom_LSB_addr_bits),
                                          int(self.no_rp_bottom_LSB_pre_decoded_bits))

        #################################################################################
        # ########## Generate the pre-decoder module for the column-periphery ###########
        #################################################################################

        self.generate_decoder_modules(self.cp_decoder_name, int(self.no_cp_addr_bits), int(self.bank_col_mux))

        ###################################################
        # ########## Generate the Delay modules ###########
        ###################################################

        ##########################################################
        # ########## Generate the Control Unit  module ###########
        ##########################################################

        self.no_bank_addr_bits = self.no_rp_addr_bits + self.no_cp_addr_bits
        print("no col addr bits", self.no_cp_addr_bits)
        print("no_bank_AddR_bits", self.no_bank_addr_bits)

        # Extract the pins from the definition.
        module_input_pins = []
        module_output_pins = []
        module_inout_pins = []
        module_wires = []
        module_reg = []

        for keys, values in cu_module_pininfo.items():
            if values[1] == 'input':
                module_input_pins.append(keys)
            elif values[1] == 'output':
                module_output_pins.append(keys)
            elif values[1] == 'inout':
                module_inout_pins.append(keys)
            elif values[1] == 'wire':
                module_wires.append(keys)
            elif values[1] == 'reg':
                module_reg.append(keys)

        # Collect all the input, input and output pins of the top-level module
        cu_module_pin_list = module_input_pins + module_output_pins + module_inout_pins
        # bca_pin_info = []
        # for bcpk in bca_module_pin_list:
        #     bca_pin_info.append('%s' % (cu_module_pininfo[bcpk][0]))

        # bca_module_pin_str = ', '.join(bca_pin_info)
        cu_module_pin_str = ', '.join(cu_module_pin_list)

        # #####################################
        # ##### Write the verilog module. #####
        # #####################################

        # Define the module name and the associated parameters.
        # Module with column instantiations.
        # No of column instantiations of specific auxcell column depends on auxcell.
        #   # Bitcell and bitcell_end_cell-> bank_rows.
        #   # edge_cell and edge_end_cell -> 2.
        #   # strap_cell and strap_end_cell -> 1.
        if self.cp_decoder_name in [self.rp_lsb_decoder_name, self.rp_msb_decoder_name]:
            if self.rp_lsb_decoder_name != self.rp_msb_decoder_name:
                self.cu_fh.write(f'`include "{self.rp_lsb_decoder_name}.v"\n')
                self.cu_fh.write(f'`include "{self.rp_msb_decoder_name}.v"\n')
            else:
                self.cu_fh.write(f'`include "{self.rp_lsb_decoder_name}.v"\n')
        else:
            self.cu_fh.write(f'`include "{self.cp_decoder_name}.v"\n')
            if self.rp_lsb_decoder_name != self.rp_msb_decoder_name:
                self.cu_fh.write(f'`include "{self.rp_lsb_decoder_name}.v"\n')
                self.cu_fh.write(f'`include "{self.rp_msb_decoder_name}.v"\n')
            else:
                self.cu_fh.write(f'`include "{self.rp_lsb_decoder_name}.v"\n')

        self.cu_fh.write(f'`include "sram_cu_delay_module.v"\n')

        self.cu_fh.write(f"module {self.cu_module_name} ({cu_module_pin_str});\n")
        self.cu_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.cu_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.cu_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.cu_fh.write("   parameter word_size    = %d;\n" % self.word_size)
        self.cu_fh.write("   parameter addr_width   = %d;\n" % self.no_bank_addr_bits)
        self.cu_fh.write("   parameter pre_dec_b    = %d;\n" % self.no_rp_bottom_pre_decoded_bits)
        self.cu_fh.write("   parameter pre_dec_t    = %d;\n" % self.no_rp_top_pre_decoded_bits)

        # module Pin definitions -> based on the keys of pin_info defined under bitcell_array.
        for in_pin in module_input_pins:
            if list(cu_module_pininfo[in_pin][2].keys())[0] == 'bus':
                self.cu_fh.write(
                    "   input [%s-1:0] %s;\n" % (cu_module_pininfo[in_pin][2]['bus'], cu_module_pininfo[in_pin][0]))
            else:
                self.cu_fh.write("   input  %s;\n" % cu_module_pininfo[in_pin][0])

        for inout_pin in module_inout_pins:
            if list(cu_module_pininfo[inout_pin][2].keys())[0] == 'bus':
                self.cu_fh.write("   inout [%s-1:0] %s;\n" % (
                    cu_module_pininfo[inout_pin][2]['bus'], cu_module_pininfo[inout_pin][0]))
            else:
                self.cu_fh.write("   inout  %s;\n" % cu_module_pininfo[inout_pin][0])

        for out_pin in module_output_pins:
            if list(cu_module_pininfo[out_pin][2].keys())[0] == 'bus':
                self.cu_fh.write("   output [%s-1:0] %s;\n" % (
                    cu_module_pininfo[out_pin][2]['bus'], cu_module_pininfo[out_pin][0]))
            else:
                self.cu_fh.write("   output  %s;\n" % cu_module_pininfo[out_pin][0])

        for wire in module_wires:
            if list(cu_module_pininfo[wire][2].keys())[0] == 'bus':
                self.cu_fh.write(
                    "   wire [%s-1:0] %s;\n" % (cu_module_pininfo[wire][2]['bus'], cu_module_pininfo[wire][0]))
            else:
                self.cu_fh.write("   wire  %s;\n" % cu_module_pininfo[wire][0])

        i = 0

        self.cu_fh.write("\n\n\n")

        self.cu_fh.write("   assign clk_gated = CLK & CE ;\n")
        self.cu_fh.write("   assign WDEn      = WE & CE ;\n")
        self.cu_fh.write("   assign PCH       = ~(WDEnB & clk_gated) ;\n")
        self.cu_fh.write("   assign WL_EN     = ~clk_gated & PCH ;\n")
        self.cu_fh.write("   assign SAEnB     = PCH ;\n")
        self.cu_fh.write("   assign WDEnB     = ~WDEn ;\n")

        # Decoder instantiations:
        # Col Decoder
        self.cu_fh.write(f"   wire [{self.bank_col_mux - 1}:0] decode_CM ;\n")
        self.cu_fh.write(
            f"   {self.cp_decoder_name} cdec0 (.Out(decode_CM), .In(ADDR[{self.no_cp_addr_bits - 1}:0]), .En(CE)) "
            f";\n")

        self.cu_fh.write("   assign CMEnB = ~decode_CM ;\n")
        self.cu_fh.write("   assign CMEn =  decode_CM ;\n")

        # Bottom decoders

        self.cu_fh.write(
            f"   {self.rp_lsb_decoder_name} rdec0 (.Out(row_predec_b[{self.no_rp_bottom_LSB_pre_decoded_bits - 1}:0]), "
            f".In(ADDR[{self.no_rp_bottom_LSB_addr_bits + self.no_cp_addr_bits - 1}:{self.no_cp_addr_bits}]), "
            f".En(~ADDR[{self.no_bank_addr_bits - 1}] & WL_EN)) ;\n")
        self.cu_fh.write(
            f"   {self.rp_msb_decoder_name} rdec1 "
            f"(.Out(row_predec_b[{self.no_rp_bottom_pre_decoded_bits - 1}:{self.no_rp_bottom_LSB_pre_decoded_bits}]), "
            f".In(ADDR[{self.no_bank_addr_bits - 2}:{self.no_rp_bottom_LSB_addr_bits + self.no_cp_addr_bits}]),"
            f" .En(~ADDR[{self.no_bank_addr_bits - 1}] & WL_EN)) ;\n")

        # Top decoders
        self.cu_fh.write(
            f"   {self.rp_lsb_decoder_name} rdec2 (.Out(row_predec_t[{self.no_rp_top_LSB_pre_decoded_bits - 1}:0]), "
            f".In(ADDR[{self.no_rp_top_LSB_addr_bits + self.no_cp_addr_bits - 1}:{self.no_cp_addr_bits}]), "
            f".En(ADDR[{self.no_bank_addr_bits - 1}] & WL_EN)) ;\n")
        self.cu_fh.write(
            f"   {self.rp_msb_decoder_name} rdec3 "
            f"(.Out(row_predec_t[{self.no_rp_top_pre_decoded_bits - 1}:{self.no_rp_top_LSB_pre_decoded_bits}]), "
            f".In(ADDR[{self.no_bank_addr_bits - 2}:{ self.no_rp_top_LSB_addr_bits + self.no_cp_addr_bits}]), "
            f".En(ADDR[{self.no_bank_addr_bits - 1}] & WL_EN)) ;\n")

        self.cu_fh.write("   sram_cu_delay_module dm (.In(WDEnB & WL_EN), .Out(SAEn)) ;\n")

        self.cu_fh.write("   DLY4_X4N_A10P5PP84TR_C14 Id20 ( .A(SAEn),       .Y(wire_delay)) ;\n")
        self.cu_fh.write("   DLY4_X4N_A10P5PP84TR_C14 Id21 ( .A(wire_delay), .Y(DoutEn)) ;\n\n")
        self.cu_fh.write("endmodule\n\n\n\n")

        self.cu_fh.close()

        return cu_module_pininfo


if __name__ == '__main__':
    # For testing the bitcell_array_verilog only

    from SRAM import sram_arch

    bank_arch = sram_arch.SRAM6TArch()

    row_periphery = bank_arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col_periphery = bank_arch.bank_top["col_periphery"]
    bitcell_array = bank_arch.bank_top["bitcell_array"]

    control_unit_top_pininfo = bank_arch.control_unit_top_pininfo

    sram_bank_config = [128, 256]
    sram_specs = {'word_size': 64}

    dic = {'auxcells': {}}
    dic['auxcells']['bitcell_array'] = {}
    dic['auxcells']['bitcell_array']['bitcell'] = {}
    dic['auxcells']['bitcell_array']['bitcell']['no_rows'] = 2
    dic['auxcells']['bitcell_array']['bitcell']['no_cols'] = 1
    dic['auxcells']['bitcell_array']['bitcell_end_cell'] = {}
    dic['auxcells']['bitcell_array']['bitcell_end_cell']['no_rows'] = 2
    dic['auxcells']['bitcell_array']['bitcell_end_cell']['no_cols'] = 1
    dic['auxcells']['bitcell_array']['edge_cell'] = {}
    dic['auxcells']['bitcell_array']['edge_cell']['no_rows'] = 1
    dic['auxcells']['bitcell_array']['edge_cell']['no_cols'] = 2
    dic['auxcells']['bitcell_array']['edge_end_cell'] = {}
    dic['auxcells']['bitcell_array']['edge_end_cell']['no_rows'] = 1
    dic['auxcells']['bitcell_array']['edge_end_cell']['no_cols'] = 1
    dic['auxcells']['bitcell_array']['strap_cell'] = {}
    dic['auxcells']['bitcell_array']['strap_cell']['no_rows'] = 1
    dic['auxcells']['bitcell_array']['strap_cell']['no_cols'] = 2
    dic['auxcells']['bitcell_array']['strap_end_cell'] = {}
    dic['auxcells']['bitcell_array']['strap_end_cell']['no_rows'] = 1
    dic['auxcells']['bitcell_array']['strap_end_cell']['no_cols'] = 1

    # ControlUnitVerilogGen(sram_bank_config, sram_specs, dic)

    # Initialize each component Generation class.
    # dic = get_tech_collaterals('12nm', 'gf', 'lp')
    cu = ControlUnitVerilogGen(sram_bank_config, sram_specs, dic)

    # Generate each component.
    cu_pin_info = cu.generate_control_unit_top_module(control_unit_top_pininfo)
