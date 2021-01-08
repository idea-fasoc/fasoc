
module sar( input clk, // sar clock input
                input en, // sar control signal // en=0 : sample phase. minimum 1 cycle. // en=1 : conversion phase. minimum WIDTH+2 cycles are needed.
                input vinp, // sar analog positive input
                input vinn, // sar analog negative input (Differential config. : connect negative input / Single-ended config. : connect vcm)
                output [@NBIT-1:0] result,
                input vcm, // common mode reference input. VDD/2 should be connected
                input vrefh,
                input vrefl);

///////////////////////////////////
////////// Internal wires //////////
///////////////////////////////////

//wire vcmpp, vcmpn; // cdac output => comparator positive, negative input
wire sample; // input is sampled when sample=1
wire outp, outn; // comparator output
wire comp_clk; // comparator clk
wire vtop_n, vtop_p;
wire [@NBIT-1:0] value; //CDAC cap control signal

sar_logic isar_logic(
	.clk_sar(clk),
	.en(en),
	.sample(sample),
	.value(value),
	.result_out(result),
	.cmp(outn),
	.cmp_clk(comp_clk)
);

cdac icdac(
        .vin_p(vinp),
        .vin_n(vinn),
        .vrefh(vrefh),
        .vrefl(vrefl),
        .vcm_p(vcm),
        .vcm_n(vcm),
        .vtop_n(vtop_n),
        .vtop_p(vtop_p),
        .sample(sample),
        .value(value)
);


comp_nand icomparator(
        .clk_sar(comp_clk),
        .vinn(vtop_n),
        .vinp(vtop_p),
        .outp(outp),
        .outn(outn)
);

endmodule
