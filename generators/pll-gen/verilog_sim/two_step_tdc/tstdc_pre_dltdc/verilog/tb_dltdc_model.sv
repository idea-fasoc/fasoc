// TB_DLTDC
`timescale 1ps/1ps

module tb_dltdc_v2 ();
	
	// parameters
	parameter PER_FB = 1e-9;
	parameter PER_REF = 1.001e-9;

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
	parameter DLTDC_NUM_PH = 3;

	// Local Parameters
	localparam DL_CCW_WIDTH_FB = func_clog2(DL_CCW_MAX_FB);
	localparam DL_FCW_WIDTH_FB = func_clog2(DL_FCW_MAX_FB);
	localparam DL_CCW_WIDTH_REF = func_clog2(DL_CCW_MAX_REF);
	localparam DL_FCW_WIDTH_REF = func_clog2(DL_FCW_MAX_REF);

	// regs
	logic		clk_fb;
	logic 		clk_ref;
	logic	[DL_CCW_WIDTH_FB-1: 0]		dl_ccw_fb;
	logic	[DL_FCW_WIDTH_FB-1: 0]		dl_fcw_fb;
	logic	[DL_CCW_WIDTH_REF-1: 0]		dl_ccw_ref;
	logic	[DL_FCW_WIDTH_REF-1: 0]		dl_fcw_ref;

	// wires
	logic [DLTDC_NUM_PH-1:0]		dltdc_out;

	// real
	real max_ref_periods = 150;
	real TIME_SCALE=1e-12;
	// submodules
	dltdc_v2 u_dltdc_v2 (
			.tdc_out	(dltdc_out		),
			.DCO_RAW_PH	(dltdc_DCO_RAW_PH	),
			.pre_CC_fb	(dltdc_pre_CC_fb	),
			.pre_CC_ref	(dltdc_pre_CC_ref	),
			.npath_CC_fb	(dltdc_npath_CC_fb	),
			.npath_CC_ref	(dltdc_npath_CC_ref	),
			.CC_fb		(dltdc_CC_fb		),
			.FC_fb		(dltdc_FC_fb		),
			.CC_ref		(dltdc_CC_ref		),
			.FC_ref		(dltdc_FC_ref		),
			.CLK_REF	(dltdc_CLK_REF		),
			.RST		(dltdc_RST		),
			.clk		(dltdc_clk		),
			.dum_in		(dltdc_dum_in		),
			.dum_out	(dltdc_dum_out		));

	// stimulus
	always begin // clk
		#(PER_FB/TIME_SCALE/2) clk_fb = ~clk_fb;	
	end
	always begin // clk
		#(PER_REF/TIME_SCALE/2) clk_ref = ~clk_ref;
	end

	// start sim
	initial
	begin
		clk_fb=1'b0;		
		clk_ref=1'b0;	
		dl_ccw_fb=DL_CCW_MAX_FB-DLTDC_NUM_PH;	
		dl_fcw_fb=0;	
		dl_ccw_ref=DL_CCW_MAX_REF;	
		dl_fcw_ref=0;

		
		$display("*** Running verilog simulation for dltdc");

		#(max_ref_periods*PER_REF/TIME_SCALE)
		$display("*** simulation ended");
		$finish;
	end	
endmodule	
