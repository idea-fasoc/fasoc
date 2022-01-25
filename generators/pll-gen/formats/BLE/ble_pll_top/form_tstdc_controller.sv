// two-step tdc decoder + dco clock counter
//`timescale 1ps/1ps

module tstdc_controller(
	CLKREF_IN, 
	DCO_RAW_PH,
	CS_TSTDC_OV,   // v 053121
	cs_tstdc_user, // 
	cs_tstdc, // ^
	// pre-dltdc
	pre_ls_ref_CC_bin_user,
	pre_ls_ref_FC_bin_user,
	post_ls_ref_CC_bin_user,
	post_ls_ref_FC_bin_user,
	pre_es_fb_CC_bin_user,
	pre_es_fb_FC_bin_user,
	post_es_fb_CC_bin_user,
	post_es_fb_FC_bin_user,
	// dltdc
	CC_fb,
	FC_fb,
	CC_ref,
	FC_ref,
	// tstdc_counter
	RST, 
	CLKREF_RETIMED_OUT,
	DCO_CLK_DIV4, 
	EMBTDC_OUT,
	DLTDC_OUT,
	dltdc_idx, // 053121
	EMBTDC_LUT,
	EMB_DLTDC_MAP_LUT,
	DLTDC_LUT,
	TSTDC_CALIB,
	TSTDC_CALIB_DONE_RECIEVE,
	TSTDC_CALIB_DONE_OUT,
	TSTDC_CALIB_BROKE_OUT,
	TSTDC_CALIB_EDGE_IDX,
	TSTDC_CALIB_STATUS, // 052321: use this to indicate when to settle in OPERATE state
	dltdc_out_min_reg_export,
	// calibration overwrite values
	pre_ls_ref_CC_ov,
	pre_ls_ref_FC_ov,
	post_ls_ref_CC_ov,
	post_ls_ref_FC_ov,
	pre_es_fb_CC_ov,
	pre_es_fb_FC_ov,
	post_es_fb_CC_ov,
	post_es_fb_FC_ov,
	emb_dltdc_map_calib_ov,
	es_calib_cnt_val,
	dltdc_record_cnt_val,
	dltdc_lsb_int_cnt_val,
	dltdc_lsb_int_margin,
	// outputs
	pre_ls_ref_CC_bin_final, // v 050521
	pre_ls_ref_FC_bin_final,
	post_ls_ref_CC_bin_final,
	post_ls_ref_FC_bin_final,
	pre_es_fb_CC_bin_final,
	pre_es_fb_FC_bin_final,
	post_es_fb_CC_bin_final,
	post_es_fb_FC_bin_final, // ^ 050521
	dltdc_out_max_final_rm_lsb,
	COUNT_ACCUM_OUT);

	// Functions

	// Parameters
	parameter dff_delay = 180e-12;
	//parameter TIME_SCALE = 1e-12;
	parameter TIME_SCALE = 1e-12;
	// pre-dltdc 
	parameter pre_NDRV_fb = 1;
	parameter pre_NDRV_ref = 1;
	
	parameter npath_NDRV = 1;
	parameter ppath_NDRV = 1;
	
	parameter npath_NCC = 3;

	parameter fm_NCC = 2; // final mux NCC

	// pre-dltdc
	// pre latch edge sel path for ref 
@@		parameter pre_ls_ref_NSTG_CC_TUNE=@rM; 
@@		parameter pre_ls_ref_NCC_TUNE 	=@rC;
@@		parameter pre_ls_ref_NFC	=@rF;
	localparam NUM_pre_ls_ref_CC = pre_ls_ref_NSTG_CC_TUNE*pre_ls_ref_NCC_TUNE; 
	localparam NUM_pre_ls_ref_FC = pre_ls_ref_NFC; 
	localparam pre_ls_ref_CC_WIDTH = func_clog2(NUM_pre_ls_ref_CC);
	localparam pre_ls_ref_FC_WIDTH = func_clog2(NUM_pre_ls_ref_FC);

	// post latch edge sel path for ref
	parameter post_ls_ref_NSTG_CC_TUNE=pre_ls_ref_NSTG_CC_TUNE;
	parameter post_ls_ref_NCC_TUNE	  =pre_ls_ref_NCC_TUNE;
	parameter post_ls_ref_NFC	  =pre_ls_ref_NFC;
	localparam NUM_post_ls_ref_CC = post_ls_ref_NSTG_CC_TUNE*post_ls_ref_NCC_TUNE; 
	localparam NUM_post_ls_ref_FC = post_ls_ref_NFC; 
	localparam post_ls_ref_CC_WIDTH = func_clog2(NUM_post_ls_ref_CC);
	localparam post_ls_ref_FC_WIDTH = func_clog2(NUM_post_ls_ref_FC);

	// pre edge sel path for fb
	parameter pre_es_fb_NSTG_CC_TUNE=pre_ls_ref_NSTG_CC_TUNE;
	parameter pre_es_fb_NCC_TUNE	=pre_ls_ref_NCC_TUNE;
	parameter pre_es_fb_NFC		=pre_ls_ref_NFC;
	localparam NUM_pre_es_fb_CC = pre_es_fb_NSTG_CC_TUNE*pre_es_fb_NCC_TUNE; // for 1 stage 
	localparam NUM_pre_es_fb_FC = pre_es_fb_NFC; // for 1 stage 
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


	// version 2
@@		parameter DLTDC_NUM_PH = @dM; 
@@		parameter dltdc_NFC_fb = @ff;
@@		parameter dltdc_NFC_ref = @rf;
@@		parameter dltdc_NDRV_fb = @fd;
@@		parameter dltdc_NDRV_ref = @rd;
@@		parameter dltdc_NCC_fb = @fc;
@@		parameter dltdc_NCC_ref = @rc;
@@		parameter DCO_NUM_PH = @nM;
	// DFF char 
	parameter dff_su_time = 20e-12;
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
	//parameter integer ACCUM_EXTRA_BITS = 9;
	parameter integer ACCUM_EXTRA_BITS = 8;
	parameter FCW_MAX = 100;
	localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
	localparam FCW_FRAC_WIDTH = 9; // ble_test
	localparam FCW_WIDTH = FCW_INT_WIDTH+FCW_FRAC_WIDTH; // ble_test
	localparam REF_ACCUM_WIDTH = FCW_WIDTH + ACCUM_EXTRA_BITS;


	// Ports
		input		 	CS_TSTDC_OV; // v 053121
		input reg [2:0] 	cs_tstdc_user;//^ 053121
		output reg [2:0] 	cs_tstdc;//^ 053121
		input 						CLKREF_IN;
		input	[DCO_NUM_PH-1:0]			DCO_RAW_PH;
		// pre-dltdc
		input	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_user;
		input	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_user;
		input	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_user;
		input	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_user;
		input	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_user;
		input	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_user;
		input	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_user;
		input	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_user;

		input 	[dltdc_NFC_fb*DLTDC_NUM_PH-1:0] 	FC_fb; 
		input 	[dltdc_NCC_fb*DLTDC_NUM_PH-1:0] 	CC_fb; 
		input 	[dltdc_NFC_ref*DLTDC_NUM_PH-1:0] 	FC_ref; 
		input 	[dltdc_NCC_ref*DLTDC_NUM_PH-1:0] 	CC_ref; 
		input						RST;
		// LUT test
		input logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMBTDC_LUT;  
		input logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMB_DLTDC_MAP_LUT;  
	//	input logic [DLTDC_NUM_PH:0][TDC_WIDTH-1:0] 	DLTDC_LUT;
		input logic [49:0][TDC_WIDTH-1:0] 	DLTDC_LUT;
		// CALIBs
		input						TSTDC_CALIB; 
		input						TSTDC_CALIB_DONE_RECIEVE; 
		input	[2:0]					TSTDC_CALIB_EDGE_IDX; 
		input	[DCO_NUM_PH-1:0]			TSTDC_CALIB_STATUS; // 052321 
		input	[8:0]					es_calib_cnt_val;
		input	[8:0]					dltdc_record_cnt_val;
		input	[8:0]					dltdc_lsb_int_cnt_val;
		input	[8:0]					dltdc_lsb_int_margin;
		input						pre_ls_ref_CC_ov;
		input						pre_ls_ref_FC_ov;
		input						post_ls_ref_CC_ov;
		input						post_ls_ref_FC_ov;
		input						pre_es_fb_CC_ov;
		input						pre_es_fb_FC_ov;
		input						post_es_fb_CC_ov;
		input						post_es_fb_FC_ov;
		input						emb_dltdc_map_calib_ov;
 
		output		[TDC_WIDTH-1:0]			dltdc_idx; // 053121 
		output						TSTDC_CALIB_DONE_OUT; 
		output						TSTDC_CALIB_BROKE_OUT; 
		output logic  					CLKREF_RETIMED_OUT; 
		output logic 	[TDC_WIDTH-1:0] 		EMBTDC_OUT;
		output logic 	[TDC_WIDTH-1:0] 		DLTDC_OUT;
		output logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]	COUNT_ACCUM_OUT;
		output						DCO_CLK_DIV4;	
		output	logic [DLTDC_NUM_PH-1:0]		dltdc_out_min_reg_export;
		output logic	[DLTDC_NUM_PH-2:0]		dltdc_out_max_final_rm_lsb;
		// 050521 update
		output logic	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_final;
		output logic	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_final;
		output logic	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_final;
		output logic	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_final;
		output logic	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_final;
		output logic	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_final;
		output logic	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_final;
		output logic	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_final;

	// Internal Signals
		logic	  					clkref_retimed_out_int; 
		logic	[DLTDC_NUM_PH-1:0]			dltdc_out;
		logic	[DCO_NUM_PH-1:0]			embtdc_out;
		logic						dltdc_np_edge;
		logic	[DCO_NUM_PH-1:0]			dltdc_edge_sel;
		logic	[2:0]					dltdc_edge_fb_idx;
		logic	[DCO_NUM_PH-1:0]			dltdc_raw_edge_sel;
		// calibration
		logic	[2:0]					smpl_dltdc_edge_fb_idx;
		logic	[2:0]					smpl_dltdc_edge_sel_idx;
		logic	[2:0]					decoded_edge_sel_idx;
		logic	[2:0]					decoded_calib_edge_sel_idx;
		logic						es_calib_done;
		logic						es_calib_done_tmp;
		logic	[DCO_NUM_PH-1:0]			cr_smpl_edge_sel;
		logic	[DCO_NUM_PH-1:0]			cr_raw_edge_sel;
		logic	[1:0]					pre_ls_ref_dir;
		logic	[8:0]					es_calib_cnt;
		logic	[8:0]					pre_fb_calib_cnt;
		logic	[8:0]					dltdc_record_min_cnt; // 051821
		logic	[8:0]					dltdc_record_max_cnt;

		logic						pre_es_fb_calib_done;
		logic						pre_es_fb_calib_done_tmp;
		logic						post_es_fb_calib_done;
		logic						dltdc_min_sat;
		logic						dltdc_max_sat;
		logic						dltdc_record_cnt_done;
		logic	[1:0]					dltdc_record_min_max;
		logic	[DLTDC_NUM_PH-1:0]			dltdc_out_min_reg;
		logic	[DLTDC_NUM_PH-1:0]			dltdc_out_min_reg_d;
		logic	[DLTDC_NUM_PH-1:0]			dltdc_out_max_reg;
		logic	[DLTDC_NUM_PH-1:0]			dltdc_out_max_reg_d;

		logic	[39:0] 					embtdc_lut_2d;
		logic	[39:0] 					emb_dltdc_map_lut_2d;
		logic	[399:0] 				dltdc_lut_2d;

		// pre-dltdc
		logic	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_tmp;
		logic	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_tmp;
		logic	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_tmp;
		logic	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_tmp;
		logic	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_tmp;
		logic	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_tmp;
		logic	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_tmp;
		logic	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_tmp;
		// gated values
		logic	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_g;
		logic	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_g;
		logic	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_g;
		logic	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_g;
		logic	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_g;
		logic	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_g;
		logic	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_g;
		logic	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_g;

		// these should be output: 050521
		//logic	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_final;
		//logic	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_final;
		//logic	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_final;
		//logic	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_final;
		//logic	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_final;
		//logic	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_final;
		//logic	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_final;
		//logic	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_final;

		logic	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin;
		logic	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin;
		logic	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin;
		logic	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin;
		logic	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin;
		logic	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin;
		logic	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin;
		logic	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin;

		// floating pins
		logic						retime_lag;
		logic						retime_edge_sel;
		logic						pre_dltdc_in_fb_out;
		logic						pre_dltdc_in_ref_out;
		logic	[7:0] 					embtdc_bin_tmp;
		logic	[4:0] 					pre_PH_fb_out;
		logic						pp_fb_begin;

		// logics
		logic	[DCO_NUM_PH-1:0]			es_check; // test purpose 
		logic						post_es_fb_out; // test purpose 
		// logics for calibration
		logic 	[DLTDC_NUM_PH-1:0]			dltdc_out_rm_lsb; // minimum condition (thermal)
		logic 						clk_ref_ls_out; // 041821
		logic						es_calib_broke;
		logic						post_es_fb_calib_broke;
		logic						pre_es_fb_calib_broke;
		//logic						pre_es_fb_incr;
		logic						pre_es_fb_change; // 050321
		logic	[8:0]					dltdc_lsb_int_cnt;
		logic	[8:0]					dltdc_lsb_int;
		logic	[8:0]					dltdc_lsb_int_d;
		logic						dltdc_record_done;
		logic 						pre_ls_ref_CC_min_lim;
		logic 						pre_ls_ref_FC_min_lim;
		logic 						pre_ls_ref_CC_max_lim;
		logic 						pre_ls_ref_FC_max_lim;
		logic 						post_es_fb_CC_min_lim;
		logic 						post_es_fb_FC_min_lim;
		logic 						post_es_fb_CC_max_lim;
		logic 						post_es_fb_FC_max_lim;
		logic 	[4:0]					pre_es_fb_CC_min_lim;
		logic 	[4:0]					pre_es_fb_FC_min_lim;
		logic 	[4:0]					pre_es_fb_CC_max_lim;
		logic 	[4:0]					pre_es_fb_FC_max_lim;


//========================================================================================\\
//                              State machine                                             \\
//========================================================================================\\
  // FSMs
	reg [2:0]	ns_tstdc;
//	reg [2:0] 	cs_tstdc;
	reg [2:0] 	cs_tstdc_g;
	parameter 	ES_CALIB 	= 3'b000;
	parameter 	POST_ES_FB_CALIB= 3'b001;
	parameter 	PRE_ES_FB_CALIB = 3'b010;
	parameter 	DLTDC_RECORD 	= 3'b011;
	parameter 	OPERATE 	= 3'b100;


`define ES_CALIB_STATE						(cs_tstdc_g == ES_CALIB )
`define POST_ES_FB_CALIB_STATE					(cs_tstdc_g == POST_ES_FB_CALIB )
`define PRE_ES_FB_CALIB_STATE					(cs_tstdc_g == PRE_ES_FB_CALIB )
`define DLTDC_RECORD_STATE					(cs_tstdc_g == DLTDC_RECORD )
`define OPERATE_STATE						(cs_tstdc_g == OPERATE ) // normal operation mode

`define DLTDC_LSB_INT_SMALL					(dltdc_lsb_int_d < (dltdc_lsb_int_cnt_val>>1)-dltdc_lsb_int_margin) // normal operation mode
`define DLTDC_LSB_INT_BIG					(dltdc_lsb_int_d > (dltdc_lsb_int_cnt_val>>1)+dltdc_lsb_int_margin) // normal operation mode
`define DLTDC_LSB_INT_SAFE					((dltdc_lsb_int_d >= (dltdc_lsb_int_cnt_val>>1)-dltdc_lsb_int_margin) && (dltdc_lsb_int_d <= (dltdc_lsb_int_cnt_val>>1)+dltdc_lsb_int_margin)) // normal operation mode

//========================================================================================\\
//                              default values                                            \\
//========================================================================================\\

	parameter	DEF_PRE_LS_REF_CC_BIN = 1; // nominal 
	parameter	DEF_PRE_LS_REF_FC_BIN = 30; // nominal 
	//parameter	DEF_PRE_LS_REF_CC_BIN = 0;  // test for late clk_ref_ls case 
	//parameter	DEF_PRE_LS_REF_CC_BIN = 4;  // test for early clk_ref_ls case 
	//parameter	DEF_PRE_LS_REF_FC_BIN = 60; // late 
	parameter	DEF_POST_LS_REF_CC_BIN = 0; 
	parameter	DEF_POST_LS_REF_FC_BIN = 60; 

	// need to consider that this signal is  [4:0][pre_es_fb_CC_WIDTH-1:0]
	parameter	DEF_PRE_ES_FB_CC_BIN = 3*(1 + 2**pre_es_fb_CC_WIDTH + 2**(pre_es_fb_CC_WIDTH*2) + 2**(pre_es_fb_CC_WIDTH*3) + 2**(pre_es_fb_CC_WIDTH*4)); // nominal 
	//parameter	DEF_PRE_ES_FB_CC_BIN = 2*(1 + 2**pre_es_fb_CC_WIDTH + 2**(pre_es_fb_CC_WIDTH*2) + 2**(pre_es_fb_CC_WIDTH*3) + 2**(pre_es_fb_CC_WIDTH*4)); // late  
	//parameter	DEF_PRE_ES_FB_CC_BIN = 4*(1 + 2**pre_es_fb_CC_WIDTH + 2**(pre_es_fb_CC_WIDTH*2) + 2**(pre_es_fb_CC_WIDTH*3) + 2**(pre_es_fb_CC_WIDTH*4)); // early 
	//parameter	DEF_PRE_ES_FB_FC_BIN = 8*(1 + 2**pre_es_fb_FC_WIDTH + 2**(pre_es_fb_FC_WIDTH*2) + 2**(pre_es_fb_FC_WIDTH*3) + 2**(pre_es_fb_FC_WIDTH*4)); // early 
	parameter	DEF_PRE_ES_FB_FC_BIN = 50*(1 + 2**pre_es_fb_FC_WIDTH + 2**(pre_es_fb_FC_WIDTH*2) + 2**(pre_es_fb_FC_WIDTH*3) + 2**(pre_es_fb_FC_WIDTH*4)); // late 
	parameter	DEF_POST_ES_FB_CC_BIN = 4; // nominal 
	//parameter	DEF_POST_ES_FB_FC_BIN = 60;  // nominal
	parameter	DEF_POST_ES_FB_FC_BIN = 44;  // nominal
	//parameter	DEF_POST_ES_FB_CC_BIN = 0; // late 
	//parameter	DEF_POST_ES_FB_FC_BIN = 10;  // late 

	parameter	MAX_PRE_LS_REF_CC_BIN = NUM_pre_ls_ref_CC;
	parameter	MAX_PRE_LS_REF_FC_BIN = NUM_pre_ls_ref_FC;

	parameter	MAX_POST_ES_FB_CC_BIN = NUM_post_es_fb_CC;
	parameter	MAX_POST_ES_FB_FC_BIN = NUM_post_es_fb_FC;

	parameter	MAX_PRE_ES_FB_CC_BIN = NUM_pre_es_fb_CC;
	parameter	MAX_PRE_ES_FB_FC_BIN = NUM_pre_es_fb_FC;

//==========================================================================================
//				Main fsm
//==========================================================================================
  always_ff @(posedge CLKREF_RETIMED_OUT or posedge RST) begin 
    if (RST) begin 
      cs_tstdc <= OPERATE;
    end else begin
      cs_tstdc <= ns_tstdc;
    end
  end 

  /// Combinational logic for next state
  always_comb begin 
    casex (cs_tstdc)
	ES_CALIB: // 0
		ns_tstdc = (es_calib_broke)? OPERATE 
					   : ((es_calib_done)? ((TSTDC_CALIB_EDGE_IDX==0)? POST_ES_FB_CALIB 
									     		    :((pre_es_fb_calib_done)? ((dltdc_record_done)? OPERATE : DLTDC_RECORD) 
														     : PRE_ES_FB_CALIB))
								 : ES_CALIB);
	POST_ES_FB_CALIB: // 1
		ns_tstdc = (post_es_fb_calib_broke)? OPERATE
						   : ((post_es_fb_calib_done==1)? DLTDC_RECORD : POST_ES_FB_CALIB);
	PRE_ES_FB_CALIB: // 2
		ns_tstdc = (pre_es_fb_calib_broke)? OPERATE
						  : ((pre_es_fb_calib_done==1)? ((pre_es_fb_change==1)? ES_CALIB : DLTDC_RECORD) 
                                                    		     	      : PRE_ES_FB_CALIB);
						  //: ((pre_es_fb_calib_done==1)? ((pre_es_fb_incr==1)? ES_CALIB : DLTDC_RECORD) 
	DLTDC_RECORD: // 3
		ns_tstdc = (dltdc_record_done)? OPERATE : DLTDC_RECORD;
	OPERATE: // 4: need to think more about the ns_tstdc for OPERATE state!!!! 051721 bookmark
		ns_tstdc = (!TSTDC_CALIB || TSTDC_CALIB_BROKE_OUT || (TSTDC_CALIB_STATUS == 5'b11111))? OPERATE // 052221 update
								  : ((TSTDC_CALIB_EDGE_IDX==0 && !es_calib_done)? ES_CALIB : PRE_ES_FB_CALIB); 

		//ns_tstdc = (TSTDC_CALIB && !es_calib_done)? ((TSTDC_CALIB_EDGE_IDX==0)? ES_CALIB : PRE_ES_FB_CALIB) 
		//						: ((TSTDC_CALIB_EDGE_IDX==4)? OPERATE : PRE_ES_FB_CALIB); // 051721 update
	
	default:
		ns_tstdc = OPERATE;
    endcase //  
  end


	assign cs_tstdc_g = (CS_TSTDC_OV)? cs_tstdc_user : cs_tstdc;
//========================================================================================\\
//                              Submodules                                                \\
//========================================================================================\\
	// map the luts
	genvar i;
	generate
		for (i=0; i<DCO_NUM_PH; i=i+1) begin
			assign embtdc_lut_2d[TDC_WIDTH*(i+1)-1:TDC_WIDTH*i] = EMBTDC_LUT[i];
			assign emb_dltdc_map_lut_2d[TDC_WIDTH*(i+1)-1:TDC_WIDTH*i] = EMB_DLTDC_MAP_LUT[i];
		end
	endgenerate

	generate
		for (i=0; i<50; i=i+1) begin
			assign dltdc_lut_2d[TDC_WIDTH*(i+1)-1:TDC_WIDTH*i] = DLTDC_LUT[i];
		end
	endgenerate

	//always @(posedge clkref_retimed_out_int or negedge clkref_retimed_out_int) begin
	//	#(dff_delay/TIME_SCALE) CLKREF_RETIMED_OUT <= clkref_retimed_out_int;
	//end


	tstdc_counter 
	u_tstdc_counter(
		.CLKREF_IN		(CLKREF_IN		), 
		.DCO_RAW_PH		(DCO_RAW_PH		),
		.pre_ls_ref_CC_bin	(pre_ls_ref_CC_bin_final	),
		.pre_ls_ref_FC_bin	(pre_ls_ref_FC_bin_final	),
		.post_ls_ref_CC_bin	(post_ls_ref_CC_bin_final	),
		.post_ls_ref_FC_bin	(post_ls_ref_FC_bin_final	),
		.pre_es_fb_CC_bin	(pre_es_fb_CC_bin_final	),
		.pre_es_fb_FC_bin	(pre_es_fb_FC_bin_final	),
		.post_es_fb_CC_bin	(post_es_fb_CC_bin_final	),
		.post_es_fb_FC_bin	(post_es_fb_FC_bin_final	),
		.CC_fb			(CC_fb			),
		.FC_fb			(FC_fb			),
		.CC_ref			(CC_ref			),
		.FC_ref			(FC_ref			),
		.RST			(RST			),
		.CLKREF_RETIMED_OUT	(CLKREF_RETIMED_OUT	),
		.DCO_CLK_DIV4		(DCO_CLK_DIV4		), 
		.EMBTDC_BIN_OUT		(EMBTDC_OUT		),
		.dltdc_idx		(dltdc_idx		), // 053121
		.DLTDC_BIN_OUT		(DLTDC_OUT		),
		.EMBTDC_LUT		(EMBTDC_LUT		), // this is for sim. for synth: embtdc_lut_2d
		.EMB_DLTDC_MAP_LUT	(EMB_DLTDC_MAP_LUT	), // this is for sim. for synth: embtdc_lut_2d
		.DLTDC_LUT		(DLTDC_LUT		), // this is for sim. for synth: embtdc_lut_2d
		.retime_lag		(retime_lag		),
		.retime_edge_sel	(retime_edge_sel	),
		.pre_dltdc_in_fb_out	(pre_dltdc_in_fb_out	),
		.pre_dltdc_in_ref_out	(pre_dltdc_in_ref_out	),
		.embtdc_bin_tmp		(embtdc_bin_tmp		),
		.pre_PH_fb_out		(pre_PH_fb_out		),
		.post_es_fb_out		(post_es_fb_out		),
		.smpl_dltdc_edge_fb_idx	(smpl_dltdc_edge_fb_idx	), // for calib
		.smpl_dltdc_edge_sel_idx(smpl_dltdc_edge_sel_idx), // for calib
		.cr_smpl_edge_sel	(cr_smpl_edge_sel	), // for calib
		.cr_raw_edge_sel	(cr_raw_edge_sel	), // for calib
		.dltdc_out		(dltdc_out		),
		.embtdc_out		(embtdc_out		),
		.dltdc_np_edge		(dltdc_np_edge		),
		.dltdc_edge_sel		(dltdc_edge_sel		),	
		//.dltdc_raw_edge_sel	(dltdc_raw_edge_sel	), // 050321	
		.es_check		(es_check		), // edge_sel calib 04/14/21
		.clk_ref_ls_out		(clk_ref_ls_out		), // 041821 
		.COUNT_ACCUM_OUT	(COUNT_ACCUM_OUT	));


//========================================================================================\\
//			 latch the state-flags, outputs at CLKREF_RETIMED		  \\ 
//========================================================================================\\
	assign pre_ls_ref_CC_min_lim  = (pre_ls_ref_CC_bin_tmp<= 0)? 1:0;
	assign pre_ls_ref_FC_min_lim  = (pre_ls_ref_FC_bin_tmp<= 0)? 1:0;
	assign pre_ls_ref_CC_max_lim  = (pre_ls_ref_CC_bin_tmp>= MAX_PRE_LS_REF_CC_BIN)? 1:0;
	assign pre_ls_ref_FC_max_lim  = (pre_ls_ref_FC_bin_tmp>= MAX_PRE_LS_REF_FC_BIN)? 1:0;

	assign post_es_fb_CC_min_lim  = (post_es_fb_CC_bin_tmp<= 0)? 1:0;
	assign post_es_fb_FC_min_lim  = (post_es_fb_FC_bin_tmp<= 0)? 1:0;
	assign post_es_fb_CC_max_lim  = (post_es_fb_CC_bin_tmp>= MAX_POST_ES_FB_CC_BIN)? 1:0;
	assign post_es_fb_FC_max_lim  = (post_es_fb_FC_bin_tmp>= MAX_POST_ES_FB_FC_BIN)? 1:0;

	assign pre_es_fb_CC_min_lim[0]  = (pre_es_fb_CC_bin_tmp[0]<= 0)? 1:0;
	assign pre_es_fb_CC_min_lim[1]  = (pre_es_fb_CC_bin_tmp[1]<= 0)? 1:0;
	assign pre_es_fb_CC_min_lim[2]  = (pre_es_fb_CC_bin_tmp[2]<= 0)? 1:0;
	assign pre_es_fb_CC_min_lim[3]  = (pre_es_fb_CC_bin_tmp[3]<= 0)? 1:0;
	assign pre_es_fb_CC_min_lim[4]  = (pre_es_fb_CC_bin_tmp[4]<= 0)? 1:0;

	assign pre_es_fb_FC_min_lim[0]  = (pre_es_fb_FC_bin_tmp[0]<= 0)? 1:0;
	assign pre_es_fb_FC_min_lim[1]  = (pre_es_fb_FC_bin_tmp[1]<= 0)? 1:0;
	assign pre_es_fb_FC_min_lim[2]  = (pre_es_fb_FC_bin_tmp[2]<= 0)? 1:0;
	assign pre_es_fb_FC_min_lim[3]  = (pre_es_fb_FC_bin_tmp[3]<= 0)? 1:0;
	assign pre_es_fb_FC_min_lim[4]  = (pre_es_fb_FC_bin_tmp[4]<= 0)? 1:0;

	assign pre_es_fb_CC_max_lim[0]  = (pre_es_fb_CC_bin_tmp[0]>= MAX_PRE_ES_FB_CC_BIN)? 1:0;
	assign pre_es_fb_CC_max_lim[1]  = (pre_es_fb_CC_bin_tmp[1]>= MAX_PRE_ES_FB_CC_BIN)? 1:0;
	assign pre_es_fb_CC_max_lim[2]  = (pre_es_fb_CC_bin_tmp[2]>= MAX_PRE_ES_FB_CC_BIN)? 1:0;
	assign pre_es_fb_CC_max_lim[3]  = (pre_es_fb_CC_bin_tmp[3]>= MAX_PRE_ES_FB_CC_BIN)? 1:0;
	assign pre_es_fb_CC_max_lim[4]  = (pre_es_fb_CC_bin_tmp[4]>= MAX_PRE_ES_FB_CC_BIN)? 1:0;

	assign pre_es_fb_FC_max_lim[0]  = (pre_es_fb_FC_bin_tmp[0]>= MAX_PRE_ES_FB_FC_BIN)? 1:0;
	assign pre_es_fb_FC_max_lim[1]  = (pre_es_fb_FC_bin_tmp[1]>= MAX_PRE_ES_FB_FC_BIN)? 1:0;
	assign pre_es_fb_FC_max_lim[2]  = (pre_es_fb_FC_bin_tmp[2]>= MAX_PRE_ES_FB_FC_BIN)? 1:0;
	assign pre_es_fb_FC_max_lim[3]  = (pre_es_fb_FC_bin_tmp[3]>= MAX_PRE_ES_FB_FC_BIN)? 1:0;
	assign pre_es_fb_FC_max_lim[4]  = (pre_es_fb_FC_bin_tmp[4]>= MAX_PRE_ES_FB_FC_BIN)? 1:0;

	assign dltdc_lsb_int_done = (dltdc_lsb_int_cnt > dltdc_lsb_int_cnt_val)? 1:0;

	assign dltdc_out_rm_lsb = dltdc_out>>1;	

	always @(posedge CLKREF_RETIMED_OUT or posedge RST) begin
		if (RST) begin
			pre_ls_ref_CC_bin_tmp <= DEF_PRE_LS_REF_CC_BIN;
			pre_ls_ref_FC_bin_tmp <= DEF_PRE_LS_REF_FC_BIN;
			post_ls_ref_CC_bin_tmp<= DEF_POST_LS_REF_CC_BIN;
			post_ls_ref_FC_bin_tmp<= DEF_POST_LS_REF_FC_BIN;
			pre_es_fb_CC_bin_tmp  <= DEF_PRE_ES_FB_CC_BIN;
			pre_es_fb_FC_bin_tmp  <= DEF_PRE_ES_FB_FC_BIN;
			post_es_fb_CC_bin_tmp <= DEF_POST_ES_FB_CC_BIN;
			post_es_fb_FC_bin_tmp <= DEF_POST_ES_FB_FC_BIN;
			// es_calib 
			es_calib_done <= 0;
			es_calib_cnt <= 0;
			es_calib_broke <= 0;
			// post_es_fb_calib 
			post_es_fb_calib_done <= 0;
			post_es_fb_calib_broke <= 0; // 0422 bookmark
			dltdc_lsb_int <= 0;
			dltdc_lsb_int_d <= 0;
			dltdc_lsb_int_cnt <= 0;
			// pre_fb_calib 
			pre_es_fb_calib_done <= 0; 
			pre_fb_calib_cnt <= 0;
			//pre_es_fb_incr <= 0;
			pre_es_fb_change <= 0;
			pre_es_fb_calib_broke <= 0; // 0422 bookmark
			// dltdc_record
			dltdc_record_min_cnt <= 0; // 051821
			dltdc_record_max_cnt <= 0; // 051821
			post_es_fb_calib_done <= 0; 
			dltdc_out_min_reg <=  {DLTDC_NUM_PH{1'b1}};
			dltdc_out_max_reg <= {DLTDC_NUM_PH{1'b0}};
			dltdc_out_min_reg_d <= {DLTDC_NUM_PH{1'b1}};
			dltdc_out_max_reg_d <= {DLTDC_NUM_PH{1'b0}};
			dltdc_out_max_final_rm_lsb <= 0;
			dltdc_out_min_reg_export <= 0;
			dltdc_record_done <= 1'b0; // 0426 bookmark

		end else if (`ES_CALIB_STATE) begin
			// when it came back to ES_CALIB from PRE_ES_FB_CALIB: break when pre_ls_ref_dir !=0
			if (pre_es_fb_calib_done==1) begin
				if ( pre_ls_ref_dir==0) begin
					es_calib_done <= es_calib_done_tmp; 
					es_calib_cnt <= es_calib_cnt + 1;
				end else begin
					es_calib_done <= es_calib_done_tmp; 	
					es_calib_broke <= 1;
				end
			// first time calib
			end else if (pre_ls_ref_CC_ov && pre_ls_ref_FC_ov) begin // overwrite CC, FC 
				es_calib_done <= 1; 
				pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_user;
				pre_ls_ref_FC_bin_tmp <= pre_ls_ref_FC_bin_user;
			end else if (pre_ls_ref_dir==1) begin // increase delay: maybe overwrite CC, not overwrite FC
				if (!pre_ls_ref_FC_max_lim) begin // when we can increase FC
					if (pre_ls_ref_CC_ov==1) begin // when CC is overwrote, only FC tuned
						pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_user;
					end else begin
						pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_tmp;
					end
					pre_ls_ref_FC_bin_tmp <= pre_ls_ref_FC_bin_tmp + 1'b1; // increment FC
				end else if (pre_ls_ref_FC_max_lim && !pre_ls_ref_CC_min_lim && !post_es_fb_CC_ov) begin  // when we can decrease CC
					pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_tmp - 1;
					pre_ls_ref_FC_bin_tmp <= 0;
				end else begin // broke: FC_max, CC no where to go: 1. CC_ov, 2. CC_min
					es_calib_broke <= 1;
				end
				es_calib_done <= es_calib_done_tmp;
				es_calib_cnt <= 0;	
			end else if (pre_ls_ref_dir==2) begin // decrease delay: maybe overwrite CC, not overwrite FC
				if (!pre_ls_ref_FC_min_lim) begin
					if (pre_ls_ref_CC_ov==1) begin // when CC is overwrote, only FC tuned
						pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_user;
					end else begin
						pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_tmp;
					end
					pre_ls_ref_FC_bin_tmp <= pre_ls_ref_FC_bin_tmp - 1'b1; // decrement FC
				end else if (pre_ls_ref_FC_min_lim && !pre_ls_ref_CC_max_lim && !pre_ls_ref_CC_ov) begin 
					pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_tmp + 1; // increment CC
					pre_ls_ref_FC_bin_tmp <= MAX_PRE_LS_REF_FC_BIN;
				end else begin // broke
					es_calib_broke <= 1;
				end
				es_calib_done <= es_calib_done_tmp;
				es_calib_cnt <= 0;	
			end else if (pre_ls_ref_dir==0)  begin  // stay
				if (pre_ls_ref_CC_ov==1) begin // when CC is overwrote, only FC tuned
					pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_user;
				end else begin
					pre_ls_ref_CC_bin_tmp <= pre_ls_ref_CC_bin_tmp;
				end
				es_calib_done <= es_calib_done_tmp; 
				es_calib_cnt <= es_calib_cnt + 1;	
			end

		end else if (`POST_ES_FB_CALIB_STATE) begin // only when locked to [0]
			if (post_es_fb_CC_ov && post_es_fb_FC_ov) begin
				post_es_fb_CC_bin_tmp <= post_es_fb_CC_bin_user;
				post_es_fb_FC_bin_tmp <= post_es_fb_FC_bin_user;
				post_es_fb_calib_done <= 1;
			// integrating dltdc_out[0]
			end else if (!dltdc_lsb_int_done) begin  // integrating dltdc_lsb: no dicision made
				if (smpl_dltdc_edge_sel_idx == TSTDC_CALIB_EDGE_IDX) begin // integrate LSB on this condition 
					dltdc_lsb_int <= dltdc_lsb_int + dltdc_out[0];
					dltdc_lsb_int_cnt <= dltdc_lsb_int_cnt + 1;
				end
				dltdc_lsb_int_d <= dltdc_lsb_int;
			end else begin
				dltdc_lsb_int <= 0;
				dltdc_lsb_int_cnt <= 0;
				if (`DLTDC_LSB_INT_SMALL) begin // when ref path is too fast: decrease post_es_fb_delay
					if (!post_es_fb_FC_min_lim) begin
						if (post_es_fb_CC_ov==1) begin // when CC is overwrote, only FC tuned
							post_es_fb_CC_bin_tmp <= post_es_fb_CC_bin_user;
						end else begin
							post_es_fb_CC_bin_tmp <= post_es_fb_CC_bin_tmp;
						end
						post_es_fb_FC_bin_tmp <= post_es_fb_FC_bin_tmp - 1'b1; // decrement FC
					end else if (post_es_fb_FC_min_lim && !post_es_fb_CC_max_lim && !post_es_fb_CC_ov) begin 
						post_es_fb_CC_bin_tmp <= post_es_fb_CC_bin_tmp+1; // increment CC 
						post_es_fb_FC_bin_tmp <= MAX_PRE_ES_FB_FC_BIN;
					end else begin // broke
						post_es_fb_calib_broke <= 1;
					end
				end else if (`DLTDC_LSB_INT_BIG) begin // when fb path is too fast: increase post_es_fb_delay
					if (!post_es_fb_FC_max_lim) begin // when we can increase FC 
						post_es_fb_CC_bin_tmp <= post_es_fb_CC_bin_tmp;
						post_es_fb_FC_bin_tmp <= post_es_fb_FC_bin_tmp + 1'b1; // increment FC
					end else if (post_es_fb_FC_max_lim && !post_es_fb_CC_min_lim && !pre_es_fb_CC_ov) begin  // when we can decrease CC
						post_es_fb_CC_bin_tmp <= post_es_fb_CC_bin_tmp-1; // decrement CC 
						post_es_fb_FC_bin_tmp <= 0;
					end else begin // broke
						post_es_fb_calib_broke <= 1;
					end
				end else if (`DLTDC_LSB_INT_SAFE) begin // appropriate delay offset between the two: stay delay
					post_es_fb_calib_done <= 1;
				end
			end

		end else if (`PRE_ES_FB_CALIB_STATE) begin // only when locked to [4~1]
			if (pre_es_fb_CC_ov && pre_es_fb_FC_ov) begin
				pre_es_fb_CC_bin_tmp <= pre_es_fb_CC_bin_user;
				pre_es_fb_FC_bin_tmp <= pre_es_fb_FC_bin_user;
				pre_es_fb_calib_done <= 1;
			// integrating dltdc_out[0]
			end else if (!dltdc_lsb_int_done) begin  // integrating dltdc_lsb: no dicision made
				if (smpl_dltdc_edge_sel_idx == TSTDC_CALIB_EDGE_IDX) begin // integrate LSB on this condition 
					dltdc_lsb_int <= dltdc_lsb_int + dltdc_out[0];
					dltdc_lsb_int_cnt <= dltdc_lsb_int_cnt + 1;
				end
				dltdc_lsb_int_d <= dltdc_lsb_int;
			end else begin
				dltdc_lsb_int <= 0;
				dltdc_lsb_int_cnt <= 0;
				if (`DLTDC_LSB_INT_SMALL) begin // when ref path is too fast: decrease pre_es_fb_delay
					if (!pre_es_fb_FC_min_lim[decoded_calib_edge_sel_idx]) begin // 052221 update: should calibrate the decoded_calib_edge_sel_idx's DTCs
						if (pre_es_fb_CC_ov==1) begin // when CC is overwrote, only FC tuned
							pre_es_fb_CC_bin_tmp <= pre_es_fb_CC_bin_user;
						end else begin
							pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx] <= pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx];
						end
						pre_es_fb_FC_bin_tmp[decoded_calib_edge_sel_idx] <= pre_es_fb_FC_bin_tmp[decoded_calib_edge_sel_idx] - 1'b1; // decrement FC
					end else if (pre_es_fb_FC_min_lim[decoded_calib_edge_sel_idx] && !pre_es_fb_CC_max_lim[decoded_calib_edge_sel_idx] && !pre_es_fb_CC_ov) begin 
						pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx] <= pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx]+1; // increment CC 
						pre_es_fb_FC_bin_tmp[decoded_calib_edge_sel_idx] <= MAX_POST_ES_FB_FC_BIN;
					end else begin // broke
						pre_es_fb_calib_broke <= 1;
					end
					pre_es_fb_change <= 1; // a flag to indicate that it increased the pre_es_fb delay: to and check if ES_CALIB is still okay
					es_calib_cnt <= 0; // reset count value for ES_CALIB
					es_calib_done <= 0; // reset done signal for ES_CALIB 
				end else if (`DLTDC_LSB_INT_BIG) begin // when fb path is too fast: increase pre_es_fb_delay
					if (!pre_es_fb_FC_max_lim[decoded_calib_edge_sel_idx]) begin // when we can increase FC 
						pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx] <= pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx];
						pre_es_fb_FC_bin_tmp[decoded_calib_edge_sel_idx] <= pre_es_fb_FC_bin_tmp[decoded_calib_edge_sel_idx] + 1'b1; // increment FC
					end else if (pre_es_fb_FC_max_lim[decoded_calib_edge_sel_idx] && !pre_es_fb_CC_min_lim[decoded_calib_edge_sel_idx] && !pre_es_fb_CC_ov) begin  // when we can decrease CC
						pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx] <= pre_es_fb_CC_bin_tmp[decoded_calib_edge_sel_idx]-1; // decrement CC 
						pre_es_fb_FC_bin_tmp[decoded_calib_edge_sel_idx] <= 0;
					end else begin // broke
						pre_es_fb_calib_broke <= 1;
					end
					//pre_es_fb_incr <= 1; // a flag to indicate that it increased the pre_es_fb delay: to and check if ES_CALIB is still okay
					pre_es_fb_change <= 1; // a flag to indicate that it increased the pre_es_fb delay: to and check if ES_CALIB is still okay
					es_calib_cnt <= 0; // reset count value for ES_CALIB
					es_calib_done <= 0; // reset done signal for ES_CALIB 
				end else if (`DLTDC_LSB_INT_SAFE) begin // appropriate delay offset between the two: stay delay
					pre_es_fb_calib_done <= 1;
				end  
			end

		end else if (`DLTDC_RECORD_STATE) begin // record the maximum value of each EMBTDC outputs: this is assuming that the catch_max is hit more than once 
			if (emb_dltdc_map_calib_ov) begin  // we need an option to overwrite this but still get the maximum values of each DCO stage
				dltdc_record_done <= 1'b1; // 0426 bookmark
			end else if (!emb_dltdc_map_calib_ov && dltdc_record_cnt_done==0 && dltdc_record_min_max==0) begin // count not done, catch min
				dltdc_out_min_reg <= dltdc_out;
				dltdc_out_min_reg_d <= dltdc_out_min_reg & dltdc_out_min_reg_d; // bit-wise AND
				dltdc_record_min_cnt <= dltdc_record_min_cnt+1; // 051821 
			end else if (!emb_dltdc_map_calib_ov && dltdc_record_cnt_done==0 && dltdc_record_min_max==1) begin // count not done, catch max
				dltdc_out_max_reg <= dltdc_out;
				dltdc_out_max_reg_d <= dltdc_out_max_reg | dltdc_out_max_reg_d; // bit-wise OR
				dltdc_record_max_cnt <= dltdc_record_max_cnt+1; // 051821 
			//end else if (!emb_dltdc_map_calib_ov && dltdc_record_cnt_done==0 && dltdc_record_min_max==2) begin // count not done, idle
			//	dltdc_record_cnt <= dltdc_record_cnt+1; 
			end else if (!emb_dltdc_map_calib_ov && dltdc_record_cnt_done==1) begin // count done, evaluate, action. export min_reg_d, max_reg_d
				dltdc_record_done <= 1'b1;
				dltdc_out_max_final_rm_lsb <= dltdc_out_max_reg_d >> 1; // remove LSB
				dltdc_out_min_reg_export <= dltdc_out_min_reg_d; // don't remove LSB: we expect it to be 0
			end

		end else if (`OPERATE_STATE) begin 
			if (TSTDC_CALIB_DONE_RECIEVE) begin // 050621: when edge is shifted and need to conduct pre_es_calib again
				if (TSTDC_CALIB_EDGE_IDX < 4) begin // before the last stage: 0517 bookmark: need to think about when the last stage changed something risky
					pre_es_fb_calib_done <= 0; // this is an issue in the last stage
					dltdc_record_done <= 0; // need to think about a scenario when this can be an issue (in the last stage?)
					dltdc_record_min_cnt <= 0;  // 051721 update
					dltdc_record_max_cnt <= 0;  // 051721 update
					dltdc_out_min_reg <=  {DLTDC_NUM_PH{1'b1}}; // 052521 update
					dltdc_out_max_reg <= {DLTDC_NUM_PH{1'b0}}; 
					dltdc_out_min_reg_d <= {DLTDC_NUM_PH{1'b1}};
					dltdc_out_max_reg_d <= {DLTDC_NUM_PH{1'b0}};
					dltdc_out_max_final_rm_lsb <= 0; // remove LSB
					dltdc_out_min_reg_export <= 0; // don't remove LSB: we expect it to be 0
				end
				dltdc_lsb_int <= 0;
				dltdc_lsb_int_cnt <= 0;
				dltdc_lsb_int_d <= 0;
			end
		end
	end			

	//assign TSTDC_CALIB_DONE_OUT = (es_calib_done && pre_es_fb_calib_done && post_es_fb_calib_done);
	assign TSTDC_CALIB_DONE_OUT = (TSTDC_CALIB_EDGE_IDX==0)? (es_calib_done && post_es_fb_calib_done && dltdc_record_done)
							       : (es_calib_done && pre_es_fb_calib_done && dltdc_record_done);
	assign TSTDC_CALIB_BROKE_OUT = (es_calib_broke || pre_es_fb_calib_broke || post_es_fb_calib_broke);

	// 052521 update
	assign pre_ls_ref_CC_bin_g	= pre_ls_ref_CC_ov?	pre_ls_ref_CC_bin_user	: pre_ls_ref_CC_bin_tmp;	
	assign pre_ls_ref_FC_bin_g	= pre_ls_ref_FC_ov?	pre_ls_ref_FC_bin_user	: pre_ls_ref_FC_bin_tmp	;
	assign post_ls_ref_CC_bin_g	= post_ls_ref_CC_ov?	post_ls_ref_CC_bin_user	: post_ls_ref_CC_bin_tmp;	
	assign post_ls_ref_FC_bin_g	= post_ls_ref_FC_ov?	post_ls_ref_FC_bin_user	: post_ls_ref_FC_bin_tmp;	
	assign pre_es_fb_CC_bin_g	= pre_es_fb_CC_ov?	pre_es_fb_CC_bin_user	: pre_es_fb_CC_bin_tmp	;
	assign pre_es_fb_FC_bin_g	= pre_es_fb_FC_ov?	pre_es_fb_FC_bin_user	: pre_es_fb_FC_bin_tmp	;
	assign post_es_fb_CC_bin_g	= post_es_fb_CC_ov?	post_es_fb_CC_bin_user	: post_es_fb_CC_bin_tmp	;
	assign post_es_fb_FC_bin_g	= post_es_fb_FC_ov?	post_es_fb_FC_bin_user	: post_es_fb_FC_bin_tmp	;
	always @(posedge CLKREF_RETIMED_OUT or posedge RST) begin // 0422 changed
		if (RST) begin
			pre_ls_ref_CC_bin_final <= DEF_PRE_LS_REF_CC_BIN;
			pre_ls_ref_FC_bin_final <= DEF_PRE_LS_REF_FC_BIN;
			post_ls_ref_CC_bin_final<= DEF_POST_LS_REF_CC_BIN;
			post_ls_ref_FC_bin_final<= DEF_POST_LS_REF_FC_BIN;
			pre_es_fb_CC_bin_final  <= DEF_PRE_ES_FB_CC_BIN;
			pre_es_fb_FC_bin_final  <= DEF_PRE_ES_FB_FC_BIN;
			post_es_fb_CC_bin_final <= DEF_POST_ES_FB_CC_BIN;
			post_es_fb_FC_bin_final <= DEF_POST_ES_FB_FC_BIN;
		end else begin
			pre_ls_ref_CC_bin_final <= pre_ls_ref_CC_bin_g; // 052521 udpate 
			pre_ls_ref_FC_bin_final <= pre_ls_ref_FC_bin_g; 
			post_ls_ref_CC_bin_final<= post_ls_ref_CC_bin_g;
			post_ls_ref_FC_bin_final<= post_ls_ref_FC_bin_g;
			pre_es_fb_CC_bin_final  <= pre_es_fb_CC_bin_g ; 
			pre_es_fb_FC_bin_final  <= pre_es_fb_FC_bin_g ; 
			post_es_fb_CC_bin_final <= post_es_fb_CC_bin_g; 
			post_es_fb_FC_bin_final <= post_es_fb_FC_bin_g; 
		end
	end

//========================================================================================\\
//			 combinational							  \\ 
//========================================================================================\\

	// decoding smpl_dltdc_edge_sel_idx to original idx
	always @* begin		
		case (smpl_dltdc_edge_sel_idx)
			3'b000: begin	decoded_edge_sel_idx = 0; end	
			3'b001: begin	decoded_edge_sel_idx = 2; end	
			3'b010: begin	decoded_edge_sel_idx = 4; end	
			3'b011: begin	decoded_edge_sel_idx = 1; end	
			3'b100: begin	decoded_edge_sel_idx = 3; end
			default: begin decoded_edge_sel_idx = 0; end
		endcase
		case (TSTDC_CALIB_EDGE_IDX)
			3'b000: begin	decoded_calib_edge_sel_idx = 0; end	
			3'b001: begin	decoded_calib_edge_sel_idx = 2; end	
			3'b010: begin	decoded_calib_edge_sel_idx = 4; end	
			3'b011: begin	decoded_calib_edge_sel_idx = 1; end	
			3'b100: begin	decoded_calib_edge_sel_idx = 3; end
			default: begin decoded_calib_edge_sel_idx = 0; end
		endcase
	end	

	always_comb begin
	// 1. es_calib (pre_ls_ref_dtc)
	// !! smpl_dltdc_edge_sel_idx is the raw_edge_sel_idx latched by CLKREF_RETIMED. so it's safe, we can trust it
	// cr_smpl_edge_sel name is confusing. It's not related to smpl_dltdc_edge_sel_idx. cr_smpl_edge_sel is an one-hot that samples the smpl_edge_sel at CLKREF_RETIMED 
		if (smpl_dltdc_edge_sel_idx == TSTDC_CALIB_EDGE_IDX) begin // check for early clk_ref_ls
			if ((es_check[decoded_edge_sel_idx]==0)&&(cr_smpl_edge_sel==cr_raw_edge_sel))  begin
				pre_ls_ref_dir = 0; // stay
			end else begin
				pre_ls_ref_dir = 1; // increase delay 
			end
		//end else if ((TSTDC_CALIB_EDGE_IDX>1)&&(smpl_dltdc_edge_sel_idx==TSTDC_CALIB_EDGE_IDX-2)) || ((TSTDC_CALIB_EDGE_IDX<=1)&&(smpl_dltdc_edge_sel_idx==TSTDC_CALIB_EDGE_IDX+3)) begin // check for late clk_ref_ls
		end else if ((smpl_dltdc_edge_sel_idx == TSTDC_CALIB_EDGE_IDX-1) || ((smpl_dltdc_edge_sel_idx==4)&&(TSTDC_CALIB_EDGE_IDX==0))) begin // check for late clk_ref_ls
			if ((es_check[decoded_edge_sel_idx]==0)&&(cr_smpl_edge_sel==cr_raw_edge_sel))  begin
				pre_ls_ref_dir = 0; // stay
			end else if (es_check[decoded_edge_sel_idx] != 0)begin // 0503 bookmark: need to decide the priority between this one and below one
				pre_ls_ref_dir = 2; // decrease delay 
			end else if ((cr_smpl_edge_sel!=cr_raw_edge_sel))begin // 0503 bookmark: need to decide the priority between this one and above one
				pre_ls_ref_dir = 1; // increase delay 
			end else begin
				pre_ls_ref_dir = 0;
			end
		end else begin // other edge latched due to jitter: this is theoretically unprobable
			pre_ls_ref_dir = 0; // stay
		end

		if (es_calib_cnt >= es_calib_cnt_val) begin
			es_calib_done_tmp = 1;
		end else begin
			es_calib_done_tmp = 0;
		end 

	// 4. dltdc record 
		if (smpl_dltdc_edge_sel_idx == TSTDC_CALIB_EDGE_IDX) begin // catch min
			dltdc_record_min_max = 0; // 0: min, 1: max
		end else if ((smpl_dltdc_edge_sel_idx == TSTDC_CALIB_EDGE_IDX-1) || ((smpl_dltdc_edge_sel_idx==4)&&(TSTDC_CALIB_EDGE_IDX==0))) begin // catch max 		
			dltdc_record_min_max = 1; // 0: min, 1: max
		end else begin // other edge: idle
			dltdc_record_min_max = 2; // 0: min, 1: max, 2: idle
		end
		//if (dltdc_record_cnt >= dltdc_record_cnt_val) begin
		if ((dltdc_record_min_cnt >= dltdc_record_cnt_val) && (dltdc_record_max_cnt >= dltdc_record_cnt_val)) begin
			dltdc_record_cnt_done = 1;
		end else begin
			dltdc_record_cnt_done = 0;
		end
	end 

endmodule

