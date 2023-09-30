import os
import logging
import sys

sys.path.append('/net/gaylord/t/kamineni/dev/pwd/memory-gen-beta/private/')

from apr_pymodules.power_plan import *

log = logging.getLogger(__name__)


def create_bank_power_plan(bank_apr_dir, tech_config_dic, rp_cu_power_route_area):
    # Grab the pdk dependent power planning details.

    voltage = tech_config_dic['power_supply']['nominal_voltage']
    peripheral_power_pin = tech_config_dic['power_supply']['pins']['peripheral_power_pin']
    bitcellarray_power_pin = tech_config_dic['power_supply']['pins']['bitcellarray_power_pin']
    ground_pin = tech_config_dic['power_supply']['pins']['ground_pin']
    stdcell_power_pin = tech_config_dic['power_supply']['pins']['stdcell_power_pin']
    stdcell_ground_pin = tech_config_dic['power_supply']['pins']['stdcell_ground_pin']
    stdcell_nwell_pin = tech_config_dic['power_supply']['pins']['stdcell_nwell_pin']
    stdcell_pwell_pin = tech_config_dic['power_supply']['pins']['stdcell_pwell_pin']

    m1_name = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M1']['name']
    m1_direction = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M1']['direction']
    m1_stripe_width = tech_config_dic['layout_info']['bank']['power_plan']['stripe_widths']['M1']
    m1_ring_width = tech_config_dic['layout_info']['bank']['power_plan']['ring_widths']['M1']

    m2_name = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M2']['name']
    m2_direction = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M2']['direction']
    m2_stripe_width = tech_config_dic['layout_info']['bank']['power_plan']['stripe_widths']['M2']
    m2_ring_width = tech_config_dic['layout_info']['bank']['power_plan']['ring_widths']['M2']

    m3_name = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M3']['name']
    m3_direction = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M3']['direction']
    m3_stripe_width = tech_config_dic['layout_info']['bank']['power_plan']['stripe_widths']['M3']
    m3_ring_width = tech_config_dic['layout_info']['bank']['power_plan']['ring_widths']['M3']

    m4_name = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M4']['name']
    m4_direction = tech_config_dic['layout_info']['bank']['power_plan']['metal_layers_props']['M4']['direction']
    m4_stripe_width = tech_config_dic['layout_info']['bank']['power_plan']['stripe_widths']['M4']
    m4_ring_width = tech_config_dic['layout_info']['bank']['power_plan']['ring_widths']['M4']

    # Create the power intent file
    pintent_fh = open(os.path.join(bank_apr_dir, 'power_intent.cpf'), 'w')
    create_power_intent(pintent_fh, voltage, ground_pin, peripheral_power_pin, bitcellarray_power_pin,
                        stdcell_power_pin, stdcell_ground_pin, stdcell_nwell_pin, stdcell_pwell_pin)

    # Create the power planning file handler
    pp_fh = open(os.path.join(bank_apr_dir, 'pre_place.tcl'), 'w')

    # Create the power rails for the STD cells
    pp_fh.write('# Creating the power rails for the STDcells\n\n')
    # Set the variable for the Std cell height

    get_stdcell_height(pp_fh)

    # Create the power rails for the STD cells
    route_std_cell_tracks(pp_fh, f'{ground_pin} {peripheral_power_pin}')

    # Create the extra M2 layers to avoid DRCs for the GF12 pdk
    pdk = os.getenv('foundry') + os.getenv('node') + os.getenv('sub_process')

    if pdk == 'gf12lp':
        pp_fh.write('# Creating the extra M2 rails for the STDcells')
        # Reset the stripe mode
        set_stdcell_stripe_mode(pp_fh, m1_name, m2_name)

        # Create the Std cell stripes over the M1 STD cell power layers
        #   Note: the order of pins here is different than that of Sroute. Because, the way tool uses the pin_list
        #   order for routing is different between the sroute and the addStripe Commands. Tool limitiation.

        m2_stripes_spacing = f"[expr $cell_pitch - {m2_stripe_width}]"
        m2_set_set_pitch = f"[expr $cell_pitch * 2]"
        m2_start_point = f"[expr 0 - {m2_stripe_width}/2]"
        m2_stop_point = f"[expr 0 - {m2_stripe_width}]"

        create_stdcell_stripes(pp_fh, f'{peripheral_power_pin} {ground_pin}', m2_name, m2_direction, m2_stripe_width,
                               m2_stripes_spacing, m2_set_set_pitch, m2_start_point, m2_stop_point)

        # Edit the vias
        reset_via_mode(pp_fh)
        set_via_mode(pp_fh)
        edit_via(pp_fh, f'{peripheral_power_pin} {ground_pin}', m1_name, m2_name)

    # Creating the M3 power mesh
    reset_via_mode(pp_fh)
    set_stdcell_stripe_mode(pp_fh, m2_name, m3_name)

    m3_stripes_spacing = f"[expr 5 * {m3_stripe_width}]"
    m3_set_set_pitch = f"[expr {m3_stripe_width} * 18]"
    m3_start_point = f"[expr {m3_stripe_width}/2]"

    create_stdcell_stripes(pp_fh, f'{peripheral_power_pin} {ground_pin}', m3_name, m3_direction, m3_stripe_width,
                           m3_stripes_spacing, m3_set_set_pitch, m3_start_point)

    ###############################################
    # Top-level power connections across bank # ###
    ###############################################

    # Creating the M4 power stripes to connect all the column periphery and the array.
    # Because of the PDK bitcell, the M4 power layers are on bca and cpare on the auxcells, so, specific options
    # are used to route the stripes from the existing stipes in the auxcells.

    set_stripe_mode_forexisting_cell_stripes(pp_fh, m4_name, m4_name)
    create_stripes_fromexisting_cell_stripes(pp_fh, f'{bitcellarray_power_pin} {peripheral_power_pin} {ground_pin}',
                                             m4_name, m4_direction)

    # For row periphery and control unit, we create the stripes on bank top-metal layer to connect the power stripes
    # of auxcells on a lower layer.
    m4_stripes_spacing = f"[expr 1.5 * {m4_stripe_width}]"
    # Area has to cover the rp and cu, with width = bank_width, and the height is same as Cu height with some negative
    # offset.
    # Added some offset to the starting point in y-direction for the routes to be with-in the STD cell area.
    m4_area_cordinates = [rp_cu_power_route_area[0], rp_cu_power_route_area[1], rp_cu_power_route_area[2],
                          rp_cu_power_route_area[3] - m4_stripe_width]
    rp_cu_no_stipes_sets = 2
    set_stdcell_and_macro_stripe_mode(pp_fh, m3_name, m4_name)
    create_stripes_specific_area(pp_fh, f'{peripheral_power_pin} {ground_pin}', m4_name, m4_direction, m4_stripe_width,
                                 m4_stripes_spacing, rp_cu_no_stipes_sets, m4_area_cordinates)


if __name__ == '__main__':

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


    os.environ['node'] = '12'
    os.environ['foundry'] = 'gf'
    os.environ['sub_process'] = 'lp'
    rp_cu_power_route_area = [0.0445, 7.361, 12.5555, 1.0885]
    tech_collateral = ''
    _tech_dic = yaml_config_parser(tech_collateral)
    apr_dir = os.getcwd()
    rp_cu_power_route_area = [0, 0.1, 12.561, 7.584]
    create_bank_power_plan(apr_dir, _tech_dic, rp_cu_power_route_area)
