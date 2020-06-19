module DLY_COMP (DLYP, DLYM, EN, DONE, YB);
input  DLYP, DLYM, EN;
output DONE, YB;
wire n1, n2, n3, n4, n5, n6, n7, d, db, DONE, YB;

INVP_X0P4N_A10P5PP84TR_C14 inv_dc_0 (.A(DLYP), .Y(n1));
INVP_X0P4N_A10P5PP84TR_C14 inv_dc_1 (.A(DLYM), .Y(n2));
INVP_X0P4N_A10P5PP84TR_C14 inv_dc_2 (.A(n3), .Y(n5));
INVP_X0P4N_A10P5PP84TR_C14 inv_dc_3 (.A(n4), .Y(n6));
INVP_X0P4N_A10P5PP84TR_C14 inv_dc_4 (.A(db), .Y(d));

NAND2_X0P4N_A10P5PP84TR_C14 nand_dc_0 (.A(n1), .B(n4), .Y(n3));
NAND2_X0P4N_A10P5PP84TR_C14 nand_dc_1 (.A(n3), .B(n2), .Y(n4));

BUF_X0P4N_A10P5PP84TR_C14 buf_dc_0 (.A(n7), .Y(YB));
BUF_X0P4N_A10P5PP84TR_C14 buf_dc_2 (.A(d), .Y(DONE));

NAND3_X0P4N_A10P5PP84TR_C14 nand_dc_2 (.A(n6), .B(n1), .C(EN), .Y(n7));
XNOR2_X0P6N_A10P5PP84TR_C14 xnor_dc_0 (.A(n5), .B(n6), .Y(db));

endmodule
