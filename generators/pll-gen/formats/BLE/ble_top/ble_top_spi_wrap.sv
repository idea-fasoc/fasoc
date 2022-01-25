// ble_top_apb

`define APB_BUS_WIDTH 32
`define DATA_APB_WIDTH 16
`define DATA_SPI_WIDTH 16
module ble_top_spi_wrap #(
  parameter APB_ADDR_WIDTH = 12      , // 1003 update
  parameter ID             = 32'hDEAD
) (
  input                            CLK_REF    ,
  input                            SPI_reset  ,
  input                            SS         ,
  input                            SCLK       ,
  input                            MOSI       ,
  output                           MISO       
);

  parameter VC_BITS = 9;

	// ble_top
//	logic RF_EXT;

	// pll_top
	logic [2:0] pre_ls_ref_CC_bin_user;
	logic [5:0] pre_ls_ref_FC_bin_user;
	logic [2:0] post_ls_ref_CC_bin_user;
	logic [5:0] post_ls_ref_FC_bin_user;
	logic [14:0] pre_es_fb_CC_bin_user;
	logic [29:0] pre_es_fb_FC_bin_user;
	logic [2:0] post_es_fb_CC_bin_user;
	logic [5:0] post_es_fb_FC_bin_user;
	logic [39:0] EMBTDC_LUT_USER; // for synth/apr
	logic [399:0] DLTDC_LUT_USER; // for synth/apr
	logic [39:0] EMB_DLTDC_MAP_LUT_USER; // for synth/apr
	//logic [4:0][7:0] EMBTDC_LUT_USER; // for beh 
	//logic [49:0][7:0] DLTDC_LUT_USER; // for beh 
	//logic [4:0][7:0] EMB_DLTDC_MAP_LUT_USER; // for beh 
	logic [6:0] dltdc_total_max_user;
	logic [8:0] es_calib_cnt_val;
	logic [8:0] dltdc_record_cnt_val;
	logic [8:0] dltdc_lsb_int_cnt_val;
	logic [8:0] dltdc_lsb_int_margin;
	logic [4:0] CC_fb_bin;
	logic [4:0] CC_ref_bin;
	logic [5:0] FC_fb_bin;
	logic [5:0] FC_ref_bin;
	logic [6:0] FCW_INT;
	logic [8:0] FCW_FRAC;
	logic [15:0] DCO_OPEN_LOOP_CTRL;
	logic [11:0] DLF_KP;
	logic [11:0] DLF_KI;
	logic [3:0] CAPTURE_MUX_SEL;
	logic [15:0] FINE_LOCK_THRESHOLD;
	logic [15:0] FREQ_LOCK_THRESHOLD;
	logic [8:0] FREQ_LOCK_COUNT;
	logic [8:0] FINE_LOCK_COUNT;
	logic [11:0] SSC_REF_COUNT;
	logic [3:0] SSC_SHIFT;
	logic [3:0] SSC_STEP;
	logic [6:0] DCO_CCW_OV_VAL;
	logic [8:0] DCO_FCW_MAX_LIMIT;
	logic [8:0] DIV_SEL;
	logic RST;
	logic TSTDC_CALIB;
	logic pre_ls_ref_CC_ov;
	logic pre_ls_ref_FC_ov;
	logic post_ls_ref_CC_ov;
	logic post_ls_ref_FC_ov;
	logic pre_es_fb_CC_ov;
	logic pre_es_fb_FC_ov;
	logic post_es_fb_CC_ov;
	logic post_es_fb_FC_ov;
	logic EMB_DLTDC_MAP_LUT_OV;
	logic DLTDC_LUT_OV;
	logic DLTDC_TOTAL_MAX_OV;
	logic USE_EMBTDC;
	logic DCO_OPEN_LOOP_EN;
	logic DITHER_EN;
	logic FINE_LOCK_ENABLE;
	logic SSC_EN;
	logic DCO_CCW_OV;
	logic OSC_EN;
//	logic SCPA_CLK_EN; 
	logic CLK_OUT_EN;
	logic	 	CS_PLL_OV; // v 053121
	logic [2:0] 	cs_pll_user;
	logic        	CS_PLL_CTRL_OV;
	logic [1:0] 	cs_pll_ctrl_user;
	logic        	CS_TSTDC_OV;
	logic [2:0] 	cs_tstdc_user;  
	logic		DLTDC_FRAC_CALIB_EN;
	logic	[6:0]	idx_ref_phase_ramp_frac_avg;	
	logic	[3:0]	cnt_ref_frac_accum_val_logtwo; // ^ inputs
	logic	[2:0]	cs_tstdc; // v outputs 
	logic	[1:0]	cs_pll_ctrl; 
	logic	[10:0]	ref_phase_ramp_frac_avg_probe;	
	logic	[3:0]	dltdc_out_max_final_bin_out; // ^ 053121 : for debug
	logic	[8:0]		embtdc_offset_user; // v 060121
	logic			EMBTDC_OFFSET_OV; // 
	logic			EDGE_CNT_OV;
	logic	[2:0]		edge_cnt_user; // ^ 060121
	logic 	[8:0]		DCO_FCW_OV_VAL; // 060221
	logic 			DCO_FCW_OV; // 060221

	// scpa
	logic						PA_STAND_ALONE; // 0929 update
	logic	[31:0]					SCPA_SEL;

	// GFSK_MOD
	logic						EN_OV;
	logic						GFSK_EN;
	logic [8:0] 				VC_CTRL_INIT;
	logic [8:0] 					PKT_LENGTH;
	logic [1:0] 					DATA_INIT;
	logic [511:0] 					DATA;
	logic [8:0] 				MOD_0_0;			
	logic [8:0] 				MOD_0_1;			
	logic [8:0] 				MOD_0_2;			
	logic [8:0] 				MOD_0_3;			
	logic [8:0] 				MOD_0_4;			
	logic [8:0] 				MOD_0_5;			
	logic [8:0] 				MOD_0_6;			
	logic [8:0] 				MOD_0_7;			
	logic [8:0] 				MOD_1_0;			
	logic [8:0] 				MOD_1_1;			
	logic [8:0] 				MOD_1_2;			
	logic [8:0] 				MOD_1_3;			
	logic [8:0] 				MOD_1_4;			
	logic [8:0] 				MOD_1_5;			
	logic [8:0] 				MOD_1_6;			
	logic [8:0] 				MOD_1_7;			
	logic [8:0] 				MOD_2_0;			
	logic [8:0] 				MOD_2_1;			
	logic [8:0] 				MOD_2_2;			
	logic [8:0] 				MOD_2_3;			
	logic [8:0] 				MOD_2_4;			
	logic [8:0] 				MOD_2_5;			
	logic [8:0] 				MOD_2_6;			
	logic [8:0] 				MOD_2_7;			
	logic [8:0] 				MOD_3_0;			
	logic [8:0] 				MOD_3_1;			
	logic [8:0] 				MOD_3_2;			
	logic [8:0] 				MOD_3_3;			
	logic [8:0] 				MOD_3_4;			
	logic [8:0] 				MOD_3_5;			
	logic [8:0] 				MOD_3_6;			
	logic [8:0] 				MOD_3_7;			
	logic [8:0] 				MOD_4_0;			
	logic [8:0] 				MOD_4_1;			
	logic [8:0] 				MOD_4_2;			
	logic [8:0] 				MOD_4_3;			
	logic [8:0] 				MOD_4_4;			
	logic [8:0] 				MOD_4_5;			
	logic [8:0] 				MOD_4_6;			
	logic [8:0] 				MOD_4_7;			
	logic [8:0] 				MOD_5_0;			
	logic [8:0] 				MOD_5_1;			
	logic [8:0] 				MOD_5_2;			
	logic [8:0] 				MOD_5_3;			
	logic [8:0] 				MOD_5_4;			
	logic [8:0] 				MOD_5_5;			
	logic [8:0] 				MOD_5_6;			
	logic [8:0] 				MOD_5_7;			
	logic [8:0] 				MOD_6_0;			
	logic [8:0] 				MOD_6_1;			
	logic [8:0] 				MOD_6_2;			
	logic [8:0] 				MOD_6_3;			
	logic [8:0] 				MOD_6_4;			
	logic [8:0] 				MOD_6_5;			
	logic [8:0] 				MOD_6_6;			
	logic [8:0] 				MOD_6_7;			
	logic [8:0] 				MOD_7_0;			
	logic [8:0] 				MOD_7_1;			
	logic [8:0] 				MOD_7_2;			
	logic [8:0] 				MOD_7_3;			
	logic [8:0] 				MOD_7_4;			
	logic [8:0] 				MOD_7_5;			
	logic [8:0] 				MOD_7_6;			
	logic [8:0] 				MOD_7_7;			

	// top_fsm
	logic     				CONT_MOD;		 
	logic					TOP_FSM_BYPASS;
	logic					EN_PA_USER;	// 0929 update
	logic					TRANS_MODE;
	logic					PLL_LOCKED_OV;
	logic					START_TX;
	logic					DEBUG_MODE;
	logic [13:0]				PLL_CNT;	// 0929 update 
	logic [9:0]				PA_CNT; 

	// outputs: pll
	logic [2:0] cs_pll;
	logic [2:0] ns_pll;
	logic [39:0] EMBTDC_CALIB_MIN_REG;
	logic [24:0] CAPTURE_MUX_OUT;
	logic [2:0] pre_ls_ref_CC_bin_final;
	logic [5:0] pre_ls_ref_FC_bin_final;
	logic [2:0] post_ls_ref_CC_bin_final;
	logic [5:0] post_ls_ref_FC_bin_final;
	logic [14:0] pre_es_fb_CC_bin_final;
	logic [29:0] pre_es_fb_FC_bin_final;
	logic [2:0] post_es_fb_CC_bin_final;
	logic [5:0] post_es_fb_FC_bin_final;
	logic DCO_FCW_MAX_LIMIT_HIT;
	logic FINE_LOCK_DETECT;
	logic PLL_LOCKED;
	logic						SCPA_OUT;
  	logic [4:0] TSTDC_CALIB_STATUS;
	logic TSTDC_CALIB_BROKE; 

  // pll outputs
  logic        dum_data_out         ;
  logic [39:0] EMBTDC_CALIB_LUT_RAW ; // 0930 update
  logic [ 5:0] PLL_RST_CNT_COND     ;

//SPI slave reg
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI1 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI2 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI3 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI4 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI5 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI6 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI7 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI8 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI9 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI10;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI11;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI12;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI13;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI14;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI15;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI16;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI17;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI18;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI19;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI20;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI21;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI22;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI23;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI24;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI25;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI26;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI27;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI28;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI29;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI30;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI31;
  logic [`DATA_SPI_WIDTH-1:0] REG_DATA_SPI32;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI1  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI2  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI3  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI4  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI5  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI6  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI7  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI8  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI9  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI10 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI11 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI12 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI13 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI14 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI15 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI16 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI17 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI18 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI19 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI20 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI21 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI22 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI23 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI24 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI25 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI26 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI27 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI28 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI29 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI30 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI31 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI32 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI33 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI34 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI35 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI36 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI37 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI38 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI39 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI40 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI41 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI42 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI43 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI44 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI45 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI46 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI47 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI48 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI49 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI50 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI51 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI52 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI53 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI54 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI55 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI56 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI57 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI58 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI59 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI60 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI61 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI62 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI63 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI64 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI65 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI66 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI67 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI68 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI69 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI70 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI71 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI72 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI73 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI74 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI75 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI76 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI77 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI78 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI79 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI80 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI81 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI82 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI83 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI84 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI85 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI86 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI87 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI88 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI89 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI90 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI91 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI92 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI93 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI94 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI95 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI96 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_CFG_SPI97 ;
  logic [`DATA_SPI_WIDTH-1:0] REG_FSM_SPI1  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_FSM_SPI2  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_FSM_SPI3  ;
  logic [`DATA_SPI_WIDTH-1:0] REG_FSM_SPI4  ;
  // input from block
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI1;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI2;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI3;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI4;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI5;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI6;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI7;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI8;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI9;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI10;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI11;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI12;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI13;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI14;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI15;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI16;
  logic [`DATA_SPI_WIDTH-1:0] IN_DATA_SPI17;


  // ble input muxing
  // REG_DATA       // default: 0
  assign DATA = {REG_DATA_SPI32,REG_DATA_SPI31, REG_DATA_SPI30, REG_DATA_SPI29,
    REG_DATA_SPI28, REG_DATA_SPI27, REG_DATA_SPI26, REG_DATA_SPI25,
    REG_DATA_SPI24, REG_DATA_SPI23, REG_DATA_SPI22, REG_DATA_SPI21,
    REG_DATA_SPI20, REG_DATA_SPI19, REG_DATA_SPI18, REG_DATA_SPI17,
    REG_DATA_SPI16, REG_DATA_SPI15, REG_DATA_SPI14, REG_DATA_SPI13,
    REG_DATA_SPI12, REG_DATA_SPI11, REG_DATA_SPI10, REG_DATA_SPI9,
    REG_DATA_SPI8, REG_DATA_SPI7, REG_DATA_SPI6, REG_DATA_SPI5, REG_DATA_SPI4,
    REG_DATA_SPI3, REG_DATA_SPI2, REG_DATA_SPI1} ;

  // REG_CONFIGS
  assign MOD_0_0 = REG_CFG_SPI1[8:0];
  assign MOD_0_1 = {REG_CFG_SPI2[1:0], REG_CFG_SPI1[15:9]};
  assign MOD_0_2 = REG_CFG_SPI2[10:2];
  assign MOD_0_3 = {REG_CFG_SPI3[3:0],REG_CFG_SPI2[15:11]};
  assign MOD_0_4 = REG_CFG_SPI3[12:4];
  assign MOD_0_5 = {REG_CFG_SPI4[5:0],REG_CFG_SPI3[15:13]};
  assign MOD_0_6 = REG_CFG_SPI4[14:6];
  assign MOD_0_7 = {REG_CFG_SPI5[7:0],REG_CFG_SPI4[15]};
  assign MOD_1_0 = {REG_CFG_SPI6[0],REG_CFG_SPI5[15:8]};
  assign MOD_1_1 = REG_CFG_SPI6[9:1];
  assign MOD_1_2 = {REG_CFG_SPI7[2:0],REG_CFG_SPI6[15:10]};
  assign MOD_1_3 = REG_CFG_SPI7[11:3];
  assign MOD_1_4 = {REG_CFG_SPI8[4:0],REG_CFG_SPI7[15:12]};
  assign MOD_1_5 = REG_CFG_SPI8[13:5];
  assign MOD_1_6 = {REG_CFG_SPI9[6:0],REG_CFG_SPI8[15:14]};
  assign MOD_1_7 = REG_CFG_SPI9[15:7];
  assign MOD_2_0 = REG_CFG_SPI10[8:0];
  assign MOD_2_1 = {REG_CFG_SPI11[1:0], REG_CFG_SPI10[15:9]};
  assign MOD_2_2 = REG_CFG_SPI11[10:2];
  assign MOD_2_3 = {REG_CFG_SPI12[3:0],REG_CFG_SPI11[15:11]};
  assign MOD_2_4 = REG_CFG_SPI12[12:4];
  assign MOD_2_5 = {REG_CFG_SPI13[5:0],REG_CFG_SPI12[15:13]};
  assign MOD_2_6 = REG_CFG_SPI13[14:6];
  assign MOD_2_7 = {REG_CFG_SPI14[7:0],REG_CFG_SPI13[15]};
  assign MOD_3_0 = {REG_CFG_SPI15[0],REG_CFG_SPI14[15:8]};
  assign MOD_3_1 = REG_CFG_SPI15[9:1];
  assign MOD_3_2 = {REG_CFG_SPI16[2:0],REG_CFG_SPI15[15:10]};
  assign MOD_3_3 = REG_CFG_SPI16[11:3];
  assign MOD_3_4 = {REG_CFG_SPI17[4:0],REG_CFG_SPI16[15:12]};
  assign MOD_3_5 = REG_CFG_SPI17[13:5];
  assign MOD_3_6 = {REG_CFG_SPI18[6:0],REG_CFG_SPI17[15:14]};
  assign MOD_3_7 = REG_CFG_SPI18[15:7];
  assign MOD_4_0 = REG_CFG_SPI19[8:0];
  assign MOD_4_1 = {REG_CFG_SPI20[1:0], REG_CFG_SPI19[15:9]};
  assign MOD_4_2 = REG_CFG_SPI20[10:2];
  assign MOD_4_3 = {REG_CFG_SPI21[3:0],REG_CFG_SPI20[15:11]};
  assign MOD_4_4 = REG_CFG_SPI21[12:4];
  assign MOD_4_5 = {REG_CFG_SPI22[5:0],REG_CFG_SPI21[15:13]};
  assign MOD_4_6 = REG_CFG_SPI22[14:6];
  assign MOD_4_7 = {REG_CFG_SPI23[7:0],REG_CFG_SPI22[15]};
  assign MOD_5_0 = {REG_CFG_SPI24[0],REG_CFG_SPI23[15:8]};
  assign MOD_5_1 = REG_CFG_SPI24[9:1];
  assign MOD_5_2 = {REG_CFG_SPI25[2:0],REG_CFG_SPI24[15:10]};
  assign MOD_5_3 = REG_CFG_SPI25[11:3];
  assign MOD_5_4 = {REG_CFG_SPI26[4:0],REG_CFG_SPI25[15:12]};
  assign MOD_5_5 = REG_CFG_SPI26[13:5];
  assign MOD_5_6 = {REG_CFG_SPI27[6:0],REG_CFG_SPI26[15:14]};
  assign MOD_5_7 = REG_CFG_SPI27[15:7];
  assign MOD_6_0 = REG_CFG_SPI28[8:0];
  assign MOD_6_1 = {REG_CFG_SPI29[1:0], REG_CFG_SPI28[15:9]};
  assign MOD_6_2 = REG_CFG_SPI29[10:2];
  assign MOD_6_3 = {REG_CFG_SPI30[3:0],REG_CFG_SPI29[15:11]};
  assign MOD_6_4 = REG_CFG_SPI30[12:4];
  assign MOD_6_5 = {REG_CFG_SPI31[5:0],REG_CFG_SPI30[15:13]};
  assign MOD_6_6 = REG_CFG_SPI31[14:6];
  assign MOD_6_7 = {REG_CFG_SPI32[7:0],REG_CFG_SPI31[15]};
  assign MOD_7_0 = {REG_CFG_SPI33[0],REG_CFG_SPI32[15:8]};
  assign MOD_7_1 = REG_CFG_SPI33[9:1];
  assign MOD_7_2 = {REG_CFG_SPI34[2:0],REG_CFG_SPI33[15:10]};
  assign MOD_7_3 = REG_CFG_SPI34[11:3];
  assign MOD_7_4 = {REG_CFG_SPI35[4:0],REG_CFG_SPI34[15:12]};
  assign MOD_7_5 = REG_CFG_SPI35[13:5];
  assign MOD_7_6 = {REG_CFG_SPI36[6:0],REG_CFG_SPI35[15:14]};
  assign MOD_7_7 = REG_CFG_SPI36[15:7];

  // pll input muxing
  // reg 37 - default values: {0000_0000_0000_0011} 
  assign RST                    = REG_CFG_SPI37[0] ;   // 1
  assign TSTDC_CALIB            = REG_CFG_SPI37[1] ;   // 1
  assign pre_ls_ref_CC_ov	= REG_CFG_SPI37[2] ;
  assign pre_ls_ref_FC_ov	= REG_CFG_SPI37[3] ;
  assign post_ls_ref_CC_ov	= REG_CFG_SPI37[4] ;
  assign post_ls_ref_FC_ov	= REG_CFG_SPI37[5] ;
  assign pre_es_fb_CC_ov	= REG_CFG_SPI37[6] ;
  assign pre_es_fb_FC_ov	= REG_CFG_SPI37[7] ;
  assign EMBTDC_LUT_OV		= REG_CFG_SPI37[8] ; // obsolete
  assign EMB_DLTDC_MAP_LUT_OV	= REG_CFG_SPI37[9] ;
  assign DLTDC_LUT_OV		= REG_CFG_SPI37[10] ;
  assign post_es_fb_CC_ov	= REG_CFG_SPI37[11] ;
  assign post_es_fb_FC_ov	= REG_CFG_SPI37[12] ;
  assign DLTDC_TOTAL_MAX_OV	= REG_CFG_SPI37[14] ;

  // reg 38 - def: {1110, 001, 0000_00, 011} - version 0
  // reg 38 - def: {1100, 000, 0101_00, 011} - version 1
  // reg 38 - def(3): {1110, 001, 0000_00, 011} - version 2 : from analog sim : for tapeout (0602)
  assign pre_ls_ref_CC_bin_user = REG_CFG_SPI38[2:0]; // 011
  assign pre_ls_ref_FC_bin_user = REG_CFG_SPI38[8:3]; // 000000
  assign post_ls_ref_CC_bin_user = REG_CFG_SPI38[11:9]; // 001 
  assign post_ls_ref_FC_bin_user[3:0] = REG_CFG_SPI38[15:12]; // 1110

  // reg 39 - def: {0110_1101_1011_01, 01} - version 0
  // reg 39 - def: {1101_1011_0110_11, 11} - version 1
  // reg 39 - def: {1101_1011_0111_00, 01} - version 2 (0602)
  assign post_ls_ref_FC_bin_user[5:4] = REG_CFG_SPI39[1:0]; // 01
  assign pre_es_fb_CC_bin_user[13:0] = REG_CFG_SPI39[15:2]; // 11011011011100

  // reg 40 - def: {000_110000_110000, 1} - version 0
  // reg 40 - def: {000_001000_001000, 0} - version 1
  // reg 40 - def: {000_110000_100111, 0} - version 2 (0602)
  assign pre_es_fb_CC_bin_user[14] = REG_CFG_SPI40[0]; // 0
  assign pre_es_fb_FC_bin_user[14:0] = REG_CFG_SPI40[15:1]; // 000_110000_100111

  // reg 41 - def: {1, 110000_110000_110} - version 0
  // reg 41 - def: {0, 001000_001000_001} - version 1
  // reg 41 - def: {1, 110000_110000_110} - version 2 (0602)
  assign pre_es_fb_FC_bin_user[29:15] = REG_CFG_SPI41[14:0]; // 110000_110000_110
  assign post_es_fb_CC_bin_user[0] = REG_CFG_SPI41[15]; // 1

  // reg 42 - def: {100, 01010, 111111, 01}
  // reg 42 - def: {100, 01010, 000000, 10} - version 2 (0602)
  assign post_es_fb_CC_bin_user[2:1] = REG_CFG_SPI42[1:0]; // 10
  assign post_es_fb_FC_bin_user = REG_CFG_SPI42[7:2]; // 000000
  assign CC_fb_bin = REG_CFG_SPI42[12:8]; // 01010 
  assign CC_ref_bin[2:0] = REG_CFG_SPI42[15:13]; // 100

  // reg 43 - def: {00,101000, 000000, 10} - version
  assign CC_ref_bin[4:3] = REG_CFG_SPI43[1:0]; // 10
  assign FC_fb_bin = REG_CFG_SPI43[7:2]; // 000000
  assign FC_ref_bin = REG_CFG_SPI43[13:8]; // 101000
  assign dltdc_lsb_int_cnt_val[1:0] = REG_CFG_SPI43[15:14]; // 00

  // reg 44 - def: {0_0000_1010, 010_0000} - version 0
  // reg 44 - def: {0_0010_0000, 001_0100} - version 1
  assign dltdc_lsb_int_cnt_val[8:2] = REG_CFG_SPI44[6:0]; // 0100000
  assign dltdc_lsb_int_margin = REG_CFG_SPI44[15:7]; // 0_0001_0100

  // reg 45 - def: {7'b0000_000, 9'b0_1000_0000} - version 0 
  // reg 45(053121) - def: {7'b0000_000, 9'b0_0001_0100} - version 1  
  assign dltdc_record_cnt_val = REG_CFG_SPI45[8:0]; // 0_0001_0100
  assign CS_PLL_OV = REG_CFG_SPI45[9]; // 0 
  assign cs_pll_user  = REG_CFG_SPI45[12:10]; // 0 
  assign CS_PLL_CTRL_OV = REG_CFG_SPI45[13]; // 0 
  assign cs_pll_ctrl_user  = REG_CFG_SPI45[15:14]; // 0 

  // reg 46(053121) - def: {4'b1000,7'b0000_001,1'b1,3'b000,1'b0}
  assign CS_TSTDC_OV = REG_CFG_SPI46[0]; // 0
  assign cs_tstdc_user = REG_CFG_SPI46[3:1]; // 0
  assign DLTDC_FRAC_CALIB_EN = REG_CFG_SPI46[4]; // 1
  assign idx_ref_phase_ramp_frac_avg = REG_CFG_SPI46[11:5]; //1
  assign cnt_ref_frac_accum_val_logtwo[3:0] = REG_CFG_SPI46[11:5]; // 4'b1000 => 2**8=256

  // reg 47(060221) - def: {16'b0} (0602)
  assign embtdc_offset_user = REG_CFG_SPI47[8:0]; // 0
  assign EMBTDC_OFFSET_OV = REG_CFG_SPI47[9]; // 0
  assign EDGE_CNT_OV = REG_CFG_SPI47[10]; // 0
  assign edge_cnt_user = REG_CFG_SPI47[13:11]; // 0
  assign DCO_FCW_OV = REG_CFG_SPI47[14]; // 0
  assign DCO_FCW_OV_VAL[0] = REG_CFG_SPI47[15]; // 0

  // 0512 bookmark
  // reg 48 - def(1): {8'b0, 8'b1111_1111}
  // reg 48 - def(2): {8'b0001_1110, 8'b1111_1111}
  // reg 48 - def(3): {8'b0001_1110, 8'b0100_0000} (0602)
  assign DCO_FCW_OV_VAL[8:1] = REG_CFG_SPI48[7:0]; // 8'b0100_0000 (64)
  assign EMBTDC_LUT_USER[7:0] = REG_CFG_SPI48[15:8] ;    // 8'b0 (0) => 8'b0001_1110 (30)
  // reg 49 - def(1): 16'b0110_0101__0011_0011
  // reg 49 - def(2): {8'b1000_0011, 8'b0101_0001} 
  assign EMBTDC_LUT_USER[23:8] = REG_CFG_SPI49[15:0] ;   // 16'b0110_0101__0011_0011 (101, 51) => {8'b1000_0011, 8'b0101_0001} (131,81)
  // reg 50 - def(1):  16'b1100_1010__1001_1000
  // reg 50 - def(2): {8'b1110_1000, 8'b1011_0110}
  assign EMBTDC_LUT_USER[39:24] = REG_CFG_SPI50[15:0] ;    // 16'b1100_1010__1001_1000 (202, 152) => {8'b1110_1000, 8'b1011_0110} (232,182)
  // reg 51
  assign EMB_DLTDC_MAP_LUT_USER[15:0] = REG_CFG_SPI51[15:0]; // 16'b0000_0111__0000_0000   (7, 0)
  // reg 52
  assign EMB_DLTDC_MAP_LUT_USER[31:16] = REG_CFG_SPI52[15:0];  // 16'b0001_0111__0000_1111 (23, 15)
  // reg 53                       // reg 53: {8'b0001_1111, 8'b0001_1111}
  assign EMB_DLTDC_MAP_LUT_USER[39:32] = REG_CFG_SPI53[7:0];  // 8'b0001_1111     (31)
//  assign dltdc_out_max_cond[7:0]       = REG_CFG_SPI53[15:8];  // 8'b0001_1111     (31)
  // reg 54 ~ 78
  assign DLTDC_LUT_USER[399:0] = {REG_CFG_SPI78, REG_CFG_SPI77, REG_CFG_SPI76, REG_CFG_SPI75, REG_CFG_SPI74,
      REG_CFG_SPI73, REG_CFG_SPI72, REG_CFG_SPI71, REG_CFG_SPI70, REG_CFG_SPI69,
      REG_CFG_SPI68, REG_CFG_SPI67, REG_CFG_SPI66, REG_CFG_SPI65, REG_CFG_SPI64,
      REG_CFG_SPI63, REG_CFG_SPI62, REG_CFG_SPI61, REG_CFG_SPI60, REG_CFG_SPI59,
      REG_CFG_SPI58, REG_CFG_SPI57, REG_CFG_SPI56, REG_CFG_SPI55, REG_CFG_SPI54};
  // reg 79 - def: {7'b0000_000, 9'b0_1100_1000} - version 1 
  assign es_calib_cnt_val[8:0] = REG_CFG_SPI79[8:0];  // 9'b0_1100_1000 (10)
//  assign pre_fb_calib_cnt_val[8:0]   = REG_CFG_SPI79[14:6];  // 9'b0_0100_0000  (64)
  // reg 80                                                                                     // reg 80: {7'b100_0000,9'b0}
  assign FCW_FRAC[8:0] = REG_CFG_SPI80[8:0];  // 0
  assign FCW_INT[6:0]  = REG_CFG_SPI80[15:9];  // 8'b0100_0000 (64)
  // reg 81                                                                                     //
  assign DCO_OPEN_LOOP_CTRL[15:0] = REG_CFG_SPI81[15:0]; // reg 81: {7'b011_1100  , 9'b0_0100_0000} (60,64)
  // reg 82 - def(1): kp_real=2.2: {4'b1100, 12'b0000_1000_1100}
  // reg 82 - def(2): kp_real=6.2: {4'b1100, 12'b0100_0000_1100}
  assign DLF_KP[11:0] = REG_CFG_SPI82[11:0]; // (1) 12'b0000_1000_1100, (2) 12'b0100_0000_1100
  assign DLF_KI[3:0]  = REG_CFG_SPI82[15:12];  // 4'b1100
  // reg 83 - def(1): {8'b0, 8'b0000_1000}
  // reg 83 - def(2): {8'b0, 8'b0100_0000}
  assign DLF_KI[11:4]            = REG_CFG_SPI83[7:0]; // (1) 8'b0000_1000, (2) 8'b0100_0000
  assign CAPTURE_MUX_SEL[3:0]    = REG_CFG_SPI83[11:8]; // 0
  assign DCO_OPEN_LOOP_EN        = REG_CFG_SPI83[12];  // 0
 // assign dltdc_out_max_cond[9:8] = REG_CFG_SPI83[14:13];// 0
  // reg 84                                                                                     // reg84: {11'b001_0100_0000,0,1,0,1,0}
  assign DITHER_EN                 = REG_CFG_SPI84[0];  // 0
  assign FINE_LOCK_ENABLE          = REG_CFG_SPI84[1];  // 1
  assign SSC_EN                    = REG_CFG_SPI84[2];  // 0
  assign OSC_EN                    = REG_CFG_SPI84[3];  // 1
  assign dum_data_in               = REG_CFG_SPI84[4];  // 0
  assign FREQ_LOCK_THRESHOLD[10:0] = REG_CFG_SPI84[15:5]; // 11'b001_0100_0000
  // reg 85
  assign FINE_LOCK_THRESHOLD[15:0] = REG_CFG_SPI85;  // 16'b0000_0000_1111_0000
  // reg 86                                                                                     // reg 86: {8'b0000_0000, 8'b0001_0000}
  assign FINE_LOCK_COUNT[8:0]       = REG_CFG_SPI86[8:0];  // 8'b0001_0000 // update 0930
  assign FREQ_LOCK_THRESHOLD[15:11] = REG_CFG_SPI86[13:9];  // 0
//  assign FREQ_LOCK_COUNT[7:0]   = REG_CFG_SPI86[15:8]; // 8'b0001_0000
  // reg 87                                                                                     // reg 87: {4'b1010, 12'b1000_0000_0000}
  assign SSC_REF_COUNT[11:0] = REG_CFG_SPI87[11:0];  // 12'b1000_0000_0000 (2048)
  assign SSC_SHIFT[3:0]      = REG_CFG_SPI87[15:12]; // 4'b1010  (10)
  // reg 88                                                                                     // reg 88: {12'b0, 4'b0101}
  assign SSC_STEP[3:0]               = REG_CFG_SPI88[3:0];  // 4'b0101 (5)
  assign FREQ_LOCK_COUNT[8:0]        = REG_CFG_SPI86[12:4];  // 8'b0001_0000 // update 0930
  // reg 89~90
  assign SCPA_SEL[31:0] = { REG_CFG_SPI90, REG_CFG_SPI89}; // 32'b1111_1111_1111_1111_1111_1111_1111_1111

  // new: 0927
  // reg 91                         // reg 91: {2'b0, 7'b010_0011, 0, 6'b00_0110}
  assign PLL_RST_CNT_COND     = REG_CFG_SPI91[5:0];   // 6'b00_0110 (6)
  assign USE_EMBTDC           = REG_CFG_SPI91[6];       // 0
  assign dltdc_total_max_user = REG_CFG_SPI91[13:7];   // 7'b010_0011 (35)
  assign DCO_CCW_OV_VAL       = {REG_CFG_SPI92[4:0],REG_CFG_SPI91[15:14]}; //  7'b011_1100 (60)
  // reg 92 ~ 93                          // reg 92: {1'b1,9'b0_1000_1100,0,5'b011_11}
  assign DCO_CCW_OV        = REG_CFG_SPI92[5];      // 0
  assign DCO_FCW_MAX_LIMIT = REG_CFG_SPI92[14:6];    // 9'b0_1000_1100
  assign EN_PA_USER        = REG_CFG_SPI92[15];    // 1
  // reg 93 ~ 94                          // reg 93: {4'b0, 1'b1, 11'b0}
  assign CLK_OUT_EN   = REG_CFG_SPI93[0];     // 0
  assign DIV_SEL      = REG_CFG_SPI93[9:1] ;   // 0
  assign EN_OV        = REG_CFG_SPI93[10];     // 0
  assign GFSK_EN      = REG_CFG_SPI93[11];     // 1
  assign VC_CTRL_INIT = {REG_CFG_SPI94[4:0],REG_CFG_SPI93[15:12]}; // 0
  // reg 94                         // reg 94: {2'b11, 9'b1_0010_1100, 5'b0}
  assign PKT_LENGTH = REG_CFG_SPI94[13:5];     // 9'b1_0010_1100
  assign DATA_INIT  = REG_CFG_SPI94[15:14];   // 2'b11
  // reg 95                         // reg 95: {10'b11_1111_1111,0,1,0,1,0,0}
//  assign CONT_MOD       = REG_CFG_SPI95[0];     // 0
  assign TOP_FSM_BYPASS = REG_CFG_SPI95[1];     // 0
  assign TRANS_MODE     = REG_CFG_SPI95[2];     // 1
  assign PLL_LOCKED_OV  = REG_CFG_SPI95[3];     // 0
  assign START_TX       = REG_CFG_SPI95[4];     // 1
  assign DEBUG_MODE     = REG_CFG_SPI95[5];     // 0
  assign PLL_CNT        = {REG_CFG_SPI96[3:0],REG_CFG_SPI95[15:6]};   // 14'B11_1111_1111_1111
  // reg 96                         // reg 96: {2'b0, 10'b00_0000_0100, 4'b1111}
  assign PA_CNT = REG_CFG_SPI96[13:4];   //10'b00_0000_0100 (4)
  // reg 97                         // reg 97: {7'b0, 9'b1_1100_0111}
  assign PA_STAND_ALONE = REG_CFG_SPI96[14];   //10'b00_0000_0100 (4)
//  assign dltdc_calib_cnt_val[8:0] = REG_CFG_SPI97[8:0];   // 9'b1_1100_0111     (31)

  // pll output muxing: 0512 bookmark
  assign IN_DATA_SPI1 = {CAPTURE_MUX_OUT[14:0],FINE_LOCK_DETECT} ;
  assign IN_DATA_SPI2 = {6'b0,CAPTURE_MUX_OUT[24:15]} ;
  assign IN_DATA_SPI3 = EMBTDC_CALIB_LUT_RAW[15:0] ; // 0930 update
  assign IN_DATA_SPI4 = EMBTDC_CALIB_LUT_RAW[31:16] ; // 0930
  assign IN_DATA_SPI5 = {EMBTDC_CALIB_MIN_REG[6:0],EMBTDC_CALIB_LUT_RAW[39:31]} ;
  assign IN_DATA_SPI6 = EMBTDC_CALIB_MIN_REG[22:7] ;
  assign IN_DATA_SPI7 = EMBTDC_CALIB_MIN_REG[37:22] ;
  assign IN_DATA_SPI8 = {14'b0,EMBTDC_CALIB_MIN_REG[39:38]} ;
  assign IN_DATA_SPI9 = {8'b0000_0000,PLL_LOCKED,DCO_FCW_MAX_LIMIT_HIT,cs_pll,ns_pll} ;
  assign IN_DATA_SPI10 = {post_ls_ref_FC_bin_final[3:0], post_ls_ref_CC_bin_final, pre_ls_ref_FC_bin_final, pre_ls_ref_CC_bin_final};
  assign IN_DATA_SPI11 = {pre_es_fb_CC_bin_final[13:0], post_ls_ref_FC_bin_final[5:4]};
  assign IN_DATA_SPI12 = {pre_es_fb_FC_bin_final[14:0], pre_es_fb_CC_bin_final[14]};
  assign IN_DATA_SPI13 = {post_es_fb_CC_bin_final[0], pre_es_fb_FC_bin_final[29:15]};
  assign IN_DATA_SPI14 = {post_es_fb_FC_bin_final, post_es_fb_CC_bin_final[2:1]}; 
  assign IN_DATA_SPI15 = {TSTDC_CALIB_STATUS, TSTDC_CALIB_BROKE}; 
  assign IN_DATA_SPI16 = {cs_tstdc[0], cs_pll_ctrl, ref_phase_ramp_frac_avg_probe}; // 053121
  assign IN_DATA_SPI17 = {10'b0, dltdc_out_max_final_bin_out,cs_tstdc[2:1]}; // 053121

  // ===========================================================================
  // spi_slave definition
  // ===========================================================================
  ble_top_spi_slave u_ble_top_spi_slave (
    //inputs from Pads
    .reset       (SPI_reset     ),
    .SS          (SS            ),
    .SCLK        (SCLK          ),
    .MOSI        (MOSI          ),
    .MISO        (MISO          ),
    .IN_DATA_SPI1(IN_DATA_SPI1  ),
    .IN_DATA_SPI2(IN_DATA_SPI2  ),
    .IN_DATA_SPI3(IN_DATA_SPI3  ),
    .IN_DATA_SPI4(IN_DATA_SPI4  ),
    .IN_DATA_SPI5(IN_DATA_SPI5  ),
    .IN_DATA_SPI6(IN_DATA_SPI6  ),
    .IN_DATA_SPI7(IN_DATA_SPI7  ),
    .IN_DATA_SPI8(IN_DATA_SPI8  ),
    .IN_DATA_SPI9(IN_DATA_SPI9  ),
    .IN_DATA_SPI10(IN_DATA_SPI10  ),
    .IN_DATA_SPI11(IN_DATA_SPI11  ),
    .IN_DATA_SPI12(IN_DATA_SPI12  ),
    .IN_DATA_SPI13(IN_DATA_SPI13  ),
    .IN_DATA_SPI14(IN_DATA_SPI14  ),
    .IN_DATA_SPI15(IN_DATA_SPI15  ),
    .IN_DATA_SPI16(IN_DATA_SPI16  ),
    .IN_DATA_SPI17(IN_DATA_SPI17  ),
    .REG_DATA1   (REG_DATA_SPI1 ),
    .REG_DATA2   (REG_DATA_SPI2 ),
    .REG_DATA3   (REG_DATA_SPI3 ),
    .REG_DATA4   (REG_DATA_SPI4 ),
    .REG_DATA5   (REG_DATA_SPI5 ),
    .REG_DATA6   (REG_DATA_SPI6 ),
    .REG_DATA7   (REG_DATA_SPI7 ),
    .REG_DATA8   (REG_DATA_SPI8 ),
    .REG_DATA9   (REG_DATA_SPI9 ),
    .REG_DATA10  (REG_DATA_SPI10),
    .REG_DATA11  (REG_DATA_SPI11),
    .REG_DATA12  (REG_DATA_SPI12),
    .REG_DATA13  (REG_DATA_SPI13),
    .REG_DATA14  (REG_DATA_SPI14),
    .REG_DATA15  (REG_DATA_SPI15),
    .REG_DATA16  (REG_DATA_SPI16),
    .REG_DATA17  (REG_DATA_SPI17),
    .REG_DATA18  (REG_DATA_SPI18),
    .REG_DATA19  (REG_DATA_SPI19),
    .REG_DATA20  (REG_DATA_SPI20),
    .REG_DATA21  (REG_DATA_SPI21),
    .REG_DATA22  (REG_DATA_SPI22),
    .REG_DATA23  (REG_DATA_SPI23),
    .REG_DATA24  (REG_DATA_SPI24),
    .REG_DATA25  (REG_DATA_SPI25),
    .REG_DATA26  (REG_DATA_SPI26),
    .REG_DATA27  (REG_DATA_SPI27),
    .REG_DATA28  (REG_DATA_SPI28),
    .REG_DATA29  (REG_DATA_SPI29),
    .REG_DATA30  (REG_DATA_SPI30),
    .REG_DATA31  (REG_DATA_SPI31),
    .REG_DATA32  (REG_DATA_SPI32),
    .REG_CONFIG1 (REG_CFG_SPI1  ),
    .REG_CONFIG2 (REG_CFG_SPI2  ),
    .REG_CONFIG3 (REG_CFG_SPI3  ),
    .REG_CONFIG4 (REG_CFG_SPI4  ),
    .REG_CONFIG5 (REG_CFG_SPI5  ),
    .REG_CONFIG6 (REG_CFG_SPI6  ),
    .REG_CONFIG7 (REG_CFG_SPI7  ),
    .REG_CONFIG8 (REG_CFG_SPI8  ),
    .REG_CONFIG9 (REG_CFG_SPI9  ),
    .REG_CONFIG10(REG_CFG_SPI10 ),
    .REG_CONFIG11(REG_CFG_SPI11 ),
    .REG_CONFIG12(REG_CFG_SPI12 ),
    .REG_CONFIG13(REG_CFG_SPI13 ),
    .REG_CONFIG14(REG_CFG_SPI14 ),
    .REG_CONFIG15(REG_CFG_SPI15 ),
    .REG_CONFIG16(REG_CFG_SPI16 ),
    .REG_CONFIG17(REG_CFG_SPI17 ),
    .REG_CONFIG18(REG_CFG_SPI18 ),
    .REG_CONFIG19(REG_CFG_SPI19 ),
    .REG_CONFIG20(REG_CFG_SPI20 ),
    .REG_CONFIG21(REG_CFG_SPI21 ),
    .REG_CONFIG22(REG_CFG_SPI22 ),
    .REG_CONFIG23(REG_CFG_SPI23 ),
    .REG_CONFIG24(REG_CFG_SPI24 ),
    .REG_CONFIG25(REG_CFG_SPI25 ),
    .REG_CONFIG26(REG_CFG_SPI26 ),
    .REG_CONFIG27(REG_CFG_SPI27 ),
    .REG_CONFIG28(REG_CFG_SPI28 ),
    .REG_CONFIG29(REG_CFG_SPI29 ),
    .REG_CONFIG30(REG_CFG_SPI30 ),
    .REG_CONFIG31(REG_CFG_SPI31 ),
    .REG_CONFIG32(REG_CFG_SPI32 ),
    .REG_CONFIG33(REG_CFG_SPI33 ),
    .REG_CONFIG34(REG_CFG_SPI34 ),
    .REG_CONFIG35(REG_CFG_SPI35 ),
    .REG_CONFIG36(REG_CFG_SPI36 ),
    .REG_CONFIG37(REG_CFG_SPI37 ),
    .REG_CONFIG38(REG_CFG_SPI38 ),
    .REG_CONFIG39(REG_CFG_SPI39 ),
    .REG_CONFIG40(REG_CFG_SPI40 ),
    .REG_CONFIG41(REG_CFG_SPI41 ),
    .REG_CONFIG42(REG_CFG_SPI42 ),
    .REG_CONFIG43(REG_CFG_SPI43 ),
    .REG_CONFIG44(REG_CFG_SPI44 ),
    .REG_CONFIG45(REG_CFG_SPI45 ),
    .REG_CONFIG46(REG_CFG_SPI46 ),
    .REG_CONFIG47(REG_CFG_SPI47 ),
    .REG_CONFIG48(REG_CFG_SPI48 ),
    .REG_CONFIG49(REG_CFG_SPI49 ),
    .REG_CONFIG50(REG_CFG_SPI50 ),
    .REG_CONFIG51(REG_CFG_SPI51 ),
    .REG_CONFIG52(REG_CFG_SPI52 ),
    .REG_CONFIG53(REG_CFG_SPI53 ),
    .REG_CONFIG54(REG_CFG_SPI54 ),
    .REG_CONFIG55(REG_CFG_SPI55 ),
    .REG_CONFIG56(REG_CFG_SPI56 ),
    .REG_CONFIG57(REG_CFG_SPI57 ),
    .REG_CONFIG58(REG_CFG_SPI58 ),
    .REG_CONFIG59(REG_CFG_SPI59 ),
    .REG_CONFIG60(REG_CFG_SPI60 ),
    .REG_CONFIG61(REG_CFG_SPI61 ),
    .REG_CONFIG62(REG_CFG_SPI62 ),
    .REG_CONFIG63(REG_CFG_SPI63 ),
    .REG_CONFIG64(REG_CFG_SPI64 ),
    .REG_CONFIG65(REG_CFG_SPI65 ),
    .REG_CONFIG66(REG_CFG_SPI66 ),
    .REG_CONFIG67(REG_CFG_SPI67 ),
    .REG_CONFIG68(REG_CFG_SPI68 ),
    .REG_CONFIG69(REG_CFG_SPI69 ),
    .REG_CONFIG70(REG_CFG_SPI70 ),
    .REG_CONFIG71(REG_CFG_SPI71 ),
    .REG_CONFIG72(REG_CFG_SPI72 ),
    .REG_CONFIG73(REG_CFG_SPI73 ),
    .REG_CONFIG74(REG_CFG_SPI74 ),
    .REG_CONFIG75(REG_CFG_SPI75 ),
    .REG_CONFIG76(REG_CFG_SPI76 ),
    .REG_CONFIG77(REG_CFG_SPI77 ),
    .REG_CONFIG78(REG_CFG_SPI78 ),
    .REG_CONFIG79(REG_CFG_SPI79 ),
    .REG_CONFIG80(REG_CFG_SPI80 ),
    .REG_CONFIG81(REG_CFG_SPI81 ),
    .REG_CONFIG82(REG_CFG_SPI82 ),
    .REG_CONFIG83(REG_CFG_SPI83 ),
    .REG_CONFIG84(REG_CFG_SPI84 ),
    .REG_CONFIG85(REG_CFG_SPI85 ),
    .REG_CONFIG86(REG_CFG_SPI86 ),
    .REG_CONFIG87(REG_CFG_SPI87 ),
    .REG_CONFIG88(REG_CFG_SPI88 ),
    .REG_CONFIG89(REG_CFG_SPI89 ),
    .REG_CONFIG90(REG_CFG_SPI90 ),
    .REG_CONFIG91(REG_CFG_SPI91 ),
    .REG_CONFIG92(REG_CFG_SPI92 ),
    .REG_CONFIG93(REG_CFG_SPI93 ),
    .REG_CONFIG94(REG_CFG_SPI94 ),
    .REG_CONFIG95(REG_CFG_SPI95 ),
    .REG_CONFIG96(REG_CFG_SPI96 ),
    .REG_CONFIG97(REG_CFG_SPI97 )
  );


  // ===========================================================================
  // ble_top definition
  // ===========================================================================

	ble_top u_ble_top(
		.PLL_RST_CNT_COND	(PLL_RST_CNT_COND	),
//		.RF_EXT			(RF_EXT			),

	// pll_top (2021)
		.pre_ls_ref_CC_bin_user		(pre_ls_ref_CC_bin_user		),
		.pre_ls_ref_FC_bin_user		(pre_ls_ref_FC_bin_user		),
		.post_ls_ref_CC_bin_user	(post_ls_ref_CC_bin_user	),
		.post_ls_ref_FC_bin_user	(post_ls_ref_FC_bin_user	),
		.pre_es_fb_CC_bin_user		(pre_es_fb_CC_bin_user		),
		.pre_es_fb_FC_bin_user		(pre_es_fb_FC_bin_user		),
		.post_es_fb_CC_bin_user		(post_es_fb_CC_bin_user		),
		.post_es_fb_FC_bin_user		(post_es_fb_FC_bin_user		),
		//.EMBTDC_LUT_USER		(embtdc_lut_user_2d		), // this is for synth/apr version
		.EMBTDC_LUT_USER		(EMBTDC_LUT_USER		),
		.DLTDC_LUT_USER			(DLTDC_LUT_USER			),
		//.EMB_DLTDC_MAP_LUT_USER		(emb_dltdc_map_lut_user_2d	), // this is for synth/apr version
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
		.FCW_FRAC			(FCW_FRAC			),
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
		.TSTDC_CALIB_BROKE		(TSTDC_CALIB_BROKE 		),
		.TSTDC_CALIB_STATUS		(TSTDC_CALIB_STATUS		),
		.DIV_SEL			(DIV_SEL			),
		.CLK_REF			(CLK_REF			),
		.RST				(RST				),
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
		.OSC_EN				(OSC_EN				),
//		.SCPA_CLK_EN			(SCPA_CLK_EN			),
		.CLK_OUT_EN			(CLK_OUT_EN			),
		.DCO_FCW_MAX_LIMIT_HIT		(DCO_FCW_MAX_LIMIT_HIT		),
		.FINE_LOCK_DETECT		(FINE_LOCK_DETECT		),
		.PLL_LOCKED			(PLL_LOCKED			),
		.CS_PLL_OV			(CS_PLL_OV			), // v 053121
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

	// scpa                                                 
		.PA_STAND_ALONE		(PA_STAND_ALONE		), // 0929 update
		.SCPA_SEL		(SCPA_SEL		),
		.SCPA_OUT		(SCPA_OUT		),

	// GFSK_.MOD                     
		.EN_OV			(EN_OV			),
		.GFSK_EN		(GFSK_EN		),
//		.CONT_MOD		(CONT_MOD		),
		.VC_CTRL_INIT		(VC_CTRL_INIT		),
		.PKT_LENGTH		(PKT_LENGTH		),
		.DATA_INIT		(DATA_INIT		),
		.DATA			(DATA			),
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
		.MOD_7_7		(MOD_7_7		),			

	// TOP_FSM             
		.EN_PA_USER		(EN_PA_USER		), // 0929 update 
		.TOP_FSM_BYPASS		(TOP_FSM_BYPASS		),
		.TRANS_MODE		(TRANS_MODE		),
		.PLL_LOCKED_OV		(PLL_LOCKED_OV		),
		.START_TX		(START_TX		),
		.DEBUG_MODE		(DEBUG_MODE		),
		.PLL_CNT		(PLL_CNT		),	 
		.PA_CNT			(PA_CNT			) 
	     );

endmodule
