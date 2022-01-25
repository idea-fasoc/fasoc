module synth_pll_dco_outbuff ( IN, IP, ON, OP);
	input IN, IP;
	output ON, OP;
	wire int1, int2;

	INV_X2N_A10P5PP84TR_C14 inva1 (.A(IN), .Y(int1) );
	INV_X2N_A10P5PP84TR_C14 inva2 (.A(IN), .Y(int1) );
	INV_X2N_A10P5PP84TR_C14 inva3 (.A(int1), .Y(ON) );

	INV_X2N_A10P5PP84TR_C14 invb1 (.A(IP), .Y(int2) );
	INV_X2N_A10P5PP84TR_C14 invb2 (.A(IP), .Y(int2) );
	INV_X2N_A10P5PP84TR_C14 invb3 (.A(int2), .Y(OP) );
endmodule

module synth_pll_dco_outbuff_40 ( in, ip, on, op);
	input in, ip;
	output on, op;
	wire int1, int2;

	INVD2BWP12T inva1 (.I(in), .ZN(int1) );
	INVD2BWP12T inva2 (.I(in), .ZN(int1) );
	INVD2BWP12T inva3 (.I(int1), .ZN(on) );

	INVD2BWP12T invb1 (.I(ip), .ZN(int2) );
	INVD2BWP12T invb2 (.I(ip), .ZN(int2) );
	INVD2BWP12T invb3 (.I(int2), .ZN(op) );
endmodule
