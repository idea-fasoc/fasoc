module synth_pll_dco_outbuff ( IN, IP, ON, OP);
	input IN, IP;
	output ON, OP;
	wire int1, int2;

	INV_X2M_A9TR inva1 (.A(IN), .Y(int1) );
	INV_X2M_A9TR inva2 (.A(IN), .Y(int1) );
	INV_X2M_A9TR inva3 (.A(int1), .Y(ON) );

	INV_X2M_A9TR invb1 (.A(IP), .Y(int2) );
	INV_X2M_A9TR invb2 (.A(IP), .Y(int2) );
	INV_X2M_A9TR invb3 (.A(int2), .Y(OP) );
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
