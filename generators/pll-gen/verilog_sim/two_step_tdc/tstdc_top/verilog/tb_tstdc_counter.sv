// testbench for tstdc_counter
`timescale 1ps/1ps

module tb_tstdc_counter();


	// Parameters
		// tstdc_counter
		parameter TDC_MAX = 18;	
		parameter TDC_COUNT_ACCUM_WIDTH = 12;	
		parameter TDC_NUM_PHASE_LATCH = 0;
		parameter TDC_NUM_RETIME_CYCLES = 3;
		parameter TDC_NUM_RETIME_DELAYS = 2;
		parameter TDC_NUM_COUNTER_DIVIDERS = 3;
		parameter DLTDC_NUM_PH = 10;
		// dltdc
		parameter DL_CCW_MAX_FB = 30;
		parameter DL_CCW_MAX_REF = 30;
		parameter DL_FCW_MAX_FB = 60;
		parameter DL_FCW_MAX_REF = 60;
		//parameter DL_CSTEP_FB = 0.9e-12; // coarse delay step per stage 
		parameter DL_CSTEP_FB = 0.2e-12; // coarse delay step per stage 
		parameter DL_FSTEP_FB = 0.3e-12; // fine delay step per stage 
		parameter DL_CSTEP_REF = 0.9e-12; // coarse delay step per stage 
		parameter DL_FSTEP_REF = 0.3e-12; // fine delay step per stage 
		parameter UNIT_DLBASE_FB = 7e-12; // unit base delay differce between two paths 
		parameter UNIT_DLBASE_REF = 7e-12; // unit base delay differce between two paths 

		parameter PER_FB = 1/2.4e9;
		parameter PER_REF = 10.000e-9;

		parameter DLTDC_PRE_DLY = PER_FB*5; 
		// analog core
		parameter NSTG=5;
		parameter NCC=254;
		parameter NFC=336; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
		parameter DCO_FBASE = 2.40e+09;	//scale
		parameter DCO_OFFSET = 0;
		parameter DCO_CCW_MAX = NCC;	//scale
		parameter DCO_CSTEP = 20e+06;	// ble_test 
		parameter DCO_FCW_MAX = NFC;	//scale
		parameter DCO_FSTEP = 200e+03;	// ble_test 
		parameter dco_center_freq=2.4e9;
		
	// Local Parameters
		// tstdc_counter
		localparam EMBTDC_WIDTH = 5;
		localparam DCO_NUM_PH = (TDC_MAX/2+1)/2; // 5 (nstage) 
		localparam DLTDC_WIDTH = 5;
		localparam TDC_WIDTH = EMBTDC_WIDTH + DLTDC_WIDTH;
		// dltdc
		localparam DL_CCW_WIDTH_FB = func_clog2(DL_CCW_MAX_FB);
		localparam DL_FCW_WIDTH_FB = func_clog2(DL_FCW_MAX_FB);
		localparam DL_CCW_WIDTH_REF = func_clog2(DL_CCW_MAX_REF);
		localparam DL_FCW_WIDTH_REF = func_clog2(DL_FCW_MAX_REF);
		// analog core
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
	// Ports
		// tstdc input
		logic 						clk_ref;
		logic 						clk_ref_d;
		logic 		[DCO_NUM_PH-1:0] 		sampled_ph_crs;	
		logic 		[DCO_NUM_PH-1:0] 		sampled_ph_raw;	
		logic 		[DLTDC_NUM_PH-1:0] 		sampled_ph_fine;	
		logic 						dco_outp;
		logic						rst;
		// tstdc output
		logic						clkref_retimed; 
		logic		[TDC_WIDTH-1:0] 		tdc_out;
		logic		[TDC_COUNT_ACCUM_WIDTH-1:0]	count_accum_out;
		logic						dco_clk_div4;
		logic		[DCO_NUM_PH-1:0] 		dltdc_edge_sel;	
		logic		[DCO_NUM_PH-1:0] 		dltdc_edge_sel_dum;	
		logic				 		dltdc_np_edge;	
		logic				 		dltdc_np_edge_dum;	
		// dltdc inputs
		logic		clk_fb;
		logic		clk_fb_dltdc_in;
		logic		clk_ref_dltdc_in;
		logic	[DL_CCW_WIDTH_FB-1: 0]		dl_ccw_fb;
		logic	[DL_FCW_WIDTH_FB-1: 0]		dl_fcw_fb;
		logic	[DL_CCW_WIDTH_REF-1: 0]		dl_ccw_ref;
		logic	[DL_FCW_WIDTH_REF-1: 0]		dl_fcw_ref;
		// analog_core input
		logic	[DCO_CCW_WIDTH-1:0]			dco_ccw_bin; //bin
		logic	[DCO_FCW_WIDTH-1:0]			dco_fcw_bin;
		logic	[DCO_FCW_WIDTH-1:0]			dco_fcw_bin_final;
	
		logic						dco_outm;
		logic						clk_div2;
		logic 	[DCO_NUM_PH-1:0]			phases_proc;
		logic 	[DCO_NUM_PH-1:0]			phases_proc_d;
		logic 	[DCO_NUM_PH-1:0]			phases_proc_d_d;
	// variables
		real max_ref_periods = 50;
		real TIME_SCALE=1e-12;
		real dco_rise;
		real time_diff; 

	// submodules		 
		tstdc_counter	#(
				.TDC_MAX			( TDC_MAX 			),	
				.TDC_COUNT_ACCUM_WIDTH		( TDC_COUNT_ACCUM_WIDTH 	),	
				.TDC_NUM_PHASE_LATCH		( TDC_NUM_PHASE_LATCH		),
				.TDC_NUM_RETIME_CYCLES		( TDC_NUM_RETIME_CYCLES		),
				.TDC_NUM_RETIME_DELAYS		( TDC_NUM_RETIME_DELAYS		),
				.TDC_NUM_COUNTER_DIVIDERS	( TDC_NUM_COUNTER_DIVIDERS	),
				.DLTDC_NUM_PH			( DLTDC_NUM_PH			))
			u_tstdc_counter	(
				.CLKREF_IN			( clk_ref		), 
				.SAMPLED_PH_CRS_IN		( sampled_ph_crs	), // from embedded TDC 
				.SAMPLED_PH_FINE_IN		( sampled_ph_fine	), // from dltdc 
				.DCO_OUTP			( dco_outp		),
				.RST				( rst			), 
				.CLKREF_RETIMED_OUT		( clkref_retimed	),
				.DCO_CLK_DIV4			( dco_clk_div4		), 
				.TDC_OUT			( tdc_out		), 
				.DLTDC_EDGE_SEL_OUT		( dltdc_edge_sel_dum	),
				.DLTDC_NP_EDGE			( dltdc_np_edge_dum	), 
				.COUNT_ACCUM_OUT		( count_accum_out	));

		dltdc_model	#(
				.UNIT_DLBASE_FB ( UNIT_DLBASE_FB),
				.UNIT_DLBASE_REF(UNIT_DLBASE_REF),
				.DL_CCW_MAX_FB	( DL_CCW_MAX_FB	),
				.DL_CSTEP_FB	( DL_CSTEP_FB	), // coarse delay step per stage 
				.DL_CCW_MAX_REF	( DL_CCW_MAX_REF),
				.DL_CSTEP_REF	( DL_CSTEP_REF	), // coarse delay step per stage 
				.DL_FCW_MAX_FB	( DL_FCW_MAX_FB	),
				.DL_FSTEP_FB	( DL_FSTEP_FB	), // fine delay step per stage 
				.DL_FCW_MAX_REF	( DL_FCW_MAX_REF),
				.DL_FSTEP_REF	( DL_FSTEP_REF	), // fine delay step per stage
				.DCO_NUM_PH	( DCO_NUM_PH	), 
				.DLTDC_NUM_PH	( DLTDC_NUM_PH	))
			u_dltdc_model	(
				//.DCO_RAW_PH	( phases_proc_d		),
				//.DCO_RAW_PH	( phases_proc_d_d	),
				//.DCO_EDGE_SEL	( dltdc_edge_sel	),
				.DL_CCW_IN_FB	( dl_ccw_fb		), 
				.DL_FCW_IN_FB	( dl_fcw_fb		),
				.DL_CCW_IN_REF	( dl_ccw_ref		), 
				.DL_FCW_IN_REF	( dl_fcw_ref		),
				.CLK_FB		( clk_fb_dltdc_in	),
				.CLK_REF	( clk_ref_dltdc_in	),	
				.PHASES_OUT	( sampled_ph_fine	));

		analog_core #(
				.DCO_CENTER_FREQ(dco_center_freq),
				.DCO_FBASE(DCO_FBASE),
				.DCO_OFFSET(DCO_OFFSET),
				.DCO_CCW_MAX(DCO_CCW_MAX),
				.DCO_CSTEP(DCO_CSTEP),
				.DCO_FCW_MAX(DCO_FCW_MAX),
				.DCO_FSTEP(DCO_FSTEP),
				.DCO_NUM_PHASES(DCO_NUM_PH))
			u_analog_core( 
				.DCO_CCW_IN(dco_ccw_bin), 
				.DCO_FCW_IN(dco_fcw_bin_final),
				.CLKREF(clk_ref),
				.CLK_DITHER(clk_div2),
				.DCO_OUTP(dco_outp),
				.DCO_OUTM(dco_outm),
				.RAW_PHASES(phases_proc),
				.SAMPLED_RAW_PHASES(sampled_ph_raw),
				.SAMPLED_PHASES_OUT(sampled_ph_crs));


		pre_dltdc u_pre_dltdc(
				.DCO_RAW_PH(phases_proc),
				.CLK_REF(clk_ref),
				.DCO_EDGE_SEL(dltdc_edge_sel),
				.CLK_REF_OUT(clk_ref_dltdc_in),
				.DLTDC_NP_EDGE(dltdc_np_edge),
				.RST(rst),
				.CLK_FB_OUT(clk_fb_dltdc_in));
		
	// edge_sel logics
	assign	dltdc_edge_sel[0] = ~(sampled_ph_raw[0]^sampled_ph_raw[1]);
	assign	dltdc_edge_sel[1] = ~(sampled_ph_raw[1]^sampled_ph_raw[2]);
	assign	dltdc_edge_sel[2] = ~(sampled_ph_raw[2]^sampled_ph_raw[3]);
	assign	dltdc_edge_sel[3] = ~(sampled_ph_raw[3]^sampled_ph_raw[4]);
	assign	dltdc_edge_sel[4] = ~(sampled_ph_raw[4]^sampled_ph_raw[0]);

	// np edge 
	always @* begin
		case(dltdc_edge_sel)
			5'b00001: dltdc_np_edge = sampled_ph_raw[0];	
			5'b00010: dltdc_np_edge = sampled_ph_raw[1];	
			5'b00100: dltdc_np_edge = sampled_ph_raw[2];	
			5'b01000: dltdc_np_edge = sampled_ph_raw[3];	
			5'b10000: dltdc_np_edge = sampled_ph_raw[4];
		endcase
	end	


	// stimulus
		//always begin // clk
		//	#(PER_FB/TIME_SCALE/2) clk_fb = ~clk_fb;	
		//end
		always begin // clk
			#(PER_REF/TIME_SCALE/2) clk_ref = ~clk_ref;
		end

		//// delay lines pre-dltdc	
		//always @(posedge clk_ref or negedge clk_ref) begin
		//	#(DLTDC_PRE_DLY/TIME_SCALE) clk_ref_d = clk_ref;
		//end

		//genvar iph;
		//generate
		//	for (iph=0; iph<DCO_NUM_PH; iph=iph+1) begin: GEN_PHASE
		//		always @(posedge phases_proc[iph] or negedge phases_proc[iph]) begin
		//			 phases_proc_d[iph] <= #(DLTDC_PRE_DLY/TIME_SCALE) phases_proc[iph];
		//		end
		//		assign phases_proc_d_d[iph] = dltdc_np_edge ? phases_proc_d[iph] : ~phases_proc_d[iph];
		//	end
		//endgenerate
		// pre-dltdc logics

		always@(posedge dco_outp) begin
			clk_div2 <= ~clk_div2;
			dco_rise = $realtime;
		end
	
		always@(posedge clk_ref) begin
			time_diff=($realtime - dco_rise);
		end

	// start sim
		initial
		begin
			clk_fb=1'b0;		
			clk_ref=1'b0;
			clk_div2=1'b0;	
			dl_ccw_fb=DL_CCW_MAX_FB-DLTDC_NUM_PH;	
			dl_fcw_fb=0;	
			dl_ccw_ref=DL_CCW_MAX_REF;	
			dl_fcw_ref=0;
			//dco_fcw_bin_final= DCO_FCW_MAX/2;
			//dco_ccw_bin= DCO_CCW_MAX/2;
			dco_fcw_bin_final= 0;
			dco_ccw_bin= 0;
	
			rst = 1'b0;
			#(PER_REF/TIME_SCALE) rst = 1'b1;
			#(4*PER_REF/TIME_SCALE) rst = 1'b0;
			
			$display("*** Running verilog simulation for dltdc");
	
			#(max_ref_periods*PER_REF/TIME_SCALE)
			$display("*** simulation ended");
			$finish;
		end	
endmodule
