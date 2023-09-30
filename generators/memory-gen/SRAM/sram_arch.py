#!/usr/bin/env python3.7.3

from .bitcell_array import BitCellarray
from .col_periphery import ColPeriphery
from .row_periphery import RowPeriphery


class SRAM6TArch(RowPeriphery, ColPeriphery, BitCellarray):
    """ This class encapsulates the hierarchical sram architecture with 6T bitcell """

    def __init__(self):
        super().__init__()
        self.bitcell_array = {}
        self.row_periphery = {}
        self.col_periphery = {}

        self.bank_top = self.get_bank_top()

        self.bank_top_pininfo = self.get_bank_top_pininfo()
        self.col_periphery_top_pininfo = self.get_col_periphery_pininfo()
        self.row_periphery_top_pininfo = self.get_row_periphery_pininfo()
        self.bitcell_array_top_pininfo = self.get_bitcell_array_pininfo()
        self.control_unit_top_pininfo = self.get_control_unit_pininfo()

    def bank_top_module(self):
        # Each of the bank components can be updated with any number of cells, but the bank structure for now is
        # standardized interms of row_periphery, col_periphery and bitcell_array.
        # If bank structure is to be updated, MemGen.py has to be updated to accommodate new bank structure.

        bank_row_periphery = self.get_row_periphery()
        bank_col_periphery = self.get_col_periphery()
        bank_bitcell_array = self.get_bitcell_array()
        bank_contol_unit = self.get_control_unit()

        bank_arch = dict(row_periphery=bank_row_periphery, col_periphery=bank_col_periphery,
                         bitcell_array=bank_bitcell_array)

        # Currently:
        #   The keys between the top_module must be same as the keys of the auxcells in respective auxcell definitions.
        #   llly the keys must match the keys in the pin-definitions of the auxcells in collateral files
        #   Required as: pins are checked for the bus or bit at auxcell modules based on the top-level module pininfo.
        # Goal:
        #   The keys of low-level hierarchy are values of the keys of the hierarchy one-level above.
        #   This makes the module-module connections felxible.
        #   Implementation issue: Checking the pin type (bus or bit) and the bus length at auxcell module level is
        #   difficult. Need to re-visit for proper implementation. Not a show-stopper.

        # self.bank_top_module_pininfo = dict(PCH=["PCH", "input", {'bit': None}],
        #                                              CMEn=["CMEn", "input", {'bus': 'col_mux'}],
        #                                              CMEnB=["CMEnB", "input", {'bus': 'col_mux'}],
        #                                              SAEn=["SAEn", "input", {'bit': None}],
        #                                              SAEnB=["SAEnB", "input", {'bit': None}],
        #                                              WE=["WE", "input", {'bit': None}],
        #                                              WEB=["WEB", "input", {'bit': None}],
        #                                              OD_EN=["OD_EN", "input", {'bit': None}],
        #                                              DIN=["DIN", "input", {'bus': 'word_size'}],
        #                                              In1=["In1", "input", {'bus': 'pre_dec_b'}],
        #                                              In2=["In2", "input", {'bus': 'pre_dec_t'}],
        #                                              DOUT=["DOUT", "output", {'bus': 'word_size'}],
        #                                              BL=["BL", "wire", {'bus': 'bank_cols'}],
        #                                              BLB=["BLB", "wire", {'bus': 'bank_cols'}],
        #                                              WL=["WL", "wire", {'bus': 'bank_rows'}],
        #                                              VDD=["VDD", "power"], VSS=["VSS", "ground"])
        self.bank_top_module_pininfo = dict(ADDR=['ADDR', "input", {'bus': 'addr_width'}],
                                            CE=['CE', "input", {'bit': None}],
                                            WE=['WE', "input", {'bit': None}],
                                            CLK=['CLK', "input", {'bit': None}],
                                            DIN=["DIN", "input", {'bus': 'word_size'}],
                                            DOUT=["DOUT", "output", {'bus': 'word_size'}],
                                            PCH=["PCH", "wire", {'bit': None}],
                                            CMEn=["CMEn", "wire", {'bus': 'col_mux'}],
                                            CMEnB=["CMEnB", "wire", {'bus': 'col_mux'}],
                                            SAEn=["SAEn", "wire", {'bit': None}],
                                            SAEnB=["SAEnB", "wire", {'bit': None}],
                                            WDEn=["WDEn", "wire", {'bit': None}],
                                            WDEnB=["WDEnB", "wire", {'bit': None}],
                                            DoutEn=["DoutEn", "wire", {'bit': None}],
                                            row_predec_b=["row_predec_b", "wire", {'bus': 'pre_dec_b'}],
                                            row_predec_t=["row_predec_t", "wire", {'bus': 'pre_dec_t'}],
                                            BL=["BL", "wire", {'bus': 'bank_cols'}],
                                            BLB=["BLB", "wire", {'bus': 'bank_cols'}],
                                            WL=["WL", "wire", {'bus': 'bank_rows'}])

        return bank_arch

    def col_periphery_module(self):
        c = ColPeriphery()
        # The auxcell instance creation can be automated in a loop, however, the tried method
        # "self.col_periphery = {cell : "c.%s()"%cell for cell in self.col_periphery_cells}" is returning instance as
        # string. Need to revisit this to aovid the instance creation on cell basis.

        # The order defines the placement of the auxcells. The index 0 is placed first
        self.col_periphery["col_top_well_contact"] = c.col_top_well_contact()
        self.col_periphery["pre_charge"] = c.pre_charge()
        self.col_periphery["col_mux"] = c.col_mux()
        self.col_periphery["write_driver"] = c.write_driver()
        self.col_periphery["sense_amplifier"] = c.sense_amplifier()
        self.col_periphery["output_driver"] = c.output_driver()
        # self.col_periphery["col_bottom_well_contact"] = c.col_bottom_well_contact()

        # Currently:
        #   The keys between the top_module must be same as the keys of the auxcells in respective auxcell definitions.
        #   llly the keys must match the keys in the pin-definitions of the auxcells in collateral files
        #   Required as: pins are checked for the bus or bit at auxcell modules based on the top-level module pininfo.
        # Goal:
        #   The keys of low-level hierarchy are values of the keys of the hierarchy one-level above.
        #   This makes the module-module connections felxible.
        #   Implementation issue: Checking the pin type (bus or bit) and the bus length at auxcell module level is
        #   difficult. Need to re-visit for proper implementation. Not a show-stopper.
        self.col_periphery_top_module_pininfo = dict(PCH=["PCH", "input", {'bit': None}],
                                                     CMEn=["CMEn", "input", {'bus': 'col_mux'}],
                                                     CMEnB=["CMEnB", "input", {'bus': 'col_mux'}],
                                                     SAEn=["SAEn", "input", {'bit': None}],
                                                     SAEnB=["SAEnB", "input", {'bit': None}],
                                                     WDEn=["WDEn", "input", {'bit': None}],
                                                     WDEnB=["WDEnB", "input", {'bit': None}],
                                                     DoutEn=["DoutEn", "input", {'bit': None}],
                                                     DIN=["DIN", "input", {'bus': 'word_size'}],
                                                     DOUT=["DOUT", "output", {'bus': 'word_size'}],
                                                     BL=["BL", "inout", {'bus': 'bank_cols'}],
                                                     BLB=["BLB", "inout", {'bus': 'bank_cols'}],
                                                     DL=["DL", "wire", {'bus': 'word_size'}],
                                                     DLB=["DLB", "wire", {'bus': 'word_size'}],
                                                     SAOut=["SAOut", "wire", {'bus': 'word_size'}])

        return self.col_periphery

    def row_periphery_module(self):
        r = RowPeriphery()

        self.row_periphery['wl_driver'] = r.wl_driver()
        self.row_periphery['row_top_well_contact'] = r.row_top_well_contact()
        self.row_periphery['row_bottom_well_contact'] = r.row_bottom_well_contact()
        self.row_periphery['row_middle_well_contact'] = r.row_middle_well_contact()

        # Currently:
        #   The keys between the top_module must be same as the keys of the auxcells in respective auxcell definitions.
        #   llly the keys must match the keys in the pin-definitions of the auxcells in collateral files
        #   Required as: pins are checked for the bus or bit at auxcell modules based on the top-level module pininfo.
        # Goal:
        #   The keys of low-level hierarchy are values of the keys of the hierarchy one-level above.
        #   This makes the module-module connections felxible.
        #   Implementation issue: Checking the pin type (bus or bit) and the bus length at auxcell module level is
        #   difficult. Need to re-visit for proper implementation. Not a show-stopper.
        self.row_periphery_top_module_pininfo = dict(row_predec_b=["row_predec_b", "input", {'bus': 'pre_dec_b'}],
                                                     row_predec_t=["row_predec_t", "input", {'bus': 'pre_dec_t'}],
                                                     WL=["WL", "output", {'bus': 'bank_rows'}])

        return self.row_periphery

    def bitcell_array_module(self):
        b = BitCellarray()

        self.bitcell_array['bitcell'] = b.bitcell()
        self.bitcell_array['bitcell_end_cell'] = b.bitcell_end_cell()
        self.bitcell_array['edge_cell'] = b.edge_cell()
        self.bitcell_array['edge_end_cell'] = b.edge_end_cell()
        self.bitcell_array['strap_cell'] = b.strap_cell()
        self.bitcell_array['strap_end_cell'] = b.strap_end_cell()

        # Currently:
        #   The keys between the top_module must be same as the keys of the auxcells in respective auxcell definitions.
        #   llly the keys must match the keys in the pin-definitions of the auxcells in collateral files
        #   Required as: pins are checked for the bus or bit at auxcell modules based on the top-level module pininfo.
        # Goal:
        #   The keys of low-level hierarchy are values of the keys of the hierarchy one-level above.
        #   This makes the module-module connections felxible.
        #   Implementation issue: Checking the pin type (bus or bit) and the bus length at auxcell module level is
        #   difficult. Need to re-visit for proper implementation. Not a show-stopper.

        self.bitcell_array_top_module_pininfo = dict(WL=["WL", "input", {'bus': 'bank_rows'}],
                                                     BL=["BL", "inout", {'bus': 'bank_cols'}],
                                                     BLB=["BLB", "inout", {'bus': 'bank_cols'}])

        return self.bitcell_array

    def control_unit_module(self):
        self.control_unit_top_module_pininfo = dict(ADDR=['ADDR', "input", {'bus': 'addr_width'}],
                                                    CE=['CE', "input", {'bit': None}],
                                                    WE=['WE', "input", {'bit': None}],
                                                    CLK=['CLK', "input", {'bit': None}],
                                                    PCH=["PCH", "output", {'bit': None}],
                                                    CMEn=["CMEn", "output", {'bus': 'col_mux'}],
                                                    CMEnB=["CMEnB", "output", {'bus': 'col_mux'}],
                                                    SAEn=["SAEn", "output", {'bit': None}],
                                                    SAEnB=["SAEnB", "output", {'bit': None}],
                                                    WDEn=["WDEn", "output", {'bit': None}],
                                                    WDEnB=["WDEnB", "output", {'bit': None}],
                                                    DoutEn=["DoutEn", "output", {'bit': None}],
                                                    row_predec_b=["row_predec_b", "output", {'bus': 'pre_dec_b'}],
                                                    row_predec_t=["row_predec_t", "output", {'bus': 'pre_dec_t'}],
                                                    clk_gated = ["clk_gated", "wire", {'bit': None}],
                                                    we_gated = ["we_gated", "wire", {'bit': None}],
                                                    WL_EN = ["WL_EN", "wire", {'bit': None}],
                                                    addr_gated = ["addr_gated", "wire", {'bus': 'addr_width'}])

        return None

    def multi_bank(self):
        pass

    def get_bank_top(self):
        return self.bank_top_module()

    def get_col_periphery(self):
        return self.col_periphery_module()

    def get_row_periphery(self):
        return self.row_periphery_module()

    def get_bitcell_array(self):
        return self.bitcell_array_module()

    def get_control_unit(self):
        return self.control_unit_module()

    def get_col_periphery_cells(self):
        return self.col_periphery.keys()

    def get_row_periphery_cells(self):
        return self.row_periphery.keys()

    def get_bitcell_array_cells(self):
        return self.bitcell_array.keys()

    def get_bank_top_pininfo(self):
        return self.bank_top_module_pininfo

    def get_col_periphery_pininfo(self):
        return self.col_periphery_top_module_pininfo

    def get_row_periphery_pininfo(self):
        return self.row_periphery_top_module_pininfo

    def get_bitcell_array_pininfo(self):
        return self.bitcell_array_top_module_pininfo

    def get_control_unit_pininfo(self):
        return self.control_unit_top_module_pininfo
