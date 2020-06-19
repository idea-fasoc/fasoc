module CDCW_CNT (TICK_TOTAL, TICK_RISE, TICK_FALL, RESETn, OE, OUT_TOTAL, OUT_RISE, OUT_FALL);

	input	TICK_TOTAL, TICK_RISE, TICK_FALL, RESETn, OE;
	output	[23:0]	OUT_TOTAL, OUT_RISE, OUT_FALL;

	CNT_24_OE CNT_TOTAL (.CLK(TICK_TOTAL), .OE(OE), .RESETn(RESETn), .OUT(OUT_TOTAL));
	CNT_24_OE CNT_RISE  (.CLK(TICK_RISE),  .OE(OE), .RESETn(RESETn), .OUT(OUT_RISE));
	CNT_24_OE CNT_FALL  (.CLK(TICK_FALL),  .OE(OE), .RESETn(RESETn), .OUT(OUT_FALL));
endmodule 

module CNT_24_OE (CLK, OE, RESETn, OUT);
	
	input	CLK, OE, RESETn;
	output [23:0] OUT;

	wire next_0, next_1, next_2, next_3, next_4, next_5;

	CNT_4_OE CNT_4_0 (.CLK(CLK), .OE(OE), .RESETn(RESETn), .NEXT(next_0), .OUT(OUT[3:0]));
	CNT_4_OE CNT_4_1 (.CLK(next_0), .OE(OE), .RESETn(RESETn), .NEXT(next_1), .OUT(OUT[7:4]));
	CNT_4_OE CNT_4_2 (.CLK(next_1), .OE(OE), .RESETn(RESETn), .NEXT(next_2), .OUT(OUT[11:8]));
	CNT_4_OE CNT_4_3 (.CLK(next_2), .OE(OE), .RESETn(RESETn), .NEXT(next_3), .OUT(OUT[15:12]));
	CNT_4_OE CNT_4_4 (.CLK(next_3), .OE(OE), .RESETn(RESETn), .NEXT(next_4), .OUT(OUT[19:16]));
	CNT_4_OE CNT_4_5 (.CLK(next_4), .OE(OE), .RESETn(RESETn), .NEXT(next_5), .OUT(OUT[23:20]));
endmodule

module CNT_4_OE (CLK, OE, RESETn, NEXT, OUT);

	input	CLK, OE, RESETn;
	output 	NEXT;
	output [3:0] OUT;

	wire next_0, next_1, next_2;

	CNT_1_OE CNT_1_0 (.CLK(CLK),    .OE(OE), .RESETn(RESETn), .NEXT(next_0), .OUT(OUT[0]));
	CNT_1_OE CNT_1_1 (.CLK(next_0), .OE(OE), .RESETn(RESETn), .NEXT(next_1), .OUT(OUT[1]));
	CNT_1_OE CNT_1_2 (.CLK(next_1), .OE(OE), .RESETn(RESETn), .NEXT(next_2), .OUT(OUT[2]));
	CNT_1_OE CNT_1_3 (.CLK(next_2), .OE(OE), .RESETn(RESETn), .NEXT(NEXT),   .OUT(OUT[3]));
endmodule

module CNT_1_OE (CLK, OE, RESETn, NEXT, OUT);

	input 	CLK, OE, RESETn;
	output	NEXT, OUT;
	
	wire qb, out_pre, nextb;
	
DFFRPQ_X1N_A10P5PP84TR_C14 DFF0 (.Q(nextb), .D(qb), .CK(CLK), .R(RESETn));
INVP_X0P4N_A10P5PP84TR_C14 INVX1_0 (.Y(qb), .A(nextb));
INVP_X0P4N_A10P5PP84TR_C14 INVX1_1 (.Y(NEXT), .A(nextb));
NAND2_X0P4N_A10P5PP84TR_C14 NAND0 (.Y(out_pre), .A(OE), .B(qb));
BUF_X0P4N_A10P5PP84TR_C14 BUFX4_0 (.Y(OUT), .A(out_pre));
endmodule


