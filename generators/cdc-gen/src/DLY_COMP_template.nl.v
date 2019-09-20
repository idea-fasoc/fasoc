module DLY_COMP (DLYP, DLYM, EN, DONE, YB);
input  DLYP, DLYM, EN;
output DONE, YB;
wire n1, n2, n3, n4, n5, n6, n7, d, db, DONE, YB;

@@ @na inv_dc_0 (.A(DLYP), .Y(n1));
@@ @na inv_dc_1 (.A(DLYM), .Y(n2));
@@ @na inv_dc_2 (.A(n3), .Y(n5));
@@ @na inv_dc_3 (.A(n4), .Y(n6));
@@ @na inv_dc_4 (.A(db), .Y(d));

@@ @nb nand_dc_0 (.A(n1), .B(n4), .Y(n3));
@@ @nb nand_dc_1 (.A(n3), .B(n2), .Y(n4));

@@ @nc buf_dc_0 (.A(n7), .Y(YB));
@@ @nc buf_dc_2 (.A(d), .Y(DONE));

@@ @nd nand_dc_2 (.A(n6), .B(n1), .C(EN), .Y(n7));
@@ @nf xnor_dc_0 (.A(n5), .B(n6), .Y(db));

endmodule
