import os

def setup_tcl():
    pass

def always_source_tcl(dir_, collateral):
    fh = open(os.path.join(dir_, 'always_source.tcl'), 'w')

    from MemGen import MemGen

    tech_config_dic = MemGen.get_tech_collaterals()

    fh.write('puts "#############################"')
    fh.write('puts "#### Power Plan Settings ####"')
    fh.write('puts "#############################"')
    fh.write('set mem_pwr_pins [list %s]'%(' '.join(i for i in tech_config_dic['mem_pwr_pins'])))
    fh.write('set mem_gnd_pins [list %s]'%(' '.join(i for i in tech_config_dic['mem_gnd_pins'])))
    fh.write('set stdcell_pwr_pins [list %s]'%(' '.join(i for i in tech_config_dic['stdcell_pwr_pins'])))
    fh.write('set stdcell_gnd_pins [list %s]'%(' '.join(i for i in tech_config_dic['stdcell_gnd_pins'])))
    fh.write('set stdcell_pwell_pins [list %s]'%(' '.join(i for i in tech_config_dic['stdcell_pwell_pins'])))
    fh.write('set stdcell_nwell_pins [list %s]'%(' '.join(i for i in tech_config_dic['stdcell_nwell_pins'])))
    fh.write('set p_rng_w      [expr %f]   ;# Power ring metal width'%(tech_config_dic['power_ring_width']))
    fh.write('set p_rng_s      [expr %f]   ;# Power ring metal space'%(tech_config_dic['power_ring_space']))
    fh.write('set p_str_w      [expr %f]   ;# Power stripe metal width'%(tech_config_dic['power_stripe_width']))
    fh.write('set p_str_s      [expr %f]   ;# Power stripe metal space'%(tech_config_dic['power_stripe_space']))
    fh.write('set p_str_p      [expr %f]   ;# Power stripe metal pitch'%(tech_config_dic['power_stripe_pitch']))

    fh.write('puts "######################"')
    fh.write('puts "### Floor planning ###"')
    fh.write('puts "######################"')
    fh.write('set t_pitch [dbGet top.fPlan.coreSite.size_y]   ;# Pitch between power rails (standard cell height)')
    fh.write('set f_pitch [dbGet head.finGridPitch]             ;# Pitch between fins')
    fh.write('set core_margin_t [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s]')
    fh.write('set core_margin_b [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s]')
    fh.write('set core_margin_r [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s]')
    fh.write('set core_margin_l [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s]')
    fh.write('set min_mem_stdcell_spacing_h %f'%(tech_config_dic['mem_stdcell_h_spacing']))
    fh.write('set min_mem_stdcell_spacing_v %f'%(tech_config_dic['mem_stdcell_v_spacing']))
    fh.write('set min_mem_mem_spacing_h     %f'%(tech_config_dic['mem_mem_h_spacing']))
    fh.write('set min_mem_mem_spacing_v     %f'%(tech_config_dic['mem_mem_v_spacing']))
