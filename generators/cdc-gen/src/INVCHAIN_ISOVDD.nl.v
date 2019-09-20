module INVCHAIN_ISOVDD (IN, in_vin, OUT);

input IN; 
inout in_vin;

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

INVXRVT_ISOVDD inv_iciso_0 (.A(IN), .VIN(in_vin), .Y(n1));
INVXRVT_ISOVDD inv_iciso_1 (.A(n1), .VIN(in_vin), .Y(n2));
INVXRVT_ISOVDD inv_iciso_2 (.A(n2), .VIN(in_vin), .Y(n3));
INVXRVT_ISOVDD inv_iciso_3 (.A(n3), .VIN(in_vin), .Y(n4));
INVXRVT_ISOVDD inv_iciso_4 (.A(n4), .VIN(in_vin), .Y(n5));
INVXRVT_ISOVDD inv_iciso_5 (.A(n5), .VIN(in_vin), .Y(n6));
INVXRVT_ISOVDD inv_iciso_6 (.A(n6), .VIN(in_vin), .Y(n7));
INVXRVT_ISOVDD inv_iciso_7 (.A(n7), .VIN(in_vin), .Y(n8));
INVXRVT_ISOVDD inv_iciso_8 (.A(n8), .VIN(in_vin), .Y(n9));
INVXRVT_ISOVDD inv_iciso_9 (.A(n9), .VIN(in_vin), .Y(n10));
INVXRVT_ISOVDD inv_iciso_10 (.A(n10), .VIN(in_vin), .Y(n11));
INVXRVT_ISOVDD inv_iciso_11 (.A(n11), .VIN(in_vin), .Y(n12));
INVXRVT_ISOVDD inv_iciso_12 (.A(n12), .VIN(in_vin), .Y(n13));
INVXRVT_ISOVDD inv_iciso_13 (.A(n13), .VIN(in_vin), .Y(n14));
INVXRVT_ISOVDD inv_iciso_14 (.A(n14), .VIN(in_vin), .Y(n15));
INVXRVT_ISOVDD inv_iciso_15 (.A(n15), .VIN(in_vin), .Y(n16));
INVXRVT_ISOVDD inv_iciso_16 (.A(n16), .VIN(in_vin), .Y(n17));
INVXRVT_ISOVDD inv_iciso_17 (.A(n17), .VIN(in_vin), .Y(n18));
INVXRVT_ISOVDD inv_iciso_18 (.A(n18), .VIN(in_vin), .Y(n19));
INVXRVT_ISOVDD inv_iciso_19 (.A(n19), .VIN(in_vin), .Y(n20));
INVXRVT_ISOVDD inv_iciso_20 (.A(n20), .VIN(in_vin), .Y(n21));

BUFX4RVT_ISOVDD buf_iciso_0 (.A(n21), .VIN(in_vin), .Y(OUT));
	

endmodule
