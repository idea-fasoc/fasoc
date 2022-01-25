// two-step tdc decoder + dco clock counter
`ifndef __TDC_COUNTER__
`define __TDC_COUNTER__


//`timescale 1ps/1ps


module tstdc_counter(
	CLKREF_IN, 
	DCO_RAW_PH,
	pre_ls_ref_CC_bin,
	pre_ls_ref_FC_bin,
	post_ls_ref_CC_bin,
	post_ls_ref_FC_bin,
	pre_es_fb_CC_bin,
	pre_es_fb_FC_bin,
	post_es_fb_CC_bin,
	post_es_fb_FC_bin,
	CC_fb,
	FC_fb,
	CC_ref,
	FC_ref,
	RST,
	CLKREF_RETIMED_OUT,
	DCO_CLK_DIV4, 
	EMBTDC_BIN_OUT,
	DLTDC_BIN_OUT,
	dltdc_idx, // 053121
	EMBTDC_LUT,
	EMB_DLTDC_MAP_LUT,
	DLTDC_LUT,
	retime_lag, // test
	retime_edge_sel, // test
	pre_dltdc_in_fb_out, // test
	pre_dltdc_in_ref_out, // test
	embtdc_bin_tmp, // test
	pre_PH_fb_out, //test
	post_es_fb_out, //test
	smpl_dltdc_edge_fb_idx, // for calib
	smpl_dltdc_edge_sel_idx, // for calib
	cr_smpl_edge_sel, // for calib
	cr_raw_edge_sel, // for calib
	dltdc_out,
	embtdc_out,
	dltdc_np_edge,
	dltdc_edge_sel,	
	es_check, // edge_sel calib 04/14/21
	clk_ref_ls_out, // 041821 
	COUNT_ACCUM_OUT);

	// Functions
	`include "FUNCTIONS.v"

	// Parameters
	// pre-dltdc
	// pre latch edge sel path for ref 
@@		parameter pre_ls_ref_NSTG_CC_TUNE=@rM;  // 2
@@		parameter pre_ls_ref_NCC_TUNE 	=@rC; // 2
@@		parameter pre_ls_ref_NFC	=@rF; // 63
	localparam NUM_pre_ls_ref_CC = pre_ls_ref_NSTG_CC_TUNE*pre_ls_ref_NCC_TUNE; 
	localparam NUM_pre_ls_ref_FC = pre_ls_ref_NFC; 
	localparam pre_ls_ref_CC_WIDTH = func_clog2(NUM_pre_ls_ref_CC);
	localparam pre_ls_ref_FC_WIDTH = func_clog2(NUM_pre_ls_ref_FC);

	// post latch edge sel path for ref
	parameter post_ls_ref_NSTG_CC_TUNE=pre_ls_ref_NSTG_CC_TUNE;
	parameter post_ls_ref_NCC_TUNE	=pre_lse_ref_NCC_TUNE;
	parameter post_ls_ref_NFC	=pre_ls_ref_NFC;
	localparam NUM_post_ls_ref_CC = post_ls_ref_NSTG_CC_TUNE*post_ls_ref_NCC_TUNE; 
	localparam NUM_post_ls_ref_FC = post_ls_ref_NFC; 
	localparam post_ls_ref_CC_WIDTH = func_clog2(NUM_post_ls_ref_CC);
	localparam post_ls_ref_FC_WIDTH = func_clog2(NUM_post_ls_ref_FC);

	// pre edge sel path for fb
	parameter pre_es_fb_NSTG_CC_TUNE=pre_ls_ref_NSTG_CC_TUNE;
	parameter pre_es_fb_NCC_TUNE	=pre_ls_ref_NCC_TUNE;
	parameter pre_es_fb_NFC		=pre_ls_ref_NFC;
	localparam NUM_pre_es_fb_CC = pre_es_fb_NSTG_CC_TUNE*pre_es_fb_NCC_TUNE; 
	localparam NUM_pre_es_fb_FC = pre_es_fb_NFC; 
	localparam pre_es_fb_CC_WIDTH = func_clog2(NUM_pre_es_fb_CC);
	localparam pre_es_fb_FC_WIDTH = func_clog2(NUM_pre_es_fb_FC);

	// post edge sel path for fb
	parameter post_es_fb_NSTG_CC_TUNE=pre_ls_ref_NSTG_CC_TUNE;
	parameter post_es_fb_NCC_TUNE	 =pre_ls_ref_NCC_TUNE;
	parameter post_es_fb_NFC	 =pre_ls_ref_NFC;
	localparam NUM_post_es_fb_CC = post_es_fb_NSTG_CC_TUNE*post_es_fb_NCC_TUNE; 
	localparam NUM_post_es_fb_FC = post_es_fb_NFC; 
	localparam post_es_fb_CC_WIDTH = func_clog2(NUM_post_es_fb_CC);
	localparam post_es_fb_FC_WIDTH = func_clog2(NUM_post_es_fb_FC);

	parameter NDECAP = 26; 
	parameter fm_NCC = 2; // final mux NCC

	// version 2
@@		parameter DLTDC_NUM_PH = @dM; // 10 
@@		parameter dltdc_NFC_fb = @ff; // 4
@@		parameter dltdc_NFC_ref = @fr; // 4
@@		parameter dltdc_NDRV_fb = @df; // 2
@@		parameter dltdc_NDRV_ref = @dr; // 2
@@		parameter dltdc_NCC_fb = @cf; // 2
@@		parameter dltdc_NCC_ref = @cr; // 2
	parameter DCO_NUM_PH = 5;
	// DFF char 
	parameter dff_su_time = 20e-12;

	// pre-dltdc delay lines
@@		parameter pre_NSTG_ref_ls = @pl; // 18
@@		parameter pre_NSTG_ref = @pr; // 30 
	//parameter pre_NSTG_fb = 8; // edge arrives @ 17*1 = 17ps
@@		parameter pre_NSTG_fb = @pf; // 12 
@@		parameter ppath_NSTG = @pp; // 3 
	//parameter ppath_NSTG = 4; // ppath (ppath_NSTG)*delay
	 
	parameter fmux_delay = 17e-12; 

	// dltdc delay lines
	parameter dltdc_fb_delay = 26e-12;
	parameter dltdc_ref_delay = 17e-12;

	// embtdc
	parameter TDC_COUNT_ACCUM_WIDTH = 15;	
	parameter TDC_NUM_PHASE_LATCH = 2;
	//parameter TDC_NUM_RETIME_CYCLES = 3;
	parameter TDC_NUM_RETIME_CYCLES = 5;
	parameter TDC_NUM_RETIME_DELAYS = 2;
	parameter TDC_NUM_COUNTER_DIVIDERS = 3;

	// Local Parameters
		localparam EMBTDC_WIDTH = 5;
		localparam DLTDC_WIDTH = 3;
		localparam TDC_WIDTH = EMBTDC_WIDTH + DLTDC_WIDTH;

	// Ports
		input 						CLKREF_IN;
		input	[DCO_NUM_PH-1:0]			DCO_RAW_PH;

		// pre-dltdc
		input	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin;
		input	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin;
		input	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin;
		input	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin;
		input	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin;
		input	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin;
		input	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin;
		input	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin;
	
		// dltdc
		input 	[dltdc_NFC_fb*DLTDC_NUM_PH-1:0] 	FC_fb; 
		input 	[dltdc_NCC_fb*DLTDC_NUM_PH-1:0] 	CC_fb; 
		input 	[dltdc_NFC_ref*DLTDC_NUM_PH-1:0] 	FC_ref; 
		input 	[dltdc_NCC_ref*DLTDC_NUM_PH-1:0] 	CC_ref; 
		input logic					RST;
		input logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMBTDC_LUT;  
		input logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMB_DLTDC_MAP_LUT;  
		input logic [49:0][TDC_WIDTH-1:0] 		DLTDC_LUT; // going to use only first 10 for now 

		// outputs
		output  					CLKREF_RETIMED_OUT; 
		output logic 	[TDC_WIDTH-1:0] 		EMBTDC_BIN_OUT;
		output logic 	[TDC_WIDTH-1:0] 		DLTDC_BIN_OUT;
		output logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]	COUNT_ACCUM_OUT;
		output						DCO_CLK_DIV4;	
		output 						retime_edge_sel;
		output 						retime_lag;
		output	[DCO_NUM_PH-1:0]			embtdc_out;
		output						dltdc_np_edge;
		output	[DCO_NUM_PH-1:0]			dltdc_edge_sel;
		output						pre_dltdc_in_fb_out;
		output						pre_dltdc_in_ref_out;
		output	[DCO_NUM_PH-1:0]			pre_PH_fb_out; // test purpose 
		output	[DCO_NUM_PH-1:0]			es_check; // test purpose 
		output						post_es_fb_out; // test purpose 
		// outputs for calibration
		output logic	[2:0]				smpl_dltdc_edge_fb_idx;
		output logic	[2:0]				smpl_dltdc_edge_sel_idx;
		output logic	[DCO_NUM_PH-1:0]		cr_smpl_edge_sel;
		output logic	[DCO_NUM_PH-1:0]		cr_raw_edge_sel;
		output logic	[DLTDC_NUM_PH-1:0]		dltdc_out; // minimum condition (thermal)
		output 	[TDC_WIDTH-1:0] 			embtdc_bin_tmp; //test
		output logic					clk_ref_ls_out; // 041821
		output logic [TDC_WIDTH-1:0]			dltdc_idx; // 053121
	// Internal Signals
		logic [TDC_WIDTH-1:0]				dltdc_idx_tmp; // 060121
		logic 	[TDC_WIDTH-1:0] 			dltdc_bin_tmp;
		logic						dco_outp;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_curr;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_prev;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_curr;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_prev;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_gray;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_binary;
		logic 						dco_gray_accum_sel;
		logic						clkref_retimed;
		logic	[DCO_NUM_PH-1:0]			dltdc_raw_edge_sel;
		logic	[2:0]					dltdc_edge_sel_idx;
		logic	[2:0]					dltdc_edge_fb_idx;

		// delay control signals for pre-dltdc DTCs: Thermal codes
		logic 	[NUM_pre_ls_ref_CC-1:0] 		pre_ls_ref_CC; 
		logic 	[NUM_pre_ls_ref_FC-1:0] 		pre_ls_ref_FC; 
		logic 	[NUM_post_ls_ref_CC-1:0] 		post_ls_ref_CC; 
		logic 	[NUM_post_ls_ref_FC-1:0] 		post_ls_ref_FC; 
		logic 	[DCO_NUM_PH-1:0][NUM_pre_es_fb_CC-1:0] 	pre_es_fb_CC; 
		logic 	[DCO_NUM_PH-1:0][NUM_pre_es_fb_FC-1:0] 	pre_es_fb_FC; 
		logic 	[NUM_post_es_fb_CC-1:0] 		post_es_fb_CC; 
		logic 	[NUM_post_es_fb_FC-1:0] 		post_es_fb_FC;

		logic						CLKREF_IN_buf0;
		logic						CLKREF_IN_buf;
		logic						CLKREF_IN_buf_sync;

	// Variables 
		integer ii;

@@		@b4 clkref_buf1 (.Y(CLKREF_IN_buf0), .A(CLKREF_IN)); // 050921 
@@		@b8 clkref_buf2 (.Y(CLKREF_IN_buf), .A(CLKREF_IN_buf0)); // 050921 

@@		@b2 clkref_buf_3 (.Y(CLKREF_IN_buf_sync),.A(CLKREF_IN_buf)); // 053121	
@@		@B2 clkref_buf_4 (.Y(CLKREF_IN_buf_sync),.A(CLKREF_IN_buf));

	tstdc_encoder u_tstdc_encoder(
		.DCO_OUTP		(dco_outp		), //-km
		.RST			(RST			),
		.DCO_EDGE_SEL		(dltdc_edge_sel		),
		.NP_EDGE		(dltdc_np_edge		),
		.DLTDC_IN		(dltdc_out		), 
		.EMBTDC_OUT		(embtdc_bin_tmp		), 
		.DLTDC_OUT		(dltdc_bin_tmp		), 
		.EMBTDC_LUT		(EMBTDC_LUT		),// LUT test 
		.EMB_DLTDC_MAP_LUT	(EMB_DLTDC_MAP_LUT	),// LUT test 
		.DLTDC_LUT		(DLTDC_LUT		),// LUT test 
		.dltdc_lut_idx		(dltdc_idx_tmp		), // 053121
		.RETIME_EDGE_SEL_OUT	(retime_edge_sel	),
		.RETIME_LAG_OUT		(retime_lag		));

	// bin => therm for the pre-dltdc control words
	// do we need to latch the termal word?
	bin2therm #(.NBIN(pre_ls_ref_CC_WIDTH),.NTHERM(NUM_pre_ls_ref_CC)) b2t_pre_ls_ref_CC (.binin(pre_ls_ref_CC_bin), .thermout(pre_ls_ref_CC));
	bin2therm #(.NBIN(pre_ls_ref_FC_WIDTH),.NTHERM(NUM_pre_ls_ref_FC)) b2t_pre_ls_ref_FC (.binin(pre_ls_ref_FC_bin), .thermout(pre_ls_ref_FC));
	bin2therm #(.NBIN(post_ls_ref_CC_WIDTH),.NTHERM(NUM_post_ls_ref_CC)) b2t_post_ls_ref_CC (.binin(post_ls_ref_CC_bin), .thermout(post_ls_ref_CC));
	bin2therm #(.NBIN(post_ls_ref_FC_WIDTH),.NTHERM(NUM_post_ls_ref_FC)) b2t_post_ls_ref_FC (.binin(post_ls_ref_FC_bin), .thermout(post_ls_ref_FC));

	bin2therm #(.NBIN(pre_es_fb_CC_WIDTH),.NTHERM(NUM_pre_es_fb_CC)) b2t_pre_es_fb_CC0 (.binin(pre_es_fb_CC_bin[0]), .thermout(pre_es_fb_CC[0]));
	bin2therm #(.NBIN(pre_es_fb_FC_WIDTH),.NTHERM(NUM_pre_es_fb_FC)) b2t_pre_es_fb_FC0 (.binin(pre_es_fb_FC_bin[0]), .thermout(pre_es_fb_FC[0]));
	bin2therm #(.NBIN(pre_es_fb_CC_WIDTH),.NTHERM(NUM_pre_es_fb_CC)) b2t_pre_es_fb_CC1 (.binin(pre_es_fb_CC_bin[1]), .thermout(pre_es_fb_CC[1]));
	bin2therm #(.NBIN(pre_es_fb_FC_WIDTH),.NTHERM(NUM_pre_es_fb_FC)) b2t_pre_es_fb_FC1 (.binin(pre_es_fb_FC_bin[1]), .thermout(pre_es_fb_FC[1]));
	bin2therm #(.NBIN(pre_es_fb_CC_WIDTH),.NTHERM(NUM_pre_es_fb_CC)) b2t_pre_es_fb_CC2 (.binin(pre_es_fb_CC_bin[2]), .thermout(pre_es_fb_CC[2]));
	bin2therm #(.NBIN(pre_es_fb_FC_WIDTH),.NTHERM(NUM_pre_es_fb_FC)) b2t_pre_es_fb_FC2 (.binin(pre_es_fb_FC_bin[2]), .thermout(pre_es_fb_FC[2]));
	bin2therm #(.NBIN(pre_es_fb_CC_WIDTH),.NTHERM(NUM_pre_es_fb_CC)) b2t_pre_es_fb_CC3 (.binin(pre_es_fb_CC_bin[3]), .thermout(pre_es_fb_CC[3]));
	bin2therm #(.NBIN(pre_es_fb_FC_WIDTH),.NTHERM(NUM_pre_es_fb_FC)) b2t_pre_es_fb_FC3 (.binin(pre_es_fb_FC_bin[3]), .thermout(pre_es_fb_FC[3]));
	bin2therm #(.NBIN(pre_es_fb_CC_WIDTH),.NTHERM(NUM_pre_es_fb_CC)) b2t_pre_es_fb_CC4 (.binin(pre_es_fb_CC_bin[4]), .thermout(pre_es_fb_CC[4]));
	bin2therm #(.NBIN(pre_es_fb_FC_WIDTH),.NTHERM(NUM_pre_es_fb_FC)) b2t_pre_es_fb_FC4 (.binin(pre_es_fb_FC_bin[4]), .thermout(pre_es_fb_FC[4]));

	bin2therm #(.NBIN(post_es_fb_CC_WIDTH),.NTHERM(NUM_post_es_fb_CC)) b2t_post_es_fb_CC (.binin(post_es_fb_CC_bin), .thermout(post_es_fb_CC));
	bin2therm #(.NBIN(post_es_fb_FC_WIDTH),.NTHERM(NUM_post_es_fb_FC)) b2t_post_es_fb_FC (.binin(post_es_fb_FC_bin), .thermout(post_es_fb_FC));

	dltdc_v3 u_dltdc_v3 (
			.clkref_retimed (clkref_retimed		),
			.tdc_out	(dltdc_out		),
			.DCO_RAW_PH	(DCO_RAW_PH		),
			.pre_ls_ref_CC	(pre_ls_ref_CC		),  // <04/05/2021 - using lpdtc_v1
			.pre_ls_ref_FC	(pre_ls_ref_FC		), 
			.post_ls_ref_CC	(post_ls_ref_CC		), 
			.post_ls_ref_FC	(post_ls_ref_FC		), 
			.pre_es_fb_CC	(pre_es_fb_CC		), 
			.pre_es_fb_FC	(pre_es_fb_FC		), 
			.post_es_fb_CC	(post_es_fb_CC		), 
			.post_es_fb_FC	(post_es_fb_FC		),
			.CC_fb		(CC_fb			),
			.FC_fb		(FC_fb			),
			.CC_ref		(CC_ref			),
			.FC_ref		(FC_ref			),
			.CLK_REF	(CLKREF_IN_buf		), // 053121
			.smpl_edge_sel_out(dltdc_edge_sel	),
			.edge_sel	(dltdc_raw_edge_sel	),
			.edge_sel_idx	(dltdc_edge_sel_idx	),
			.pre_PH_fb_out	(pre_PH_fb_out		), //test
			.pre_dltdc_in_fb_out	(pre_dltdc_in_fb_out	), //test
			.pre_dltdc_in_ref_out	(pre_dltdc_in_ref_out	), //test
			.np_edge	(dltdc_np_edge		),
			.post_es_fb_out	(post_es_fb_out		), //test
			.embtdc_out_out (embtdc_out		),
			.edge_fb_idx	(dltdc_edge_fb_idx	),
			.es_check	(es_check		),
			.clk_ref_ls_out	(clk_ref_ls_out		)
			);


	// Encode the sampled phases in binary
	// latch encoder on retimed edge
	always @(posedge clkref_retimed or posedge RST) begin
		if (RST) begin
			smpl_dltdc_edge_fb_idx <= 0;
			smpl_dltdc_edge_sel_idx <= 0;
			cr_smpl_edge_sel <= 0;
			cr_raw_edge_sel <= 0;
			// tdc val
			EMBTDC_BIN_OUT <= 0;
			DLTDC_BIN_OUT <= 0; 
			// count val
			clkref_accum_curr <= 0;
			clkref_accum_prev <= 0;
			dco_gray_accum_sel <= 0;
		end else begin
			smpl_dltdc_edge_fb_idx <= dltdc_edge_fb_idx;
			smpl_dltdc_edge_sel_idx <= dltdc_edge_sel_idx;
			cr_smpl_edge_sel <= dltdc_edge_sel;
			cr_raw_edge_sel <= dltdc_raw_edge_sel;
			// tdc val
			EMBTDC_BIN_OUT <= embtdc_bin_tmp;
			DLTDC_BIN_OUT <= dltdc_bin_tmp;
			// count val
			clkref_accum_curr <= dco_accum_curr;
			clkref_accum_prev <= dco_accum_prev;
			dco_gray_accum_sel <= retime_lag;
			dltdc_idx <= dltdc_idx_tmp;
		end	
	end


	always @(posedge dco_outp or posedge RST) begin
		if (RST) begin
			dco_accum_curr <= 0;
			dco_accum_prev <= 0;
		end
		else begin
			dco_accum_curr <= dco_accum_curr + 1;
			dco_accum_prev <= dco_accum_curr;
		end
	end	

	// combinational
	assign dco_outp = DCO_RAW_PH[0];
	assign DCO_CLK_DIV4 = dco_accum_curr[1];

	// convert back to binary
	assign	clkref_accum_binary = dco_gray_accum_sel ? clkref_accum_prev : clkref_accum_curr;

	// assign the output
	assign	COUNT_ACCUM_OUT = clkref_accum_binary;

	assign	CLKREF_RETIMED_OUT = clkref_retimed;

	// Retime CLKREF
 		// Instantiate the retime synchronizer
		clkref_sync #(
				.TDC_NUM_RETIME_CYCLES(TDC_NUM_RETIME_CYCLES),
				.TDC_NUM_RETIME_DELAYS(TDC_NUM_RETIME_DELAYS))
			u_clkref_sync(
				.CLKREF_IN(CLKREF_IN_buf_sync), // 053121
				.DCO_OUTP(dco_outp),
				.RETIME_EDGE_SEL_IN(retime_edge_sel),
				.CLKREF_RETIMED_OUT(clkref_retimed));



	// decap cells
	generate 
		genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<NDECAP ; i=i+1)
		begin:decap 
		       DCDC_CAP_UNIT unit ( );
		end
	endgenerate


endmodule

module clkref_sync(
	CLKREF_IN,
	DCO_OUTP,
	RETIME_EDGE_SEL_IN,
	CLKREF_RETIMED_OUT);

	// Parameters
		parameter TDC_NUM_RETIME_CYCLES = 5;
		parameter TDC_NUM_RETIME_DELAYS = 2;

	// Ports
		input			CLKREF_IN;
		input			DCO_OUTP;		
		input			RETIME_EDGE_SEL_IN;

		output reg 		CLKREF_RETIMED_OUT;


	// Interconnect
		reg 	[TDC_NUM_RETIME_CYCLES-1:0]		retime_posedge_path;
		reg 	[TDC_NUM_RETIME_CYCLES-1:0]		retime_negedge_path;
		reg 									retime_negedge_start;
		wire 									retime_sel_edge_mux;


		reg 	[TDC_NUM_RETIME_DELAYS-1:0]		retime_delays;


	// Variables
		integer ii;


	// Synchronization of CLKREF with DCO_OUTP

 		// positive edge path 

			always @(posedge DCO_OUTP) begin
				// posedge path	
				retime_posedge_path[0] <= CLKREF_IN;
				for(ii=1;ii<TDC_NUM_RETIME_CYCLES;ii=ii+1) begin
					retime_posedge_path[ii] <= retime_posedge_path[ii-1];
 				end
				// negedge path
				retime_negedge_path[0] <= retime_negedge_start;
				for(ii=1;ii<TDC_NUM_RETIME_CYCLES;ii=ii+1) begin
					retime_negedge_path[ii] <= retime_negedge_path[ii-1];
				end
				// retime delay
				retime_delays[0] <= retime_sel_edge_mux;
				for(ii=1;ii<TDC_NUM_RETIME_DELAYS;ii=ii+1) begin
				
					retime_delays[ii] <= retime_delays[ii-1];
				end
				CLKREF_RETIMED_OUT <= retime_delays[TDC_NUM_RETIME_DELAYS-1];
			end	

		// negative edge path start

			always @(negedge DCO_OUTP) begin
				retime_negedge_start <= CLKREF_IN;
			end



		// retimne CLKREF
			
			// mux the negative and positve paths 
			assign retime_sel_edge_mux = RETIME_EDGE_SEL_IN ? 
				retime_posedge_path[TDC_NUM_RETIME_CYCLES-1] :
				retime_negedge_path[TDC_NUM_RETIME_CYCLES-1];


endmodule

// 100% combinational
module tstdc_encoder (
	DCO_OUTP, //-km
	RST,
	DCO_EDGE_SEL,
	NP_EDGE,
	DLTDC_IN, 
	EMBTDC_OUT, 
	DLTDC_OUT, 
	EMBTDC_LUT,
	EMB_DLTDC_MAP_LUT,
	DLTDC_LUT,
	dltdc_lut_idx,
	RETIME_EDGE_SEL_OUT,
	RETIME_LAG_OUT);

	// Functions

	// Parameters
		parameter TDC_CRS_MAX = 10;
		parameter TDC_FINE_MAX = 10;
		parameter TDC_NUM_PHASE_LATCH = 2; 
		parameter DLTDC_NUM_PH = 10;
		parameter EMBTDC_WIDTH = 5;
		parameter DLTDC_WIDTH = 3;

	// Local Paramters
		localparam DCO_NUM_PH = 5;
	//	localparam EMBTDC_WIDTH = func_clog2(TDC_CRS_MAX);
	//	localparam DLTDC_WIDTH = func_clog2(TDC_FINE_MAX);
		localparam TDC_WIDTH = EMBTDC_WIDTH + DLTDC_WIDTH;

	// Ports
		input				DCO_OUTP;
		input				RST;
		input 	[DCO_NUM_PH-1:0] 	DCO_EDGE_SEL; 
		input				NP_EDGE; 
		input 	[DLTDC_NUM_PH-1:0] 	DLTDC_IN;  
		input reg [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] EMBTDC_LUT;  
		input logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMB_DLTDC_MAP_LUT;  
		input reg [49:0][TDC_WIDTH-1:0] DLTDC_LUT;  
	
		output reg [TDC_WIDTH-1:0] 	EMBTDC_OUT;  
		output reg [TDC_WIDTH-1:0] 	DLTDC_OUT;  
		output reg 			RETIME_EDGE_SEL_OUT;
		output reg 			RETIME_LAG_OUT;
		output reg [TDC_WIDTH-1:0]	dltdc_lut_idx; // 053121
	// Internal Signals
		reg [(TDC_NUM_PHASE_LATCH-1)*DCO_NUM_PH-1:0]	sampled_phases_latch;  //-km
		reg [DCO_NUM_PH-1:0]				sampled_phases_curr;  //-km
		reg [TDC_WIDTH-1:0]		embtdc_bin_tmp;
		reg 				retime_edge_sel;
		reg 				retime_lag;
		reg [DCO_NUM_PH-1:0]		dltdc_edge_sel_tmp; // one-hot
		reg				dltdc_np_edge_tmp; // neg or posedge of DCO phase
		reg [TDC_WIDTH-1:0]		dltdc_bin_tmp;
		reg [TDC_WIDTH-1:0]		dltdc_idx;
		reg [TDC_WIDTH-1:0]		embtdc_idx;
		logic 	[DLTDC_NUM_PH-1:0] 	DLTDC_IN_rm_lsb;  

	// Variables
		integer ii;
	// Behavioral

		// Convert sampled phases to binary
			always @* begin 
				// coarse: single ended decoding
				case({DCO_EDGE_SEL})
					6'b00001: begin embtdc_idx <= 0;  retime_edge_sel <= 0; retime_lag <= 0;end  // LUT test
					6'b00100: begin embtdc_idx <= 1;  retime_edge_sel <= 0; retime_lag <= 0;end
					6'b10000: begin embtdc_idx <= 2;  retime_edge_sel <= 1; retime_lag <= 0;end
					6'b00010: begin embtdc_idx <= 3;  retime_edge_sel <= 1; retime_lag <= 0;end
					6'b01000: begin embtdc_idx <= 4;  retime_edge_sel <= 0; retime_lag <= 1;end
					default:
						begin 
						    embtdc_idx <= 0; retime_edge_sel <=0; retime_lag<=0;
						end
				endcase
			end
			always @* begin 
				// fine
				//casex(DLTDC_IN)
				casex(DLTDC_IN_rm_lsb) // 051921 removing LSB
					10'b??_????_???0: begin dltdc_idx <= 0; end // LUT test 
					10'b??_????_??01: begin dltdc_idx <= 1; end 
					10'b??_????_?011: begin dltdc_idx <= 2; end 
					10'b??_????_0111: begin dltdc_idx <= 3; end 
					10'b??_???0_1111: begin dltdc_idx <= 4; end 
					10'b??_??01_1111: begin dltdc_idx <= 5; end 
					10'b??_?011_1111: begin dltdc_idx <= 6; end 
					10'b??_0111_1111: begin dltdc_idx <= 7; end // this should be 
					10'b?0_1111_1111: begin dltdc_idx <= 8; end  
					10'b01_1111_1111: begin dltdc_idx <= 9; end 
					10'b11_1111_1111: begin dltdc_idx <= 10; end
					default: dltdc_idx <= 0; // LUT_test 
				endcase
			end

		// assign output signals
		assign dltdc_lut_idx =  EMB_DLTDC_MAP_LUT[embtdc_idx]+dltdc_idx;
		assign EMBTDC_OUT = EMBTDC_LUT[embtdc_idx];
		assign DLTDC_OUT = (EMB_DLTDC_MAP_LUT[embtdc_idx]+dltdc_idx < 49)? DLTDC_LUT[EMB_DLTDC_MAP_LUT[embtdc_idx]+dltdc_idx] : DLTDC_LUT[49]; // 1011 update
		assign RETIME_EDGE_SEL_OUT = retime_edge_sel;
		assign RETIME_LAG_OUT = retime_lag;

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
`endif
