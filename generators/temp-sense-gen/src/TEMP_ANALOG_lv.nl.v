module TEMP_ANALOG_lv (EN, OUT, OUTB);
 input  EN;
// inout in_vin;
 output OUT, OUTB;
 wire  n;
wire n1; 
wire n2; 
wire n3; 
wire n4; 
wire n5; 
wire n6; 
wire n7; 
wire nx1, nx2, nx3, nb1, nb2; 
NAND2X1RVT_ISOVDD a_nand_0 ( .A(EN), .B(n7), .Y(n1), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_0 ( .A(n1), .Y(n2), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_1 ( .A(n2), .Y(n3), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_2 ( .A(n3), .Y(n4), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_3 ( .A(n4), .Y(n5), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_4 ( .A(n5), .Y(n6), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_5 ( .A(n6), .Y(n7), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_m1 ( .A(n7), .Y(nx1), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_m2 ( .A(n7), .Y(nx2), .VIN(1'b1));
INVXRVT_ISOVDD a_inv_m3 ( .A(nx2), .Y(nx3), .VIN(1'b1));
BUFX4RVT_ISOVDD a_buf_3 ( .A(nx3), .Y(nb2), .VIN(1'b1));
BUFX4RVT_ISOVDD a_buf_0 ( .A(nx1), .Y(nb1), .VIN(1'b1));
BUFX4RVT_ISOVDD a_buf_1 ( .A(nb1), .Y(OUT), .VIN(1'b1));
BUFX4RVT_ISOVDD a_buf_2 ( .A(nb2), .Y(OUTB), .VIN(1'b1));

endmodule
