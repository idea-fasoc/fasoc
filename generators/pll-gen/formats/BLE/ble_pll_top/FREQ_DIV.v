//`timescale 1ns/1ps
module FREQ_DIV (RESET, CLK_40M, CLK_8M);

	input		RESET;
	input		CLK_40M;
	output reg      CLK_8M;

	reg [2:0]	cnt;

	always@ ( posedge CLK_40M or posedge RESET) begin
		if (RESET) begin
			cnt <= 0;
			CLK_8M <= 0;
		end else begin
			if (cnt < 4) begin
				cnt <= cnt+1;
				if(cnt==1) begin
					CLK_8M <= 1;
				end else if (cnt == 3) begin
					CLK_8M <= 0;
				end	
			end else if (cnt==4) begin
				cnt <= 0;
			end
		end
	end

endmodule
