module synth_pll_dco_interp ( INA, INB, IPA, IPB, ON, OP);
	input INA, INB, IPA, IPB;
	output ON, OP;
	wire int1, int2;

	INV_X2M_A9TR inva1 (.A(INA), .Y(int1) );
	INV_X2M_A9TR inva2 (.A(INB), .Y(int1) );
	INV_X2M_A9TR inva3 (.A(int1), .Y(ON) );
	
	INV_X2M_A9TR invb1 (.A(IPA), .Y(int2) );
	INV_X2M_A9TR invb2 (.A(IPB), .Y(int2) );
	INV_X2M_A9TR invb3 (.A(int2), .Y(OP) );
endmodule

module synth_pll_dco_interp_40 ( INA, INB, IPA, IPB, ON, OP);
	input INA, INB, IPA, IPB;
	output ON, OP;
	wire int1, int2;
	
	INVD2BWP12T inva1 (.I(INA), .ZN(int1) );
	INVD2BWP12T inva2 (.I(INB), .ZN(int1) );
	INVD2BWP12T inva3 (.I(int1), .ZN(ON) );

	INVD2BWP12T invb1 (.I(IPA), .ZN(int2) );
	INVD2BWP12T invb2 (.I(IPB), .ZN(int2) );
	INVD2BWP12T invb3 (.I(int2), .ZN(OP) );
endmodule
