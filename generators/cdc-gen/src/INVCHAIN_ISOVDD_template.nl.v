module INVCHAIN_ISOVDD (IN, in_vin, OUT);

input IN; 
inout in_vin;

output OUT;

@@ wire n@nn;
wire out_pre;

@@ @na inv_iciso_0 (.A(IN), .VIN(in_vin), .Y(n1));
@@ @nb inv_iciso_@ni (.A(n@n1), .VIN(in_vin), .Y(n@n2));

@@ @nc buf_iciso_0 (.A(n@n3), .VIN(in_vin), .Y(OUT));
	

endmodule
