####################################################################################
#                              ALWAYS_SOURCE PLUG-IN
#####################################################################################
#
# This plug-in script is called from all flow scripts after loading the setup.tcl
# but after to loading the design data.  It can be used to set variables that affect
# non-persistent information
#
#####################################################################################
set t_pitch [dbGet top.fPlan.coreSite.size_y] ;# Standard Cell Height
set f_pitch [dbGet head.finGridPitch]         ;# Pitch between fins

# Top Metal Min Width
#set m_width [lindex [lsort -real -decreasing [dbGet head.layers.minWidth]] 0] ;
set m_width [lindex [lsort -real -decreasing [dbGet head.layers.minWidth]] 1] ;

# Floorplan Variables
#set core_width    420 ;# Core Area Width
#set core_height   370 ;# Core Area Height
@@ set core_width    @cW ;# Core Area Width
@@ set core_height   @cH ;# Core Area Height

set coreBox_llx   [dbGet top.fplan.coreBox_llx]
set coreBox_lly   [dbGet top.fplan.coreBox_lly]
set coreBox_urx   [dbGet top.fplan.coreBox_urx]
set coreBox_ury   [dbGet top.fplan.coreBox_ury]

set pwr_net_list {VDD VSS}             ;# List of Power nets

set p_rng_w       1.6 ;# Power ring metal width
set p_rng_s       0.8  ;# Power ring metal space

set core_margin_t [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s + 2] 
set core_margin_b [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s + 2]
set core_margin_r [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s + 2]
set core_margin_l [expr ([llength $pwr_net_list] * ($p_rng_w + $p_rng_s)) + $p_rng_s + 2]

set die_width     [expr $core_width  + $core_margin_l + $core_margin_r]
set die_height    [expr $core_height + $core_margin_b + $core_margin_t]

#-------------------------------------------------------------------------------
# Hard Macro related 
#-------------------------------------------------------------------------------
#- dco
@@ set IGXorigin @dX 
@@ set IGYorigin @dY 
set IGxpitch 0.2
set IGypitch 1.8
#- outbuff_div
#set bufIGXorigin 45
#set bufIGYorigin 28.8
@@ set bufIGXorigin @bX
@@ set bufIGYorigin @bY

@@ set DCO_W @dW 
@@ set DCO_H @dH 
set DCO_LEFT [expr $IGXorigin] 
set DCO_BOTTOM [expr $IGYorigin] 
set DCO_RIGHT [expr $DCO_LEFT + $DCO_W]
set DCO_TOP [expr $DCO_BOTTOM + $DCO_H]
set PD_MARGIN [expr 2*$p_rng_w + 3*$p_rng_s]
set Halo_W 5.4

set BUF_W 355.2 
set BUF_H 99.2 
set BUF_LEFT [expr $bufIGXorigin] 
set BUF_BOTTOM [expr $bufIGYorigin] 
set BUF_RIGHT [expr $BUF_LEFT + $BUF_W]
set BUF_TOP [expr $BUF_BOTTOM + $BUF_H]
