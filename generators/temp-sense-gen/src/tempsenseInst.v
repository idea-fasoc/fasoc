module tempsenseInst
(

	input CLK_REF,
	input RESET_COUNTERn,
	input [3:0] SEL_CONV_TIME,
	input en,
	input VIN,

 	output [23:0] DOUT,
	output DONE,
	output out, outb,
	output lc_out
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
	TEMP_ANALOG temp_analog_0(
		.EN(en),
		//.in_vin(VIN),
		.OUT(out),
		.OUTB(outb)
	);



//	LC1P2TO3P6X1RVT_VDDX4 a_lc_0(.A(out), .AB(outb), .VIN(VIN), .Y(lc_0));
//	BUFH_X4M_A9TR a_buffer_0 (.A(lc_0), .Y(lc_out));
	SLC_cell a_lc_0(.A(out), .AB(outb), .Y(lc_0));
	BUF_X0P4N_A10P5PP84TR_C14 a_buffer_0 (.A(lc_0), .Y(lc_out));
	
endmodule

