// verilog
`ifndef __ANALOG_CORE__
`define __ANALOG_CORE__


`timescale 1ns/1ps

//`include "dco_model.v"
//`include "dco_model_noise.v"

module analog_core( 
	DCO_CCW_IN, 
	DCO_FCW_IN, 
	CLKREF, 
	CLK_DITHER, 
	DCO_OUTP, 
	DCO_OUTM,
	SAMPLED_PHASES_OUT);



	// Functions
//	`include "functions.v"


	// Parameters

		// DCO Base operating frequency
		parameter DCO_CENTER_FREQ = 2.4e9;
		parameter DCO_FBASE = 450e6;
		parameter DCO_OFFSET = 0;
		parameter DCO_VT_VARIATION = 150e6;

		// DCO Coarse Controls (covers ~3GHz)
		parameter DCO_CCW_MAX = 31;
		parameter DCO_CSTEP = 40e6;

		// DCO Fine Controls (covers ~50MHz)
		parameter DCO_FCW_MAX = 1023;
		parameter DCO_FSTEP = 500e3;

		// DCO number of phases
		parameter DCO_NUM_PHASES = 5;




	// Local Parameters
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);



	// Ports
		input 		[DCO_CCW_WIDTH-1: 0] 	DCO_CCW_IN;
		input 		[DCO_FCW_WIDTH-1: 0] 	DCO_FCW_IN;
		input 								CLKREF;
		input 								CLK_DITHER;

		output 								DCO_OUTP;
		output 								DCO_OUTM;
		output reg	[DCO_NUM_PHASES-1:0]	SAMPLED_PHASES_OUT;


	// Internal Signals
		wire 		[DCO_NUM_PHASES-1:0] 	phases;
		wire 		[DCO_NUM_PHASES-1:0] 	phases_proc;
		reg 		[DCO_CCW_WIDTH-1: 0] 	dco_ccw;
		reg 		[DCO_FCW_WIDTH-1: 0] 	dco_fcw;


	// Variables
		real vt_variation;


	// Structural
		//dco_model #(
		dco_model_noise #(
				.DCO_CENTER_FREQ(DCO_CENTER_FREQ), 
				.DCO_FBASE(DCO_FBASE), 
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_VT_VARIATION(DCO_VT_VARIATION),
				.DCO_CCW_MAX(DCO_CCW_MAX), 
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX), 
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PHASES))
			u_dco_model ( 
				.DCO_CCW_IN(dco_ccw), 
				.DCO_FCW_IN(dco_fcw), 
				.PHASES_OUT(phases)
		);

		assign DCO_OUTP = phases[2];  // test-km
		assign DCO_OUTM = ~DCO_OUTP;

	
	// Behavioral

		// invert phases[2*k]
		genvar genvar_ii;
		generate

			for (genvar_ii=0;genvar_ii<DCO_NUM_PHASES;genvar_ii=genvar_ii+1) 
				begin :INV_ODD
					if (genvar_ii%2==0) begin
						assign phases_proc[genvar_ii] = phases[genvar_ii]; // test-km
					end else begin
						assign phases_proc[genvar_ii] = ~phases[genvar_ii]; // test-km
					end
				end
		endgenerate
						


		initial begin
			vt_variation = 0;
		end


		always @(posedge CLKREF) begin

			SAMPLED_PHASES_OUT <= phases_proc;

		end


		always @(posedge CLK_DITHER) begin

			dco_ccw <= DCO_CCW_IN;
			dco_fcw <= DCO_FCW_IN;

		end

		//always @(negedge CLKREF) begin

		//	dco_ccw <= DCO_CCW_IN;
		//	dco_fcw <= DCO_FCW_IN;

		//end


		always @* begin
			u_dco_model.vt_variation = vt_variation;
		end


endmodule


`endif
