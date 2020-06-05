
module sar(clk, en, vin_p, vin_n, result, vcm, vdd, vnw, vpw, vss);

///////////////////////////////////
////////// Digital inputs//////////
///////////////////////////////////

input clk; // sar clock input
input en; // sar control signal // en=0 : sample phase. minimum 1 cycle. // en=1 : conversion phase. minimum WIDTH+2 cycles are needed.

input vin_p; // sar analog positive input
input vin_n; // sar analog negative input (Differential config. : connect negative input / Single-ended config. : connect vcm)

output [@NBIT-1:0] result; // ADC output

///////////////////////////////////
////////// Analog inputs //////////
///////////////////////////////////

inout vcm; // common mode reference input. VDD/2 should be connected
inout vdd; // power supply
inout vss; // ground
inout vnw; // power supply
inout vpw; // ground

///////////////////////////////////
////////// Internal wires //////////
///////////////////////////////////

wire vtop_p, vtop_n; // cdac output => comparator positive, negative input
wire sample; // input is sampled when sample=1
wire outp, outn; // comparator output
wire clk_comp; // comparator clk

wire [@NBIT-1:0] value; //CDAC cap control signal
//This part only works with 8 bit 
sar_logic isar_logic(
	.clk_sar(clk),
	.en(en),
	.sample(sample),
	.value(value),
	.result_out(result),
	.cmp(outn),
	.cmp_clk(clk_comp),
	.VDD(vdd),
	.VNW(vnw),
	.VPW(vpw),
	.VSS(vss)
);

cdac icdac(
	.vin_p(vin_p),
	.vin_n(vin_n),
	.vrefh(vdd),
	.vrefl(vss),
	.vcm_p(vcm),
	.vcm_n(vcm),
	.vtop_n(vtop_n),
	.vtop_p(vtop_p),
	.sample(sample),
	.value(value),
	.vdd(vdd),
	.vnw(vnw),
	.vpw(vpw),
	.vss(vss)
);

comp_nand_ver0 icomparator(
	.clk_sar(clk_comp),
	.vinn(vtop_n),
	.vinp(vtop_p),
	.outp(outp),
	.outn(outn),
	.vdd(vdd),
	.vnw(vnw),
	.vpw(vpw),
	.vss(vss)
);

endmodule
