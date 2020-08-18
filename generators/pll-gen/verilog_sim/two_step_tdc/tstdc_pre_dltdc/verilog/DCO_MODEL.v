`ifndef __DCO_MODEL__
`define __DCO_MODEL__

`timescale 1fs/1fs
`include "mLingua_pwl.vh"

module DCO_MODEL( 
    DCO_CCW_IN, 
    DCO_FCW_IN, 
    PHASES_OUT);


	// Functions

        
    // Parameters

		// DCO Base operating frequency
		parameter DCO_FBASE = 450e6;
		parameter DCO_OFFSET = 0;
		parameter DCO_VT_VARIATION = 175e6;
        parameter real DCO_JITTER = 0.005; // rms jitter in (jitter/period)

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
		input			[DCO_CCW_WIDTH-1: 0]	DCO_CCW_IN;
		input			[DCO_FCW_WIDTH-1: 0]	DCO_FCW_IN;
		output reg		[DCO_NUM_PHASES-1:0]	PHASES_OUT;


	// Internal Signals
		wire dco_clk;


	// Variables
		real frequency;
		real vt_variation;
	

	// Functional


		// Initialze the frequency and generate and edge
			initial begin
				frequency = DCO_FBASE;
				vt_variation = 0;
			end


		// Set the DCO frequency as a PWL signal
            pwl freq_pwl;
			
            always @* begin
				frequency = DCO_FBASE + DCO_OFFSET + vt_variation*DCO_VT_VARIATION/2 +
					DCO_FSTEP*$itor(DCO_FCW_IN) + DCO_CSTEP*$itor(DCO_CCW_IN) ;
			end

            real2pwl #(
                .tr(100e-12) // risetime of frequency change
            ) real2pwl_i (
                .en(1'b1),
                .in(frequency),
                .out(freq_pwl)
            );


		// DaVE implementation of frequency to clock
            pwl_integrator #(
                .etol(0.01),
                .modulo(0.5),
                .noise(DCO_JITTER)
            ) integ_i (
                .gain(1.0),
                .si(freq_pwl), 
                .trigger(dco_clk),
                // unused outputs explicitly indicated to avoid warnings
                .so(),
                .i_modulo()
            );


		// generate the phases

			genvar genvar_ii;
			generate
				for (genvar_ii=DCO_NUM_PHASES-1;genvar_ii>=0;genvar_ii=genvar_ii-1) 
				   begin : GEN_PHASE
                       always @(dco_clk) begin
                           PHASES_OUT[genvar_ii] <= #(1.0*(DCO_NUM_PHASES-1-genvar_ii)/frequency/DCO_NUM_PHASES * 1s) dco_clk;
                       end
                   end
				endgenerate

endmodule


`endif

