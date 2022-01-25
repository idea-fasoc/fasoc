// ble_top

module ble_top (
	// TOP
	input	[5:0]	PLL_RST_CNT_COND,
//	input RF_EXT,

	// pll_top
@@		input [2:0] pre_ls_ref_CC_bin_user,
@@		input [5:0] pre_ls_ref_FC_bin_user,
@@		input [2:0] post_ls_ref_CC_bin_user,
@@		input [5:0] post_ls_ref_FC_bin_user,
@@		input [14:0] pre_es_fb_CC_bin_user,
@@		input [29:0] pre_es_fb_FC_bin_user,
@@		input [2:0] post_es_fb_CC_bin_user,
@@		input [5:0] post_es_fb_FC_bin_user,
	//input [39:0] EMBTDC_LUT_USER, // for synth/apr
	//input [399:0] DLTDC_LUT_USER, // for synth/apr
	//input [39:0] EMB_DLTDC_MAP_LUT_USER, // for synth/apr
@@		input [@nM:0][7:0] EMBTDC_LUT_USER, // 4 
	input [49:0][7:0] DLTDC_LUT_USER, // for beh 
@@		input [@NM:0][7:0] EMB_DLTDC_MAP_LUT_USER, // 4 
	input [6:0] dltdc_total_max_user,
	input [8:0] es_calib_cnt_val,
	input [8:0] dltdc_record_cnt_val,
	input [8:0] dltdc_lsb_int_cnt_val,
	input [8:0] dltdc_lsb_int_margin,
@@		input [@fc:0] CC_fb_bin, // 4
@@		input [@rc:0] CC_ref_bin, // 4
@@		input [@ff:0] FC_fb_bin, // 5
@@		input [@rf:0] FC_ref_bin,
	input [6:0] FCW_INT,
	input [8:0] FCW_FRAC,
	input [15:0] DCO_OPEN_LOOP_CTRL,
	input [11:0] DLF_KP,
	input [11:0] DLF_KI,
	input [3:0] CAPTURE_MUX_SEL,
	input [15:0] FINE_LOCK_THRESHOLD,
	input [15:0] FREQ_LOCK_THRESHOLD,
	input [8:0] FREQ_LOCK_COUNT,
	input [8:0] FINE_LOCK_COUNT,
	input [11:0] SSC_REF_COUNT,
	input [3:0] SSC_SHIFT,
	input [3:0] SSC_STEP,
@@		input [6:0] DCO_CCW_OV_VAL,
@@		input [8:0] DCO_FCW_MAX_LIMIT,
	output [2:0] cs_pll,
	output [2:0] ns_pll,
	output [39:0] EMBTDC_CALIB_MIN_REG,
	//output [39:0] EMBTDC_CALIB_LUT_RAW, // for synth/apr
	output [4:0][7:0] EMBTDC_CALIB_LUT_RAW, // for beh
	output [24:0] CAPTURE_MUX_OUT,
@@		output [2:0] pre_ls_ref_CC_bin_final,
@@		output [5:0] pre_ls_ref_FC_bin_final,
@@		output [2:0] post_ls_ref_CC_bin_final,
@@		output [5:0] post_ls_ref_FC_bin_final,
@@		output [14:0] pre_es_fb_CC_bin_final,
@@		output [29:0] pre_es_fb_FC_bin_final,
@@		output [2:0] post_es_fb_CC_bin_final,
@@		output [5:0] post_es_fb_FC_bin_final,
	output	TSTDC_CALIB_BROKE,
	output [4:0] TSTDC_CALIB_STATUS,
	input [8:0] DIV_SEL,
	input CLK_REF,
	input RST,
	input TSTDC_CALIB,
	input pre_ls_ref_CC_ov,
	input pre_ls_ref_FC_ov,
	input post_ls_ref_CC_ov,
	input post_ls_ref_FC_ov,
	input pre_es_fb_CC_ov,
	input pre_es_fb_FC_ov,
	input post_es_fb_CC_ov,
	input post_es_fb_FC_ov,
	input EMB_DLTDC_MAP_LUT_OV,
	input DLTDC_LUT_OV,
	input DLTDC_TOTAL_MAX_OV,
	input USE_EMBTDC,
	input DCO_OPEN_LOOP_EN,
	input DITHER_EN,
	input FINE_LOCK_ENABLE,
	input SSC_EN,
	input DCO_CCW_OV,
	input OSC_EN,
//	input SCPA_CLK_EN, 
	input CLK_OUT_EN,
	output DCO_FCW_MAX_LIMIT_HIT,
	output FINE_LOCK_DETECT,
	output PLL_LOCKED,
	input	 	CS_PLL_OV, // v 053121
	input [2:0] 	cs_pll_user,
	input        	CS_PLL_CTRL_OV,
	input [1:0] 	cs_pll_ctrl_user,
	input        	CS_TSTDC_OV,
	input [2:0] 	cs_tstdc_user,  
	input		DLTDC_FRAC_CALIB_EN,
	input	[6:0]	idx_ref_phase_ramp_frac_avg,	
	input	[3:0]	cnt_ref_frac_accum_val_logtwo,
	input	[8:0]		embtdc_offset_user, // v 060121
	input					EMBTDC_OFFSET_OV, // 
	input					EDGE_CNT_OV,
	input	[2:0]				edge_cnt_user, // ^ 060121
	input 	[8:0]		DCO_FCW_OV_VAL, // 060221
	input 					DCO_FCW_OV, // 060221

	output	[2:0]	cs_tstdc, 
	output	[1:0]	cs_pll_ctrl, 
	output	[10:0]	ref_phase_ramp_frac_avg_probe,	
	output	[3:0]	dltdc_out_max_final_bin_out, // ^ 053121 : for debug

	// scpa
	input						PA_STAND_ALONE, // 0929 update
	input	[31:0]					SCPA_SEL,
	output						SCPA_OUT,

	// GFSK_MOD
	input						EN_OV,
	input						GFSK_EN,
	input [8:0] 				VC_CTRL_INIT,
	input [8:0] 					PKT_LENGTH,
	input [1:0] 					DATA_INIT,
	input [511:0] 					DATA,
	input [8:0] 				MOD_0_0,			
	input [8:0] 				MOD_0_1,			
	input [8:0] 				MOD_0_2,			
	input [8:0] 				MOD_0_3,			
	input [8:0] 				MOD_0_4,			
	input [8:0] 				MOD_0_5,			
	input [8:0] 				MOD_0_6,			
	input [8:0] 				MOD_0_7,			
	input [8:0] 				MOD_1_0,			
	input [8:0] 				MOD_1_1,			
	input [8:0] 				MOD_1_2,			
	input [8:0] 				MOD_1_3,			
	input [8:0] 				MOD_1_4,			
	input [8:0] 				MOD_1_5,			
	input [8:0] 				MOD_1_6,			
	input [8:0] 				MOD_1_7,			
	input [8:0] 				MOD_2_0,			
	input [8:0] 				MOD_2_1,			
	input [8:0] 				MOD_2_2,			
	input [8:0] 				MOD_2_3,			
	input [8:0] 				MOD_2_4,			
	input [8:0] 				MOD_2_5,			
	input [8:0] 				MOD_2_6,			
	input [8:0] 				MOD_2_7,			
	input [8:0] 				MOD_3_0,			
	input [8:0] 				MOD_3_1,			
	input [8:0] 				MOD_3_2,			
	input [8:0] 				MOD_3_3,			
	input [8:0] 				MOD_3_4,			
	input [8:0] 				MOD_3_5,			
	input [8:0] 				MOD_3_6,			
	input [8:0] 				MOD_3_7,			
	input [8:0] 				MOD_4_0,			
	input [8:0] 				MOD_4_1,			
	input [8:0] 				MOD_4_2,			
	input [8:0] 				MOD_4_3,			
	input [8:0] 				MOD_4_4,			
	input [8:0] 				MOD_4_5,			
	input [8:0] 				MOD_4_6,			
	input [8:0] 				MOD_4_7,			
	input [8:0] 				MOD_5_0,			
	input [8:0] 				MOD_5_1,			
	input [8:0] 				MOD_5_2,			
	input [8:0] 				MOD_5_3,			
	input [8:0] 				MOD_5_4,			
	input [8:0] 				MOD_5_5,			
	input [8:0] 				MOD_5_6,			
	input [8:0] 				MOD_5_7,			
	input [8:0] 				MOD_6_0,			
	input [8:0] 				MOD_6_1,			
	input [8:0] 				MOD_6_2,			
	input [8:0] 				MOD_6_3,			
	input [8:0] 				MOD_6_4,			
	input [8:0] 				MOD_6_5,			
	input [8:0] 				MOD_6_6,			
	input [8:0] 				MOD_6_7,			
	input [8:0] 				MOD_7_0,			
	input [8:0] 				MOD_7_1,			
	input [8:0] 				MOD_7_2,			
	input [8:0] 				MOD_7_3,			
	input [8:0] 				MOD_7_4,			
	input [8:0] 				MOD_7_5,			
	input [8:0] 				MOD_7_6,			
	input [8:0] 				MOD_7_7,			

	// top_fsm
//	input     				CONT_MOD,		 
	input					TOP_FSM_BYPASS,
	input					EN_PA_USER,	// 0929 update
	input					TRANS_MODE,
	input					PLL_LOCKED_OV,
	input					START_TX,
	input					DEBUG_MODE,
	input [13:0]				PLL_CNT,	// 0929 update 
	input [9:0]				PA_CNT 
	);


// ANALOG CORE
	parameter DCO_FBASE = 2.30e+09;	//scale
	parameter DCO_OFFSET = 0;
	parameter DCO_CSTEP = 5.5e+06;	// ble_test 
	parameter DCO_FSTEP = 180e+03;	// ble_test 
	parameter dco_center_freq=2.4e9;

	logic     				CONT_MOD;		// 1015 
// internal signals	
	logic      					MOD_ON;		 
	logic						CLK_8M;
	logic      					PLL_CAL_DONE;		 
	logic     					EN_PA;		 
	logic     					EN_PLL;		 

	logic						pa_stand_alone_g;
	logic						pa_en; // 0929 update
	logic						top_fsm_pll_rst;	
	logic						pll_scpa_out;
	logic 		[8:0]				pll_fcw_frac;  
	logic 		[8:0]				gfsk_mod_pll_fcw_frac;  
	logic		[5:0]				pll_rst_cnt;
	logic						pll_rst;
	logic						clkref_pll_in;
	logic						clkref_d0;
	logic						clkref_d1;
	logic						clkref_freq_div;
	logic						pll_osc_en;

//****************************************************************************************\\
//                              enable signals                                             \\
//****************************************************************************************\\

	assign	pll_osc_en 	= (TOP_FSM_BYPASS) ? OSC_EN : EN_PLL ;
	assign	pll_rst		= (TOP_FSM_BYPASS) ? RST : top_fsm_pll_rst; 
	assign 	pll_fcw_frac	= (TOP_FSM_BYPASS) ? FCW_FRAC: gfsk_mod_pll_fcw_frac;
	assign 	pa_en		= (TOP_FSM_BYPASS) ? EN_PA_USER: EN_PA;
	assign  pa_stand_alone_g = (pa_en)? 0: PA_STAND_ALONE; 

	always @(posedge CLK_REF or posedge RST) begin
		if (RST) begin
			top_fsm_pll_rst <= 1'b1;
			pll_rst_cnt <= 1'b0;
		// pll en/disable	
		end else if (EN_PLL) begin
			if (pll_rst_cnt < PLL_RST_CNT_COND) begin
				pll_rst_cnt <= pll_rst_cnt + 1 ;
			end else begin
				top_fsm_pll_rst <= 0;
			end
		end else if (~EN_PLL || ~EN_PA) begin
			top_fsm_pll_rst <= 1'b1;
			pll_rst_cnt <= 1'b0;
		end
	end

//****************************************************************************************\\
//                              Submodules                                                \\
//****************************************************************************************\\

	BUFH_X14N_A10P5PP84TR_C14 clkref_buf (.Y(clkref_pll_in), .A(CLK_REF)); // 1015 update
	BUFH_X14N_A10P5PP84TR_C14 clkref_buf4 (.Y(clkref_pll_in), .A(CLK_REF)); // 1015 update


	BUFH_X2N_A10P5PP84TR_C14 clkref_buf1 (.Y(clkref_d0), .A(CLK_REF)); // 1015 update
	BUFH_X4N_A10P5PP84TR_C14 clkref_buf2 (.Y(clkref_d1), .A(clkref_d0)); // 1015 update
	BUFH_X4N_A10P5PP84TR_C14 clkref_buf3 (.Y(clkref_freq_div), .A(clkref_d1)); // 1015 update
	ble_pll_top u_ble_pll_top(
		.CLK_REF			(clkref_pll_in			),
		.CS_PLL_OV			(CS_PLL_OV			), // v 0531
		.cs_pll_user			(cs_pll_user			),
		.CS_PLL_CTRL_OV			(CS_PLL_CTRL_OV			),
		.cs_pll_ctrl_user		(cs_pll_ctrl_user		),
		.dltdc_out_max_final_bin_out	(dltdc_out_max_final_bin_out	), 
		.CS_TSTDC_OV			(CS_TSTDC_OV			),
		.cs_tstdc_user			(cs_tstdc_user			), 
		.cnt_ref_frac_accum_val_logtwo  (cnt_ref_frac_accum_val_logtwo	), 
		.DLTDC_FRAC_CALIB_EN		(DLTDC_FRAC_CALIB_EN		),
		.cs_tstdc			(cs_tstdc   			), 
		.cs_pll_ctrl			(cs_pll_ctrl			), 
		.idx_ref_phase_ramp_frac_avg	(idx_ref_phase_ramp_frac_avg	), // ^ 053121	
		.embtdc_offset_user		(embtdc_offset_user		), // v 060121
		.EMBTDC_OFFSET_OV		(EMBTDC_OFFSET_OV		), // 
		.EDGE_CNT_OV			(EDGE_CNT_OV			),
		.edge_cnt_user			(edge_cnt_user			), // ^ 060121
		.DCO_FCW_OV_VAL			(DCO_FCW_OV_VAL			), // 060221
		.ref_phase_ramp_frac_avg_probe	(ref_phase_ramp_frac_avg_probe	),	
		.DCO_FCW_OV			(DCO_FCW_OV			), // 060221
		.pre_ls_ref_CC_bin_user		(pre_ls_ref_CC_bin_user		),
		.pre_ls_ref_FC_bin_user		(pre_ls_ref_FC_bin_user		),
		.post_ls_ref_CC_bin_user	(post_ls_ref_CC_bin_user	),
		.post_ls_ref_FC_bin_user	(post_ls_ref_FC_bin_user	),
		.pre_es_fb_CC_bin_user		(pre_es_fb_CC_bin_user		),
		.pre_es_fb_FC_bin_user		(pre_es_fb_FC_bin_user		),
		.post_es_fb_CC_bin_user		(post_es_fb_CC_bin_user		),
		.post_es_fb_FC_bin_user		(post_es_fb_FC_bin_user		),
		.EMBTDC_LUT_USER		(EMBTDC_LUT_USER		),
		.DLTDC_LUT_USER			(DLTDC_LUT_USER			),
		.EMB_DLTDC_MAP_LUT_USER		(EMB_DLTDC_MAP_LUT_USER		),
		.dltdc_total_max_user		(dltdc_total_max_user		),
		.es_calib_cnt_val		(es_calib_cnt_val		),
		.dltdc_record_cnt_val		(dltdc_record_cnt_val		),
		.dltdc_lsb_int_cnt_val		(dltdc_lsb_int_cnt_val		),
		.dltdc_lsb_int_margin		(dltdc_lsb_int_margin		),
		.CC_fb_bin			(CC_fb_bin			),
		.CC_ref_bin			(CC_ref_bin			),
		.FC_fb_bin			(FC_fb_bin			),
		.FC_ref_bin			(FC_ref_bin			),
		.FCW_INT			(FCW_INT			),
		.FCW_FRAC			(pll_fcw_frac			),
		.DCO_OPEN_LOOP_CTRL		(DCO_OPEN_LOOP_CTRL		),
		.DLF_KP				(DLF_KP				),
		.DLF_KI				(DLF_KI				),
		.CAPTURE_MUX_SEL		(CAPTURE_MUX_SEL		),
		.FINE_LOCK_THRESHOLD		(FINE_LOCK_THRESHOLD		),
		.FREQ_LOCK_THRESHOLD		(FREQ_LOCK_THRESHOLD		),
		.FREQ_LOCK_COUNT		(FREQ_LOCK_COUNT		),
		.FINE_LOCK_COUNT		(FINE_LOCK_COUNT		),
		.SSC_REF_COUNT			(SSC_REF_COUNT			),
		.SSC_SHIFT			(SSC_SHIFT			),
		.SSC_STEP			(SSC_STEP			),
		.DCO_CCW_OV_VAL			(DCO_CCW_OV_VAL			),
 
		.DCO_FCW_MAX_LIMIT		(DCO_FCW_MAX_LIMIT		),
		.cs_pll				(cs_pll				),
		.ns_pll				(ns_pll				),
		.EMBTDC_CALIB_MIN_REG		(EMBTDC_CALIB_MIN_REG		),
		.EMBTDC_CALIB_LUT_RAW		(EMBTDC_CALIB_LUT_RAW		),
		.CAPTURE_MUX_OUT		(CAPTURE_MUX_OUT		),
		.pre_ls_ref_CC_bin_final	(pre_ls_ref_CC_bin_final	),
		.pre_ls_ref_FC_bin_final	(pre_ls_ref_FC_bin_final	),
		.post_ls_ref_CC_bin_final	(post_ls_ref_CC_bin_final	),
		.post_ls_ref_FC_bin_final	(post_ls_ref_FC_bin_final	),
		.pre_es_fb_CC_bin_final		(pre_es_fb_CC_bin_final		),
		.pre_es_fb_FC_bin_final		(pre_es_fb_FC_bin_final		),
		.post_es_fb_CC_bin_final	(post_es_fb_CC_bin_final	),
		.post_es_fb_FC_bin_final	(post_es_fb_FC_bin_final	),
		.TSTDC_CALIB_BROKE		(TSTDC_CALIB_BROKE		),
		.TSTDC_CALIB_STATUS		(TSTDC_CALIB_STATUS		),
		.RST				(pll_rst			),
		.TSTDC_CALIB			(TSTDC_CALIB			),
		.pre_ls_ref_CC_ov		(pre_ls_ref_CC_ov		),
		.pre_ls_ref_FC_ov		(pre_ls_ref_FC_ov		),
		.post_ls_ref_CC_ov		(post_ls_ref_CC_ov		),
		.post_ls_ref_FC_ov		(post_ls_ref_FC_ov		),
		.pre_es_fb_CC_ov		(pre_es_fb_CC_ov		),
		.pre_es_fb_FC_ov		(pre_es_fb_FC_ov		),
		.post_es_fb_CC_ov		(post_es_fb_CC_ov		),
		.post_es_fb_FC_ov		(post_es_fb_FC_ov		),
		.EMB_DLTDC_MAP_LUT_OV		(EMB_DLTDC_MAP_LUT_OV		),
		.DLTDC_LUT_OV			(DLTDC_LUT_OV			),
		.DLTDC_TOTAL_MAX_OV		(DLTDC_TOTAL_MAX_OV		),
		.USE_EMBTDC			(USE_EMBTDC			),
		.DCO_OPEN_LOOP_EN		(DCO_OPEN_LOOP_EN		),
		.DITHER_EN			(DITHER_EN			),
		.FINE_LOCK_ENABLE		(FINE_LOCK_ENABLE		),
		.SSC_EN				(SSC_EN				),
		.DCO_CCW_OV			(DCO_CCW_OV			),
		.OSC_EN				(pll_osc_en			),
		.SCPA_CLK_EN			(pa_en			),
		.CLK_OUT_EN			(CLK_OUT_EN			),
		.DIV_SEL			(DIV_SEL			),
		.DCO_FCW_MAX_LIMIT_HIT		(DCO_FCW_MAX_LIMIT_HIT		),
		.FINE_LOCK_DETECT		(FINE_LOCK_DETECT		),
		.PLL_LOCKED			(PLL_LOCKED			));

	// SCPA
	SCPA_Final u_scpa (
		.PA_TEST		(pa_stand_alone_g	),
		.SEL			(SCPA_SEL		));
	//	.RF			(pll_scpa_out		), // this will be a power net in implementation
//		.VO			(SCPA_OUT		));

	// GFSK_MOD
	GFSK_CTRL_V2	u_gfsk_ctrl_v2 (
		.CLK_8M			(CLK_8M			),
		.RESET			(RST			),
		.PLL_CAL_DONE		(PLL_CAL_DONE		),
		.EN_OV			(EN_OV			),
		.GFSK_EN		(GFSK_EN		),
		.VC_CTRL_INIT		(VC_CTRL_INIT		),
		.CONT_MOD		(CONT_MOD		),	
		.PKT_LENGTH		(PKT_LENGTH		),
		.DATA_INIT		(DATA_INIT		),
		.DATA			(DATA			),
		.VC_CTRL		(gfsk_mod_pll_fcw_frac	),
		.MOD_ON			(MOD_ON			),
		.MOD_0_0		(MOD_0_0		),			
		.MOD_0_1		(MOD_0_1		),			
		.MOD_0_2		(MOD_0_2		),			
		.MOD_0_3		(MOD_0_3		),			
		.MOD_0_4		(MOD_0_4		),			
		.MOD_0_5		(MOD_0_5		),			
		.MOD_0_6		(MOD_0_6		),			
		.MOD_0_7		(MOD_0_7		),			
		.MOD_1_0		(MOD_1_0		),			
		.MOD_1_1		(MOD_1_1		),			
		.MOD_1_2		(MOD_1_2		),			
		.MOD_1_3		(MOD_1_3		),			
		.MOD_1_4		(MOD_1_4		),			
		.MOD_1_5		(MOD_1_5		),			
		.MOD_1_6		(MOD_1_6		),			
		.MOD_1_7		(MOD_1_7		),			
		.MOD_2_0		(MOD_2_0		),			
		.MOD_2_1		(MOD_2_1		),			
		.MOD_2_2		(MOD_2_2		),			
		.MOD_2_3		(MOD_2_3		),			
		.MOD_2_4		(MOD_2_4		),			
		.MOD_2_5		(MOD_2_5		),			
		.MOD_2_6		(MOD_2_6		),			
		.MOD_2_7		(MOD_2_7		),			
		.MOD_3_0		(MOD_3_0		),			
		.MOD_3_1		(MOD_3_1		),			
		.MOD_3_2		(MOD_3_2		),			
		.MOD_3_3		(MOD_3_3		),			
		.MOD_3_4		(MOD_3_4		),			
		.MOD_3_5		(MOD_3_5		),			
		.MOD_3_6		(MOD_3_6		),			
		.MOD_3_7		(MOD_3_7		),			
		.MOD_4_0		(MOD_4_0		),			
		.MOD_4_1		(MOD_4_1		),			
		.MOD_4_2		(MOD_4_2		),			
		.MOD_4_3		(MOD_4_3		),			
		.MOD_4_4		(MOD_4_4		),			
		.MOD_4_5		(MOD_4_5		),			
		.MOD_4_6		(MOD_4_6		),			
		.MOD_4_7		(MOD_4_7		),			
		.MOD_5_0		(MOD_5_0		),			
		.MOD_5_1		(MOD_5_1		),			
		.MOD_5_2		(MOD_5_2		),			
		.MOD_5_3		(MOD_5_3		),			
		.MOD_5_4		(MOD_5_4		),			
		.MOD_5_5		(MOD_5_5		),			
		.MOD_5_6		(MOD_5_6		),			
		.MOD_5_7		(MOD_5_7		),			
		.MOD_6_0		(MOD_6_0		),			
		.MOD_6_1		(MOD_6_1		),			
		.MOD_6_2		(MOD_6_2		),			
		.MOD_6_3		(MOD_6_3		),			
		.MOD_6_4		(MOD_6_4		),			
		.MOD_6_5		(MOD_6_5		),			
		.MOD_6_6		(MOD_6_6		),			
		.MOD_6_7		(MOD_6_7		),			
		.MOD_7_0		(MOD_7_0		),			
		.MOD_7_1		(MOD_7_1		),			
		.MOD_7_2		(MOD_7_2		),			
		.MOD_7_3		(MOD_7_3		),			
		.MOD_7_4		(MOD_7_4		),			
		.MOD_7_5		(MOD_7_5		),			
		.MOD_7_6		(MOD_7_6		),			
		.MOD_7_7		(MOD_7_7		));

 
	TOP_FSM_V1  u_top_fsm_v1 (
		.CLK_8M			(CLK_8M			), 
		.RESET			(RST			),
		.TRANS_MODE		(TRANS_MODE		), 
		.PLL_LOCKED		(PLL_LOCKED		), 
		.PLL_LOCKED_OV		(PLL_LOCKED_OV		), 
		.MOD_ON			(MOD_ON			), 
		.START_TX		(START_TX		), 
		.DEBUG_MODE		(DEBUG_MODE		), 
		.PLL_CNT		(PLL_CNT		), 
		.PA_CNT			(PA_CNT			), 
		.PLL_CAL_DONE		(PLL_CAL_DONE		), 
		.CONT_MOD		(CONT_MOD		), 
		.EN_PA			(EN_PA			), 
		.EN_PLL			(EN_PLL			));

	FREQ_DIV u_freq_div	(
		.RESET		(RST		),
		.CLK_40M	(clkref_freq_div	),
		.CLK_8M		(CLK_8M		));


endmodule





