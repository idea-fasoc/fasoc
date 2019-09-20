module TEMP_ANALOG (EN, in_vin, OUT, OUTB);
 input  EN;
 inout in_vin;
 output OUT, OUTB;
 wire  n;
@@ wire n@nn; 
wire nx1, nx2, nx3, nb1, nb2; 
@@ @na a_nand_0 ( .A(EN), .B(n@n0), .VIN(in_vin), .Y(n1));
@@ @nb a_inv_@ni ( .A(n@n1), .VIN(in_vin), .Y(n@n2));
@@ @ng a_inv_m1 ( .A(n@n3), .VIN(in_vin), .Y(nx1));
@@ @nk a_inv_m2 ( .A(n@n4), .VIN(in_vin), .Y(nx2));
@@ @nm a_inv_m3 ( .A(nx2), .VIN(in_vin), .Y(nx3));
@@ @np a_buf_3 ( .A(nx3), .VIN(in_vin), .Y(nb2));
@@ @nc a_buf_0 ( .A(nx1), .VIN(in_vin), .Y(nb1));
@@ @nd a_buf_1 ( .A(nb1), .VIN(in_vin), .Y(OUT));
@@ @ne a_buf_2 ( .A(nb2), .VIN(in_vin), .Y(OUTB));
@@ @nf a_header_@nh(.VIN(in_vin));

endmodule
