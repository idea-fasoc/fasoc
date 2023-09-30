

class ColPeriVerilogGen:
    """
    Generates the col-periphery module along with auxcell modules for the given architecture and specifications.
    """

    def __init__(self, sram_bank_config, sram_specs, tech_config_dic):

        self.word_size = sram_specs['word_size']
        self.bank_rows = sram_bank_config[0]
        self.bank_cols = sram_bank_config[1]
        self.tech_config_dic = tech_config_dic

        # Colmux ratio from the architecture point.
        self.bank_col_mux = self.bank_cols / self.word_size

        # Module Name
        self.cp_module_name =  f'col_periphery_{self.bank_rows}rows_{self.bank_cols}cols'
        self.cp_fh = open(f"{self.cp_module_name}.v", 'w')
        self.cp_fh.write("`timescale 1ns / 1ns\n")

        # Collects all the pins of all auxcells to compare with the col_periphery module
        self.auxcell_pin_collection = {}


    def generate_auxcell_module(self, auxcell):
        """
        Generates the verilog module for the speicified auxcell
        :param self.cp_fh: File handler to which the verilog module has to be written.
        :param auxcell: Auxcell instance which enables accessing the specific properties.
        :return: All the auxcell pins in the form of dictionary.
        """

        # Collect the auxcell properties.
        auxcell_name = auxcell.get_cellname()
        auxcell_pininfo = auxcell.get_pininfo()

        auxcell_input_pins = auxcell.get_input_pins()
        auxcell_output_pins = auxcell.get_output_pins()
        auxcell_inout_pins = auxcell.get_inout_pins()

        # auxcell_pin_str = ', '.join([auxcell_pininfo[i][0] for i in auxcell_pininfo.keys()])
        # Collect all auxcell pins except the power pins.
        auxcell_pins_list = auxcell_input_pins + auxcell_output_pins + auxcell_inout_pins
        auxcell_pin_str = ', '.join([i for i in auxcell_pins_list])

        # The parameter assignments are standardized as per the bus variables in the sram_arch.
        # Gets updated as new bus variables are added in the sram_arch
        param_col_mux      = self.bank_col_mux
        param_bank_rows    = self.bank_rows
        param_bank_cols    = self.bank_cols
        param_word_size    = self.word_size

        # Write the verilog module.
        self.cp_fh.write("module  %s_%dcols (%s);\n" % (auxcell_name, self.bank_cols, auxcell_pin_str))
        self.cp_fh.write("   parameter col_mux      = %d;\n" % param_col_mux)
        self.cp_fh.write("   parameter bank_rows    = %d;\n" % param_bank_rows)
        self.cp_fh.write("   parameter bank_cols    = %d;\n" % param_bank_cols)
        self.cp_fh.write("   parameter word_size    = %d;\n" % param_word_size)
        for in_pin in auxcell_input_pins:
            # If the pin is bus, then define the bus with the specific parameter.
            # The respective parameter is deinfed in the auxcell pins definition.
            if list(self.cp_module_pininfo[in_pin][2].keys())[0] == 'bus':
                self.cp_fh.write("   input [%s-1:0] %s;\n" % (self.cp_module_pininfo[in_pin][2]['bus'], in_pin))
            else:
                self.cp_fh.write("   input  %s;\n" % in_pin)

        for inout_pin in auxcell_inout_pins:
            if list(self.cp_module_pininfo[inout_pin][2].keys())[0] == 'bus':
                self.cp_fh.write("   inout [%s-1:0] %s;\n" % (self.cp_module_pininfo[inout_pin][2]['bus'], inout_pin))
            else:
                self.cp_fh.write("   inout  %s;\n" % inout_pin)

        for out_pin in auxcell_output_pins:
            if list(self.cp_module_pininfo[out_pin][2].keys())[0] == 'bus':
                self.cp_fh.write("   output [%s-1:0] %s;\n" % (self.cp_module_pininfo[out_pin][2]['bus'], out_pin))
            else:
                self.cp_fh.write("   input  %s;\n" % out_pin)

        # Get the key value of auxcell to figure out the auxcell
        for key, value in self.col_periphery.items():
            if value == auxcell:
                auxcell_key = key

        if not auxcell.is_column_muxed():

            for icol in range(0, self.bank_cols):
                pin_list = []

                # Pin Connection by name. values = pin from auxcells. So, the pin connection is '.value(key)'
                for k in auxcell_pins_list:
                    if list(self.cp_module_pininfo[k][2].keys())[0] == 'bus':
                        pin_list.append('.%s(%s[%d])' % (auxcell_pininfo[k][0], k, icol))
                    else:
                        pin_list.append('.%s(%s)' % (auxcell_pininfo[k][0], k))

                pin_connection = ', '.join(pin_list)
                self.cp_fh.write("   %s inst%d (%s); \n" % (auxcell_name, icol, pin_connection))
        else:

            for icol in range(0, self.word_size):

                pin_list = []
                for k in auxcell_pins_list:
                    if list(self.cp_module_pininfo[k][2].keys())[0] == 'bus':
                        if eval('param_'+self.cp_module_pininfo[k][2]['bus']) == auxcell_pininfo[k][2]['no_bits']:
                            pin_list.append('.%s(%s)' % (auxcell_pininfo[k][0], k))
                        else:
                            no_bits = auxcell_pininfo[k][2]['no_bits']
                            lsb_value = icol * no_bits
                            msb_value = ((icol + 1) * no_bits) - 1

                            if lsb_value == msb_value:
                                pin_list.append('.%s(%s[%d])' % (auxcell_pininfo[k][0], k, lsb_value))
                            else:
                                pin_list.append('.%s(%s[%d:%d])' % (auxcell_pininfo[k][0], k, msb_value, lsb_value))
                    else:
                        pin_list.append('.%s(%s)' % (auxcell_pininfo[k][0], k))

                # for k in auxcell_pins_list:
                #     pin_list.append('.%s(%s[i])' % (auxcell_pininfo[k][0], k))
                pin_connection = ', '.join(pin_list)
                self.cp_fh.write("   %s inst%d (%s); \n" % (auxcell_name, icol, pin_connection))

        self.cp_fh.write("endmodule\n\n\n\n")

        return auxcell_pininfo

    def generate_col_peri_top_module(self, cp_module_pininfo: dict, col_periphery):
        """
        Generates the column-periphery array verilog module along with the respective auxcell verilog module instances
        generated through generate_auxcell_module

        :param self.cp_fh: File handler to which the verilog module has to be written.
        :param cp_module_pininfo: Pin information of Column periphery module defined in the SRAM architecture.
        :param col_periphery: Column periphery architecture with the auxcells.
        :return: None
        """
        self.cp_module_pininfo = cp_module_pininfo
        self.col_periphery = col_periphery

        # Generate the modules for the given architecture point and the specified auxcells.
        for auxcell in self.col_periphery.keys():

            # getattr(self, auxcell)(col_periphery[auxcell], sram_specs, sram_arch)
            pin_info = self.generate_auxcell_module(self.col_periphery[auxcell])
            self.auxcell_pin_collection.update(pin_info)

        # Collect pins that are wires connecting the auxcell verilog instances at the top-level module by comparing
        # pin information from col_periphery top-level definition and auxcells info from the generate_auxcell_module.

        # module_wires = {}
        # for k, v in self.auxcell_pin_collection.items():
        #     if k not in list(cp_module_pininfo.keys()):
        #         module_wires[k] = v

        # Extract the pin types from the definition.
        module_input_pins = []
        module_output_pins = []
        module_inout_pins = []
        module_wires = []
        module_power_pins = []
        module_ground_pins = []

        for keys, values in cp_module_pininfo.items():
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

        # Top-level module defintion.
        cp_module_pin_list = module_input_pins + module_output_pins + module_inout_pins

        # Obtain the col_periphery module pin string from the cp_module_pininfo name value
        # cp_pin_info = []
        # for k in cp_module_pin_list:
        #     cp_pin_info.append('%s' % (cp_module_pininfo[k][0]))
        # cp_module_pin_str = ', '.join(cp_pin_info)

        # Module pin lstr from the cp_module_pininfo keys.
        cp_module_pin_str = ', '.join(cp_module_pin_list)

        self.cp_fh.write(f"module {self.cp_module_name} ({cp_module_pin_str});\n" )
        # The parameters below are used to define the size for the pin buses. Standardized with the pin info definition
        # from sram_char.py
        self.cp_fh.write("   parameter col_mux      = %d;\n" % self.bank_col_mux)
        self.cp_fh.write("   parameter bank_rows    = %d;\n" % self.bank_rows)
        self.cp_fh.write("   parameter bank_cols    = %d;\n" % self.bank_cols)
        self.cp_fh.write("   parameter word_size    = %d;\n" % self.word_size)

        # Define the pins, pins type.
        for in_pin in module_input_pins:
            if list(cp_module_pininfo[in_pin][2].keys())[0] == 'bus':
                self.cp_fh.write("   input [%s-1:0] %s;\n" % (cp_module_pininfo[in_pin][2]['bus'],  cp_module_pininfo[in_pin][0]))
            else:
                #self.cp_fh.write("   input  %s;\n" % in_pin)
                self.cp_fh.write("   input  %s;\n" % cp_module_pininfo[in_pin][0])

        for inout_pin in module_inout_pins:
            if list(cp_module_pininfo[inout_pin][2].keys())[0] == 'bus':
                #self.cp_fh.write("   inout [%s-1:0] %s;\n" % (cp_module_pininfo[inout_pin][2]['bus'], inout_pin))
                self.cp_fh.write("   inout [%s-1:0] %s;\n" % (cp_module_pininfo[inout_pin][2]['bus'], cp_module_pininfo[inout_pin][0]))
            else:
                #self.cp_fh.write("   inout [%s-1:0] %s;\n" % (cp_module_pininfo[inout_pin][2]['bus'], inout_pin))
                self.cp_fh.write("   inout [%s-1:0] %s;\n" % (cp_module_pininfo[inout_pin][2]['bus'], cp_module_pininfo[inout_pin][0]))

        for out_pin in module_output_pins:
            if list(cp_module_pininfo[out_pin][2].keys())[0] == 'bus':
                #self.cp_fh.write("   output [%s-1:0] %s;\n" % (cp_module_pininfo[out_pin][2]['bus'], out_pin))
                self.cp_fh.write("   output [%s-1:0] %s;\n" % (cp_module_pininfo[out_pin][2]['bus'], cp_module_pininfo[out_pin][0]))
            else:
                #self.cp_fh.write("   input  %s;\n" % out_pin)
                self.cp_fh.write("   output  %s;\n" % cp_module_pininfo[out_pin][0])

        for wire in module_wires:
            if list(cp_module_pininfo[out_pin][2].keys())[0] == 'bus':
                #self.cp_fh.write("   wire [%s-1:0] %s;\n" % (self.auxcell_pin_collection[wire][2]['bus'], wire))
                self.cp_fh.write("   wire [%s-1:0] %s;\n" % (cp_module_pininfo[wire][2]['bus'], cp_module_pininfo[wire][0]))
            else:
                #self.cp_fh.write("   wire  %s;\n" % wire)
                self.cp_fh.write("   wire  %s;\n" % cp_module_pininfo[wire][0])

        # Create a column array instance for each of the auxcells defined under col_periphery in sram_arch
        i = 0
        for k, v in self.col_periphery.items():
            # Collect the auxcell properties.
            auxcell_module_name = v.get_cellname()
            auxcell_module_pininfo = v.get_pininfo()
            auxcell_module_pins_list = v.get_input_pins() + v.get_output_pins() + v.get_inout_pins()
            pin_info =[]
            for p in auxcell_module_pins_list:
                if p in list(cp_module_pininfo.keys()):
                    # .auxcellmodulepin -> key value(toplevelmodulepin -> key value)
                    pin_info.append('.%s(%s)' % (p, cp_module_pininfo[p][0]))
                else:
                    pin_info.append('.%s(%s)' % (auxcell_module_pininfo[p][0], p))

            auxcell_module_pin_str = ', '.join(i for i in pin_info)

            # The auxcell column instance module naming is standardized: auxcell_name_#cols;
            # instance name = cp_inst(auxcell_num); auxcell_num = index num as per col_periphery definition in sram_arch
            self.cp_fh.write("   %s_%dcols  cp_inst%d ( %s );\n" % (
            auxcell_module_name, self.bank_cols, i, auxcell_module_pin_str))
            i = i + 1

        self.cp_fh.write("endmodule\n\n\n\n")

        self.cp_fh.close()

        return cp_module_pininfo

if __name__ == '__main__':

    # For Col_Periphery.py testing purpose only.
    from SRAM import sram_arch

    bank_arch = sram_arch.SRAM6TArch()

    row_periphery = bank_arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col_periphery = bank_arch.bank_top["col_periphery"]
    bitcell_array = bank_arch.bank_top["bitcell_array"]

    col_periphery_top_pininfo = bank_arch.col_periphery_top_pininfo
    # sram_components = dict(row_periphery=row_periphery, col_periphery=col_periphery, bitcell_array=bitcell_array)


    sram_bank_config = [32, 512]
    sram_specs = {'word_size': 128}

    dic = {}
    dic['auxcells']={}
    dic['auxcells']['bitcell_array']={}
    dic['auxcells']['bitcell_array']['bitcell']={}
    dic['auxcells']['bitcell_array']['bitcell']['no_rows'] = 2
    dic['auxcells']['bitcell_array']['bitcell']['no_cols'] = 1

    cp = ColPeriVerilogGen(sram_bank_config, sram_specs, dic)

    cp_pin_info = cp.generate_col_peri_top_module(col_periphery_top_pininfo, col_periphery)
