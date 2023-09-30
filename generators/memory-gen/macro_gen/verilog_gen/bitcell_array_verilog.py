import sys


class BitcellArrayVerilogGen:
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

        # # Module Name
        self.bca_module_name = f'bitcell_array_{self.bank_rows}rows_{self.bank_cols}cols'
        self.bca_fh = open(f"{self.bca_module_name}.v", 'w')
        self.bca_fh.write("`timescale 1ns / 1ns\n")

        # Collects all the pins of all auxcells to compare with the row_periphery module
        self.auxcell_pin_collection = {}

    def generate_auxcell_module(self, auxcell):
        """
        Generates the single row (1 dimension) and multi-columns (as specified by sram_arch) auxcells verilog module.
        :param self.bca_fh: File handler to which the verilog module is written
        :param auxcell: Auxcell instance which enables accessing the specific properties.
        :return: All the auxcell pins in the form of dictionary.
        """

        # Collect the auxcell properties.
        auxcell_name = auxcell.get_cellname()
        auxcell_pininfo = auxcell.get_pininfo()

        auxcell_input_pins = auxcell.get_input_pins()
        auxcell_output_pins = auxcell.get_output_pins()
        auxcell_inout_pins = auxcell.get_inout_pins()

        # Get the key value of auxcell to figure out the auxcell
        for key, value in self.bitcell_array.items():
            if value == auxcell:
                auxcell_key = key

        # Collect the no of rows /cols that each auxcell covers in a single layout instance.
        auxcell_no_rows = self.tech_config_dic['auxcells']['bitcell_array'][auxcell_key]['no_rows']
        auxcell_no_cols = self.tech_config_dic['auxcells']['bitcell_array'][auxcell_key]['no_cols']

        # Collect all auxcell pin keys except the power pins.
        auxcell_pins_list = auxcell_input_pins + auxcell_output_pins + auxcell_inout_pins
        auxcell_pin_str = ', '.join([i for i in auxcell_pins_list])

        # #####################################
        # ##### Write the verilog module. #####
        # #####################################

        # Define the module name and the associated parameters.
        # Module with auxcell instantiations for the entire column.
        # No of auxcells per column = bank_cols/auxcell_cols.
        # No of rows covered per column = auxcell_rows.
        self.bca_fh.write("module  %s_%dcolumns (%s);\n" % (auxcell_name, self.bank_cols, auxcell_pin_str))
        self.bca_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.bca_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.bca_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.bca_fh.write("   parameter word_size    = %d;\n" % self.word_size)

        # Define the pin defintions: Pins considered: Input, Output, and Inout pins.
        for in_pin in auxcell_input_pins:  # For each of the auxcell input pin (based on keys of auxcell_pin_info def)
            if self.bca_module_pininfo[in_pin][2]['bus'] == 'bank_rows':
                # If the pin type is bus (checked from the top-level moddule pin defintion), and is equal to bank_rows
                # The pin length can be a single-bit or equal to the no_bits defined at the auxcell_pininfo definition.
                # Because, the auxcell module is created for a single row.
                if auxcell_pininfo[in_pin][2]['no_bits'] > 1:
                    self.bca_fh.write("   input [%d:0] %s;\n" % (auxcell_no_rows - 1, in_pin))
                else:
                    self.bca_fh.write("   input %s;\n" % (in_pin))
            elif self.bca_module_pininfo[in_pin][2]['bus'] == 'bank_cols':
                # If the pin type is bus (checked from the top-level moddule pin defintion), and is equal to bank_cols
                # The pin length is same as the bus length. as the auxcell module is created for all columns in a row.
                self.bca_fh.write("   input [%s-1:0] %s;\n" % (self.bca_module_pininfo[in_pin][2]['bus'], in_pin))
            else:
                # If the pin is not a bus, it pin length is 1.
                self.bca_fh.write("   input  %s;\n" % in_pin)

        for inout_pin in auxcell_inout_pins:
            if self.bca_module_pininfo[inout_pin][2]['bus'] == 'bank_rows':
                if auxcell_pininfo[in_pin][2]['no_bits'] > 1:
                    self.bca_fh.write("   inout [%d:0] %s;\n" % (auxcell_no_rows - 1, inout_pin))
                else:
                    self.bca_fh.write("   inout %s;\n" % (inout_pin))
            elif self.bca_module_pininfo[inout_pin][2]['bus'] == 'bank_cols':
                self.bca_fh.write("   inout [%s-1:0] %s;\n" % (self.bca_module_pininfo[inout_pin][2]['bus'], inout_pin))
            else:
                self.bca_fh.write("   inout  %s;\n" % inout_pin)

        for out_pin in auxcell_output_pins:
            if self.bca_module_pininfo[out_pin][2]['bus'] == 'bank_rows':
                if auxcell_pininfo[in_pin][2]['no_bits'] > 1:
                    self.bca_fh.write("   out [%d:0] %s;\n" % (auxcell_no_rows - 1, out_pin))
                else:
                    self.bca_fh.write("   out %s;\n" % (out_pin))
            elif self.bca_module_pininfo[out_pin][2]['bus'] == 'bank_cols':
                self.bca_fh.write("   out [%s-1:0] %s;\n" % (self.bca_module_pininfo[out_pin][2]['bus'], out_pin))
            else:
                self.bca_fh.write("   out  %s;\n" % out_pin)

        # Define the auxcell instantions
        if auxcell_key == 'bitcell':

            # Get the bitcell_end_cell properties from the bitcell_array definition under the bitcell_array.py
            bitcell_end_cell_inst = self.bitcell_array['bitcell_end_cell']
            bitcell_end_cell_name = bitcell_end_cell_inst.get_cellname()
            bitcell_end_cell_pininfo = bitcell_end_cell_inst.get_pininfo()
            bitcell_end_cell_pinlist = bitcell_end_cell_inst.get_input_pins() + bitcell_end_cell_inst.get_inout_pins() \
                                       + bitcell_end_cell_inst.get_output_pins()
            # Collect the no of rows /cols that each auxcell covers in a single layout instance.
            end_cell_auxcell_no_cols = self.tech_config_dic['auxcells']['bitcell_array']['bitcell_end_cell']['no_cols']

            if self.bank_cols % auxcell_no_cols == 0:  # Need to check the possibility of iterating the loop to make sure
                # the bust bit lengths from the loop is same as the total number of required bits.
                no_iters = int(self.bank_cols/auxcell_no_cols) # Estimate the no of auxcells to instantiate.
                for icol in range(0, no_iters + 2):  # Plus two to include the end_cells on both sides of the col-array.
                    if icol == 0 or icol == no_iters + 1:
                        # Write the bitcell_end_cell instantiation
                        pin_list = []
                        for p in bitcell_end_cell_pinlist:
                            # Considers only column buses as the entire row is considered by default.
                            pin_list.append('.%s(%s)' % (bitcell_end_cell_pininfo[p][0], p))
                        pin_connection = ', '.join(pin_list)

                        self.bca_fh.write(f'   {bitcell_end_cell_name} inst{icol} ({pin_connection});\n')
                    else:  # Instantiate the bitcell modules
                        pin_list = []
                        for p in auxcell_pins_list:
                            # Considers only column buses as the entire row is considered by default.
                            if self.bca_module_pininfo[p][2]['bus'] == 'bank_cols':
                                lsb = (icol -1)*auxcell_no_cols
                                msb = (icol) *auxcell_no_cols - 1
                                if lsb == msb:
                                    pin_list.append('.%s(%s[%d])' % (auxcell_pininfo[p][0], p, lsb))
                                else:
                                    pin_list.append(
                                        '.%s(%s[%d:%d])' % (auxcell_pininfo[p][0], p, msb, lsb))
                                # if auxcell_no_cols > 1:
                                #     # The -1 numbering below is because of inserting the end cells at 0 and
                                #     # self.bank_cols+1 of icol counter. With out substracting -1, the pin bus numbering
                                #     # here starts from 1 instead of 0, and ends at self.bank_cols, instead of
                                #     # self.bank_cols-1. For Ex: BL adn BLB for 128 bus width, they would start from 1 and
                                #     # end at 128 instead of 0 and 127. Hold true for the edge_cell and strap_cell
                                #     pin_list.append(
                                #         '.%s(%s[%d:%d])' % (auxcell_pininfo[p][0], p, icol + auxcell_no_cols - 1,
                                #                             icol - 1))
                                # else:
                                #     pin_list.append('.%s(%s[%d])' % (auxcell_pininfo[p][0], p, icol - 1))
                            else:
                                pin_list.append('.%s(%s)' % (auxcell_pininfo[p][0], p))
                        pin_connection = ', '.join(pin_list)

                        self.bca_fh.write(f'   {auxcell_name} inst{icol} ({pin_connection});\n')
            else:
                print("The number of bank columns must be divisible by auxcell columns to instantiate the modules"
                      "with correct bus bits. \n")
                print(f"Can not generate the bank column for the {auxcell_name}. Refer above for more details.\n")
                sys.exit(1)
        elif auxcell_key == 'edge_cell':

            # Get the edge_end_cell properties from the bitcell_array definition under the bitcell_array.py
            edge_end_cell_inst = self.bitcell_array['edge_end_cell']
            edge_end_cell_name = edge_end_cell_inst.get_cellname()
            edge_end_cell_pininfo = edge_end_cell_inst.get_pininfo()
            edge_end_cell_pinlist = edge_end_cell_inst.get_input_pins() + edge_end_cell_inst.get_inout_pins() \
                                       + edge_end_cell_inst.get_output_pins()
            # Collect the no of rows /cols that each auxcell covers in a single layout instance.
            end_cell_auxcell_no_cols = self.tech_config_dic['auxcells']['bitcell_array']['edge_end_cell']['no_cols']

            if self.bank_cols % auxcell_no_cols == 0: # Need to check the possibility of iterating the loop to make sure
                # the bust bit lengths from the loop is same as the total number of required bits.
                no_iters = int(self.bank_cols/auxcell_no_cols) # Estimate the no of auxcells to instantiate.
                for icol in range(0, no_iters + 2):  # Plus two to include the end_cells on both sides of the col-array.
                    if icol == 0 or icol == no_iters + 1:
                        # Write the edge_end_cell instantiation
                        pin_list = []
                        for p in edge_end_cell_pinlist:
                            # Considers only column buses as the entire row is considered by default.
                            pin_list.append('.%s(%s)' % (edge_end_cell_pininfo[p][0], p))
                        pin_connection = ', '.join(pin_list)

                        self.bca_fh.write(f'   {edge_end_cell_name} inst{icol} ({pin_connection});\n')
                    else:  # Instantiate the bitcell modules
                        pin_list = []
                        for p in auxcell_pins_list:
                            # Considers only column buses as the entire row is considered by default.
                            if self.bca_module_pininfo[p][2]['bus'] == 'bank_cols':
                                lsb = (icol -1)*auxcell_no_cols
                                msb = (icol) *auxcell_no_cols - 1
                                if lsb == msb:
                                    pin_list.append('.%s(%s[%d])' % (auxcell_pininfo[p][0], p, lsb))
                                else:
                                    pin_list.append(
                                        '.%s(%s[%d:%d])' % (auxcell_pininfo[p][0], p, msb, lsb))
                            else:
                                pin_list.append('.%s(%s)' % (auxcell_pininfo[p][0], p))
                        pin_connection = ', '.join(pin_list)

                        self.bca_fh.write(f'   {auxcell_name} inst{icol} ({pin_connection});\n')
            else:
                print("The number of bank columns must be divisible by auxcell columns to instantiate the modules"
                      "with correct bus bits. \n")
                print(f"Can not generate the bank column for the {auxcell_name}. Refer above for more details.\n")
                sys.exit(1)
        elif auxcell_key == 'strap_cell':

            # Get the strap_end_cell properties from the bitcell_array definition under the bitcell_array.py
            strap_end_cell_inst = self.bitcell_array['strap_end_cell']
            strap_end_cell_name = strap_end_cell_inst.get_cellname()
            strap_end_cell_pininfo = strap_end_cell_inst.get_pininfo()
            strap_end_cell_pinlist = strap_end_cell_inst.get_input_pins() + strap_end_cell_inst.get_inout_pins() \
                                    + strap_end_cell_inst.get_output_pins()
            # Collect the no of rows /cols that each auxcell covers in a single layout instance.
            end_cell_auxcell_no_cols = self.tech_config_dic['auxcells']['bitcell_array']['strap_end_cell']['no_cols']

            if self.bank_cols % auxcell_no_cols == 0: # Need to check the possibility of iterating the loop to make sure
                # the bust bit lengths from the loop is same as the total number of required bits.
                no_iters = int(self.bank_cols/auxcell_no_cols) # Estimate the no of auxcells to instantiate.
                for icol in range(0, no_iters + 2):  # Plus two to include the end_cells on both sides of the col-array.
                    if icol == 0 or icol == no_iters + 1:
                        # Write the strap_end_cell instantiation
                        pin_list = []
                        for p in strap_end_cell_pinlist:
                            # Considers only column buses as the entire row is considered by default.
                            pin_list.append('.%s(%s)' % (strap_end_cell_pininfo[p][0], p))
                        pin_connection = ', '.join(pin_list)

                        self.bca_fh.write(f'   {strap_end_cell_name} inst{icol} ({pin_connection});\n')
                    else:  # Instantiate the bitcell modules
                        pin_list = []
                        for p in auxcell_pins_list:
                            # Considers only column buses as the entire row is considered by default.
                            if self.bca_module_pininfo[p][2]['bus'] == 'bank_cols':
                                lsb = (icol -1)*auxcell_no_cols
                                msb = (icol) *auxcell_no_cols - 1
                                if lsb == msb:
                                    pin_list.append('.%s(%s[%d])' % (auxcell_pininfo[p][0], p, lsb))
                                else:
                                    pin_list.append(
                                        '.%s(%s[%d:%d])' % (auxcell_pininfo[p][0], p, msb, lsb))
                            else:
                                pin_list.append('.%s(%s)' % (auxcell_pininfo[p][0], p))
                        pin_connection = ', '.join(pin_list)

                        self.bca_fh.write(f'   {auxcell_name} inst{icol} ({pin_connection});\n')
            else:
                print("The number of bank columns must be divisible by auxcell columns to instantiate the modules"
                      "with correct bus bits. \n")
                print(f"Can not generate the bank column for the {auxcell_name}. Refer above for more details.\n")
                sys.exit(1)

        self.bca_fh.write("endmodule\n\n\n\n")

        return auxcell_pininfo

    def generate_bitcell_array_top_module(self, bca_module_pininfo: dict, bitcell_array):
        """
        Generates the row-periphery array verilog module along with the respective auxcell verilog module instances
        generated through  generate_auxcell_module

        :param bca_module_pininfo: Pin information of bitcell array module defined in the SRAM architecture.
        :param bitcell_array: Column periphery architecture with the auxcells.
        :return: None
        """
        self.bca_module_pininfo = bca_module_pininfo
        self.bitcell_array = bitcell_array

        # Generate the auxcell modules for the given architecture point and the specified auxcells.

        for auxcell in self.bitcell_array.keys():
            # getattr(self, auxcell)(row_periphery[auxcell], sram_specs, sram_arch)
            if auxcell in ['bitcell', 'edge_cell', 'strap_cell']:
                pin_info = self.generate_auxcell_module(self.bitcell_array[auxcell])
                self.auxcell_pin_collection.update(pin_info)

        # Extract the pins from the definition.
        module_input_pins = []
        module_output_pins = []
        module_inout_pins = []
        module_power_pins = []
        module_ground_pins = []
        module_wires = []

        for keys, values in bca_module_pininfo.items():
            if values[1] == 'input':
                module_input_pins.append(keys)
            elif values[1] == 'output':
                module_output_pins.append(keys)
            elif values[1] == 'inout':
                module_inout_pins.append(keys)
            elif values[1] == 'wire':
                module_wires.append(keys)
            elif values[1] == 'power':
                module_power_pins.append(keys)
            elif values[1] == 'ground':
                module_ground_pins.append(keys)

        # Collect all the input, input and output pins of the top-level module
        bca_module_pin_list = module_input_pins + module_output_pins + module_inout_pins
        # bca_pin_info = []
        # for bcpk in bca_module_pin_list:
        #     bca_pin_info.append('%s' % (bca_module_pininfo[bcpk][0]))

        # bca_module_pin_str = ', '.join(bca_pin_info)
        bca_module_pin_str = ', '.join(bca_module_pin_list)

        # #####################################
        # ##### Write the verilog module. #####
        # #####################################

        # Define the module name and the associated parameters.
        # Module with column instantiations.
        # No of column instantiations of specific auxcell column depends on auxcell.
        #   # Bitcell and bitcell_end_cell-> bank_rows.
        #   # edge_cell and edge_end_cell -> 2.
        #   # strap_cell and strap_end_cell -> 1.

        self.bca_fh.write(f"module {self.bca_module_name} ({bca_module_pin_str});\n")
        self.bca_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.bca_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.bca_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.bca_fh.write("   parameter word_size    = %d;\n" % self.word_size)

        # module Pin definitions -> based on the keys of pin_info defined under bitcell_array.
        for in_pin in module_input_pins:
            if list(bca_module_pininfo[in_pin][2].keys())[0] == 'bus':
                self.bca_fh.write(
                    "   input [%s-1:0] %s;\n" % (bca_module_pininfo[in_pin][2]['bus'], bca_module_pininfo[in_pin][0]))
            else:
                self.bca_fh.write("   input  %s;\n" % bca_module_pininfo[in_pin][0])

        for inout_pin in module_inout_pins:
            if list(bca_module_pininfo[inout_pin][2].keys())[0] == 'bus':
                self.bca_fh.write("   inout [%s-1:0] %s;\n" % (
                    bca_module_pininfo[inout_pin][2]['bus'], bca_module_pininfo[inout_pin][0]))
            else:
                self.bca_fh.write("   inout  %s;\n" % bca_module_pininfo[inout_pin][0])

        for out_pin in module_output_pins:
            if list(bca_module_pininfo[out_pin][2].keys())[0] == 'bus':
                self.bca_fh.write("   output [%s-1:0] %s;\n" % (
                    bca_module_pininfo[out_pin][2]['bus'], bca_module_pininfo[out_pin][0]))
            else:
                self.bca_fh.write("   output  %s;\n" % bca_module_pininfo[out_pin][0])

        for wire in module_wires:
            if list(bca_module_pininfo[wire][2].keys())[0] == 'bus':
                self.bca_fh.write(
                    "   wire [%s-1:0] %s;\n" % (bca_module_pininfo[wire][2]['bus'], bca_module_pininfo[wire][0]))
            else:
                self.bca_fh.write("   wire  %s;\n" % bca_module_pininfo[wire][0])

        i = 0

        for k, v in self.bitcell_array.items():
            auxcell_no_rows = self.tech_config_dic['auxcells']['bitcell_array'][k]['no_rows']
            auxcell_no_cols = self.tech_config_dic['auxcells']['bitcell_array'][k]['no_cols']
            auxcell_module_name = v.get_cellname()
            auxcell_module_pininfo = v.get_pininfo()
            auxcell_module_pins_list = v.get_input_pins() + v.get_output_pins() + v.get_inout_pins()

            pin_info = []
            for p in auxcell_module_pins_list:
                if p in list(bca_module_pininfo.keys()):
                    if list(bca_module_pininfo[p][2].keys())[0] == 'bus':
                        if bca_module_pininfo[p][2]['bus'] == 'bank_rows':
                            if auxcell_no_rows > 1:  #
                                pin_info.append('.%s(%s[i+%d:i])' % (auxcell_module_pininfo[p][0],
                                                                     bca_module_pininfo[p][0], auxcell_no_rows - 1))
                            else:
                                pin_info.append('.%s(%s[i])' % (auxcell_module_pininfo[p][0], bca_module_pininfo[p][0]))
                        else:
                            pin_info.append('.%s(%s)' % (auxcell_module_pininfo[p][0], bca_module_pininfo[p][0]))
                else:
                    pin_info.append('.%s(%s)' % (auxcell_module_pininfo[p][0], p))

            auxcell_module_pin_str = ', '.join(i for i in pin_info)

            if k == 'bitcell':
                # Bitcell is a two dimensional array.
                #   First, Column array is generated as a module using generate_auxcell_module
                #   Next column array module is instantiated for self.bank_rows times.

                # Generate the column array module
                # pin_info = self.generate_auxcell_module(self.bitcell_array[k])
                # self.auxcell_pin_collection.update(pin_info)
                inst_counter = 0
                for in_num in range(0, self.bank_rows, auxcell_no_rows):
                    col_module_pin_list = []
                    for p in auxcell_module_pins_list:
                        if p in list(bca_module_pininfo.keys()):
                            if list(bca_module_pininfo[p][2].keys())[0] == 'bus':
                                if bca_module_pininfo[p][2]['bus'] == 'bank_rows':
                                    if auxcell_no_rows > 1:
                                        col_module_pin_list.append('.%s(%s[%d:%d])' % (auxcell_module_pininfo[p][0],
                                                                                       bca_module_pininfo[p][0],
                                                                                       in_num + auxcell_no_rows - 1,
                                                                                       in_num))
                                    else:
                                        col_module_pin_list.append('.%s(%s[%d:%d])' % (auxcell_module_pininfo[p][0],
                                                                                       bca_module_pininfo[p][0],
                                                                                       in_num + auxcell_no_rows - 1,
                                                                                       in_num))
                                else:
                                    col_module_pin_list.append(
                                        '.%s(%s)' % (auxcell_module_pininfo[p][0], bca_module_pininfo[p][0]))
                            else:
                                col_module_pin_list.append(
                                    '.%s(%s)' % (auxcell_module_pininfo[p][0], bca_module_pininfo[p][0]))
                        else:
                            col_module_pin_list.append('.%s(%s)' % (auxcell_module_pininfo[p][0], p))
                    col_module_pin_str = ', '.join(i for i in col_module_pin_list)
                    self.bca_fh.write("   %s_%dcolumns bc_ca%d ( %s ); \n" % (auxcell_module_name,
                                                                              self.bank_cols, inst_counter,
                                                                              col_module_pin_str))
                    # self.bank_cols, in_num,
                    inst_counter = inst_counter + 1
            elif k == 'edge_cell':
                # Two instances of edge_cells, each cell would be at top and bottom.
                # ca -> column array, b-> bottom edge cell ca, t -> top edge cell ca.
                self.bca_fh.write("   %s_%dcolumns  edge_ca_b ( %s );\n" % (auxcell_module_name, self.bank_cols,
                                                                               auxcell_module_pin_str))
                self.bca_fh.write("   %s_%dcolumns  edge_ca_t ( %s );\n" % (auxcell_module_name, self.bank_cols,
                                                                               auxcell_module_pin_str))
            elif k == 'strap_cell':
                # ca -> column array
                self.bca_fh.write("   %s_%dcolumns  strap_ca ( %s );\n" % (auxcell_module_name, self.bank_cols,
                                                                                   auxcell_module_pin_str))
            i = i + 1

        self.bca_fh.write("endmodule\n\n\n\n")

        self.bca_fh.close()

        return bca_module_pininfo


if __name__ == '__main__':
    # For testing the bitcell_array_verilog only

    from SRAM import sram_arch

    bank_arch = sram_arch.SRAM6TArch()

    row_periphery = bank_arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col_periphery = bank_arch.bank_top["col_periphery"]
    bitcell_array = bank_arch.bank_top["bitcell_array"]

    bitcell_array_top_pininfo = bank_arch.bitcell_array_top_pininfo

    # sram_components = dict(row_periphery=row_periphery, row_periphery=row_periphery, bitcell_array=bitcell_array)
    bca_periphery_pins = dict(WL=["WL", "input", {'bus': 'bank_rows'}],
                              BL=["BL", "inout", {'bus': 'bank_cols'}], BLB=["BLB", "inout", {'bus': 'bank_cols'}],
                              VDD=["VDD", "power"], VSS=["VSS", "ground"])
    sram_bank_config = [32, 32]
    sram_specs = {'word_size': 32}

    dic = {}
    dic['auxcells'] = {}
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

    BitcellArrayVerilogGen(sram_bank_config, sram_specs, dic)

    # Initialize each component Generation class.
    # dic = get_tech_collaterals('12nm', 'gf', 'lp')
    bca = BitcellArrayVerilogGen(sram_bank_config, sram_specs, dic)

    # Generate each component.
    bca_pin_info = bca.generate_bitcell_array_top_module(bitcell_array_top_pininfo, bitcell_array)

