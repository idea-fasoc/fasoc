// verilog
`ifndef __ANALOG_CORE__
`define __ANALOG_CORE__


`timescale 1ns/1ps


module ANALOG_CORE( 
	DCO_CCW_IN, 
	DCO_FCW_IN, 
	CLKREF, 
	DCO_OUTP, 
	DCO_OUTM,
	SAMPLED_PHASES_OUT);



	// Functions


	// Parameters

		// DCO Base operating frequency
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
		parameter DCO_NUM_PHASES = 63;




	// Local Parameters
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);



	// Ports
		input 		[DCO_CCW_WIDTH-1: 0] 	DCO_CCW_IN;
		input 		[DCO_FCW_WIDTH-1: 0] 	DCO_FCW_IN;
		input 								CLKREF;

		output 								DCO_OUTP;
		output 								DCO_OUTM;
		output reg	[DCO_NUM_PHASES-1:0]	SAMPLED_PHASES_OUT;


	// Internal Signals
		wire 		[DCO_NUM_PHASES-1:0] 	phases;
		reg 		[DCO_CCW_WIDTH-1: 0] 	dco_ccw;
		reg 		[DCO_FCW_WIDTH-1: 0] 	dco_fcw;


	// Variables
		real vt_variation;


	// Structural
		DCO_MODEL #(
				.DCO_FBASE(DCO_FBASE), 
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_VT_VARIATION(DCO_VT_VARIATION),
				.DCO_CCW_MAX(DCO_CCW_MAX), 
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX), 
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PHASES))
			dco_model ( 
				.DCO_CCW_IN(dco_ccw), 
				.DCO_FCW_IN(dco_fcw), 
				.PHASES_OUT(phases)
		);

		assign DCO_OUTP = phases[DCO_NUM_PHASES-1];
		assign DCO_OUTM = ~DCO_OUTP;

	
	// Behavioral
		initial begin
			vt_variation = 0;
		end


		always @(posedge CLKREF) begin

			SAMPLED_PHASES_OUT <= phases;

		end



		always @(negedge CLKREF) begin

			dco_ccw <= DCO_CCW_IN;
			dco_fcw <= DCO_FCW_IN;

		end


		always @* begin
			dco_model.vt_variation = vt_variation;
		end


endmodule


`endif
