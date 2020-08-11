`ifndef __DCO_MODEL__
`define __DCO_MODEL__

`timescale 1fs/1fs

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

		localparam TIME_SCALE = 1e-15;


	// Ports
		input			[DCO_CCW_WIDTH-1: 0]	DCO_CCW_IN;
		input			[DCO_FCW_WIDTH-1: 0]	DCO_FCW_IN;
		output reg		[DCO_NUM_PHASES-1:0]	PHASES_OUT;


	// Internal Signals
		reg dco_clk;


	// Variables
		real frequency;
		real vt_variation;
	

	// Functional


		// Initialze the frequency and generate and edge
			initial begin
				frequency = DCO_FBASE;
				vt_variation = 0;

				dco_clk = 1'b0;
				#(1/frequency/2/TIME_SCALE);
				dco_clk = ~dco_clk;
			end


		// Set the DCO frequency and delay betwen phases
			always @* begin
				frequency = DCO_FBASE + DCO_OFFSET + vt_variation*DCO_VT_VARIATION/2 +
					DCO_FSTEP*$itor(DCO_FCW_IN) + DCO_CSTEP*$itor(DCO_CCW_IN) ;
			end


		// Make the fast clocks oscillate
			always @(posedge dco_clk) begin
				#(1/frequency/2/TIME_SCALE) dco_clk <= ~dco_clk;
			end


			always @(negedge dco_clk) begin
				#(1/frequency/2/TIME_SCALE) dco_clk <= ~dco_clk;
			end


		// generate the phases

			genvar genvar_ii;
			generate

				for (genvar_ii=DCO_NUM_PHASES;genvar_ii>0;genvar_ii=genvar_ii-1) 
					begin : GEN_PHASE

						if (genvar_ii == DCO_NUM_PHASES ) 
							begin

								always @(posedge dco_clk) begin
									PHASES_OUT[genvar_ii-1] = dco_clk;
								end

								always @(negedge dco_clk) begin
									PHASES_OUT[genvar_ii-1] = dco_clk;
								end
							end
						else
							begin

								always @(posedge PHASES_OUT[genvar_ii]) begin
									#(1/frequency/TIME_SCALE/DCO_NUM_PHASES) PHASES_OUT[genvar_ii-1] = PHASES_OUT[genvar_ii];
								end

								always @(negedge PHASES_OUT[genvar_ii]) begin
									#(1/frequency/TIME_SCALE/DCO_NUM_PHASES) PHASES_OUT[genvar_ii-1] = PHASES_OUT[genvar_ii];
								end
							end
					end

				endgenerate

endmodule


`endif

