module TEMP_ANALOG_hv
(
input CLK_REF,
input RESET_COUNTERn,
input [3:0] SEL_CONV_TIME,
input en,
input out, outb,

output [23:0] DOUT,
output DONE,
output lc_out,
inout VIN
);

wire lc_0;
//	reg  iso;
//	assign iso = 0 ;
counter async_counter_0(
	// Input
	.CLK_SENS       (lc_out),
	.CLK_REF        (CLK_REF),
	.RESET_COUNTERn (RESET_COUNTERn),
	.SEL_CONV_TIME  (SEL_CONV_TIME),
	// Output
	.DOUT           (DOUT),
	.DONE  		(DONE)
);


@@ @nf a_header_@nh(.VIN(VIN));
SLC_cell a_lc_0(.A(out), .AB(outb), .Y(lc_0));
BUF_X0P4N_A10P5PP84TR_C14 a_buffer_0 (.A(lc_0), .Y(lc_out));
	
endmodule

