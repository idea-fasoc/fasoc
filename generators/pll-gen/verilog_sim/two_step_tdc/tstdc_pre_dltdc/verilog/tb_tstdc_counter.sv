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
		// pre-dltdc 
		parameter pre_NDRV_fb = 1;
		parameter pre_NDRV_ref = 2;
		parameter pre_NCC_fb = 4;
		parameter pre_NCC_ref = 2;
		parameter npath_NDRV = 4;
		parameter ppath_NDRV = 2;
		parameter npath_NCC = 4;
		parameter ppath_NCC = 6;
		parameter pre_NSTG_ref = 6; // dltdc ref in @ 17*6 = 102ps
		parameter pre_NSTG_fb = 1; // edge arrives @ 17*1 = 17ps
		parameter npath_NSTG = 3; // npath
		parameter ppath_NSTG = 4;

		// dltdc delay line	
		parameter dl_NSTG = 10; 
		parameter dl_NFC_fb = 6;
		parameter dl_NFC_ref = 6;
		parameter dl_NDRV_fb = 1;
		parameter dl_NDRV_ref = 2;
		parameter dl_NCC_fb = 4;
		parameter dl_NCC_ref = 2;
		parameter DCO_NUM_PH = 5;

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
//		localparam DCO_NUM_PH = (TDC_MAX/2+1)/2; // 5 (nstage) 
		localparam DLTDC_WIDTH = 5;
		localparam TDC_WIDTH = EMBTDC_WIDTH + DLTDC_WIDTH;
		// pre-dltdc
		localparam PRE_CCW_MAX_FB = pre_NCC_fb*pre_NSTG_fb;
		localparam PRE_CCW_MAX_REF = pre_NCC_ref*pre_NSTG_ref;
		localparam NPATH_CCW_MAX = npath_NCC*(npath_NSTG); // first stage is not controllable
		localparam PPATH_CCW_MAX = ppath_NCC*(ppath_NSTG); // first stage is not controllable
		localparam PRE_CCW_WIDTH_FB  = func_clog2(PRE_CCW_MAX_FB); 
		localparam PRE_CCW_WIDTH_REF = func_clog2(PRE_CCW_MAX_REF);
		localparam NPATH_CCW_WIDTH   = func_clog2(NPATH_CCW_MAX); 
		localparam PPATH_CCW_WIDTH   = func_clog2(PPATH_CCW_MAX);
		// dltdc
		localparam DL_CCW_MAX_FB = dl_NCC_fb*dl_NSTG;
		localparam DL_FCW_MAX_FB = dl_NFC_fb*dl_NSTG;
		localparam DL_CCW_MAX_REF = dl_NCC_ref*dl_NSTG;
		localparam DL_FCW_MAX_REF = dl_NFC_ref*dl_NSTG;
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
		logic 		[dl_NSTG-1:0] 		sampled_ph_fine;	
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
			// thermal coded
		logic	[PRE_CCW_MAX_FB-1:0]		dl_pre_CC_fb;	
		logic	[PRE_CCW_MAX_REF-1:0]		dl_pre_CC_ref;	
		logic	[NPATH_CCW_MAX-1:0]		dl_npath_CC_fb;	
		logic	[PPATH_CCW_MAX-1:0]		dl_ppath_CC_fb;	
		logic	[DL_CCW_MAX_FB-1: 0]		dl_ccw_fb;
		logic	[DL_FCW_MAX_FB-1: 0]		dl_fcw_fb;
		logic	[DL_CCW_MAX_REF-1: 0]		dl_ccw_ref;
		logic	[DL_FCW_MAX_REF-1: 0]		dl_fcw_ref;
			// binary coded
		logic	[PRE_CCW_WIDTH_FB-1:0]		dl_pre_CC_fb_bin;	
		logic	[PRE_CCW_WIDTH_REF-1:0]		dl_pre_CC_ref_bin;	
		logic	[NPATH_CCW_WIDTH-1:0]		dl_npath_CC_fb_bin;	
		logic	[PPATH_CCW_WIDTH-1:0]		dl_ppath_CC_fb_bin;	
		logic	[DL_CCW_WIDTH_FB-1: 0]		dl_ccw_fb_bin;
		logic	[DL_FCW_WIDTH_FB-1: 0]		dl_fcw_fb_bin;
		logic	[DL_CCW_WIDTH_REF-1: 0]		dl_ccw_ref_bin;
		logic	[DL_FCW_WIDTH_REF-1: 0]		dl_fcw_ref_bin;
		logic					dum_clk;
		logic					dum_in;
		logic					dum_out;
		logic					tie_hi;
		logic					tie_lo;
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
		real max_ref_periods = 500;
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
				.DLTDC_NUM_PH			( dl_NSTG			))
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

	dltdc_v2 u_dltdc_v2 (
			.tdc_out	(sampled_ph_fine	),
			.DCO_RAW_PH	(phases_proc		),
			.pre_CC_fb	(dl_pre_CC_fb		),
			.pre_CC_ref	(dl_pre_CC_ref		),
			.npath_CC_fb	(dl_npath_CC_fb		),
			.ppath_CC_fb	(dl_ppath_CC_fb		),
			.CC_fb		(dl_ccw_fb		),
			.FC_fb		(dl_fcw_fb		),
			.CC_ref		(dl_ccw_ref		),
			.FC_ref		(dl_fcw_ref		),
			.CLK_REF	(clk_ref		),
			.RST		(rst			),
			.clk		(dum_clk		),
			.dum_in		(dum_in			),
			.dum_out	(dum_out		));


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

	bin2therm #(.NBIN(PRE_CCW_WIDTH_FB),.NTHERM(PRE_CCW_MAX_FB)) decPREfb 		(.binin(dl_pre_CC_fb_bin 	), .thermout(dl_pre_CC_fb));
	bin2therm #(.NBIN(PRE_CCW_WIDTH_REF),.NTHERM(PRE_CCW_MAX_REF)) decPREref	(.binin(dl_pre_CC_ref_bin	), .thermout(dl_pre_CC_ref));	
	bin2therm #(.NBIN(NPATH_CCW_WIDTH  ),.NTHERM(NPATH_CCW_MAX  )) decPREnp 	(.binin(dl_npath_CC_fb_bin	), .thermout(dl_npath_CC_fb));	
	bin2therm #(.NBIN(PPATH_CCW_WIDTH  ),.NTHERM(PPATH_CCW_MAX  )) decPREpp 	(.binin(dl_ppath_CC_fb_bin	), .thermout(dl_ppath_CC_fb));	
	bin2therm #(.NBIN(DL_CCW_WIDTH_FB  ),.NTHERM(DL_CCW_MAX_FB  )) decCCfb 		(.binin(dl_ccw_fb_bin		), .thermout(dl_ccw_fb));		
	bin2therm #(.NBIN(DL_FCW_WIDTH_FB  ),.NTHERM(DL_FCW_MAX_FB  )) decFCfb 		(.binin(dl_fcw_fb_bin		), .thermout(dl_fcw_fb));		
	bin2therm #(.NBIN(DL_CCW_WIDTH_REF ),.NTHERM(DL_CCW_MAX_REF )) decCCref 	(.binin(dl_ccw_ref_bin		), .thermout(dl_ccw_ref));		
	bin2therm #(.NBIN(DL_FCW_WIDTH_REF ),.NTHERM(DL_FCW_MAX_REF )) decFCref 	(.binin(dl_fcw_ref_bin		), .thermout(dl_fcw_ref));		

	// stimulus
		always begin // clk
			#(PER_REF/TIME_SCALE/2) clk_ref = ~clk_ref;
		end

		always@(posedge dco_outp) begin
			clk_div2 <= ~clk_div2;
	//		dco_rise = $realtime;
		end

	// ----------------------------------------------
	// time difference record for sim
	always @(posedge phases_proc[0] or negedge phases_proc[0] or posedge phases_proc[1] or negedge phases_proc[1] or posedge phases_proc[2] or negedge phases_proc[2] or posedge phases_proc[3] or negedge phases_proc[3] or posedge phases_proc[4] or negedge phases_proc[4] ) begin
		dco_rise = $realtime;
	end
	
	always @(posedge clk_ref) begin
		time_diff=($realtime - dco_rise);
	end
	// start sim
		initial
		begin
			clk_ref=1'b0;
			clk_div2=1'b0;
			dl_pre_CC_fb_bin = PRE_CCW_MAX_FB;	
			dl_pre_CC_ref_bin = PRE_CCW_MAX_REF;	
			dl_npath_CC_fb_bin = NPATH_CCW_MAX;
			dl_ppath_CC_fb_bin = PPATH_CCW_MAX;
			dl_ccw_fb_bin=DL_CCW_MAX_FB-dl_NSTG;	
			dl_fcw_fb_bin=0;	
			dl_ccw_ref_bin=DL_CCW_MAX_REF;	
			dl_fcw_ref_bin=0;
			//dco_fcw_bin_final= DCO_FCW_MAX/2;
			//dco_ccw_bin= DCO_CCW_MAX/2;
			dco_fcw_bin_final= 0;
			dco_ccw_bin= 0;
	
			rst = 1'b0;
			#(PER_REF/TIME_SCALE) rst = 1'b1;
			#(2*PER_REF/TIME_SCALE) rst = 1'b0;
			
			$display("*** Running verilog simulation for dltdc");
	
			#(max_ref_periods*PER_REF/TIME_SCALE)
			$display("*** simulation ended");
			$finish;
		end	
endmodule

module bin2therm (binin, thermout);
	parameter NBIN = 4;
	parameter NTHERM = 16;
	input [NBIN-1:0] binin;
	output [NTHERM-1:0] thermout;

	generate
		genvar i;
		for(i=0; i<=NTHERM-1; i=i+1) begin: thermloop
			assign thermout[i] = (binin > i) ? 1: 0;
		end
	endgenerate

endmodule

module therm2bin (thermin, binout);
	parameter NBIN = 4;
	parameter NTHERM = 16;
	input [NTHERM-1:0] thermin;
	output logic [NBIN-1:0] binout;
	logic [NBIN-1:0] bin1;
	
	integer i;

	always @(thermin) begin
		bin1 = 0;
		for (i=0; i<=NTHERM-1; i=i+1) begin
			if(thermin[i] == 1'b1) begin
				bin1 = i;
			end
		end
	end

	always @(bin1) begin
		binout = bin1;
	end

endmodule

