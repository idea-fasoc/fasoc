module CDC_ANALOG2 (IN, OREF);

input IN;
output OREF;


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

INV_X1M_A9TR inv_ic_0 (.A(IN), .Y(n1));
INV_X1M_A9TR inv_ic_1 (.A(n1), .Y(n2));
INV_X1M_A9TR inv_ic_2 (.A(n2), .Y(n3));
INV_X1M_A9TR inv_ic_3 (.A(n3), .Y(n4));
INV_X1M_A9TR inv_ic_4 (.A(n4), .Y(n5));
INV_X1M_A9TR inv_ic_5 (.A(n5), .Y(n6));
INV_X1M_A9TR inv_ic_6 (.A(n6), .Y(n7));
INV_X1M_A9TR inv_ic_7 (.A(n7), .Y(n8));
INV_X1M_A9TR inv_ic_8 (.A(n8), .Y(n9));
INV_X1M_A9TR inv_ic_9 (.A(n9), .Y(n10));
INV_X1M_A9TR inv_ic_10 (.A(n10), .Y(n11));
INV_X1M_A9TR inv_ic_11 (.A(n11), .Y(n12));
INV_X1M_A9TR inv_ic_12 (.A(n12), .Y(n13));
INV_X1M_A9TR inv_ic_13 (.A(n13), .Y(n14));
INV_X1M_A9TR inv_ic_14 (.A(n14), .Y(n15));
INV_X1M_A9TR inv_ic_15 (.A(n15), .Y(n16));
INV_X1M_A9TR inv_ic_16 (.A(n16), .Y(n17));
INV_X1M_A9TR inv_ic_17 (.A(n17), .Y(n18));
INV_X1M_A9TR inv_ic_18 (.A(n18), .Y(n19));
INV_X1M_A9TR inv_ic_19 (.A(n19), .Y(n20));
INV_X1M_A9TR inv_ic_20 (.A(n20), .Y(n21));

BUF_X4M_A9TR buf_ic_0 (.A(n21), .Y(OREF));
	

endmodule
