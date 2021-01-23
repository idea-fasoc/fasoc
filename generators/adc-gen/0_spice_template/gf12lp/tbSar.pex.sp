
.OPTION
+    artist=2
+    ingold=2
+    parhier=LOCAL
+    psf=2
+    gmin=1E-25
+    gmindc=1E-25
+    reltol=1E-6
+    dvdt=2
+    lvltim=3
+    runlvl=6
*+    autostop
*+    post
+    post=0
+    nomod
+    method=gear
*+    probe
*+    accurate
*+    probe probe=1
*+    kcltest
*+    measdgt=8
*+    numdgt=12

.option finesim_output = tr0
*.option finesim_method = GEAR
*.option finesim_mode = spicehd

.LIB "/afs/eecs.umich.edu/kits/GF/12LP/V1.0_2.1/Models/HSPICE/models/12LP_Hspice.lib" TT
*.INCLUDE "/afs/eecs.umich.edu/kits/GF/.contrib/12lp/zhehongw/sc10p5mcpp84_12lp_base_rvt_c14.cdl"

.TEMP 25

*.include "../spice/sar.cdl"
*.include "../spice/cdac.cdl"
*.include "../spice/sar_logic.cdl"
*.include "../spice/comp_nand.cdl"
.include "../spice/sar.pex.cdl"
.include "../spice/sar.pex.netlist"
*.include "../spice/sar.pex.netlist.pex"
*.include "../spice/sar.pex.netlist.pxi"

.hdl "../spice/dac.va"

xainv0 en enb vdd ainv
xainv1 enb valid_d vdd ainv

.param vddx=0.8

.param fxxx=1
*.param fxxx=2
.param fxxx_vcm=1
*The sw_width/sw_width_vcm is actually numbers of fins, integer number, with default value 4.
*And total basic width is sw_width*fxxx/sw_width*fxxx_vcm
.param cap_val = @capVal
.param sw_width = @widthi
.param sw_width_vcm = @widthc
.param freq_sample = @fsmpl

.param tclk = 1/(freq_sample*12)

vclk_sar              clk_sar             0	pulse	0 1 10n 10p 10p 'tclk*0.5' tclk
ven                   en                  0	pulse	0 1 'tclk*2+10n+1n' 10p 10p 'tclk*10' 'tclk*12'	

vin_p	vin_p    0      sin	0.4 0.4 'freq_sample*2/256' 1n 0 0
vin_n	vin_n    0      sin	0.4 0.4 'freq_sample*2/256' 1n 0 180
*vin_p	vin_p    0      sin	0.4 0.4 'freq_sample*127/256' 1n 0 0
*vin_n	vin_n    0      sin	0.4 0.4 'freq_sample*127/256' 1n 0 180

vcm		vcm		0	dc	0.4

vrefh	vrefh	0	dc	vddx
vrefl	vrefl	0	dc	0.0

vdd	vdd	0	dc	vddx
vss	vss	0	dc	0

.print p(vdd)
.print p(vss)
.print p(vrefh)
.print p(vrefl)
.print p(vcm)
.print p(vin_p)
.print p(vin_n)

.inc ./meas_card_pex

.TRAN 0.1p 'tclk*12*260'

.END
