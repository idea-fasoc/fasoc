`ifndef __SSC_GENERATOR__
`define __SSC_GENERATOR__

`timescale 1ns/1ps

module ssc_generator(
	CLKREF,
	RST,
	SSC_EN,
	COUNT_LIM,
	STEP,
	SHIFT,
	MOD_OUT
);
	
	// Functions
//	`include "functions.v"

	// Parameters
	parameter COUNT_WIDTH = 12;
	parameter ACCUM_WIDTH = 16;
	parameter MOD_WIDTH = 5;
	parameter SHIFT_WIDTH = func_clog2(ACCUM_WIDTH-1);

	input 		CLKREF, RST, SSC_EN;
	input 		[COUNT_WIDTH-1:0] COUNT_LIM;
	input 		[3:0] STEP;
	input 		[SHIFT_WIDTH-1:0] SHIFT;

	output  	[MOD_WIDTH-1:0] MOD_OUT;

	reg			[ACCUM_WIDTH-1:0] accum;
	wire		[ACCUM_WIDTH-1:0] accum_shift;

	reg			[COUNT_WIDTH-1:0] count;

	assign accum_shift = accum >> SHIFT;
	assign MOD_OUT = accum_shift[MOD_WIDTH-1:0];

	always @(posedge CLKREF) begin
		if (RST) begin
			accum <= 0;
			count <= 0;
		end
		else if (SSC_EN) begin
			if (count < (COUNT_LIM >> 1)) begin 
				accum <= accum + STEP;
			end
			else begin
				accum <= accum - STEP;
			end

			if (count >= COUNT_LIM-1) begin
				count <= 0;
				accum <= 0; //ensure accum is reset every cycle regardless of bugs
			end
			else begin
				count <= count +1;
			end
		end
	end

endmodule
`endif
