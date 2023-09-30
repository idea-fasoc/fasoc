import logging
import math
import os
import re
import sys
from collections import namedtuple

sys.path.append('/net/gaylord/t/kamineni/dev/pwd/memory-gen-beta/')
# sys.path.append('/net/gaylord/t/kamineni/dev/pwd/memory-gen-beta/SRAM')
sys.path.append('/net/gaylord/t/kamineni/dev/pwd/memory-gen-beta/private/')
from globals.global_utils import get_cell_size
from apr_pymodules.floorplan import *

log = logging.getLogger(__name__)


class FloorPlan:

    def __init__(self):
        self.auxcelllibdir = os.getenv('auxcell_lib_path')
        self.auxcells_lef_dir = os.path.join(self.auxcelllibdir, 'LEF')

    def create_bank_floorplan(self, bank_apr_dir, bank_top_module_name, tech_config_dic, sram_bank_arch,
                              sram_bank_config, sram_specs, bus_params):
        """ Function to create the sram bank floor plan and generate the  floorplan.tcl file for apr"""

        self.bank_apr_dir = bank_apr_dir
        self.bank_top_module_name = bank_top_module_name

        self.bank_scripts_dir = os.path.dirname(self.bank_apr_dir)
        self.bank_gen_dir = os.path.dirname(self.bank_scripts_dir)
        self.bank_synth_area_report = os.path.join(self.bank_gen_dir,
                                                   f'reports/dc/{self.bank_top_module_name}.mapped.area'
                                                   f'.rpt')

        self.tech_config_dic = tech_config_dic

        self.bank_arch_type = self.tech_config_dic['layout_info']['bank']['bank_arch_type']

        self.row_periphery = sram_bank_arch['row_periphery']
        self.col_periphery = sram_bank_arch['col_periphery']
        self.bitcell_array = sram_bank_arch['bitcell_array']

        self.bank_rows = sram_bank_config[0]
        self.bank_cols = sram_bank_config[1]
        self.word_size = sram_specs['word_size']
        self.bank_bus_params = bus_params

        self.h_layer = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_layer']
        self.h_width = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_min_width']
        self.h_depth = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_depth']

        # Look for the auxcell LEF directory
        if not os.path.isdir(self.auxcells_lef_dir):
            log.error(
                f"The  {self.auxcells_lef_dir} dir does not exists, which is required for floor-planning the SRAM "
                f"macro bank")
            log.error("Make sure the auxcell lef files are present and re-run MemGen."
                      "Exiting MemGen.....")
            sys.exit(1)

        #################################
        # Estimate the size of the bank #
        #################################

        self.bank_size = self.get_banksize(self.bitcell_array, self.row_periphery, self.col_periphery)

        print("Total bank size is ", self.bank_size.bank_size_x, self.bank_size.bank_size_y)

        # Check for CU area, and update the bank size accodingly.
        # Should we consider the io pins for bank size?

        ###############################################
        # Determine bank component start co-ordinates #
        ###############################################

        # Determine the starting points of bitcell array, row_periphery and column-periphery.
        # Starting points are determined with respect to the bitcell array core.

        self.start_co_ordinates = self.get_bank_comp_start_coord(self.bitcell_array, self.row_periphery,
                                                                 self.col_periphery)

        # Row Periphery
        self._start_rp_x = self.start_co_ordinates[0].rp_start_x
        self._start_rp_y = self.start_co_ordinates[0].rp_start_y

        print("row_periphery start co-ordinates", self._start_rp_x, self._start_rp_y)

        # Column Periphery
        self._start_cp_x = self.start_co_ordinates[1].cp_start_x
        self._start_cp_y = self.start_co_ordinates[1].cp_start_y

        print("col_periphery start co-ordinates", self._start_cp_x, self._start_cp_y)

        # Bitcell array
        self._start_bca_x = self.start_co_ordinates[2].bca_start_x
        self._start_bca_y = self.start_co_ordinates[2].bca_start_y

        print("bitcell array start co-ordinates", self._start_bca_x, self._start_bca_y)

        #########################
        # Generate the I/O plan #
        #########################
        # This has to be updated for the cu_rp_bca_cp as well.
        self.create_bank_io_plan(bank_apr_dir)

        # Create a floor plan file
        self.fp_fh = open(os.path.join(bank_apr_dir, 'floorplan.tcl'), 'w')
        # Floorplan based on die size.
        # Die margins are 0 for bank.
        floorplan_command = floorplan('innovus', self.bank_size.bank_size_x, self.bank_size.bank_size_y,
                                      [0, 0, 0, 0])
        self.fp_fh.write(floorplan_command + '\n')

        ioplan_command = load_pin_io('innovus', False, self.io_file)
        self.fp_fh.write(ioplan_command + '\n')

        ###########################
        # Place the bank auxcells #
        ###########################

        # Row-periphery placement
        self.place_row_periphery(self.row_periphery, self._start_rp_x, self._start_rp_y)

        # Bitcell array Placement.
        self.place_bitcell_array(self.bitcell_array, self._start_bca_x, self._start_bca_y)

        # Col_periphery Placement.

        self.place_col_periphery(self.col_periphery, self._start_cp_x, self._start_cp_y)

        # Cut the STD cells rows so as to place the control unit cells in the dedicated area.
        #  ______________
        # |       |      |
        # |  BCA  |  CP  |
        # |_______|______|
        # |       |
        # |   RP  |
        # |_______|
        # Cutting a rectinlinear is not available. So, need to cut two times covering different area.
        # This has to be updated for the cu_rp_bca_cp as well.
        # 1st cut covering BCA + RP
        self.fp_fh.write("######### Cut the area around the bitcell array, colum-periphery and the row periphery "
                         "######### \n")

        rp_bca_LLX = 0
        rp_bca_LLY = 0
        rp_bca_URX = self.bitcell_array_size.size_x
        rp_bca_URY = self.bank_size.bank_size_y

        cut1_commad = create_area_rowcut('innovus', rp_bca_LLX, rp_bca_LLY, rp_bca_URX, rp_bca_URY)
        self.fp_fh.write(f'{cut1_commad}\n')

        # 2nd Cut covering CP
        cp_LLX = self.bitcell_array_size.size_x
        # cp_LLY = self.bitcell_array_size.size_y
        cp_LLY = self.row_periphery_size.size_y
        cp_URX = self.bank_size.bank_size_x
        cp_URY = self.bank_size.bank_size_y

        cut2_commad = create_area_rowcut('innovus', cp_LLX, cp_LLY, cp_URX, cp_URY)
        self.fp_fh.write(f'{cut2_commad}\n')

        # ## Cutting around CU for allowing signal routing between RP and CP. ###
        self.fp_fh.write("######### Cut the area around the CU to enable routing space ######## \n")
        LS_LLX = self.row_periphery_size.size_x
        LS_LLY = 0
        LS_URX = self.row_periphery_size.size_x + self.tech_config_dic['layout_info']['bank']['control_unit_spacing'][
            'min_ls_gap']
        # LS_URY = self.row_periphery_size.size_y + self.tech_config_dic['layout_info']['bank']['component_spacing'][
        # 'min_rp_bca_spacing']
        LS_URY = self._start_bca_y

        cut_ls_commad = create_area_rowcut('innovus', LS_LLX, LS_LLY, LS_URX, LS_URY)
        self.fp_fh.write(f'{cut_ls_commad}\n')

        # Top side
        if self._start_cp_y - self.row_periphery_size.size_y < self.tech_config_dic['layout_info']['bank']['control_unit_spacing']['min_ts_gap']:
            # If the Rp_bca_spacing + bitcell_edge_cell_height (Col periphery starting point) < required spacing
            # Calculate the difference and adjust it for the TS_LLY point.
            height_diff = self.tech_config_dic['layout_info']['bank']['control_unit_spacing']['min_ts_gap'] - (self._start_cp_y - self.row_periphery_size.size_y)
            TS_LLX = self.row_periphery_size.size_x
            TS_LLY = self.row_periphery_size.size_y - height_diff
            TS_URX = self.bank_size.bank_size_x
            TS_URY = self._start_cp_y

            cut_ts_commad = create_area_rowcut('innovus', TS_LLX, TS_LLY, TS_URX, TS_URY)
            self.fp_fh.write(f'{cut_ts_commad}\n')
        else:
            TS_LLX = self.row_periphery_size.size_x
            TS_LLY = self.row_periphery_size.size_y
            TS_URX = self.bank_size.bank_size_x
            TS_URY = self._start_cp_y
            # No need to cut a row here as it is already taken-care of while cutting rows for CP.


        BS_LLX = self.row_periphery_size.size_x
        BS_LLY = 0
        BS_URX = self.bank_size.bank_size_x
        BS_URY = self.tech_config_dic['layout_info']['bank']['control_unit_spacing']['min_bs_gap']

        cut_bs_commad = create_area_rowcut('innovus', BS_LLX, BS_LLY, BS_URX, BS_URY)
        self.fp_fh.write(f'{cut_bs_commad}\n')

        #
        RS_LLX = self.bank_size.bank_size_x - self.tech_config_dic['layout_info']['bank']['control_unit_spacing'][
            'min_rs_gap']
        RS_LLY = 0
        RS_URX = self.bank_size.bank_size_x
        # RS_URY = self.row_periphery_size.size_y + self.tech_config_dic['layout_info']['bank']['component_spacing']
        # ['min_rp_bca_spacing']
        RS_URY = self._start_bca_y

        cut_rs_commad = create_area_rowcut('innovus', RS_LLX, RS_LLY, RS_URX, RS_URY)
        self.fp_fh.write(f'{cut_rs_commad}\n')

        # Create Route Blockages

        # return the rp and cu power routing area co-ordinates.
        # Width = bank_width from origin.
        # Height = height of CU STD cell rows calculated with BS_URY, and TS_LLY
        return [0, BS_URY, self.bank_size.bank_size_x, TS_LLY]

    def get_banksize(self, bitcell_array, row_periphery, col_periphery):
        """ Determines the size of the bank and variables for the floor-planning"""

        self.row_periphery_size = self.get_rowperiphery_size(row_periphery)
        self.col_periphery_size = self.get_colperiphery_size(col_periphery)
        self.bitcell_array_size = self.get_bitcellarray_size(bitcell_array)

        # Estimate the bank size from the component sizes and the default allowed spacing between each components as
        # sepcified in the tech collateral file.

        # For FinFets as seen in GF12, there is restriction on the fin orientation, which makes the size calculation
        # different.
        # The min spacing can be either vertical or horizontal. Depending on the how the periphery is added with the
        # bitcell array

        # Estimate the bank sizes
        if self.bank_arch_type == 'cu_rp_bca_cp':

            self.bank_size_x = round(self.row_periphery_size.size_x + self.bitcell_array_size.size_x + \
                                     self.tech_config_dic['layout_info']['bank']['component_spacing'][
                                         'min_rp_bca_spacing'], 3)
            self.bank_size_y = round(self.col_periphery_size.size_y + self.bitcell_array_size.size_y + \
                                     self.tech_config_dic['layout_info']['bank']['component_spacing'][
                                         'min_cp_bca_spacing'], 3)

        elif self.bank_arch_type == 'rp_bca_cp_cu':

            self.bank_size_x = round(self.col_periphery_size.size_x + \
                                     max(self.bitcell_array_size.size_x, self.row_periphery_size.size_x) + \
                                     self.tech_config_dic['layout_info']['bank']['component_spacing'][
                                         'min_cp_bca_spacing'], 3)
            self.bank_size_y = round(self.row_periphery_size.size_y + \
                                     max(self.bitcell_array_size.size_y, self.col_periphery_size.size_y) + \
                                     self.tech_config_dic['layout_info']['bank']['component_spacing'][
                                         'min_rp_bca_spacing'], 3)

        print("Total Bank size before CU update", self.bank_size_x, self.bank_size_y)

        #################################################################################################
        # Estimate the CU size and re-adjust the bank size to accommodate the CU placement and routing. #
        #################################################################################################

        # Estimate the initial CU area:
        self.cu_size_x = round(self.bank_size_x - self.bitcell_array_size.size_x, 3)
        self.cu_size_y = round(self.bank_size_y - self.bitcell_array_size.size_y, 3)

        print("Initial CU sizes before update", self.cu_size_x, self.cu_size_y)

        # # Estimate the CU size and re-adjust the bank size to accommodate the CU placement and routing.

        # with open(self.bank_synth_area_report, 'r')as file:
        #     filedata = file.read()
        # m = re.search('Total cell area: *([0-9.]*)', filedata)

        # if m:
        #     self.synth_cu_area = round(float(m.group(1)), 3)
        # else:
        #     print(f'Synthesis of {self.bank_top_module_name} Failed')
        #     sys.exit(1)

        # # Estimate the required control unit area.
        # # Setting 2.5 -> considering the Cu area estimation from synthesis as 40% of total req area to accommodate for
        # # routing and congestion. Can update this with a more realistic estimate through CU area model.

        # self.req_cu_area = round(2.5 * self.synth_cu_area, 3)

        # # Estimate the size diff
        # self.req_cu_extra_area = self.req_cu_area - self.synth_cu_area

        # # Calculate the extra x and y dimensions to be added to bank size.
        # # Aussming the x and y dimensions of bank are increased equally.
        # # Can update later with a model that results less area overhead with the extra x- and y dimensions.

        # self.extra_bank_size_x = round(math.sqrt(self.req_cu_extra_area), 3)
        # self.extra_bank_size_y = self.extra_bank_size_x
        # Temporarily making the extra bank size as 0.0 for testing the floorplanpy
        self.extra_bank_size_x = 0
        self.extra_bank_size_y = 0
        # The new bank size
        self.bank_size_x = round(self.bank_size_x + self.extra_bank_size_x, 3)
        self.bank_size_y = round(self.bank_size_y + self.extra_bank_size_y, 3)

        # Update the CU area
        self.cu_size_x = round(self.cu_size_x + self.extra_bank_size_x, 3)
        self.cu_size_y = round(self.cu_size_y + self.extra_bank_size_y, 3)

        # Check if the bank_size width can accommodate the pin_depth of the DIN and Dout along size the CP
        # This has to be updated for the cu_rp_bca_cp as well
        width_req_diff = self.bank_size_x - (self.bitcell_array_size.size_x +
                                             self.tech_config_dic['layout_info']['bank']['component_spacing']
                                             ['min_cp_bca_spacing'] + self.col_periphery_size.size_x + self.h_depth)

        if width_req_diff < 0:
            # Adjust the bank size to accommodate the pindepth
            print("The width req diff", width_req_diff)
            print("Before updating the banks size width for pin depth", self.bank_size_x)
            self.bank_size_x = self.bank_size_x + self.h_depth
            print("After updating the banks size width for pin depth", self.bank_size_x)
        # Return the values
        _get_banksize = namedtuple("get_banksize", ["bank_size_x", "bank_size_y"])

        return _get_banksize(self.bank_size_x, self.bank_size_y)

    def get_rowperiphery_size(self, row_periphery):
        """ Determines the width (size.x) and height (size.y) of row periphery
        Input: Row periphery architecture.
        """
        # Initialize the
        rp_size_x = 0
        rp_size_y = 0  # Initialize sizes

        # Obtain the cell sizes from their respective LEF files and update the their properties.
        for k, v in row_periphery.items():
            row_auxcell_lef_file = os.path.join(self.auxcells_lef_dir, v.get_cellname() + '.lef')
            size = get_cell_size(row_auxcell_lef_file)
            size_x = size.size_x
            size_y = size.size_y
            print("row_periphery cell sizes from lef parsing", k, v.get_cellname(), size_x, size_y)
            # Update the cell size
            v.update_size(size_x, size_y)

        # For Finet as seen in GF12, the Fin orientation restricts the row_periphery is to be bottom of bitcell array
        # which changes the way component width and height are calculated in the planar cmos.

        # Considering position of row_periphery to bitcell array through the below key word. Key name will be updated.

        if self.bank_arch_type == 'cu_rp_bca_cp':
            """ The sizes are calculated with the following assumptions:
            1. The height of wl driver matches the height pitch of bitcell. 
            2. The height of middle well contact is equal to height of bitcell strap cell. The bottom and top
            contacts need not be same height of edge_cell of bitcell array. If same, the height of row_periphery will 
            be same as bitcell array; else, height diff = 2*bitcell_edge_height - (bottom_tap + top_tap). Make sure, the
            difference is considered while calculating bank size and also placement of row_periphery cells in floorplan.
            Nevertheless, the bitcell height and widths are not used here for calculating the row_periphery size.
            3. The widths of row_periphery cells (wl_driver and well contacts) are same."""

            for key, value in row_periphery.items():
                rows_auxcell_covers = self.tech_config_dic['auxcells']['row_periphery'][key]['no_rows']
                if key == 'wl_driver':
                    rp_size_y = rp_size_y + value.get_size().size_y * (self.bank_rows / rows_auxcell_covers)
                else:
                    rp_size_y = rp_size_y + value.get_size().size_y

            rp_size_x = round(rp_size_x, 3)
            rp_size_x = row_periphery['wl_driver'].get_size().size_x

        elif self.bank_arch_type == 'rp_bca_cp_cu':
            """ The sizes are calculated with the following assumptions:
            1. The width of wl driver matches the width pitch of bitcell. 
            2. The width of middle well contact is equal to width of bitcell strap cell. The bottom(right) and top(left)
            contacts need not be of same width of edge_cell of bitcell array. If same, the width of row_periphery will 
            be same as bitcell array; else, width diff = 2*bitcell_edge_width - (bottom_tap + top_tap). Make sure, the
            difference is considered while calculating bank size and also placement of row_periphery cells in floorplan.
            Nevertheless, the bitcell height and widths are not used here for calculating the row_periphery size.
            3. The heights of row_periphery cells (wl_driver and well contacts) are same."""

            for key, value in row_periphery.items():
                rows_auxcell_covers = self.tech_config_dic['auxcells']['row_periphery'][key]['no_rows']
                if key == 'wl_driver':
                    rp_size_x = rp_size_x + value.get_size().size_x * int(self.bank_rows / rows_auxcell_covers)
                else:
                    rp_size_x = rp_size_x + value.get_size().size_x
            rp_size_x = round(rp_size_x, 3)
            rp_size_y = row_periphery['wl_driver'].get_size().size_y

        _get_size = namedtuple("get_rowperiphery_size", ["size_x", "size_y"])

        print("row_periphery size", rp_size_x, rp_size_y)

        return _get_size(rp_size_x, rp_size_y)

    def get_colperiphery_size(self, col_periphery):
        """ Determines the width (size.x) and height (size.y) of column periphery
        Input: Column periphery architecture.
        """
        # Initialize the Sizes
        cp_size_x = 0
        cp_size_y = 0

        # Obtain the cell sizes from their respective LEF files and update the their properties.
        for k, v in col_periphery.items():
            col_auxcell_lef_file = os.path.join(self.auxcells_lef_dir, v.get_cellname() + '.lef')
            size = get_cell_size(col_auxcell_lef_file)
            _size_x = size.size_x
            _size_y = size.size_y
            print("col_periphery cell sizes from lef parsing", k, v.get_cellname(), _size_x, _size_y)
            # Update the cell size
            v.update_size(_size_x, _size_y)

        # Considering position of row_periphery to bitcell array through the below key word. Key name will be updated.

        if self.bank_arch_type == 'cu_rp_bca_cp':
            # For FinFET:
            """ The sizes are calculated with the following assumptions:
            1. Col-periphery cells are designed as per the bitcell pitch. Non-column mux cells are single pitch width,  
            and the col-muxed cells width is multiple of no_col_mux_cols and bitcell width. 
            2. All Non-col mux cells are equal in their widths, and all the colmuxed cells are equal in their widths. 
            3. For col periphery width calculation, the pitch width of bitcell is estimated as width of pre_charge.
            4. Nevertheless, the bitcell height and widths are not used here for calculating the row_periphery size. """

            cp_size_x = round(col_periphery['pre_charge'].get_size().size_x * self.bank_cols, 3)

            for auxcell in col_periphery.keys():
                size = col_periphery[auxcell].get_size()
                cp_size_y = cp_size_y + size.size_y

        elif self.bank_arch_type == 'rp_bca_cp_cu':
            # For FinFET:
            """ The sizes are calculated with the following assumptions:
            1. Col-periphery cells are designed as per the bitcell pitch. Non-column mux cells are single pitch height,  
            and the col-muxed cells height is multiple of no_col_mux_cols and bitcell height. 
            2. All Non-col mux cells are equal in their heights, and all then colmuxed cells are equal in their heights. 
            3. For col periphery height calculation, pitch height of bitcell is estimated as height of pre_charge.
            4. Nevertheless, the bitcell height and widths are not used here for calculating the row_periphery size. """

            for auxcell in col_periphery.keys():
                size = col_periphery[auxcell].get_size()
                cp_size_x = cp_size_x + size.size_x

            cp_size_x = round(cp_size_x, 3)
            cp_size_y = round(col_periphery['pre_charge'].get_size().size_y * self.bank_cols, 3)

        _get_size = namedtuple("get_colperiphery_size", ["size_x", "size_y"])

        print("col_periphery size", cp_size_x, cp_size_y)

        return _get_size(cp_size_x, cp_size_y)

    def get_bitcellarray_size(self, bitcell_array):
        """ Determines the width (size.x) and height (size.y) of bitcell array.
        Input: Bitcell array architecture
        """
        # Initialize the sizes
        bca_size_x = 0
        bca_size_y = 0

        for k, v in bitcell_array.items():
            bca_auxcell_lef_file = os.path.join(self.auxcells_lef_dir, v.get_cellname() + '.lef')
            size = get_cell_size(bca_auxcell_lef_file)
            _size_x = size.size_x
            _size_y = size.size_y
            print("bitcell array sizes from lef parsing", k, v.get_cellname(), _size_x, _size_y)
            # Update the cell size
            v.update_size(_size_x, _size_y)

        # Considering the rows and cols of bitcell array are inverted due to the change in position of peripheral
        # components wrt bitcell arrat. Considering the difference through the below key word. Key name will be updated.

        rows_auxcell_covers = self.tech_config_dic['auxcells']['bitcell_array']['bitcell']['no_rows']
        cols_auxcell_covers = self.tech_config_dic['auxcells']['bitcell_array']['bitcell']['no_cols']
        # Bitcell array architecture is standardized interms of bitcell, edge_cell, strap_cell, and their end_cells.
        if self.bank_arch_type == 'cu_rp_bca_cp':

            bca_size_x = round((self.bank_cols / cols_auxcell_covers) * bitcell_array['bitcell'].get_size().size_x + \
                               2 * bitcell_array['bitcell_end_cell'].get_size().size_x, 3)
            bca_size_y = round((self.bank_rows / rows_auxcell_covers) * bitcell_array['bitcell'].get_size().size_y \
                               + 2 * bitcell_array['edge_cell'].get_size().size_y \
                               + bitcell_array['strap_cell'].get_size().size_y, 3)

        elif self.bank_arch_type == 'rp_bca_cp_cu':
            bca_size_y = round((self.bank_cols / cols_auxcell_covers) * bitcell_array['bitcell'].get_size().size_y + \
                               2 * bitcell_array['bitcell_end_cell'].get_size().size_y, 3)
            bca_size_x = round((self.bank_rows / rows_auxcell_covers) * bitcell_array['bitcell'].get_size().size_x \
                               + 2 * bitcell_array['edge_cell'].get_size().size_x \
                               + bitcell_array['strap_cell'].get_size().size_x, 3)

        _get_size = namedtuple("get_bitcellarray_size", ["size_x", "size_y"])

        print("bitcell_array size", bca_size_x, bca_size_y)

        return _get_size(bca_size_x, bca_size_y)

    def get_bank_comp_start_coord(self, bitcell_array, row_periphery, col_periphery) -> list:

        # Get start co-ordinates of bitcell array and periphery with the new bank size.

        if self.bank_arch_type == 'cu_rp_bca_cp':
            pass
        elif self.bank_arch_type == 'rp_bca_cp_cu':
            #  ____________________
            # |       |   |       |
            # |  BCA  |   |  CP   |
            # |_______bca cp______|
            # |       |
            # |   RP  |
            # |_______(rp)  # rp, bca, cp represnts the start co-ordinates positions

            # Row periphery start cor-ordinates.
            # if self.bitcell_array_size.size_x == self.row_periphery_size.size_x:
            #     self.rp_start_x = round(self.row_periphery_size.size_x, 3)
            # else:
            #     # the
            #     self.rp_start_x = round(self.bitcell_array_size.size_x - \
            #                             (bitcell_array['edge_cell'].get_size().size_x -
            #                              row_periphery['row_bottom_well_contact'].get_size().size_x), 3)
            # Assuming the row periphery, and the bitcell array has same width, with widths of bottom, middle, and
            # top well contacts matches with the bottom edge cell, strap cell and top edge cells of bitcell array.
            self.rp_start_x = round(self.row_periphery_size.size_x, 3)
            self.rp_start_y = 0

            # Copl periphery Including Gap to the right of col_periphery to place the DIN and DOUT pins. As next
            # step, can parse the outputbuffer, determine the DOUT and DIn locations, and place them appropriately.
            # self.cp_start_x = round(self.bank_size_x - self.col_periphery_size.size_x - round((self.h_depth * 2), 3), 3)
            # self.cp_start_y = round(self.bank_size_y - (self.row_periphery_size.size_y +
            #                                       self.tech_config_dic['layout_info']['bank']['component_spacing'][
            #                                           'min_rp_bca_spacing'] +
            #                                       bitcell_array['bitcell_end_cell'].get_size().size_y
            #                                       ), 3)

            # Modified from above: Col periphery will be next to bca with the min_cp_bca_spacing, Any extra size
            # required to accommodate the Cu size will be on to the right side of col-peripery, where the DIN and DOUT
            # pins are placed.

            self.cp_start_x = round(
                self.bitcell_array_size.size_x + self.tech_config_dic['layout_info']['bank']['component_spacing'][
                    'min_cp_bca_spacing'], 3)
            self.cp_start_y = round(
                self.bank_size_y - self.bitcell_array_size.size_y + bitcell_array['bitcell_end_cell'].get_size().size_y,
                3)  # Same y-cor as bitcell array.

            # Bitcell array
            self.bca_start_x = round(self.bitcell_array_size.size_x, 3)
            self.bca_start_y = round(self.bank_size_y - self.bitcell_array_size.size_y, 3)

        rp_start_coord = namedtuple("get_bank_comp_start_coord", ["rp_start_x", "rp_start_y"])
        cp_start_coord = namedtuple("get_bank_comp_start_coord", ["cp_start_x", "cp_start_y"])
        bca_start_coord = namedtuple("get_bank_comp_start_coord", ["bca_start_x", "bca_start_y"])

        return [rp_start_coord(self.rp_start_x, self.rp_start_y), cp_start_coord(self.cp_start_x, self.cp_start_y),
                bca_start_coord(self.bca_start_x, self.bca_start_y)]

    def place_row_periphery(self, row_pheriphery, start_x_cor, start_y_cor):

        self.fp_fh.write('############################\n')
        self.fp_fh.write('# Place the row periphery. #\n')
        self.fp_fh.write('############################\n\n')

        # Initial placement co-ordinates
        row_periphery_x = start_x_cor
        row_periphery_y = start_y_cor

        # Collect the orientations of all the auxcells from tech collateral.
        # Can later update this by parsing the LEF of respective auxcells.
        row_top_well_contact_orientations = row_pheriphery['row_top_well_contact'].get_orientations()
        row_bottom_well_contact_orientations = row_pheriphery['row_bottom_well_contact'].get_orientations()
        row_middle_well_contact_orientations = row_pheriphery['row_middle_well_contact'].get_orientations()
        # The orientations for wl driver can be 2, and we need to conider that.
        row_wl_driver_orientations = row_pheriphery['wl_driver'].get_orientations()

        self.fp_fh.write('##################################\n')
        self.fp_fh.write('# Place the bottom well contact. #\n')
        self.fp_fh.write('##################################\n\n')

        # Update the initial placement co-ordinates as per the bank_arch type.
        # For rp_bca_cp_cu type,substract the width of the bottom well contact. For the cu_rp_bca_cp type, as it is.
        if self.bank_arch_type == 'cu_rp_bca_cp':
            row_periphery_x = row_periphery_x
            row_periphery_y = row_periphery_y
        elif self.bank_arch_type == 'rp_bca_cp_cu':
            print("row peripery x for bottom well contact before rounding",
                  row_periphery_x - row_pheriphery['row_bottom_well_contact'].get_size().size_x)
            row_periphery_x = round(row_periphery_x - row_pheriphery['row_bottom_well_contact'].get_size().size_x, 3)
            row_periphery_y = row_periphery_y

        instance_name = 'rp/rp_bwc'
        orientation = row_bottom_well_contact_orientations[0]

        macro_place_command = place_macro('innovus', instance_name, row_periphery_x, row_periphery_y, orientation)
        self.fp_fh.write(macro_place_command + '\n')

        self.fp_fh.write('###########################################\n')
        self.fp_fh.write('# Place the bottom half word-line drivers #\n')
        self.fp_fh.write('###########################################\n\n')

        # The number of WL drivers instances -> on the no of rows each wl_driver covers.
        wld_auxcell_no_rows = self.tech_config_dic['auxcells']['row_periphery']['wl_driver']['no_rows']

        for i in range(0, int(self.bank_rows / (2 * wld_auxcell_no_rows))):

            # Update the placement co-ordinates from previous auxcell (1st bottom-well cap, later WL driver) placement.
            if self.bank_arch_type == 'cu_rp_bca_cp':
                # x co-ord remains same, and y co-ord gets updated
                row_periphery_x = row_periphery_x
                if i == 0:
                    row_periphery_y = round(
                        row_periphery_y + row_pheriphery['row_bottom_well_contact'].get_size().size_y, 3)
                else:
                    row_periphery_y = round(row_periphery_y + row_pheriphery['wl_driver'].get_size().size_y, 3)
            elif self.bank_arch_type == 'rp_bca_cp_cu':
                # y co-ord reamins same, and x co-ord gets updated.
                row_periphery_x = round(row_periphery_x - row_pheriphery['wl_driver'].get_size().size_x, 3)
                row_periphery_y = row_periphery_y

            # Instance name is adapted from verilog generation.
            # If Verilog generation of row_periphery changes, the instance_name has to be updated accordingly
            instance_name = 'rp/rp_wld_b/inst%d' % i

            if len(row_wl_driver_orientations) > 1:
                if (i % 2) == 0:
                    orientation = row_wl_driver_orientations[0]
                else:
                    orientation = row_wl_driver_orientations[1]
            else:
                orientation = row_wl_driver_orientations[0]

            macro_place_command = place_macro('innovus', instance_name, row_periphery_x, row_periphery_y, orientation)
            self.fp_fh.write(macro_place_command + '\n')

        self.fp_fh.write('##################################\n')
        self.fp_fh.write('# Place the middle well contact. #\n')
        self.fp_fh.write('##################################\n\n')

        # Update the placement co-ordinates from the previous placed auxcell (wl driver)
        # For rp_bca_cp_cu type,substract the width of auxcell, for the cu_rp_bca_cp type, add the height of auxcell.

        if self.bank_arch_type == 'cu_rp_bca_cp':
            # x co-ord remains same, and y co-ord gets updated
            row_periphery_x = row_periphery_x
            row_periphery_y = round(row_periphery_y + row_pheriphery['wl_driver'].get_size().size_y, 3)
        elif self.bank_arch_type == 'rp_bca_cp_cu':
            # y co-ord reamins same, and x co-ord gets updated.
            row_periphery_x = round(row_periphery_x - row_pheriphery['row_middle_well_contact'].get_size().size_x, 3)
            row_periphery_y = row_periphery_y

        # Place the middle well contact.
        instance_name = 'rp/rp_mwc'
        orientation = row_middle_well_contact_orientations[0]
        macro_place_command = place_macro('innovus', instance_name, row_periphery_x, row_periphery_y, orientation)
        self.fp_fh.write(macro_place_command + '\n')

        self.fp_fh.write('########################################\n')
        self.fp_fh.write('# Place the top half word-line drivers #\n')
        self.fp_fh.write('########################################\n\n')

        # Place the other half the no of rows WL drivers
        # The number of WL drivers depends on the no of rows each wl_drvercovers.
        # Below needs to be updated.
        for i in range(0, int(self.bank_rows / (2 * wld_auxcell_no_rows))):
            # The number is again started from 0 for the instance_name. The verilog is generated this way.

            # Update the placement co-ordinates from previous auxcell (1st bottom-well cap, later WL driver) placement.
            if self.bank_arch_type == 'cu_rp_bca_cp':
                # x co-ord remains same, and y co-ord gets updated
                row_periphery_x = row_periphery_x
                if i == 0:
                    row_periphery_y = round(
                        row_periphery_y + row_pheriphery['row_middle_well_contact'].get_size().size_y, 3)
                else:
                    row_periphery_y = round(row_periphery_y + row_pheriphery['wl_driver'].get_size().size_y, 3)
            elif self.bank_arch_type == 'rp_bca_cp_cu':
                # y co-ord reamins same, and x co-ord gets updated.
                row_periphery_x = round(row_periphery_x - row_pheriphery['wl_driver'].get_size().size_x, 3)
                row_periphery_y = row_periphery_y

            instance_name = 'rp/rp_wld_t/inst%d' % i

            if len(row_wl_driver_orientations) > 1:
                if (i % 2) == 0:
                    orientation = row_wl_driver_orientations[0]
                else:
                    orientation = row_wl_driver_orientations[1]
            else:
                orientation = row_wl_driver_orientations[0]

            macro_place_command = place_macro('innovus', instance_name, row_periphery_x, row_periphery_y, orientation)

            self.fp_fh.write(macro_place_command + '\n')

        self.fp_fh.write('##################################\n')
        self.fp_fh.write('# Place the top well contact. #\n')
        self.fp_fh.write('##################################\n\n')

        # Update the placement co-ordinates from the previous placed auxcell (wl driver)
        # For rp_bca_cp_cu type,substract the width of auxcell, for the cu_rp_bca_cp type, add the height of auxcell.

        if self.bank_arch_type == 'cu_rp_bca_cp':
            # x co-ord remains same, and y co-ord gets updated
            row_periphery_x = row_periphery_x
            row_periphery_y = round(row_periphery_y + row_pheriphery['wl_driver'].get_size().size_y, 3)
        elif self.bank_arch_type == 'rp_bca_cp_cu':
            # y co-ord reamins same, and x co-ord gets updated.
            row_periphery_x = round(row_periphery_x - row_pheriphery['row_top_well_contact'].get_size().size_x, 3)
            row_periphery_y = row_periphery_y

        instance_name = 'rp/rp_twc'
        orientation = row_top_well_contact_orientations[0]

        macro_place_command = place_macro('innovus', instance_name, row_periphery_x, row_periphery_y, orientation)
        self.fp_fh.write(macro_place_command + '\n')

    def place_col_periphery(self, col_periphery, start_x_cor, start_y_cor):
        # To-do:
        # Add instance names
        # Work on the pin locations.

        self.fp_fh.write('############################\n')
        self.fp_fh.write('# Place the col periphery. #\n')
        self.fp_fh.write('############################\n\n\n')

        # Initializing the co-ordinates.
        # The initial co-ordinates corresponds to the auxcell that is next to bitcell array, which is the first key in
        # col_periphery dic
        col_periphery_x = start_x_cor
        col_periphery_y = start_y_cor

        auxcell_counter = 0
        for k, v in col_periphery.items():
            # Obtaint the auxcell properties
            auxcell_x = v.get_size().size_x
            auxcell_y = v.get_size().size_y
            auxcell_orientations = self.tech_config_dic['auxcells']['col_periphery'][k]['orientations']  # List

            self.fp_fh.write('##############################################################\n')
            self.fp_fh.write(f'#### Placing the {v.get_cellname()} col periphery auxcell#\n')
            self.fp_fh.write('##############################################################\n\n')

            # The initial co-ordinates corresponds to the auxcell that is next to bitcell array, which is the first
            # key in col_periphery dic

            if self.bank_arch_type == 'cu_rp_bca_cp':
                col_periphery_x = start_x_cor
                col_periphery_y = round(col_periphery_y - auxcell_y, 3)

            if not v.is_column_muxed():

                # Place the auxcell repeatedly for bank_cols times.
                for i in range(0, self.bank_cols):
                    instance_name = 'cp/cp_inst%d/inst%d' % (auxcell_counter, i)

                    if len(auxcell_orientations) > 1:  # Check for different orientations of the current auxcell.
                        if (i % 2) == 0:
                            orientation = auxcell_orientations[0]
                        else:
                            orientation = auxcell_orientations[1]
                    else:
                        orientation = auxcell_orientations[0]

                    macro_place_command = place_macro('innovus', instance_name, col_periphery_x, col_periphery_y,
                                                      orientation)

                    self.fp_fh.write(macro_place_command + '\n')

                    # Update the placement co-ordinates for column placement.
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        # x co-ord gets updated, and y co-ord remains same.
                        col_periphery_x = round(col_periphery_x + auxcell_x, 3)
                        col_periphery_y = col_periphery_y
                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # y co-ord remains same, and x co-ord gets updated.
                        col_periphery_x = col_periphery_x
                        col_periphery_y = round(col_periphery_y + auxcell_y, 3)

            else:
                for i in range(0, self.word_size):

                    instance_name = 'cp/cp_inst%d/inst%d' % (auxcell_counter, i)

                    if len(auxcell_orientations) > 1:  # Check for different orientations of the current auxcell.
                        if (i % 2) == 0:
                            orientation = auxcell_orientations[0]
                        else:
                            orientation = auxcell_orientations[1]
                    else:
                        orientation = auxcell_orientations[0]

                    macro_place_command = place_macro('innovus', instance_name, col_periphery_x, col_periphery_y,
                                                      orientation)

                    self.fp_fh.write(macro_place_command + '\n')

                    # Update the placement co-ordinates for column placement.
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        # x co-ord gets updated, and y co-ord remains same.
                        col_periphery_x = round(col_periphery_x + auxcell_x, 3)
                        col_periphery_y = col_periphery_y
                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # y co-ord remains same, and x co-ord gets updated.
                        col_periphery_x = col_periphery_x
                        col_periphery_y = round(col_periphery_y + auxcell_y, 3)

            auxcell_counter = auxcell_counter + 1  # Keep track of the auxcells placed.

            # Update the placement cor-ordinates for the next auxcell when bank type arch type is rp_bca_cp_cu.
            # For the other arch_type the updates happen at the start of this loop
            if self.bank_arch_type == 'rp_bca_cp_cu':
                col_periphery_x = round(col_periphery_x + auxcell_x, 3)
                col_periphery_y = start_y_cor

    def place_bitcell_array(self, bitcell_array, start_x_cor, start_y_cor):
        # To-do:
        # Update on how to calculate the even or odd value of row and col for bitcell array, col and row periphery
        # Add the pin locations

        self.fp_fh.write('###########################\n')
        self.fp_fh.write('# Place the bitcell array #\n')
        self.fp_fh.write('###########################\n\n\n')

        # Initialize the locations for the placement of bitcell array.
        bitcell_array_x = start_x_cor
        bitcell_array_y = start_y_cor

        # Bitcell Array placement is a two dimensional array, with standardized architecture.
        # var i = no_rows of array and j = no_cols of array
        # Placement of cells starts at i=0, j=0. In planar FETs, loc(0,0) = Lower left. In FinFETS as seen in GF12, the
        # fin orientation restriction makes the loc(0,0) rotate by 90 to Lower Right -> Update the bitcell_array_x

        bitcell_array_x = round(bitcell_array_x + self.bitcell_array_size.size_x, 3)

        # Collect the orientations of all the bitcell array auxcells
        edge_end_cell_orientations = bitcell_array['edge_end_cell'].get_orientations()  # list of lists
        edge_cell_orientations = bitcell_array['edge_cell'].get_orientations()  # list of lists
        strap_end_cell_orientations = bitcell_array['strap_end_cell'].get_orientations()  # list
        strap_cell_orientations = bitcell_array['strap_cell'].get_orientations()  # list
        bitcell_end_orientations = bitcell_array['bitcell_end_cell'].get_orientations()  # list of lists
        bitcell_orientations = bitcell_array['bitcell'].get_orientations()  # list of Lists

        # Collect the sizes of the bitcell array auxcells
        edge_cell_size_x = bitcell_array['edge_cell'].get_size().size_x
        edge_cell_size_y = bitcell_array['edge_cell'].get_size().size_y
        edge_end_cell_size_x = bitcell_array['edge_end_cell'].get_size().size_x
        edge_end_cell_size_y = bitcell_array['edge_end_cell'].get_size().size_y
        strap_cell_size_x = bitcell_array['strap_cell'].get_size().size_x
        strap_cell_size_y = bitcell_array['strap_cell'].get_size().size_y
        strap_end_cell_size_x = bitcell_array['strap_end_cell'].get_size().size_x
        strap_end_cell_size_y = bitcell_array['strap_end_cell'].get_size().size_y
        bitcell_size_x = bitcell_array['bitcell'].get_size().size_x
        bitcell_size_y = bitcell_array['bitcell'].get_size().size_y
        bitcell_end_cell_size_x = bitcell_array['bitcell_end_cell'].get_size().size_x
        bitcell_end_cell_size_y = bitcell_array['bitcell_end_cell'].get_size().size_y

        # Number of rows each bitcell covers
        # In 12nm, the foundry bitcell covers two rows per bitcell instance
        bitcell_no_rows = self.tech_config_dic['auxcells']['bitcell_array']['bitcell']['no_rows']
        bitcell_no_cols = self.tech_config_dic['auxcells']['bitcell_array']['bitcell']['no_cols']
        edge_cell_no_cols = self.tech_config_dic['auxcells']['bitcell_array']['edge_cell']['no_cols']
        edge_cell_no_rows = self.tech_config_dic['auxcells']['bitcell_array']['edge_cell']['no_rows']
        strap_cell_no_cols = self.tech_config_dic['auxcells']['bitcell_array']['strap_cell']['no_cols']
        strap_cell_no_rows = self.tech_config_dic['auxcells']['bitcell_array']['strap_cell']['no_rows']

        bitcell_counter = 0

        # Number of rows of bitcell column arrays
        no_rows_bc_ca = int(self.bank_rows / bitcell_no_rows)

        inst_counter = 0  # The counter to keep track and name the bitcell column arrays as per the verilog generation.
        for i in range(0, no_rows_bc_ca + 3):
            # self.bank_rows + 3 --> 3 here accounts for extra rows to place the edge cells on top and bottom and strap
            # in the middle.

            if i == 0 or i == (no_rows_bc_ca + 2):  # Bottom and top rows, place edge cells. 2 instd 3 to account 0

                self.fp_fh.write('####################################\n')
                self.fp_fh.write('# Place the edge cell column array #\n')
                self.fp_fh.write('####################################\n\n\n')

                # Initialize the placement co-ordinates to place the edge_cell column cells.
                if i == 0:
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        bitcell_array_x = start_x_cor
                        bitcell_array_y = start_y_cor
                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # Substract the edege_cell width as the placement co-ord's have to be LL corner -> Inv requires.
                        bitcell_array_x = round(start_x_cor - edge_cell_size_x, 3)
                        bitcell_array_y = start_y_cor
                elif i == no_rows_bc_ca + 2:  # For the last row, the x and y values have to be updated from other rows.
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        bitcell_array_x = start_x_cor
                        bitcell_array_y = round(bitcell_array_y + bitcell_size_y, 3)
                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # Substract the edege_cell width as the placement co-ord's have to be LL corner -> Inv requires.
                        bitcell_array_x = round(bitcell_array_x - edge_cell_size_x, 3)
                        bitcell_array_y = start_y_cor

                # Get the no of edge cells per row
                no_edge_cells = int(self.bank_cols / edge_cell_no_cols)

                for j in range(0, no_edge_cells + 2):
                    # self.bank_cols + 2 --> 2 here accounts for extra columns to place the end cells.
                    # Obtain the Instance name for the edge_cells
                    print("J is ", j)
                    if i == 0:
                        instance_name = 'bca/edge_ca_b/inst%d' % j
                    elif i == no_rows_bc_ca + 2:  # The top-most row of bitcell array to place the top edge cell ca.
                        instance_name = 'bca/edge_ca_t/inst%d' % j

                    # Obtain the orientations
                    if j == 0:  # Orientations for edge_end_cell
                        if i == 0:
                            orientation = edge_end_cell_orientations[0][0]
                        elif i == no_rows_bc_ca + 2:
                            orientation = edge_end_cell_orientations[1][0]
                    elif j == no_edge_cells + 1:
                        if i == 0:
                            orientation = edge_end_cell_orientations[0][1]
                        elif i == no_rows_bc_ca + 2:
                            orientation = edge_end_cell_orientations[1][1]
                    elif (j % 2) == 0:
                        if i == 0:
                            # [1] index of internal list is considered here as the starting number for edge_cell will
                            # 1, as 0 is occupied by edge_end_cell. So, the even number of j will be odd number for edge
                            # cell and vice-versa
                            orientation = edge_cell_orientations[0][1]
                        elif i == no_rows_bc_ca + 2:
                            orientation = edge_cell_orientations[1][1]
                    else:  # Orientations for edge_cells
                        if i == 0:
                            orientation = edge_cell_orientations[0][0]
                        elif i == no_rows_bc_ca + 2:
                            orientation = edge_cell_orientations[1][0]

                    macro_place_command = place_macro('innovus', instance_name, bitcell_array_x, bitcell_array_y,
                                                      orientation)

                    self.fp_fh.write(macro_place_command + '\n')

                    # Update the placement co-ordinates for placing the next cell of the column arrays
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        # X-cordinate gets updated. Y-cordinate remain same.
                        if j == 0 or j == no_edge_cells + 1:
                            bitcell_array_x = round(bitcell_array_x + edge_end_cell_size_x, 3)
                        else:
                            bitcell_array_x = round(bitcell_array_x + edge_cell_size_x, 3)

                        bitcell_array_y = bitcell_array_y

                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # y-cordinate gets updated. x - cordinate remain same.
                        bitcell_array_x = bitcell_array_x
                        if j == 0 or j == no_edge_cells + 1:
                            print("Entered, when J =0")
                            bitcell_array_y = round(bitcell_array_y + edge_end_cell_size_y, 3)
                            print("array_y", bitcell_array_y)
                        else:
                            bitcell_array_y = round(bitcell_array_y + edge_cell_size_y, 3)

            elif i == int(no_rows_bc_ca / 2) + 1:  # For half bitcell rows, place strap  row. +1 for extra edge cells.

                self.fp_fh.write('#####################################\n')
                self.fp_fh.write('# Place the strap cell column array #\n')
                self.fp_fh.write('#####################################\n\n\n')

                # Initialize the placement cordinates for the strap column array cells
                if self.bank_arch_type == 'cu_rp_bca_cp':
                    bitcell_array_x = start_x_cor
                    bitcell_array_y = round(bitcell_array_y + bitcell_size_x, 3)
                elif self.bank_arch_type == 'rp_bca_cp_cu':
                    # Substract the edege_cell width as the placement co-ord's have to be LL corner -> Inv requires.
                    bitcell_array_x = round(bitcell_array_x - strap_cell_size_x, 3)
                    bitcell_array_y = start_y_cor

                # Get the no of edge cells per row
                no_strap_cells_prow = int(self.bank_cols / strap_cell_no_cols)

                for j in range(0, no_strap_cells_prow + 2):  # + 2 to accounts for strap end cells.

                    # Get the instance name
                    instance_name = 'bca/strap_ca/inst%d' % j

                    # Get the orientations

                    if j == 0:
                        orientation = strap_end_cell_orientations[0]  # --> need to consider the fin restriction here.
                    elif j == no_strap_cells_prow + 1:  # First and Last cols, place strap_end cells. 1 instd 2 to
                        orientation = strap_end_cell_orientations[1]
                    elif (j % 2) == 0:  # Given the number strap cell start will be from 1
                        orientation = strap_cell_orientations[1]  # --> need to consider the fin restriction here.
                    else:
                        orientation = strap_cell_orientations[0]

                    macro_place_command = place_macro('innovus', instance_name, bitcell_array_x, bitcell_array_y,
                                                      orientation)

                    self.fp_fh.write(macro_place_command + '\n')

                    # Update the placement co-ordinates
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        # X-cordinate gets updated. Y-cordinate remain same.
                        if j == 0 or j == no_strap_cells_prow + 1:
                            bitcell_array_x = round(bitcell_array_x + strap_end_cell_size_x, 3)
                        else:
                            bitcell_array_x = round(bitcell_array_x + strap_cell_size_x, 3)

                        bitcell_array_y = bitcell_array_y

                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # y-cordinate gets updated. x - cordinate remain same.
                        bitcell_array_x = bitcell_array_x
                        if j == 0 or j == no_strap_cells_prow + 1:
                            bitcell_array_y = round(bitcell_array_y + strap_end_cell_size_y, 3)
                        else:
                            bitcell_array_y = round(bitcell_array_y + strap_cell_size_y, 3)

            else:  # Place the bitcells

                self.fp_fh.write('#######################################\n')
                self.fp_fh.write('# Place the bitcell cell column array #\n')
                self.fp_fh.write('#######################################\n\n\n')

                # Initialize the placement cordinates for the bitcell column array cells
                if self.bank_arch_type == 'cu_rp_bca_cp':
                    if i == 1:
                        bitcell_array_x = start_x_cor
                        bitcell_array_y = round(bitcell_array_y + edge_cell_size_y, 3)
                        pass
                    elif i == self.bank_rows + 2:
                        bitcell_array_x = start_x_cor
                        bitcell_array_y = round(bitcell_array_y + strap_cell_size_y, 3)
                        pass
                    else:
                        bitcell_array_x = start_x_cor
                        bitcell_array_y = round(bitcell_array_y + bitcell_size_x, 3)
                        pass
                elif self.bank_arch_type == 'rp_bca_cp_cu':
                    # Substract the edege_cell width as the placement co-ord's have to be LL corner -> Inv requires.
                    bitcell_array_x = round(bitcell_array_x - bitcell_size_x, 3)
                    bitcell_array_y = start_y_cor

                # Get the no of edge cells per row
                no_bitcells_prow = int(self.bank_cols / bitcell_no_cols)
                for j in range(0, no_bitcells_prow + 2):
                    # self.bank_cols + 2 --> 2 here accounts for extra columns to place the end cells.
                    # obtain the instance name
                    # instance_name = 'bca/bca_ca%d/inst%d' % (i, j)
                    instance_name = 'bca/bc_ca%d/inst%d' % (inst_counter, j)
                    # Get the orientations:
                    if i in range(1, int(no_rows_bc_ca / 2) + 1):
                        # Below strap orientations -> by checking i in range(1, no_rows_bc_ca/2 + 1)
                        if i % 2 == 0:  # List of Lists: From 0th index list, choose 2 and 3 indexes.
                            if j == 0:
                                orientation = bitcell_end_orientations[0][0]  # 1 -> The odd number of bitcell, is even
                            elif j == no_bitcells_prow + 1:
                                orientation = bitcell_end_orientations[0][1]  # 1 -> The odd number of bitcell, is even
                            elif j % 2 == 0:  # Placing the bitcells, Choose Left orientation
                                orientation = bitcell_orientations[0][3]  # 1 -> The odd number of bitcell, is even
                            else:  # Placing the bitcell, Choose right orientation
                                orientation = bitcell_orientations[0][2]  # 1 -> The odd number of bitcell, is even
                        else:  # List of Lists: From the 0th index list, choose the 0 and 1 indexes
                            if j == 0:
                                orientation = bitcell_end_orientations[0][0]  # 1 -> The odd number of bitcell, is even
                            elif j == no_bitcells_prow + 1:
                                orientation = bitcell_end_orientations[0][1]  # 1 -> The odd number of bitcell, is even
                            elif j % 2 == 0:  # Choose Left
                                orientation = bitcell_orientations[0][1]  # 1 -> The odd number of bitcell, is even
                            else:  # Choose right
                                orientation = bitcell_orientations[0][0]  # 1 -> The odd number of bitcell, is even
                    elif i in range(int(no_rows_bc_ca / 2) + 2, no_rows_bc_ca + 2):
                        # Above strap orientations -> by checking i in range(no_rows_bc_ca/2 + 2, no_rows_bca_ca + 2)
                        if i % 2 == 0:  # List of Lists: From 1st index list, choose 2 and 3 indexes.
                            if j == 0:
                                orientation = bitcell_end_orientations[1][0]  # 1 -> The odd number of bitcell, is even
                            elif j == no_bitcells_prow + 1:
                                orientation = bitcell_end_orientations[1][1]  # 1 -> The odd number of bitcell, is even
                            elif j % 2 == 0:  # Choose Left
                                orientation = bitcell_orientations[1][3]  # 1 -> The odd number of bitcell, is even
                            else:  # Choose right
                                orientation = bitcell_orientations[1][2]  # 1 -> The odd number of bitcell, is even
                        else:  # List of Lists: From the 1st index list, choose the 0 and 1 indexes
                            if j == 0:
                                orientation = bitcell_end_orientations[1][0]  # 1 -> The odd number of bitcell, is even
                            elif j == no_bitcells_prow + 1:
                                orientation = bitcell_end_orientations[1][1]  # 1 -> The odd number of bitcell, is even
                            elif j % 2 == 0:  # Choose Left
                                orientation = bitcell_orientations[1][1]  # 1 -> The odd number of bitcell, is even
                            else:  # Choose right
                                orientation = bitcell_orientations[1][0]  # 1 -> The odd number of bitcell, is even

                    macro_place_command = place_macro('innovus', instance_name, bitcell_array_x, bitcell_array_y,
                                                      orientation)

                    self.fp_fh.write(macro_place_command + '\n')

                    # Update the placement co-ordinates for the next auxcell of the same column
                    if self.bank_arch_type == 'cu_rp_bca_cp':
                        # X-cordinate gets updated. Y-cordinate remain same.
                        if j == 0 or j == no_bitcells_prow + 1:
                            bitcell_array_x = round(bitcell_array_x + bitcell_end_cell_size_x, 3)
                        else:
                            bitcell_array_x = round(bitcell_array_x + bitcell_size_x, 3)

                        bitcell_array_y = bitcell_array_y

                    elif self.bank_arch_type == 'rp_bca_cp_cu':
                        # y-cordinate gets updated. x - cordinate remain same.
                        bitcell_array_x = bitcell_array_x
                        if j == 0 or j == no_bitcells_prow + 1:
                            bitcell_array_y = round(bitcell_array_y + bitcell_end_cell_size_y, 3)
                        else:
                            bitcell_array_y = round(bitcell_array_y + bitcell_size_y, 3)

                inst_counter = inst_counter + 1

    def create_bank_io_plan(self, bank_apr_dir):
        # Has to update for the cu_rp_bca_cp as well
        # Obtain the pin layer info from tech collateral file
        self.h_layer = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_layer']
        self.h_width = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_min_width']
        self.h_depth = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_depth']
        """
         Determine the top-level module pins, and the corresponding components (rp and cp only as bca pins are all
         connected to rp and bca) associated with the respective pins.
        # Pin placement:
            1st method: Most exhaustive:
                - Parse the auxcells, and obtain the pin location and corresponding side of the respective pin. Using
                 the pin placement info, determine the pin placement (offset, placement side, metal layer pin width)
                 info with respect to bank. This requires lot of work, but would help in reducing the pin routing.
                 - Mostly required for DIN and DOUT

            2nd method: Simple:
                - Obtain the column-mux size, spread the DIN and DOUT across the col_periphery size. For FinFets,
                 all pins location is to the right-side of the bank and for planar-cmos its bottom-side.
        # Implementing Method-2 now, and can later do 1, time-permitting.
        """

        self.io_file = 'pin_place.io'
        self.pinio_fh = open(os.path.join(bank_apr_dir, self.io_file), 'w')

        # Write the pre-amble of IO file.
        self.pinio_fh.write('(globals \n')
        self.pinio_fh.write('   version = 3\n')
        self.pinio_fh.write('   io_order = default\n')
        self.pinio_fh.write(')\n')
        self.pinio_fh.write('(iopin\n')
        self.pinio_fh.write('   (right\n')

        # Obtaining the top-level modules pin info from the defined SRAM Architecure.
        from SRAM import sram_arch

        bank_arch = sram_arch.SRAM6TArch()
        self.bank_top_pininfo = bank_arch.bank_top_pininfo

        # For 1st method:
        # # Collect the bank and the components pin ipininfo
        # self.col_periphery_top_pininfo = bank_arch.col_periphery_top_pininfo
        # self.row_periphery_top_pininfo = bank_arch.row_periphery_top_pininfo
        # self.bitcell_array_top_pininfo = bank_arch.bitcell_array_top_pininfo

        # # Obtain pins to be placed on the Col_Periphery_Side, and row_periphery side.
        # # For col_periphery, the pins can be on the bottom and on the right side.
        # module_wires = {}
        # for k, v in self.component_pin_collection.items():
        #     if k not in list(self.bank_top_pininfo.keys()):
        #         module_wires[k] = v

        # Obtain the Col-muxing size
        self.col_mux = int(self.bank_cols / self.word_size)

        # For bus widths.
        bank_rows = self.bank_rows
        col_mux = self.col_mux
        word_size = self.word_size
        # addr = self.address

        # For FinFETs
        self.col_mux_size = round(self.col_mux * self.bitcell_array['bitcell'].get_size().size_y, 3)

        # Conditions: Only the Din and Dout are placed on the col-periphery side, the rest of inputs are placed to
        # CU side as the rest of the pins are I/O's to the control unit.

        # Pin Offset --> For FinFets Right side, starting from bottom and scaling on Y until the Row_periphery height.
        # For planar, it will bottom, starting from left and scaling up on X until the Row_periphery width.
        # Pin_offset other than Din and Dout pins
        pin_offset = round(0.01 * self.row_periphery_size.size_y,
                           3)  # 1% of size as starting to avoid the extreme low point.

        # Total number of pins including the bus pins, but excluding the DIN and DOUT to calculate pin_step
        total_pins = 0
        for k, v in self.bank_top_pininfo.items():
            if v[1] != 'wire':
                if k in ['DIN', 'DOUT']:
                    continue
                elif list(v[2].keys())[0] == 'bus':
                    total_pins = total_pins + self.bank_bus_params[v[2]['bus']]
                else:
                    total_pins = total_pins + 1
        import math

        # Determine the pin step based on the height of the row_periphery and total no of pins to be placed.
        # pin_step = math.floor((self.row_periphery_size.size_y - pin_offset) / total_pins)
        pin_step = round((self.row_periphery_size.size_y - pin_offset) / total_pins, 3)

        # Can add a condition to check if the pin_step (given pins are more than the height) causes DRC errors.

        # # Obtain the pin layer info from tech collateral file
        # self.h_layer = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_layer']
        # self.h_width = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_min_width']
        # self.h_depth = self.tech_config_dic['layout_info']['bank']['pin_placement']['h_depth']

        for k, v in self.bank_top_pininfo.items():
            if k == 'DIN':
                din_offset = round(self._start_cp_y + 0.25 * self.col_mux_size,
                                   3)  # Starting the Din pin location at 1/4 of
                # Col_mux_size.
                for i in range(self.word_size):
                    self.pinio_fh.write(
                        f'       (pin name="{v[0]}[{i}]"    offset={din_offset}    layer={self.h_layer}   '
                        f'width={self.h_width}  depth={self.h_depth}  place_status=fixed)\n')
                    din_offset = round(din_offset + self.col_mux_size, 3)
            elif k == 'DOUT':
                dout_offset = round(self._start_cp_y + 0.75 * self.col_mux_size,
                                    3)  # Starting the Dout pin location at 3/4 of
                # Col_mux_size.
                for i in range(self.word_size):
                    self.pinio_fh.write(
                        f'       (pin name="{v[0]}[{i}]"    offset={dout_offset}    layer={self.h_layer}   '
                        f'width={self.h_width}  depth={self.h_depth}  place_status=fixed)\n')
                    dout_offset = round(dout_offset + self.col_mux_size, 3)
            elif v[1] != 'wire':
                if list(v[2].keys())[0] == 'bus':
                    for pi in range(0, self.bank_bus_params[v[2]['bus']]):
                        self.pinio_fh.write(
                            f'       (pin name="{v[0]}[{pi}]"    offset={pin_offset}    layer={self.h_layer}   '
                            f'width={self.h_width}  depth={self.h_depth}  place_status=fixed)\n')

                        pin_offset = round(pin_offset + pin_step, 3)
                else:
                    self.pinio_fh.write(
                        f'       (pin name="{v[0]}"    offset={pin_offset}    layer={self.h_layer}   '
                        f'width={self.h_width}  depth={self.h_depth}  place_status=fixed)\n')

                pin_offset = round(pin_offset + pin_step, 3)

        # For Planar
        # self.col_mux_size = self.col_mux * self.bitcell_array['bitcell'].get_size().size_x

        self.pinio_fh.write('   )\n')
        self.pinio_fh.write(')\n')


if __name__ == '__main__':
    # For testing the floorplan only

    from SRAM import sram_arch

    bank_arch = sram_arch.SRAM6TArch()
    row_periphery = bank_arch.bank_top["row_periphery"]  # Dict: Keys = Auxcells Names; Values=Auxcell Instances.
    col_periphery = bank_arch.bank_top["col_periphery"]
    bitcell_array = bank_arch.bank_top["bitcell_array"]

    bitcell_array_top_pininfo = bank_arch.bitcell_array_top_pininfo

    # sram_components = dict(row_periphery=row_periphery, row_periphery=row_periphery, bitcell_array=bitcell_array)
    sram_bank_config = [8, 8]
    sram_specs = {'word_size': 2}

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


    def yaml_config_parser(config_file) -> dict:
        """ Parses the config file and returns a dict the list of the cells and connection
        :rtype: object
        """
        import yaml

        try:
            with open(config_file) as fh:
                yaml_config_dic = yaml.load(fh)
        except yaml.YAMLError as err:
            print("Exception while loading the config file %s" % config_file, err)
            sys.exit(1)

        return yaml_config_dic


    tech_collateral = ''
    _tech_dic = yaml_config_parser(tech_collateral)
    _auxcell_lib_path = _tech_dic['auxcells']['auxcells_lib_dir']
    import os

    os.environ['auxcell_lib_path'] = _auxcell_lib_path

    _bank_arch = dict(row_periphery=row_periphery, col_periphery=col_periphery, bitcell_array=bitcell_array)

    _auxcells_dic = _tech_dic["auxcells"]


    def update_sram_auxcells(auxcells_dic, sram_default_components) -> dict:
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


    updated_bank_arch = update_sram_auxcells(_auxcells_dic, _bank_arch)
    bus_params = dict(addr_width=int(math.log2(sram_bank_config[0])) + 2, word_size=sram_specs['word_size'])
    fp = FloorPlan()
    # Create the bank floorplan.
    apr_dir = os.getcwd()
    module_name = f'sram_bank_{sram_bank_config[0]}rows_{sram_bank_config[1]}cols'
    rp_cu_area = fp.create_bank_floorplan(apr_dir, module_name, _tech_dic, updated_bank_arch, sram_bank_config, sram_specs,
                             bus_params)
    print(rp_cu_area)
