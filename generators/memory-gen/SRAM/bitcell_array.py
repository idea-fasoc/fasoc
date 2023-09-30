#!/usr/bin/env python3.7.3

from .bitcellprops import BitCellProps


class BitCellarray():

    def __init__(self):
        pass

    def bitcell(self):
        name = "bitcell_6T"
        pin_map = dict(WL=["WL", "input", {'no_bits': 2}],
                       BL=["BL", "inout", {'no_bits': 1}], BLB=["BLB", "inout", {'no_bits': 1}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = False
        column_muxing = False
        mirror_x = True
        mirror_y = True

        is_bitcell = True
        orientations = []
        self.bitcell = BitCellProps()
        self.bitcell.update_cellname(name)  # update cell name
        self.bitcell.update_pininfo(pin_map)
        self.bitcell.update_column_muxing(column_muxing)
        self.bitcell.update_layout_props(is_layout_only, mirror_x, mirror_y)
        self.bitcell.update_orientations(orientations)

        return self.bitcell

    def bitcell_end_cell(self):
        name = "bitcell_end_cell_6T"
        pin_map = dict(WL=["WL", "input", {'no_bits': 2}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = False
        mirror_y = True

        self.bitcell_end_cell = BitCellProps()
        self.bitcell_end_cell.update_cellname(name)  # update cell name
        self.bitcell_end_cell.update_pininfo(pin_map)
        self.bitcell_end_cell.update_column_muxing(column_muxing)
        self.bitcell_end_cell.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.bitcell_end_cell

    def edge_cell(self):
        name = "edge_cell_6T"
        pin_map = dict(BL=["BL", "inout", {'no_bits': 2}], BLB=["BLB", "inout", {'no_bits': 2}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = True
        mirror_y = True

        self.edgecell = BitCellProps()
        self.edgecell.update_cellname(name)  # update cell name
        self.edgecell.update_pininfo(pin_map)
        self.edgecell.update_column_muxing(column_muxing)
        self.edgecell.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.edgecell

    def edge_end_cell(self):
        name = "edge_end_cell_6T"
        pin_map = dict(VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = False
        mirror_y = True

        self.edge_end_cell = BitCellProps()
        self.edge_end_cell.update_cellname(name)  # update cell name
        self.edge_end_cell.update_pininfo(pin_map)
        self.edge_end_cell.update_column_muxing(column_muxing)
        self.edge_end_cell.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.edge_end_cell

    def strap_cell(self):
        name = "strap_cell_6T"
        pin_map = dict(BL=["BL", "inout", {'no_bits': 2}], BLB=["BLB", "inout", {'no_bits': 2}],
                       VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = False
        mirror_y = True

        self.strap_cell = BitCellProps()
        self.strap_cell.update_cellname(name)  # update cell name
        self.strap_cell.update_pininfo(pin_map)
        self.strap_cell.update_column_muxing(column_muxing)
        self.strap_cell.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.strap_cell

    def strap_end_cell(self):
        name = "strap_end_cell_6T"
        pin_map = dict(VDD=["VDD", "power"], VSS=["VSS", "ground"])

        is_layout_only = True
        column_muxing = False
        mirror_x = False
        mirror_y = True

        self.strap_end_cell = BitCellProps()
        self.strap_end_cell.update_cellname(name)  # update cell name
        self.strap_end_cell.update_pininfo(pin_map)
        self.strap_end_cell.update_column_muxing(column_muxing)
        self.strap_end_cell.update_layout_props(is_layout_only, mirror_x, mirror_y)

        return self.strap_end_cell
