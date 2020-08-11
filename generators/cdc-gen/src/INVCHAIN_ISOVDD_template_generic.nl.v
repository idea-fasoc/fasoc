module INVCHAIN_ISOVDD (IN, OUT);

input IN; 
//inout in_vin;

output OUT;

@@ wire n@nn;
wire out_pre;

@@ @na inv_iciso_0 (.A(IN), .Y(n1));
@@ @nb inv_iciso_@ni (.A(n@n1), .Y(n@n2));

@@ @nc buf_iciso_0 (.A(n@n3), .Y(OUT));
	

endmodule
