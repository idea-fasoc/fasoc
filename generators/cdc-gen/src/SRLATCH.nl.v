module SRLATCH(R, S, Q, QB);
	input R, S;
	output Q, QB;

	NOR2X1HVT a_nor_0 (.A(R), .B(QB), .Y(Q));
	NOR2X1HVT a_nor_1 (.A(S), .B(Q), .Y(QB));

endmodule
