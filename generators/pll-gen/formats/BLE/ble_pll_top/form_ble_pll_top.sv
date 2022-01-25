// pll_top
// Functions as an arbiter between pll_controller <=> tstdc_counter
// wraps pll_controller, tstdc_counter, ble_dco

module ble_pll_top(
	// inputs
		CLK_REF,
		RST,
	// tstdc calibration
		TSTDC_CALIB,

	// user values
		pre_ls_ref_CC_bin_user, // V 050421
		pre_ls_ref_FC_bin_user,
		post_ls_ref_CC_bin_user,
		post_ls_ref_FC_bin_user,
		pre_es_fb_CC_bin_user,
		pre_es_fb_FC_bin_user,
		post_es_fb_CC_bin_user,
		post_es_fb_FC_bin_user,
		EMBTDC_LUT_USER,
		DLTDC_LUT_USER, // 0928 update
		EMB_DLTDC_MAP_LUT_USER,
		dltdc_total_max_user, // this will be applied when 1. ~TSTDC_CALIB 2. DLTDC_LUT_OV

	// calibration configs
		es_calib_cnt_val,
		dltdc_record_cnt_val,
		dltdc_lsb_int_cnt_val,
		dltdc_lsb_int_margin,
		pre_ls_ref_CC_ov,
		pre_ls_ref_FC_ov,
		post_ls_ref_CC_ov,
		post_ls_ref_FC_ov,
		pre_es_fb_CC_ov,
		pre_es_fb_FC_ov,
		post_es_fb_CC_ov,
		post_es_fb_FC_ov,
		//emb_dltdc_map_calib_ov, // ^ 050421 
		EMB_DLTDC_MAP_LUT_OV,
		DLTDC_LUT_OV,
		DLTDC_TOTAL_MAX_OV, // 0928 update
		USE_EMBTDC,

	// dltdc values
		CC_fb_bin, 
		CC_ref_bin,
		FC_fb_bin, 
		FC_ref_bin,

	// pll_controller
		FCW_INT,			// integer FCW to the PLL 
		FCW_FRAC,			// fractional FCW to the PLL, not tested yet 
		DCO_OPEN_LOOP_CTRL,	// combined CW to the DCO, only valid in open loop    
		DCO_OPEN_LOOP_EN,	// switch between open and close loop
		DLF_KP,		// loop filter Kp for slow mode 
		DLF_KI,		// loop filter Ki for slow mode
		CAPTURE_MUX_SEL,	// Select among different internal signals to view for testing purposes.
		DITHER_EN,
		FINE_LOCK_ENABLE,
		FINE_LOCK_THRESHOLD,
		FREQ_LOCK_THRESHOLD,
		FREQ_LOCK_COUNT,
		FINE_LOCK_COUNT,
		SSC_EN,
		SSC_REF_COUNT,
		SSC_SHIFT,
		SSC_STEP,
		DCO_CCW_OV_VAL,
		DCO_CCW_OV,
		DCO_FCW_MAX_LIMIT, 		// valid range of FCW

		DCO_FCW_OV_VAL, // v 0602
		DCO_FCW_OV, // ^ 0602
		EMBTDC_OFFSET_OV, // v 0601
		embtdc_offset_user, 
		EDGE_CNT_OV,
		edge_cnt_user, // ^
		CS_PLL_OV, // v 0531
		cs_pll_user,
		CS_PLL_CTRL_OV,
		cs_pll_ctrl_user,
		CS_TSTDC_OV,
		cs_tstdc_user,
		DLTDC_FRAC_CALIB_EN, 
		cnt_ref_frac_accum_val_logtwo,
		idx_ref_phase_ramp_frac_avg,	

	// outputs
		ref_phase_ramp_frac_avg_probe,	
		dltdc_out_max_final_bin_out, // 053121 : for debug
		cs_tstdc, 
		cs_pll,
		cs_pll_ctrl, // ^ 053121
		ns_pll,
		EMBTDC_CALIB_MIN_REG,  
		EMBTDC_CALIB_LUT_RAW, // 0928 update 
		DCO_FCW_MAX_LIMIT_HIT, 		// valid range of FCW
		FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode.
		PLL_LOCKED, 
		CAPTURE_MUX_OUT,	// OUTPUT: The internal signal selected to view as an output.
		pre_ls_ref_CC_bin_final, // v 050521: outputs from tstdc_controller
		pre_ls_ref_FC_bin_final,
		post_ls_ref_CC_bin_final,
		post_ls_ref_FC_bin_final,
		pre_es_fb_CC_bin_final,
		pre_es_fb_FC_bin_final,
		post_es_fb_CC_bin_final,
		post_es_fb_FC_bin_final, // ^
		TSTDC_CALIB_BROKE, // 0523 UPDATE 
		TSTDC_CALIB_STATUS, // 0523 UPDATE 

	// dco
		OSC_EN,
		SCPA_CLK_EN, 
		CLK_OUT_EN, 
		DIV_SEL);

// Functions
	`include "FUNCTIONS.v"
	parameter TIME_SCALE = 1e-12;

// DCO parameters
@@		parameter NSTG=@nM;
	parameter DCO_NUM_PH = NSTG;
@@		parameter NCC=@nC;
	//parameter NFC=16; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
@@		parameter NFC=@nF; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
	parameter DCO_CCW_MAX = NCC*NSTG;	//scale
	parameter DCO_FCW_MAX = NFC*NSTG*2;	// *2 for *_half operation
	parameter DCO_FCW_MAX_H = NFC*NSTG*1;	//scale
// ANALOG CORE
	parameter DCO_FBASE = 2.30e+09;	//scale
	parameter DCO_OFFSET = 0;
	parameter DCO_CSTEP = 5.5e+06;	// ble_test 
	parameter DCO_FSTEP = 180e+03;	// ble_test 
	parameter dco_center_freq=2.4e9;

// pll_controller parameters
	parameter FCW_MAX = 100;  //km for test
	parameter FCW_MIN = 10;
	parameter KP_WIDTH = 12;
	parameter KP_FRAC_WIDTH = 6;
	parameter KI_WIDTH = 12;
	parameter KI_FRAC_WIDTH = 10;
	parameter ACCUM_EXTRA_BITS = 8;
	parameter FILTER_EXTRA_BITS = 4;
	parameter integer FINE_LOCK_THSH_MAX = 20;	//scale not sure
	parameter integer FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;	//scale not sure
	parameter CAPTURE_WIDTH = 25;
	parameter SSC_COUNT_WIDTH = 12;
	parameter SSC_ACCUM_WIDTH = 16;
	parameter SSC_MOD_WIDTH = 5;
	parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

// tstdc_counter parameters
	// dltdc delay line	
@@		parameter dltdc_NSTG = @dM; 
@@		parameter dltdc_NFC_fb = @ff;
@@		parameter dltdc_NFC_ref = @rf;
@@		parameter dltdc_NDRV_fb = @fd;
@@		parameter dltdc_NDRV_ref = @rd;
@@		parameter dltdc_NCC_fb = @fc;
@@		parameter dltdc_NCC_ref = @rc;
	parameter TDC_NUM_PHASE_LATCH = 2;
	parameter TDC_NUM_RETIME_CYCLES = 5;
	parameter TDC_NUM_RETIME_DELAYS = 2;
	parameter TDC_NUM_COUNTER_DIVIDERS = 3;
	localparam EMBTDC_WIDTH = 5;
	localparam DLTDC_WIDTH = 3;
	localparam TDC_WIDTH = 8;
	localparam NUM_CC_fb = dltdc_NCC_fb*dltdc_NSTG; 
	localparam CC_fb_WIDTH = func_clog2(NUM_CC_fb);
	localparam NUM_FC_fb = dltdc_NFC_fb*dltdc_NSTG; 
	localparam FC_fb_WIDTH = func_clog2(NUM_FC_fb);
	localparam NUM_CC_ref = dltdc_NCC_ref*dltdc_NSTG; 
	localparam CC_ref_WIDTH = func_clog2(NUM_CC_ref);
	localparam NUM_FC_ref = dltdc_NFC_ref*dltdc_NSTG; 
	localparam FC_ref_WIDTH = func_clog2(NUM_FC_ref);
	// 050421
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

// Local Parameters
	localparam DCO_CCW_BIN_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_BIN_WIDTH = func_clog2(DCO_FCW_MAX);
	localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
	localparam DLTDC_NUM_PH = dltdc_NSTG;
	localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
	localparam FCW_FRAC_WIDTH = 9; // ble_test
	localparam FCW_WIDTH = FCW_INT_WIDTH+FCW_FRAC_WIDTH; // ble_test
	localparam TDC_ROUND_WIDTH = FCW_FRAC_WIDTH; // ble_test
	localparam REF_ACCUM_WIDTH = FCW_WIDTH + ACCUM_EXTRA_BITS;
	localparam TDC_COUNT_ACCUM_WIDTH = REF_ACCUM_WIDTH - FCW_FRAC_WIDTH;	
	//parameter TDC_COUNT_ACCUM_WIDTH = 15; // is this right?	
	localparam TDC_SHIFT=FCW_FRAC_WIDTH-TDC_WIDTH;	
	localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
	localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

	// ports
	// tstdc calibration
	input						CLK_REF;
	input						RST;
	input						TSTDC_CALIB;	

	// user values
	input	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_user;
	input	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_user;
	input	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_user;
	input	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_user;
	input	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_user;
	input	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_user;
	input	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_user;
	input	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_user;
	input [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 		EMBTDC_LUT_USER;  
	input [49:0][TDC_WIDTH-1:0] 			DLTDC_LUT_USER; // 0928 update
	input [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 		EMB_DLTDC_MAP_LUT_USER;  
	input	[6:0]					dltdc_total_max_user;

	// calibration configs
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
//	input						emb_dltdc_map_calib_ov;
	input						EMB_DLTDC_MAP_LUT_OV;
	input						DLTDC_LUT_OV;
	input						DLTDC_TOTAL_MAX_OV;
	input						USE_EMBTDC;

	// dltdc values	
	logic 	[dltdc_NFC_fb*DLTDC_NUM_PH-1:0] 	FC_fb; 
	logic 	[dltdc_NCC_fb*DLTDC_NUM_PH-1:0] 	CC_fb; 
	logic 	[dltdc_NFC_ref*DLTDC_NUM_PH-1:0] 	FC_ref; 
	logic 	[dltdc_NCC_ref*DLTDC_NUM_PH-1:0] 	CC_ref; 
	input 	[FC_fb_WIDTH-1:0] 			FC_fb_bin; 
	input 	[CC_fb_WIDTH-1:0] 			CC_fb_bin; 
	input 	[FC_ref_WIDTH-1:0] 			FC_ref_bin; 
	input 	[CC_ref_WIDTH-1:0] 			CC_ref_bin; 

	// pll_controller
	input 		[FCW_INT_WIDTH-1:0] 		FCW_INT;
	input 		[FCW_FRAC_WIDTH-1:0]		FCW_FRAC;  
	input 		[DCO_CCW_WIDTH +
	      			 DCO_FCW_WIDTH-1:0]	DCO_OPEN_LOOP_CTRL;
	input 						FINE_LOCK_ENABLE;	
	input  	[FCW_WIDTH-1:0]				FINE_LOCK_THRESHOLD;
	input						DCO_OPEN_LOOP_EN;	// switch between open and close loop
	input	[KP_WIDTH-1:0]				DLF_KP;
	input	[KI_WIDTH-1:0] 				DLF_KI;
	input	[3:0] 					CAPTURE_MUX_SEL;
	input						DITHER_EN;
	input  	[FCW_WIDTH-1:0]				FREQ_LOCK_THRESHOLD;
	input  	[FINE_LOCK_COUNT_WIDTH-1:0]		FREQ_LOCK_COUNT;
	input  	[FINE_LOCK_COUNT_WIDTH-1:0]		FINE_LOCK_COUNT;
	input 						SSC_EN;
	input 	[11:0]					SSC_REF_COUNT;
	input 	[3:0]					SSC_SHIFT;
	input 	[3:0]					SSC_STEP;
	input 		[DCO_FCW_BIN_WIDTH-1:0]		DCO_FCW_MAX_LIMIT;	
	input	 					DCO_CCW_OV;
	input 		[DCO_CCW_BIN_WIDTH-1:0]		DCO_CCW_OV_VAL;
	input 		[DCO_FCW_BIN_WIDTH-1:0]		DCO_FCW_OV_VAL; // 060221
	input 						DCO_FCW_OV; // 060221
	input		 	CS_PLL_OV;
	input reg [2:0] 	cs_pll_user;
	input		 	CS_PLL_CTRL_OV;
	input reg [1:0] 	cs_pll_ctrl_user;
	input		 	CS_TSTDC_OV;
	input reg [2:0] 	cs_tstdc_user;
	input	[FCW_FRAC_WIDTH-1:0]			embtdc_offset_user; // v 060121
	input						EMBTDC_OFFSET_OV; // 
	input						EDGE_CNT_OV;
	input	[2:0]					edge_cnt_user; // ^ 060121

	// outputs
	output logic [2:0] 				cs_tstdc;
	output logic [1:0] 				cs_pll_ctrl;
	output reg [2:0]	ns_pll;
	output reg [2:0] 	cs_pll;
	output logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMBTDC_CALIB_MIN_REG;  
	output logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 	EMBTDC_CALIB_LUT_RAW;  // 0928 update 
	output logic					DCO_FCW_MAX_LIMIT_HIT;
	output						FINE_LOCK_DETECT;	// OUTPUT: lock detect; goes high when error is within lock_thsh; also if goes high; PLL switches to slow mode. 
	output						PLL_LOCKED;	        // high when OPERATE state & FINE_LOCK_DETECT 
	output logic 	[CAPTURE_WIDTH-1 :0]		CAPTURE_MUX_OUT;
	output	[pre_ls_ref_CC_WIDTH-1:0]		pre_ls_ref_CC_bin_final; // 050521: outputs from tstdc_controller
	output	[pre_ls_ref_FC_WIDTH-1:0]		pre_ls_ref_FC_bin_final;
	output	[post_ls_ref_CC_WIDTH-1:0]		post_ls_ref_CC_bin_final;
	output	[post_ls_ref_FC_WIDTH-1:0]		post_ls_ref_FC_bin_final;
	output	[DCO_NUM_PH-1:0][pre_es_fb_CC_WIDTH-1:0] pre_es_fb_CC_bin_final;
	output	[DCO_NUM_PH-1:0][pre_es_fb_FC_WIDTH-1:0] pre_es_fb_FC_bin_final;
	output	[post_es_fb_CC_WIDTH-1:0]		post_es_fb_CC_bin_final;
	output	[post_es_fb_FC_WIDTH-1:0]		post_es_fb_FC_bin_final;
	output logic					TSTDC_CALIB_BROKE; // 052321: update for debug 
	output logic	[DCO_NUM_PH-1:0]		TSTDC_CALIB_STATUS;  // 052321
	output logic	[3:0]				dltdc_out_max_final_bin_out; // 053121 : for debug

	// dco
	input						OSC_EN;
   	input 						SCPA_CLK_EN;
   	input 						CLK_OUT_EN;
   	input [8:0] 					DIV_SEL;

	// logics
	logic	[TDC_WIDTH-1:0]				dltdc_idx; // 053121	
	logic	[TDC_WIDTH-1:0]				dltdc_idx_d; // 053121	
	logic [2:0] 					cs_pll_g;// ^
	logic						SCPA_OUT;
	logic						CLK_OUT; // will be defined as power
	logic						emb_dltdc_map_calib_ov; // 0928 update
	logic						clkref_retimed; // main clock

	logic [25:0][49:0][TDC_WIDTH-1:0] 		DLTDC_LUT_LIB;
	logic [49:0][TDC_WIDTH-1:0] 			DLTDC_CALIB_LUT;
	logic [DLTDC_NUM_PH:0][TDC_WIDTH-1:0] 		DLTDC_ACCUM_LUT;
	logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 		tstdc_emb_dltdc_map_lut;  
	logic						tstdc_calib_edge_shift_done;
	logic						tstdc_calib_edge_shift_step;
	logic						tstdc_calib_done_recieve;
	logic						tstdc_calib_done;
	logic	[2:0]					edge_cnt;
	logic	[2:0]					edge_cnt_g; // 060121
	logic	[2:0]					edge_cnt_pre;
	logic						edge_cnt_update;
	logic						freq_lock_rst;
	logic	[3:0]					dltdc_out_max_final_bin;
	logic	[6:0]					dltdc_total_max;
	logic	[6:0]					dltdc_total_max_g;
	logic						tstdc_calib;
	logic	[FCW_FRAC_WIDTH-1:0]			embtdc_offset;
	logic	[FCW_FRAC_WIDTH-1:0]			embtdc_offset_final;

	// pll_controller
	logic	[FCW_FRAC_WIDTH-1:0] 			pll_fcw_frac; // ble_test
	logic 	[TDC_WIDTH-1:0]				embtdc_out;
	logic						dco_open_loop_en;
	logic	[DCO_CCW_WIDTH-1:0]			dco_open_loop_cc;
	logic	[DCO_FCW_WIDTH-1:0] 			dco_open_loop_fc;
	logic	[TDC_COUNT_ACCUM_WIDTH-1:0]		count_accum_out;
	logic						fine_lock_detect;
	logic	[1:0]					fine_lock_detect_d;
	logic	[DCO_CCW_MAX-1:0]			dco_ccw; //therm
	logic	[DCO_FCW_MAX_H-1:0]			dco_fcw;
	logic	[DCO_FCW_MAX_H-1:0]			dco_fcw_g;
	logic	[DCO_FCW_MAX_H-1:0]			dco_fcbw;
	logic	[DCO_FCW_MAX_H-1:0]			dco_fcbw_g;
	logic	[DCO_CCW_WIDTH-1:0]			dco_ccw_bin; //bin
	logic	[DCO_FCW_WIDTH-1:0]			dco_fcw_bin;
	logic	[DCO_FCW_WIDTH-1:0]			dco_fcw_bin_final;
	logic 	[TDC_WIDTH-1:0]				pll_frac_phase_in;
	logic 		[DCO_CCW_MAX-1:0]		DCO_CCW_OV_VAL_therm; // 052921
	logic 		[DCO_FCW_MAX-1:0]		DCO_FCW_OV_VAL_therm; // 052921
	logic 		[DCO_FCW_MAX_H-1:0]		DCO_FCW_OV_VAL_therm_p; // 052921
	logic 		[DCO_FCW_MAX_H-1:0]		DCO_FCBW_OV_VAL_therm_p; // 052921

	// tstdc_controller
	logic	[DCO_NUM_PH-1:0]			phases_proc;
	logic						dco_clk_div4;
	logic 	[TDC_WIDTH-1:0]				dltdc_out;
	logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 		tstdc_embtdc_lut;  
	logic [49:0][TDC_WIDTH-1:0] 			tstdc_dltdc_lut;
	logic [DCO_NUM_PH-1:0][TDC_WIDTH-1:0] 		EMB_DLTDC_MAP_LUT;  
	logic	[DLTDC_NUM_PH-1:0]			dltdc_out_max_final;
	logic						tstdc_rst;
	logic						pll_ctrl_rst;

	// dco
	logic	[119:0] 				dco_cc;
	logic	[79:0] 					dco_fc;
	logic	[79:0] 					dco_fcb;
	logic						dco_osc_en;
	logic		 				dco_clk_out;
	logic		 				dco_scpa_clk;
	logic						dco_clk;
	logic						dco_dum_in;
	logic		 				dco_dum_out;
	logic						DCO_CLK_OUT;
	logic						DCO_SCPA_CLK;

	// LUT test
	// CALIBs
	//logic						tstdc_calib_broke; 
	logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		COUNT_ACCUM_OUT;
	logic	[DLTDC_NUM_PH-1:0]			dltdc_out_min_reg_export;
	logic	[DLTDC_NUM_PH-2:0]			dltdc_out_max_final_rm_lsb;

	// 053121 : added dltdc calibration stuffs
	logic	[49:0] [10:0]					cnt_ref_frac_accum;
	input	[3:0]					cnt_ref_frac_accum_val_logtwo;
	logic	[FCW_FRAC_WIDTH-1:0]				ref_phase_ramp_frac; // 053121	
	logic	[49:0] [FCW_FRAC_WIDTH+12-1:0]			ref_phase_ramp_frac_accum;
	logic	[49:0] [FCW_FRAC_WIDTH+2-1:0]			ref_phase_ramp_frac_avg;
	logic	[49:0]						dltdc_frac_calib_status;
	input							DLTDC_FRAC_CALIB_EN;
	input	[6:0]						idx_ref_phase_ramp_frac_avg;	
	output	[FCW_FRAC_WIDTH+2-1:0]				ref_phase_ramp_frac_avg_probe;	



	logic						clkref_tdc_in; // v 050921
	logic 						divbuf_dum_clk;
	logic 						divbuf_dum_in ;
	logic 						divbuf_dum_out; // ^ 
//==========================================================================================
//                              State definition                                             
//==========================================================================================
	parameter 	PLL_IDLE = 3'b000;
	parameter 	PLL_TSTDC_CALIB_EDGE_SHIFT = 3'b001;
	parameter 	PLL_TSTDC_CALIB = 3'b010;
	parameter	PLL_OPERATE = 3'b011;
`define PLL_IDLE_STATE						(cs_pll_g == PLL_IDLE )
`define PLL_TSTDC_CALIB_EDGE_SHIFT_STATE             		(cs_pll_g == PLL_TSTDC_CALIB_EDGE_SHIFT )
`define PLL_TSTDC_CALIB_STATE					(cs_pll_g == PLL_TSTDC_CALIB )
`define PLL_OPERATE_STATE					(cs_pll_g == PLL_OPERATE )

	assign cs_pll_g = (CS_PLL_OV)? cs_pll_user : cs_pll;
	assign edge_cnt_g = (EDGE_CNT_OV)? edge_cnt_user : edge_cnt;
//==========================================================================================
//				Main fsm
//==========================================================================================
  always_ff @(posedge clkref_retimed or posedge RST) begin 
    if (RST) begin 
      cs_pll <= PLL_IDLE;
    end else begin
      cs_pll <= ns_pll;
    end
  end 

  // Combinational logic for next state
  always_comb begin 
    casex (cs_pll)
	PLL_IDLE: // different from RST. preserve all values so that the user can debug
	  ns_pll = (TSTDC_CALIB_BROKE)? PLL_IDLE
				      : (TSTDC_CALIB)? PLL_TSTDC_CALIB_EDGE_SHIFT : PLL_OPERATE; // calib=0 => need to be able to diagnose tstdc status

	PLL_TSTDC_CALIB_EDGE_SHIFT:
	  ns_pll =(tstdc_calib_edge_shift_done)? PLL_TSTDC_CALIB 
						  : ((tstdc_calib_edge_shift_step==1)? PLL_OPERATE : PLL_TSTDC_CALIB_EDGE_SHIFT); 

	PLL_TSTDC_CALIB:
	  ns_pll = (TSTDC_CALIB_BROKE)? PLL_IDLE
				      : (tstdc_calib_done)? PLL_TSTDC_CALIB_EDGE_SHIFT: PLL_TSTDC_CALIB;

	PLL_OPERATE:
	  ns_pll = PLL_OPERATE;

	default:
	  ns_pll = PLL_IDLE;

    endcase // casez (cs_pll)
  end

//========================================================================================
//			 main function: sequential					
//========================================================================================

	// latch flag signals on clkref_retimed edge
	always @(posedge clkref_retimed or posedge RST) begin
		if (RST) begin // PLL_INIT?
			edge_cnt <= 0;
			edge_cnt_pre <= 0;
			tstdc_calib_edge_shift_step <= 1'b0;
			tstdc_calib_edge_shift_done <= 1'b0;
			tstdc_calib <= 1'b0;
			freq_lock_rst <= 0;
			tstdc_rst <= 1'b1;
			pll_ctrl_rst <= 1'b1;
			edge_cnt_update <= 1'b0;
			EMBTDC_CALIB_LUT_RAW <= 0;	
			EMBTDC_CALIB_MIN_REG <= 0;
			tstdc_calib_done_recieve <= 1'b0;
			TSTDC_CALIB_STATUS <= 5'b0;
			// 053121
			ref_phase_ramp_frac_accum <= 0;
			cnt_ref_frac_accum <= 0; 
			ref_phase_ramp_frac_avg <= 0;
			dltdc_frac_calib_status <= 0;
			dltdc_idx_d <= 0; // 0601 update


		end else if (`PLL_IDLE_STATE) begin // PLL_INIT?
			// do nothing? below is place-holder	
			pll_ctrl_rst <= 1'b0;

		end else if (`PLL_TSTDC_CALIB_EDGE_SHIFT_STATE) begin // shift edge when edge_cnt<4. Even shift edge when emb_dltdc_map_calib_ov==1 
			tstdc_rst <= 1'b0;
			if (edge_cnt<4 || (edge_cnt==4 && tstdc_calib_done==0)) begin // not the last edge
				tstdc_calib_done_recieve <= 1'b0; // 051721
				pll_ctrl_rst <= 1'b1;
				tstdc_calib <= 1'b0;
				fine_lock_detect_d <= 2'b0;
				if (edge_cnt_update==0)begin
					edge_cnt <= edge_cnt_pre;
					edge_cnt_pre <= edge_cnt_pre +1;
					edge_cnt_update <= 1;
				end
				tstdc_calib_edge_shift_done <= 1'b1;
			end else if (edge_cnt==4 && tstdc_calib_done==1) begin // the last edge
				edge_cnt <= 4;
				edge_cnt_pre <= 0;
				tstdc_calib_edge_shift_step <= 1;  // combinational starts scaling lut
				tstdc_calib_edge_shift_done <= 1'b0;
			end
			if (!emb_dltdc_map_calib_ov) begin // 0928 update
				case (edge_cnt)
					0:begin	EMBTDC_CALIB_LUT_RAW[4] <= dltdc_out_max_final_bin; EMBTDC_CALIB_MIN_REG[4] <= dltdc_out_min_reg_export; end
					1:begin	EMBTDC_CALIB_LUT_RAW[0] <= dltdc_out_max_final_bin; EMBTDC_CALIB_MIN_REG[0] <= dltdc_out_min_reg_export; end
					2:begin	EMBTDC_CALIB_LUT_RAW[1] <= dltdc_out_max_final_bin; EMBTDC_CALIB_MIN_REG[1] <= dltdc_out_min_reg_export; end
					3:begin	EMBTDC_CALIB_LUT_RAW[2] <= dltdc_out_max_final_bin; EMBTDC_CALIB_MIN_REG[2] <= dltdc_out_min_reg_export; end
					4:begin	EMBTDC_CALIB_LUT_RAW[3] <= dltdc_out_max_final_bin; EMBTDC_CALIB_MIN_REG[3] <= dltdc_out_min_reg_export; end
					default:begin	EMBTDC_CALIB_LUT_RAW[3] <=0;  EMBTDC_CALIB_MIN_REG[3] <=0; end
				endcase
			end	

		end else if (`PLL_TSTDC_CALIB_STATE) begin
			tstdc_rst <= 1'b0;
			edge_cnt_update <= 1'b0;
			pll_ctrl_rst <= 1'b0;
			tstdc_calib_edge_shift_done <= 1'b0;
			if (fine_lock_detect) begin
				tstdc_calib <= 1'b1;
			end
			if (tstdc_calib_done==1) begin
				freq_lock_rst <= 1'b1;
				tstdc_calib_done_recieve <= 1'b1;
				TSTDC_CALIB_STATUS[edge_cnt] <= 1'b1;
			end else begin
				freq_lock_rst <= 1'b0;
			end
		end// else if (`PLL_OPERATE_STATE) begin

		else if (`PLL_OPERATE_STATE) begin
			dltdc_idx_d <= dltdc_idx;
			tstdc_rst <= 1'b0;
			pll_ctrl_rst <= 1'b0;
			tstdc_calib_edge_shift_step <= 1;  // combinational starts scaling lut
			freq_lock_rst <= 1'b0;
			// record ref_frac_dltdc_toggle_lut : 053121
			if ( DLTDC_FRAC_CALIB_EN && FINE_LOCK_DETECT ) begin // 0601 udpate
				if ((cnt_ref_frac_accum[dltdc_idx] < 2**cnt_ref_frac_accum_val_logtwo) && (dltdc_idx_d != dltdc_idx)) begin
					ref_phase_ramp_frac_accum[dltdc_idx] <= ref_phase_ramp_frac_accum[dltdc_idx] + ref_phase_ramp_frac;
					cnt_ref_frac_accum[dltdc_idx] <= cnt_ref_frac_accum[dltdc_idx] + 1; 
				end else if(cnt_ref_frac_accum[dltdc_idx] >= 2**cnt_ref_frac_accum_val_logtwo)  begin
					dltdc_frac_calib_status[dltdc_idx] <= 1;
					ref_phase_ramp_frac_avg[dltdc_idx] <= (ref_phase_ramp_frac_accum[dltdc_idx] >> cnt_ref_frac_accum_val_logtwo);
				end	
			end 
		end
	end

	// debugging signal
	assign ref_phase_ramp_frac_avg_probe = ref_phase_ramp_frac_avg[idx_ref_phase_ramp_frac_avg];

	//================================================================================
	// latch debug signals
	//================================================================================
	always @ (posedge clkref_retimed or posedge RST) begin
		if(RST) begin
			dltdc_out_max_final_bin_out <= 0;
		//end else if(tstdc_calib_done) begin
		end else begin // 060121
			dltdc_out_max_final_bin_out <= dltdc_out_max_final_bin;
		end
	end 
//========================================================================================
//			 main function: combinational			
//========================================================================================
	therm2bin #(.NTHERM(dltdc_NSTG-1), .NBIN(4)) u_t2b1 (.thermin(dltdc_out_max_final_rm_lsb), .binout(dltdc_out_max_final_bin));
	// 051121 : bin2therm for dltdc control
	bin2therm #(.NBIN(CC_fb_WIDTH),.NTHERM(NUM_CC_fb)) b2t_CC_fb (.binin(CC_fb_bin), .thermout(CC_fb));
	bin2therm #(.NBIN(FC_fb_WIDTH),.NTHERM(NUM_FC_fb)) b2t_FC_fb (.binin(FC_fb_bin), .thermout(FC_fb));
	bin2therm #(.NBIN(CC_ref_WIDTH),.NTHERM(NUM_CC_ref)) b2t_CC_ref (.binin(CC_ref_bin), .thermout(CC_ref));
	bin2therm #(.NBIN(FC_ref_WIDTH),.NTHERM(NUM_FC_ref)) b2t_FC_ref (.binin(FC_ref_bin), .thermout(FC_ref));
	bin2therm #(.NBIN(DCO_CCW_BIN_WIDTH),.NTHERM(DCO_CCW_MAX)) b2t_dco_ccw_ov (.binin(DCO_CCW_OV_VAL), .thermout(DCO_CCW_OV_VAL_therm));
	bin2therm #(.NBIN(DCO_FCW_BIN_WIDTH),.NTHERM(DCO_FCW_MAX)) b2t_dco_fcw_ov (.binin(DCO_FCW_OV_VAL), .thermout(DCO_FCW_OV_VAL_therm));

	genvar i;
	generate // 060221
		for (i=0; i<DCO_FCW_MAX/2; i=i+1) begin
			assign DCO_FCBW_OV_VAL_therm_p[i] = DCO_FCW_OV_VAL_therm[2*i+1]; // processed
			assign DCO_FCW_OV_VAL_therm_p[i] = ~DCO_FCW_OV_VAL_therm[2*i];
		end
	endgenerate

	always_comb begin
	// 1. tstdc_calib_edge_shift
		if (tstdc_calib_edge_shift_step == 0) begin
			// 0523 update: to ensure mid-rise operation during calibration
			if (edge_cnt==0) begin
				embtdc_offset = 0;
			end else begin // (lut[cnt]+lut[cnt-1])/2
				embtdc_offset = ((EMBTDC_LUT_USER[edge_cnt]<<<TDC_SHIFT)>>1) + ((EMBTDC_LUT_USER[edge_cnt-1]<<<TDC_SHIFT)>>1);
			end
			EMB_DLTDC_MAP_LUT[0] = 0; 
			EMB_DLTDC_MAP_LUT[1] = 0; 
			EMB_DLTDC_MAP_LUT[2] = 0; 
			EMB_DLTDC_MAP_LUT[3] = 0; 
			EMB_DLTDC_MAP_LUT[4] = 0; 
			dltdc_total_max    = 0;
		end else begin
			embtdc_offset = 0;
			EMB_DLTDC_MAP_LUT[0] = 0; 
			EMB_DLTDC_MAP_LUT[1] = EMBTDC_CALIB_LUT_RAW[0]+1; 
			EMB_DLTDC_MAP_LUT[2] = EMBTDC_CALIB_LUT_RAW[0] + EMBTDC_CALIB_LUT_RAW[1] +2; 
			EMB_DLTDC_MAP_LUT[3] = EMBTDC_CALIB_LUT_RAW[0] + EMBTDC_CALIB_LUT_RAW[1] + EMBTDC_CALIB_LUT_RAW[2] +3; 
			EMB_DLTDC_MAP_LUT[4] = EMBTDC_CALIB_LUT_RAW[0] + EMBTDC_CALIB_LUT_RAW[1] + EMBTDC_CALIB_LUT_RAW[2] + EMBTDC_CALIB_LUT_RAW[3] +4;
			dltdc_total_max    = EMBTDC_CALIB_LUT_RAW[0] + EMBTDC_CALIB_LUT_RAW[1] + EMBTDC_CALIB_LUT_RAW[2] + EMBTDC_CALIB_LUT_RAW[3] + EMBTDC_CALIB_LUT_RAW[4] +5;
		end
	end

	// map dltdc_calib_lut
	always_comb begin 
		casex (dltdc_total_max_g)
			25: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[0];
			26: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[1];
			27: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[2];
			28: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[3];
			29: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[4];
			30: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[5];
			31: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[6];
			32: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[7];
			33: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[8];
			34: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[9];
			35: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[10];
			36: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[11];
			37: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[12];
			38: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[13];
			39: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[14];
			40: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[15];
			41: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[16];
			42: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[17];
			43: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[18];
			44: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[19];
			45: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[20];
			46: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[21];
			47: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[22]; // 1012 update
			48: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[23];
			49: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[24];
			50: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[25];
			default: DLTDC_CALIB_LUT = DLTDC_LUT_LIB[2];
		endcase
	end

	dltdc_lut_lib u_dltdc_lut_lib( .DLTDC_LUT_LIB( DLTDC_LUT_LIB));

//==========================================================================================
//				Signal gating
//==========================================================================================

assign pll_fcw_frac = (`PLL_OPERATE_STATE)? FCW_FRAC : 0;
assign pll_frac_phase_in = (`PLL_OPERATE_STATE)? ((USE_EMBTDC)? embtdc_out : dltdc_out) : embtdc_out;
assign tstdc_embtdc_lut = EMBTDC_LUT_USER; // used when: only embtdc is used 
assign tstdc_emb_dltdc_map_lut = (`PLL_OPERATE_STATE&&(!EMB_DLTDC_MAP_LUT_OV))? EMB_DLTDC_MAP_LUT : EMB_DLTDC_MAP_LUT_USER; 
assign tstdc_dltdc_lut = (`PLL_OPERATE_STATE)? ((DLTDC_LUT_OV)? DLTDC_LUT_USER : DLTDC_CALIB_LUT) : 0; // 0928 update 
assign dltdc_total_max_g = (DLTDC_TOTAL_MAX_OV)? dltdc_total_max_user: dltdc_total_max; // 0928 update
assign emb_dltdc_map_calib_ov = EMB_DLTDC_MAP_LUT_OV && DLTDC_TOTAL_MAX_OV; // 0928 update
assign PLL_LOCKED = (`PLL_OPERATE_STATE)? FINE_LOCK_DETECT : 0;
assign FINE_LOCK_DETECT = fine_lock_detect; 
assign embtdc_offset_final = (USE_EMBTDC)? 0 
					 : (EMBTDC_OFFSET_OV)? embtdc_offset_user : embtdc_offset; // 060121 update 

assign dco_fcw_g = (DCO_FCW_OV)? DCO_FCW_OV_VAL_therm_p : dco_fcw; // 060221 update 
assign dco_fcbw_g = (DCO_FCW_OV)? DCO_FCBW_OV_VAL_therm_p : dco_fcbw; // 060221 update
 
//==========================================================================================
//				Define submodules	
//==========================================================================================

	pll_controller 
		`ifndef SYNorAPR
			#(	
				.FCW_MAX(FCW_MAX),
				.FCW_MIN(FCW_MIN),
				.DCO_CCW_MAX(DCO_CCW_MAX),
				.DCO_FCW_MAX(DCO_FCW_MAX),
				.KP_WIDTH(KP_WIDTH),
				.KP_FRAC_WIDTH(KP_FRAC_WIDTH),
				.KI_WIDTH(KI_WIDTH),
				.KI_FRAC_WIDTH(KI_FRAC_WIDTH),
				.ACCUM_EXTRA_BITS(ACCUM_EXTRA_BITS),
				.FILTER_EXTRA_BITS(FILTER_EXTRA_BITS),
				.FINE_LOCK_THSH_MAX(FINE_LOCK_THSH_MAX),
				.FINE_LOCK_COUNT_MAX(FINE_LOCK_COUNT_MAX),
				.CAPTURE_WIDTH(CAPTURE_WIDTH))
		`endif
		u_pll_controller (
			.CLKREF_RETIMED		(clkref_retimed		),	// retimed reference clk   
			.RST			(pll_ctrl_rst		),				// active high reset 
			.FCW_INT		(FCW_INT		),			// integer FCW to the PLL 
			.FCW_FRAC		(pll_fcw_frac		),			// fractional FCW to the PLL		(			), not tested yet 
			.DCO_OPEN_LOOP_CTRL	(DCO_OPEN_LOOP_CTRL	),	// combined CW to the DCO		(			), only valid in open loop    
			.DCO_OPEN_LOOP_EN	(DCO_OPEN_LOOP_EN	),	// switch between open and close loop
			.DLF_KP			(DLF_KP			),		// loop filter Kp for slow mode 
			.DLF_KI			(DLF_KI			),		// loop filter Ki for slow mode
			.COUNT_IN		(count_accum_out	),		// retimed clkref sampled counter input(this is the coarse DCO phase) 
			.FRAC_PHASE_IN		(pll_frac_phase_in	),		// retimed clkref sampled DLTDC output(this is the super-fine DCO phase)  
			.FINE_LOCK_ENABLE	(FINE_LOCK_ENABLE	),
			.FINE_LOCK_THRESHOLD	(FINE_LOCK_THRESHOLD	),
			.FINE_LOCK_COUNT	(FINE_LOCK_COUNT	),
			.FREQ_LOCK_RST		(freq_lock_rst		),
			.FREQ_LOCK_THRESHOLD	(FREQ_LOCK_THRESHOLD	),
			.FREQ_LOCK_COUNT	(FREQ_LOCK_COUNT	),
			.CAPTURE_MUX_SEL	(CAPTURE_MUX_SEL	),	// Select among different internal signals to view for testing purposes.
			.DITHER_EN		(DITHER_EN		),
			.CLK_DITHER		(dco_clk_div4		),
			.EMBTDC_OFFSET		(embtdc_offset_final	),
			.DCO_CCW_OV		(DCO_CCW_OV		),		// OUTPUT: coarse CW to the DCO  (thermal) 
			.DCO_CCW_OV_VAL		(DCO_CCW_OV_VAL_therm	),		// 052921 
			.DCO_FCW_MAX_LIMIT	(DCO_FCW_MAX_LIMIT	),		// OUTPUT: fine CW to the DCO (thermal)
                                                                        
			.ref_phase_ramp_frac	(ref_phase_ramp_frac	),     // 053121
 
			.SSC_EN			(SSC_EN			),
			.SSC_REF_COUNT		(SSC_REF_COUNT		),
			.SSC_STEP		(SSC_STEP		),
			.SSC_SHIFT		(SSC_SHIFT		),
                                                  
			.CS_PLL_CTRL_OV		(CS_PLL_CTRL_OV		), // v 053121
			.cs_pll_ctrl_user	(cs_pll_ctrl_user	), // 
			.cs_pll_ctrl		(cs_pll_ctrl		), // ^

			.DCO_FCW_MAX_LIMIT_HIT	(DCO_FCW_MAX_LIMIT_HIT  ),		// OUTPUT: fine CW to the DCO (thermal)
			.DCO_CCW_OUT		(dco_ccw		),		// OUTPUT: coarse CW to the DCO  (thermal) 
			.DCO_FCW_OUT		(dco_fcw		),		// OUTPUT: fine CW to the DCO (thermal)
			.DCO_FCBW_OUT		(dco_fcbw		),		// OUTPUT: fine CW to the DCO (thermal)
			.FINE_LOCK_DETECT	(fine_lock_detect	),	// OUTPUT: lock detect		(			), goes high when error is within lock_thsh		(			), also if goes high		(			), PLL switches to slow mode. 
			.CAPTURE_MUX_OUT	(CAPTURE_MUX_OUT	));	// OUTPUT: The internal signal selected to view as an output. 


	BUFH_X14N_A10P5PP84TR_C14 clkref_buf (.Y(clkref_tdc_in), .A(CLK_REF)); // 050921 
	tstdc_controller #(
			//.TIME_SCALE			( TIME_SCALE			),
			.TDC_COUNT_ACCUM_WIDTH		( TDC_COUNT_ACCUM_WIDTH 	),	
			.TDC_NUM_PHASE_LATCH		( TDC_NUM_PHASE_LATCH		),
			.TDC_NUM_RETIME_CYCLES		( TDC_NUM_RETIME_CYCLES		),
			.TDC_NUM_RETIME_DELAYS		( TDC_NUM_RETIME_DELAYS		),
			.TDC_NUM_COUNTER_DIVIDERS	( TDC_NUM_COUNTER_DIVIDERS	),
			.DLTDC_NUM_PH			( DLTDC_NUM_PH			))
	u_tstdc_controller(
			.CLKREF_IN			(clkref_tdc_in			), 
			.DCO_RAW_PH			(phases_proc			),
			// pre-dltdc                     
			.pre_ls_ref_CC_bin_user		(pre_ls_ref_CC_bin_user		),
			.pre_ls_ref_FC_bin_user		(pre_ls_ref_FC_bin_user		),
			.post_ls_ref_CC_bin_user	(post_ls_ref_CC_bin_user	),
			.post_ls_ref_FC_bin_user	(post_ls_ref_FC_bin_user	),
			.pre_es_fb_CC_bin_user		(pre_es_fb_CC_bin_user		),
			.pre_es_fb_FC_bin_user		(pre_es_fb_FC_bin_user		),
			.post_es_fb_CC_bin_user		(post_es_fb_CC_bin_user		),
			.post_es_fb_FC_bin_user		(post_es_fb_FC_bin_user		),
			// dltdc                        
			.CC_fb				(CC_fb				),
			.FC_fb				(FC_fb				),
			.CC_ref				(CC_ref				),
			.FC_ref				(FC_ref				),
			// tstdc_counter               
			.RST				(tstdc_rst			), 
			.CLKREF_RETIMED_OUT		(clkref_retimed			),
			.DCO_CLK_DIV4			(dco_clk_div4			), 
			.EMBTDC_OUT			(embtdc_out			),
			.DLTDC_OUT			(dltdc_out			),
			.EMBTDC_LUT			(tstdc_embtdc_lut		),
			.EMB_DLTDC_MAP_LUT		(tstdc_emb_dltdc_map_lut	), // 052221 update
			.DLTDC_LUT			(tstdc_dltdc_lut		),
			.dltdc_idx			(dltdc_idx			), //053121
			.TSTDC_CALIB			(tstdc_calib			),
			.TSTDC_CALIB_DONE_RECIEVE	(tstdc_calib_done_recieve	),
			.TSTDC_CALIB_STATUS		(TSTDC_CALIB_STATUS		), // 052321 update
			.TSTDC_CALIB_DONE_OUT		(tstdc_calib_done		),
			.TSTDC_CALIB_BROKE_OUT		(TSTDC_CALIB_BROKE		),
			.TSTDC_CALIB_EDGE_IDX		(edge_cnt_g			), // 060121
			.dltdc_out_min_reg_export	(dltdc_out_min_reg_export	),
			// calibration overwrite values
			.CS_TSTDC_OV			(CS_TSTDC_OV			), // v 053121
			.cs_tstdc_user			(cs_tstdc_user			), // ^
			.cs_tstdc			(cs_tstdc			), // ^

			.pre_ls_ref_CC_ov		(pre_ls_ref_CC_ov		),
			.pre_ls_ref_FC_ov		(pre_ls_ref_FC_ov		),
			.post_ls_ref_CC_ov		(post_ls_ref_CC_ov		),
			.post_ls_ref_FC_ov		(post_ls_ref_FC_ov		),
			.pre_es_fb_CC_ov		(pre_es_fb_CC_ov		),
			.pre_es_fb_FC_ov		(pre_es_fb_FC_ov		),
			.post_es_fb_CC_ov		(post_es_fb_CC_ov		),
			.post_es_fb_FC_ov		(post_es_fb_FC_ov		),
			.emb_dltdc_map_calib_ov		(emb_dltdc_map_calib_ov		),
			.es_calib_cnt_val		(es_calib_cnt_val		),
			.dltdc_record_cnt_val		(dltdc_record_cnt_val		),
			.dltdc_lsb_int_cnt_val		(dltdc_lsb_int_cnt_val		),
			.dltdc_lsb_int_margin		(dltdc_lsb_int_margin		),
			// outputs
			.pre_ls_ref_CC_bin_final	(pre_ls_ref_CC_bin_final	), // v 050521: bookmark
			.pre_ls_ref_FC_bin_final	(pre_ls_ref_FC_bin_final	),
			.post_ls_ref_CC_bin_final	(post_ls_ref_CC_bin_final	),
			.post_ls_ref_FC_bin_final	(post_ls_ref_FC_bin_final	),
			.pre_es_fb_CC_bin_final		(pre_es_fb_CC_bin_final		),
			.pre_es_fb_FC_bin_final		(pre_es_fb_FC_bin_final		),
			.post_es_fb_CC_bin_final	(post_es_fb_CC_bin_final	),
			.post_es_fb_FC_bin_final	(post_es_fb_FC_bin_final	), // ^ 050521
			.dltdc_out_max_final_rm_lsb	(dltdc_out_max_final_rm_lsb	),
			.COUNT_ACCUM_OUT		(count_accum_out		));

	ble_dco u_ble_dco (
			.PH_out		(phases_proc	), 
			.CC		(dco_ccw	), 
			.FC		(dco_fcw_g	), // 060221 
			.FCB		(dco_fcbw_g	), // 060221 
			.osc_en		(OSC_EN	), 
			.CLK_OUT	(dco_clk_out	), // 060421 
//			.SCPA_CLK	(SCPA_OUT	), 
			.clk		(dco_clk	), 
			.dum_in		(dco_dum_in	), 
			.dum_out	(dco_dum_out	));
	div_buf u_div_buf (
			.CLK_IN		(dco_clk_out	), 
			.SCPA_CLK_EN	(SCPA_CLK_EN	), 
			.CLK_OUT_EN	(CLK_OUT_EN	), 
			.div_sel	(DIV_SEL	), 
			.RST		(RST		), 
			.clk		(divbuf_dum_clk	), 
			.dum_in		(divbuf_dum_in	), 
			.dum_out	(divbuf_dum_out	)); 
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
				//bin1 = i;
				bin1 = bin1 + 1;
			end
		end
	end

	always @(bin1) begin
		binout = bin1;
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

