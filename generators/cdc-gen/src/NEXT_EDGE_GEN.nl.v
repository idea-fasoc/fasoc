module NEXT_EDGE_GEN (RESET, VLOWDLY, FINISH, DONEF, DONER, OUTR, OUTF, CONVFINISH, CLK, SENSE);
input  RESET, VLOWDLY, FINISH, DONEF, DONER;
output OUTR, OUTF, CONVFINISH, CLK, SENSE;
wire n1, n2, n3, n4, n5, n6, n7, d, db, DONE, YB, reset_in, vlowdly_in, finish_in, donef_in, doner_in, outf_out, outr_out, convfinish_out, clk_out, sens_out;
wire n8, n9, n10, n11, n12, n13;



//input
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_0 (.A(RESET), .Y(reset_in));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_1 (.A(VLOWDLY), .Y(vlowdly_in));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_2 (.A(FINISH), .Y(finish_in));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_3 (.A(DONEF), .Y(donef_in));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_4 (.A(DONER), .Y(doner_in));

//output
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_5 (.A(outf_out), .Y(OUTF));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_6 (.A(outr_out), .Y(OUTR));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_7 (.A(convfinish_out), .Y(CONVFINISH));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_8 (.A(clk_out), .Y(CLK));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_9 (.A(sens_out), .Y(SENSE));


BUF_X0P4N_A10P5PP84TR_C14 buf_neg_10 (.A(n1), .Y(n2));
BUF_X0P4N_A10P5PP84TR_C14 buf_neg_11 (.A(n4), .Y(n5));
NAND2_X0P4N_A10P5PP84TR_C14 nand_neg_0 (.A(donef_in), .B(n3), .Y(n1));
NAND2_X0P4N_A10P5PP84TR_C14 nand_neg_1 (.A(vlowdly_in), .B(doner_in), .Y(n4));
NAND2_X0P4N_A10P5PP84TR_C14 nand_neg_2 (.A(n7), .B(n11), .Y(n12));
NAND2_X0P4N_A10P5PP84TR_C14 nand_neg_3 (.A(outf_out), .B(sens_out), .Y(n13));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_0 (.A(vlowdly_in), .Y(n3));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_1 (.A(outf_out), .Y(outr_out));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_2 (.A(reset_in), .Y(n7));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_3 (.A(n7), .Y(n8));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_4 (.A(finish_in), .Y(n9));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_5 (.A(convfinish_out), .Y(n11));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_6 (.A(n12), .Y(sens_out));
INVP_X0P4N_A10P5PP84TR_C14 inv_neg_7 (.A(n13), .Y(clk_out));
SRLATCH sr_neg_0 (.R(n5), .S(n2), .Q(outf_out), .QB(n6));
SRLATCH sr_neg_1 (.R(n8), .S(n9), .Q(convfinish_out), .QB(n10));
endmodule



module SRLATCH(R, S, Q, QB);
	input R, S;
	output Q, QB;

NOR2_X0P4N_A10P5PP84TR_C14 a_nor_0 (.A(R), .B(QB), .Y(Q));
NOR2_X0P4N_A10P5PP84TR_C14 a_nor_1 (.A(S), .B(Q), .Y(QB));

endmodule
