module NEXT_EDGE_GEN (RESET, VLOWDLY, FINISH, DONEF, DONER, OUTR, OUTF, CONVFINISH, CLK, SENSE);
input  RESET, VLOWDLY, FINISH, DONEF, DONER;
output OUTR, OUTF, CONVFINISH, CLK, SENSE;
wire n1, n2, n3, n4, n5, n6, n7, d, db, DONE, YB, reset_in, vlowdly_in, finish_in, donef_in, doner_in, outf_out, outr_out, convfinish_out, clk_out, sens_out;
wire n8, n9, n10, n11, n12, n13;



//input
@@ @na buf_neg_0 (.A(RESET), .Y(reset_in));
@@ @na buf_neg_1 (.A(VLOWDLY), .Y(vlowdly_in));
@@ @na buf_neg_2 (.A(FINISH), .Y(finish_in));
@@ @na buf_neg_3 (.A(DONEF), .Y(donef_in));
@@ @na buf_neg_4 (.A(DONER), .Y(doner_in));

//output
@@ @na buf_neg_5 (.A(outf_out), .Y(OUTF));
@@ @na buf_neg_6 (.A(outr_out), .Y(OUTR));
@@ @na buf_neg_7 (.A(convfinish_out), .Y(CONVFINISH));
@@ @na buf_neg_8 (.A(clk_out), .Y(CLK));
@@ @na buf_neg_9 (.A(sens_out), .Y(SENSE));


@@ @na buf_neg_10 (.A(n1), .Y(n2));
@@ @na buf_neg_11 (.A(n4), .Y(n5));
@@ @nb nand_neg_0 (.A(donef_in), .B(n3), .Y(n1));
@@ @nb nand_neg_1 (.A(vlowdly_in), .B(doner_in), .Y(n4));
@@ @nb nand_neg_2 (.A(n7), .B(n11), .Y(n12));
@@ @nb nand_neg_3 (.A(outf_out), .B(sens_out), .Y(n13));
@@ @nc inv_neg_0 (.A(vlowdly_in), .Y(n3));
@@ @nc inv_neg_1 (.A(outf_out), .Y(outr_out));
@@ @nc inv_neg_2 (.A(reset_in), .Y(n7));
@@ @nc inv_neg_3 (.A(n7), .Y(n8));
@@ @nc inv_neg_4 (.A(finish_in), .Y(n9));
@@ @nc inv_neg_5 (.A(convfinish_out), .Y(n11));
@@ @nc inv_neg_6 (.A(n12), .Y(sens_out));
@@ @nc inv_neg_7 (.A(n13), .Y(clk_out));
SRLATCH sr_neg_0 (.R(n5), .S(n2), .Q(outf_out), .QB(n6));
SRLATCH sr_neg_1 (.R(n8), .S(n9), .Q(convfinish_out), .QB(n10));
endmodule



module SRLATCH(R, S, Q, QB);
	input R, S;
	output Q, QB;

@@ @nd a_nor_0 (.A(R), .B(QB), .Y(Q));
@@ @nd a_nor_1 (.A(S), .B(Q), .Y(QB));

endmodule
