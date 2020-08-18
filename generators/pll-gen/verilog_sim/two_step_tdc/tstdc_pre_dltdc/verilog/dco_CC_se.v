// dco_CC_se model
`timescale 1ps/1ps

module dco_CC_se (EN, IN, OUT);

	input EN;
	input IN;
	output reg OUT;

	parameter CC_delay = 17e-12; 
	real TIME_SCALE=1e-12;

	always @(posedge IN or negedge IN) begin
		if (EN) begin
			OUT = #(CC_delay/TIME_SCALE) ~IN;
		end
	end

endmodule
