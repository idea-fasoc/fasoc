module CDC_ANALOG2 (IN, OREF);

input IN;
output OREF;


@@ wire n@nn;
wire out_pre;

@@ @na inv_ic_0 (.A(IN), .Y(n1));
@@ @nb inv_ic_@ni (.A(n@n1), .Y(n@n2));

@@ @nc buf_ic_0 (.A(n@n3), .Y(OREF));
	

endmodule
