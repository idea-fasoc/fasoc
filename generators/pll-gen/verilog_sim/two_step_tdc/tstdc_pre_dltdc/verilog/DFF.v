// DFF
`timescale 1ps/1ps

module DFFQ_X1N_A10P5PP84TR_C14 ( Q, D, CK);
	parameter su_time = 14e-12;

	real TIME_SCALE=1e-12;

	input	D;
	input	CK;
	output reg Q;

	always @(posedge CK) begin
		Q <= #(su_time/TIME_SCALE) D;
	end

endmodule

