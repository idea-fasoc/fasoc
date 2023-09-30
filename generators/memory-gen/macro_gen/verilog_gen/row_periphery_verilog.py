import math
import sys


class RowPeriVerilogGen:
    """
    Generates the row-periphery module along with auxcell modules for the given architecture and specifications.
    """

    def __init__(self, sram_bank_config, sram_specs, tech_config_dic):

        self.word_size = sram_specs['word_size']
        self.bank_rows = sram_bank_config[0]
        self.bank_cols = sram_bank_config[1]
        self.tech_config_dic = tech_config_dic

        # Colmux ratio from the architecture point.
        self.bank_col_mux = self.bank_cols / self.word_size

        # Module Name
        self.rp_module_name = f'row_periphery_{self.bank_rows}rows_{self.bank_cols}cols'
        self.rp_fh = open(f"{self.rp_module_name}.v", 'w')
        self.rp_fh.write("`timescale 1ns / 1ns\n")

        # Collects all the pins of all auxcells to compare with the row_periphery module
        self.auxcell_pin_collection = {}

        # Generate the modules for the given architecture point and the specified auxcells.
        # for auxcell in row_periphery.keys():

        #     # getattr(self, auxcell)(row_periphery[auxcell], sram_specs, sram_arch)
        #     pin_info = self.generate_auxcell_module(self.rp_fh, row_periphery[auxcell])
        #     self.auxcell_pin_collection.update(pin_info)

        # self.generate_row_peri_top_module(self.rp_fh, rp_module_pininfo, row_periphery)

    def generate_auxcell_module(self, auxcell):
        """
        Generates the verilog module for the speicified auxcell
        :param self.rp_fh: File handler to which the verilog module has to be written.
        :param auxcell: Auxcell instance which enables accessing the specific properties.
        :return: All the auxcell pins in the form of dictionary.
        """

        # Collect the auxcell properties.
        auxcell_name = auxcell.get_cellname()
        auxcell_pininfo = auxcell.get_pininfo()

        auxcell_input_pins = auxcell.get_input_pins()
        auxcell_output_pins = auxcell.get_output_pins()
        auxcell_inout_pins = auxcell.get_inout_pins()

        # Collect all auxcell pins except the power pins.
        auxcell_pins_list = auxcell_input_pins + auxcell_output_pins + auxcell_inout_pins
        auxcell_pin_str = ', '.join([i for i in auxcell_pins_list])

        # Write the verilog module.
        # The verilog module instantiates the auxcells for rows=self.bank_rows and considering the auxcell pin props.
        # The module pins are standardized : input pins = In, output pins = WL
        module_input_pins = ['In']
        module_output_pins = ['WL']
        module_inout_pins = []
        module_pins_list = module_input_pins + module_output_pins + module_inout_pins
        module_pin_str = ', '.join([i for i in module_pins_list])

        self.rp_fh.write("module  %s_%drows (%s);\n" % (auxcell_name, int(self.bank_rows / 2), module_pin_str))
        self.rp_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.rp_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.rp_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.rp_fh.write("   parameter word_size    = %d;\n" % self.word_size)
        self.rp_fh.write("   parameter pre_dec_b    = %d;\n" % self.no_rp_bottom_pre_decoded_bits)
        self.rp_fh.write("   parameter pre_dec_t    = %d;\n" % self.no_rp_top_pre_decoded_bits)

        for in_pin in module_input_pins:
            # If the pin is bus, then define the bus with the specific parameter.
            # The respective parameter is deinfed in the auxcell pins definition.
            self.rp_fh.write("   input [%s-1:0] %s;\n" % ('pre_dec_b', in_pin))

        for inout_pin in module_inout_pins:
            self.rp_fh.write("   inout %s;\n" % (inout_pin))

        for out_pin in module_output_pins:
            self.rp_fh.write("   output [%d:0] %s;\n" % (int(self.bank_rows / 2) - 1, out_pin))

        # Get the key value of auxcell to figure out the auxcell
        for key, value in self.row_periphery.items():
            if value == auxcell:
                auxcell_key = key

        if auxcell_key == 'wl_driver':  # Should comapre with key rather than the auxcell_name as values are
            row_wl_driver_orientations = self.row_pheriphery['wl_driver'].get_orientations()
            if (row_wl_driver_orientations[0][0] == row_wl_driver_orientations[0][1]) and \
                    (row_wl_driver_orientations[1][0] == row_wl_driver_orientations[1][1]):
                inst_counter = 0
                in1_no_bits = auxcell_pininfo['In1'][2]['no_bits']
                in2_no_bits = auxcell_pininfo['In2'][2]['no_bits']
                wl_no_bits = auxcell_pininfo['WL'][2]['no_bits']
                # The number of instantiations here are counted based on the in2_no_bits and in1_no_bits. This required
                # hardcodfing the pin informaiton. Can use something like auxcell_no_rows and auxcell_no_cols to estimate
                # it with out hardcoing, lllar to Bitcell.
                for msb in range(0, self.no_rp_bottom_MSB_pre_decoded_bits, in2_no_bits):
                    for lsb in range(0, self.no_rp_bottom_LSB_pre_decoded_bits, in1_no_bits):
                        if in1_no_bits > 1:
                            in1_pin = '.%s(In[%d:%d])' % (auxcell_pininfo['In1'][0], lsb + in1_no_bits - 1, lsb)
                        else:
                            in1_pin = '.%s(In[%d])' % (auxcell_pininfo['In1'][0], lsb)
                        if in2_no_bits > 1:
                            lsb_value = msb + self.no_rp_bottom_LSB_pre_decoded_bits
                            msb_value = msb + self.no_rp_bottom_LSB_pre_decoded_bits + in2_no_bits - 1
                            print("lsb and msb value of In2 pins", lsb_value, msb_value)
                            in2_pin = '.%s(In[%d:%d])' % (auxcell_pininfo['In2'][0],
                                                          msb_value,
                                                          lsb_value)
                        else:
                            print("msb value of In2 pins", msb)
                            in2_pin = '.%s(In[%d])' % (auxcell_pininfo['In2'][0], msb + self.no_rp_bottom_LSB_pre_decoded_bits)
                        if wl_no_bits > 1:
                            if inst_counter == 0:
                                wl_lsb_value = inst_counter
                                wl_msb_value = inst_counter + wl_no_bits - 1
                            else:
                                # wl_lsb_value = inst_counter + wl_no_bits - 1
                                wl_lsb_value = wl_lsb_value + wl_no_bits
                                wl_msb_value = wl_msb_value + wl_no_bits
                            # lsb_value = inst_counter
                            # msb_value = nst_counter + wl_no_bits -1

                            wl_pin = '.%s(WL[%d:%d])' % (auxcell_pininfo['WL'][0], wl_msb_value, wl_lsb_value)
                        else:
                            wl_pin = '.%s(WL[%d])' % (auxcell_pininfo['WL'][0], inst_counter)

                        self.rp_fh.write("   %s inst%d (%s, %s, %s); \n" % (auxcell_name,
                                                                            inst_counter,
                                                                            in1_pin,
                                                                            in2_pin,
                                                                            wl_pin))
                        inst_counter = inst_counter + 1
            else:
                pass
        else:
            # pdk dependent and keys are standardized.
            pin_list = []

            # Pin Connection by name. values = pin from auxcells. So, the pin connection is '.value(key)'
            for k in auxcell_pins_list:
                pin_list.append('.%s(%s)' % (auxcell_pininfo[k][0], k))

            pin_connection = ', '.join(pin_list)
            self.rp_fh.write("           %s inst (%s); \n" % (auxcell_name, pin_connection))
            self.rp_fh.write("       end \n")
            self.rp_fh.write("   endgenerate \n")

        # For floor-planning block placement, how can we return instance names for each auxcell so as to place the
        # instance.

        self.rp_fh.write("endmodule\n\n\n\n")

        return auxcell_pininfo

    def generate_row_peri_top_module(self, rp_module_pininfo: dict, row_periphery):
        """
        Generates the row-periphery array verilog module along with the respective auxcell verilog module instances
        generated through  generate_auxcell_module

        :param self.rp_fh: File handler to which the verilog module has to be written.
        :param rp_module_pininfo: Pin information of row periphery module defined in the SRAM architecture.
        :param row_periphery: Row periphery architecture with the auxcells.
        :return: None
        """
        # Declare the variables.
        self.rp_module_pininfo = rp_module_pininfo
        self.row_periphery = row_periphery

        #####################################################################
        # Estimate the number of pre_decoded inputs based on the no of rows #
        #####################################################################

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

        # Generate the modules for the given architecture point and the specified auxcells.
        for auxcell in self.row_periphery.keys():

            # getattr(self, auxcell)(row_periphery[auxcell], sram_specs, sram_arch)
            if auxcell == 'wl_driver':  # The rest of the auxcells are only well contacts that are instantiated at top.
                pin_info = self.generate_auxcell_module(self.row_periphery[auxcell])
                self.auxcell_pin_collection.update(pin_info)

        # Collect pins that are wires connecting the auxcell verilog instances at the top-level module by comparing
        # pin information from row_periphery top-level definition and auxcells info from the generate_auxcell_module.

        # Extract the pin types from the definition.
        module_input_pins = []
        module_output_pins = []
        module_inout_pins = []
        module_power_pins = []
        module_ground_pins = []
        module_wires = []

        for keys, values in rp_module_pininfo.items():
            if values[1] == 'input':
                module_input_pins.append(keys)
            elif values[1] == 'output':
                module_output_pins.append(keys)
            elif values[1] == 'inout':
                module_inout_pins.append(keys)
            elif values[1] == 'power':
                module_power_pins.append(keys)
            elif values[1] == 'ground':
                module_ground_pins.append(keys)

        # Top-level module defintion.
        rp_module_pin_list = module_input_pins + module_output_pins + module_inout_pins
        rp_pin_info = []
        for k in rp_module_pin_list:
            rp_pin_info.append('%s' % (rp_module_pininfo[k][0]))

        rp_module_pin_str = ', '.join(rp_pin_info)
        # rp_module_pin_str = ', '.join(rp_module_pin_list)

        self.rp_fh.write(f"module {self.rp_module_name} ({rp_module_pin_str});\n")
        self.rp_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.rp_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.rp_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.rp_fh.write("   parameter word_size    = %d;\n" % self.word_size)
        self.rp_fh.write("   parameter pre_dec_b    = %d;\n" % self.no_rp_bottom_pre_decoded_bits)
        self.rp_fh.write("   parameter pre_dec_t    = %d;\n" % self.no_rp_top_pre_decoded_bits)

        for in_pin in module_input_pins:
            if list(rp_module_pininfo[in_pin][2].keys())[0] == 'bus':
                self.rp_fh.write(
                    "   input [%s-1:0] %s;\n" % (rp_module_pininfo[in_pin][2]['bus'], rp_module_pininfo[in_pin][0]))
            else:
                self.rp_fh.write("   input  %s;\n" % rp_module_pininfo[in_pin][0])

        for inout_pin in module_inout_pins:
            if list(rp_module_pininfo[inout_pin][2].keys())[0] == 'bus':
                self.rp_fh.write("   inout [%s-1:0] %s;\n" % (
                rp_module_pininfo[inout_pin][2]['bus'], rp_module_pininfo[inout_pin][0]))
            else:
                self.rp_fh.write("   inout  %s;\n" % rp_module_pininfo[inout_pin][0])

        for out_pin in module_output_pins:
            if list(rp_module_pininfo[out_pin][2].keys())[0] == 'bus':
                self.rp_fh.write(
                    "   output [%s-1:0] %s;\n" % (rp_module_pininfo[out_pin][2]['bus'], rp_module_pininfo[out_pin][0]))
            else:
                self.rp_fh.write("   output  %s;\n" % rp_module_pininfo[out_pin][0])

        for wire in module_wires:
            if list(rp_module_pininfo[wire][2].keys())[0] == 'bus':
                self.rp_fh.write(
                    "   wire [%s-1:0] %s;\n" % (rp_module_pininfo[wire][2]['bus'], rp_module_pininfo[wire][0]))
            else:
                self.rp_fh.write("   wire  %s;\n" % self.auxcell_pin_collection[wire][0])

        i = 0
        for k, v in self.row_periphery.items():
            auxcell_module_name = v.get_cellname()
            auxcell_module_pininfo = v.get_pininfo()
            auxcell_module_pins_list = v.get_input_pins() + v.get_output_pins() + v.get_inout_pins()
            # auxcell_module_pin_str = ', '.join(auxcell_module_pininfo[i][0] for i in auxcell_module_pininfo.keys())
            pin_info = []
            for p in auxcell_module_pins_list:
                if p in list(rp_module_pininfo.keys()):
                    pin_info.append('.%s(%s)' % (auxcell_module_pininfo[p][0], rp_module_pininfo[p][0]))
                else:
                    pin_info.append('.%s(%s)' % (auxcell_module_pininfo[p][0], p))

            # auxcell_module_pin_str = ', '.join(i for i in auxcell_module_pins_list)
            auxcell_module_pin_str = ', '.join(i for i in pin_info)

            if k == 'wl_driver':
                self.rp_fh.write("   %s_%drows  rp_wld_b ( .In(row_predec_b), .WL(WL[%d:0]));\n" % (
                    auxcell_module_name, int(self.bank_rows / 2), self.no_rp_bottom_rows - 1))
                self.rp_fh.write("   %s_%drows  rp_wld_t ( .In(row_predec_t), .WL(WL[%d:%d]));\n" % (
                    auxcell_module_name, int(self.bank_rows / 2), self.bank_rows - 1, self.no_rp_bottom_rows))

            elif k == 'row_bottom_well_contact':
                self.rp_fh.write("   %s  rp_bwc ( %s );\n" % (
                    auxcell_module_name, auxcell_module_pin_str))
            elif k == 'row_middle_well_contact':
                self.rp_fh.write("   %s rp_mwc ( %s );\n" % (
                    auxcell_module_name, auxcell_module_pin_str))
            elif k == 'row_top_well_contact':
                self.rp_fh.write("   %s  rp_twc ( %s );\n" % (
                    auxcell_module_name, auxcell_module_pin_str))
            i = i + 1

        self.rp_fh.write("endmodule\n\n\n\n")

        self.rp_fh.close()

        return rp_module_pininfo


if __name__ == '__main__':
    from SRAM import sram_arch

    bank_arch = sram_arch.SRAM6TArch()

    row_periphery = bank_arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col_periphery = bank_arch.bank_top["col_periphery"]
    bitcell_array = bank_arch.bank_top["bitcell_array"]

    row_periphery_top_pininfo = bank_arch.row_periphery_top_pininfo

    sram_bank_config = [256, 128]
    sram_specs = {'word_size': 32}

    dic = {}
    dic['auxcells'] = {}
    dic['auxcells']['bitcell_array'] = {}
    dic['auxcells']['bitcell_array']['bitcell'] = {}
    dic['auxcells']['bitcell_array']['bitcell']['no_rows'] = 2
    dic['auxcells']['bitcell_array']['bitcell']['no_cols'] = 1

    rp = RowPeriVerilogGen(sram_bank_config, sram_specs, dic)

    cp_pin_info = rp.generate_row_peri_top_module(row_periphery_top_pininfo, row_periphery)
    # print(cp_pin_info)
