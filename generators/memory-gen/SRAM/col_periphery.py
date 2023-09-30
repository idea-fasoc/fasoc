#!/usr/bin/env python3.7.3
from .cellprops import CellProps


class ColPeriphery():

    def __init__(self):
        pass

    def pre_charge(self):
        name = "pre_charge_1x"
        pin_map = dict(PCH=["PCH", "input", {'no_bits': 1}],
                       BL=["BL", "inout", {'no_bits': 1}],
                       BLB=["BLB", "inout", {'no_bits': 1}],
                       VDD=["VDD", "power"],
                       VSS=["VSS", "ground"])

        is_layout_only = False
        column_muxing = False
        mirror_x = False
        mirror_y = True

        self.pre_charge = CellProps()
        self.pre_charge.update_cellname(name)  # update cell name
        self.pre_charge.update_pininfo(pin_map)  # update pin mapping
        self.pre_charge.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.pre_charge.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.pre_charge

    def col_mux(self):
        name = "col_mux_4x"
        pin_map = dict(CMEn=["EN", "input", {'no_bits': 4}], CMEnB=["ENB", "input", {'no_bits': 4}],
                       BL=["BL", "inout", {'no_bits': 4}], BLB=["BLB", "inout", {'no_bits': 4}],
                       DL=["DL", "inout", {'no_bits': 1}], DLB=["DLB", "inout", {'no_bits': 1}],
                       VDD=["VDD", "power"],
                       VSS=["VSS", "ground"]) # DL and DLB -> Muxed BL and BLB
        is_layout_only = False
        column_muxing = True
        mirror_x = False
        mirror_y = True

        self.col_mux = CellProps()
        self.col_mux.update_cellname(name)  # update cell name
        self.col_mux.update_pininfo(pin_map)
        self.col_mux.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.col_mux.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.col_mux

    def write_driver(self):
        name = "write_driver_4x"
        pin_map = dict(WDEn=["WE", "input", {'no_bits': 1}], WDEnB=["WEB", "input", {'no_bits': 1}],
                       DIN=["DIN", "input", {'no_bits': 1}],
                       DL=["WD", "inout", {'no_bits': 1}], DLB=["WDB", "inout", {'no_bits': 1}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        # pin_map = dict(WE=["WE", "input", {'no_bits': 1}], WEB=["WEB", "input", {'no_bits': 1}],
        #                DIN=["DIN", "input", {'no_bits': 'word_size'}], DL=["DL", "inout", {'no_bits': 'word_size'}],
        #                DLB=["DLB", "inout", {'no_bits': 'word_size'}], VDD=["VDD", "power"], VSS=["VSS", "ground"])
        is_layout_only = False
        column_muxing = True
        mirror_x = False
        mirror_y = True

        self.write_driver = CellProps()
        self.write_driver.update_cellname(name)  # update cell name
        self.write_driver.update_pininfo(pin_map)
        self.write_driver.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.write_driver.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.write_driver

    def sense_amplifier(self):
        name = "sense_amplifier_4x"
        pin_map = dict(SAEn=["SA_EN", "input", {'no_bits': 1}], SAEnB=["SA_PCH", "inout", {'no_bits': 1}],
                       DL=["BL", "inout", {'no_bits': 1}], DLB=["BLB", "inout", {'no_bits': 1}],
                       SAOut=["DL", "inout", {'no_bits': 1}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        # pin_map = dict(SAEn=["SAEn", "input", {'no_bits': 1}], SAEnB=["SAEnB", "inout", {'no_bits': 1}],
        #                DL=["DL", "inout", {'no_bits': 'word_size'}], DLB=["DLB", "inout", {'no_bits': 'word_size'}],
        #                VDD=["VDD", "power"], VSS=["VSS", "ground"])
        is_layout_only = False
        column_muxing = True
        mirror_x = False
        mirror_y = True

        self.sense_amplifier = CellProps()
        self.sense_amplifier.update_cellname(name)  # update cell name
        self.sense_amplifier.update_pininfo(pin_map)
        self.sense_amplifier.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.sense_amplifier.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.sense_amplifier

    def output_driver(self):
        name = "output_driver_4x"
        pin_map = dict(DOUT=["DOUT", "output", {'no_bits': 1}], DoutEn=["Output_EN", "input", {'no_bits': 1}],
                       SAOut=["DIN", "input", {'no_bits': 1}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = False
        column_muxing = True
        mirror_x = False
        mirror_y = True

        self.output_driver = CellProps()
        self.output_driver.update_cellname(name)  # update cell name
        self.output_driver.update_pininfo(pin_map)
        self.output_driver.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.output_driver.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.output_driver

    def col_top_well_contact(self):
        name = "col_top_well_contact_4x"
        pin_map = dict(BL=["BL", "inout", {'no_bits': 4}], BLB=["BLB", "inout", {'no_bits': 4}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = True
        mirror_x = False
        mirror_y = True

        self.col_top_well_contact = CellProps()
        self.col_top_well_contact.update_cellname(name)  # update cell name
        self.col_top_well_contact.update_pininfo(pin_map)
        self.col_top_well_contact.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.col_top_well_contact.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.col_top_well_contact

    def col_bottom_well_contact(self):
        name = "col_bottom_well_contact_4x"
        pin_map = dict(VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = True
        mirror_x = False
        mirror_y = True

        self.col_bottom_well_contact = CellProps()
        self.col_bottom_well_contact.update_cellname(name)  # update cell name
        self.col_bottom_well_contact.update_pininfo(pin_map)
        self.col_bottom_well_contact.update_column_muxing(column_muxing)  # Update if cell is column muxed.
        self.col_bottom_well_contact.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.col_bottom_well_contact

    def get_col_periphery_cells(self):
        return self.col_periphery_cells.keys()

    def get_col_periphery_pins(self):
        return self.pins

    @classmethod
    def get_col_periphery_cls(cls):
        return cls()
