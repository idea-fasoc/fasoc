module INVCHAIN_ISOVDD (IN, OUT);

input IN; 
//inout in_vin;

output OUT;

wire n1;
wire n2;
wire n3;
wire n4;
wire n5;
wire n6;
wire n7;
wire n8;
wire n9;
wire n10;
wire n11;
wire n12;
wire n13;
wire n14;
wire n15;
wire n16;
wire n17;
wire n18;
wire n19;
wire n20;
wire n21;
wire out_pre;

INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_0 (.A(IN), .Y(n1));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_1 (.A(n1), .Y(n2));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_2 (.A(n2), .Y(n3));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_3 (.A(n3), .Y(n4));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_4 (.A(n4), .Y(n5));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_5 (.A(n5), .Y(n6));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_6 (.A(n6), .Y(n7));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_7 (.A(n7), .Y(n8));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_8 (.A(n8), .Y(n9));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_9 (.A(n9), .Y(n10));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_10 (.A(n10), .Y(n11));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_11 (.A(n11), .Y(n12));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_12 (.A(n12), .Y(n13));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_13 (.A(n13), .Y(n14));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_14 (.A(n14), .Y(n15));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_15 (.A(n15), .Y(n16));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_16 (.A(n16), .Y(n17));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_17 (.A(n17), .Y(n18));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_18 (.A(n18), .Y(n19));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_19 (.A(n19), .Y(n20));
INVP_X0P4N_A10P5PP84TR_C14 inv_iciso_20 (.A(n20), .Y(n21));

BUF_X0P4N_A10P5PP84TR_C14 buf_iciso_0 (.A(n21), .Y(OUT));
	

endmodule
