`ifndef __DLTDC_MODEL__
`define __DLTDC_MODEL__

//`timescale 1ps/1ps

module dltdc_model( 
	DCO_RAW_PH,
	DCO_EDGE_SEL,
	DL_CCW_IN_FB, 
	DL_FCW_IN_FB,
	DL_CCW_IN_REF, 
	DL_FCW_IN_REF,
//	CLK_FB,
	CLK_REF,	
	PHASES_OUT);

        
    // Parameters
	parameter UNIT_DLBASE_FB = 7e-12; // unit base delay differce between two paths 
	parameter UNIT_DLBASE_REF = 7e-12; // unit base delay differce between two paths 

	// DL Coarse Controls (covers ~3GHz)
	parameter DL_CCW_MAX_FB = 30;
	parameter DL_CSTEP_FB = 0.9e-12; // coarse delay step per stage 
	parameter DL_CCW_MAX_REF = 30;
	parameter DL_CSTEP_REF = 0.9e-12; // coarse delay step per stage 

	// DL Fine Controls (covers ~50MHz)
	parameter DL_FCW_MAX_FB = 60;
	parameter DL_FSTEP_FB = 0.3e-12; // fine delay step per stage 
	parameter DL_FCW_MAX_REF = 60;
	parameter DL_FSTEP_REF = 0.3e-12; // fine delay step per stage 

	// DL number of phases
	parameter DLTDC_NUM_PH = 10;
	parameter DCO_NUM_PH = 5;

	// DFF character
	parameter DFF_ST = 11e-12; // DFF setup time
	parameter DFF_HT = -4e-12; // DFF hold time
	parameter DFF_CTQ_DELAY = 3e-12; // DFF CK to Q delay 


	// Local Parameters
	localparam DL_CCW_WIDTH_FB = func_clog2(DL_CCW_MAX_FB);
	localparam DL_FCW_WIDTH_FB = func_clog2(DL_FCW_MAX_FB);
	localparam DL_CCW_WIDTH_REF = func_clog2(DL_CCW_MAX_REF);
	localparam DL_FCW_WIDTH_REF = func_clog2(DL_FCW_MAX_REF);

	localparam TIME_SCALE = 1e-12;


	// Ports
	input			[DCO_NUM_PH-1:0]	DCO_RAW_PH;
	input			[DCO_NUM_PH-1:0]	DCO_EDGE_SEL;
	//input						CLK_FB;
	input						CLK_REF;
	input			[DL_CCW_WIDTH_FB-1: 0]	DL_CCW_IN_FB;
	input			[DL_FCW_WIDTH_FB-1: 0]	DL_FCW_IN_FB;
	input			[DL_CCW_WIDTH_REF-1: 0]	DL_CCW_IN_REF;
	input			[DL_FCW_WIDTH_REF-1: 0]	DL_FCW_IN_REF;
	output reg		[DLTDC_NUM_PH-1:0]	PHASES_OUT;


	// Internal Signals
	logic 	[DLTDC_NUM_PH-1:0]	clk_fb_d;
	logic 	[DLTDC_NUM_PH-1:0]	clk_ref_d;
	logic 	[DLTDC_NUM_PH-1:0]	phases_out_tmp;
	logic				clk_fb;
	// noise
	real freq_noise;

	// Variables
	real frequency;
	real vt_variation;
	real delay_per_stg_fb;
	real delay_per_stg_ref;
	

	always @* begin
		delay_per_stg_fb = UNIT_DLBASE_FB + (DL_CCW_MAX_FB - DL_CCW_IN_FB)*DL_CSTEP_FB + DL_FCW_IN_FB*DL_FSTEP_FB;
		delay_per_stg_ref = UNIT_DLBASE_REF + (DL_CCW_MAX_REF - DL_CCW_IN_REF)*DL_CSTEP_REF + DL_FCW_IN_REF*DL_FSTEP_REF;
	end
	// Functional
	genvar istg;
	generate
		for (istg=0; istg<DLTDC_NUM_PH; istg=istg+1) begin: GEN_PHASE
			always @(posedge clk_fb_d[istg] or negedge clk_fb_d[istg]) begin // generate delay line	
				#(delay_per_stg_fb/TIME_SCALE) clk_fb_d[istg+1] = clk_fb_d[istg];
			end
			always @(posedge clk_ref_d[istg] or negedge clk_ref_d[istg]) begin // generate delay line	
				#(delay_per_stg_ref/TIME_SCALE) clk_ref_d[istg+1] = clk_ref_d[istg];
			end
			always @(posedge phases_out_tmp[istg] or negedge phases_out_tmp[istg]) begin // generate delay line	
				#(DFF_CTQ_DELAY/TIME_SCALE) PHASES_OUT[istg] = phases_out_tmp[istg];
			end
			always @(posedge clk_ref_d[istg]) begin // generate phases
				phases_out_tmp[istg] = clk_fb_d[istg];
			end
		end
	endgenerate


	always @* begin 
		// coarse: single ended decoding
		case(DCO_EDGE_SEL)
			// second version: linear approximated
			5'b00001: clk_fb = DCO_RAW_PH[0];
			5'b00010: clk_fb = ~DCO_RAW_PH[1];
			5'b00100: clk_fb = DCO_RAW_PH[2];
			5'b01000: clk_fb = ~DCO_RAW_PH[3];
			5'b10000: clk_fb = DCO_RAW_PH[4];
			default:
				clk_fb = DCO_RAW_PH[0];
		endcase
	end



	always @* begin
		#(DFF_ST/TIME_SCALE) clk_fb_d[0] = clk_fb;
	end

	assign	clk_ref_d[0] = CLK_REF;

endmodule

`endif
