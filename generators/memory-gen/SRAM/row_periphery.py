#!/usr/bin/env python3.7.3
from .cellprops import CellProps


class RowPeriphery():

    def __init__(self):
        pass

    def wl_driver(self):
        name = "wordline_driver_2x"
        # pin_map = dict(In1=["In1", "input", {'bus': 'pre_dec_LSB'}], In2=["In2", "input", {'bus': 'pre_dec_MSB'}],
        #                WL=["WL", "output", {'bus': 'bank_rows'}],
        #                VDD=["VDD", "power"], VSS=["VSS", "ground"])
        pin_map = dict(In1=["IN1", "input", {'no_bits': 2}],
                       In2=["IN2", "input", {'no_bits': 1}],
                       WL=["WL", "output", {'no_bits': 2}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])
        is_layout_only = False
        column_muxing = False
        mirror_x = True
        mirror_y = False

        self.wl_driver = CellProps()
        self.wl_driver.update_cellname(name)  # update cell name
        self.wl_driver.update_pininfo(pin_map)
        self.wl_driver.update_column_muxing(column_muxing)
        self.wl_driver.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.wl_driver

    def row_top_well_contact(self):
        name = "row_top_well_contact_1x"
        pin_map = dict(VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = True
        mirror_y = False

        self.row_top_well_contact = CellProps()
        self.row_top_well_contact.update_cellname(name)  # update cell name
        self.row_top_well_contact.update_pininfo(pin_map)
        self.row_top_well_contact.update_column_muxing(column_muxing)
        self.row_top_well_contact.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.row_top_well_contact

    def row_middle_well_contact(self):
        name = "row_middle_well_contact_1x"
        pin_map = dict(VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = True
        mirror_y = False

        self.row_middle_well_contact = CellProps()
        self.row_middle_well_contact.update_cellname(name)  # update cell name
        self.row_middle_well_contact.update_pininfo(pin_map)
        self.row_middle_well_contact.update_column_muxing(column_muxing)
        self.row_middle_well_contact.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.row_middle_well_contact

    def row_bottom_well_contact(self):
        name = "row_bottom_well_contact_1x"
        pin_map = dict(VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = True
        mirror_y = False

        self.row_bottom_well_contact = CellProps()
        self.row_bottom_well_contact.update_cellname(name)  # update cell name
        self.row_bottom_well_contact.update_pininfo(pin_map)
        self.row_bottom_well_contact.update_column_muxing(column_muxing)
        self.row_bottom_well_contact.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.row_bottom_well_contact

    def get_row_periphery_cells(self):
        return self.row_periphery_cells.keys()

    def get_row_periphery_pins(self):
        return self.pins

    @classmethod
    def get_row_periphery_cls(cls):
        return cls()
