//`timescale 1ns/1ps

//`include "pll_fsm_define.sv"
//`include "ssc_generator.v"
module pll_controller(
	CLKREF_RETIMED,	// retimed reference clk   
	RST,				// active high reset 
	FCW_INT,			// integer FCW to the PLL 
	FCW_FRAC,			// fractional FCW to the PLL, not tested yet 
	DCO_OPEN_LOOP_CTRL,	// combined CW to the DCO, only valid in open loop    
	DCO_OPEN_LOOP_EN,	// switch between open and close loop
	DLF_KP,		// loop filter Kp for slow mode 
	DLF_KI,		// loop filter Ki for slow mode
	COUNT_IN,			// retimed clkref sampled counter input(this is the coarse DCO phase) 
	FRAC_PHASE_IN,				// retimed clkref sampled DLTDC output(this is the super-fine DCO phase)  
	FREQ_LOCK_THRESHOLD,
	FREQ_LOCK_COUNT,
	FREQ_LOCK_RST,
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,
	CAPTURE_MUX_SEL,	// Select among different internal signals to view for testing purposes.
	DITHER_EN,
	CLK_DITHER,
	EMBTDC_OFFSET,  // for edge_sel offset
	DCO_CCW_OV_VAL,
	DCO_CCW_OV,
	DCO_FCW_MAX_LIMIT, 		// valid range of FCW

	CS_PLL_CTRL_OV, // v 053121
	cs_pll_ctrl_user,//
	cs_pll_ctrl,//^

	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,

	ref_phase_ramp_frac, // 053121
	DCO_FCW_MAX_LIMIT_HIT, 		// valid range of FCW
	DCO_CCW_OUT,		// OUTPUT: coarse CW to the DCO  (thermal) 
	DCO_FCW_OUT,		// OUTPUT: fine CW to the DCO (thermal)
	DCO_FCBW_OUT,		// OUTPUT: fine CW to the DCO (thermal)
	FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode. 
	CAPTURE_MUX_OUT);	// OUTPUT: The internal signal selected to view as an output. 

	// Functions
//	`include "functions.v"
	//=======================================================================
	// Parameters to tweak. sync with higher level blocks
	//=======================================================================
	// dco parameters
	//parameter NCC = 24;
	//parameter NFC = 16;
	parameter NCC = 24;
	parameter NFC = 28;
	parameter NSTG = 5;
	parameter integer DCO_CCW_MAX = NCC*NSTG;
	parameter integer DCO_FCW_MAX = NFC*NSTG*2; // half_FC
	parameter integer DCO_FCW_MAX_H = NFC*NSTG; // half_FC

	parameter integer DCO_CCW_MAX_H = DCO_CCW_MAX/2;
	parameter integer DCO_FCW_MAX_Q = DCO_FCW_MAX/4;
	// controller parameters
	parameter integer FCW_MAX = 100;
	parameter integer FCW_MIN = 10;
	parameter integer KP_WIDTH = 12;
	parameter integer KP_FRAC_WIDTH = 6;
	parameter integer KI_WIDTH = 12;
	parameter integer KI_FRAC_WIDTH = 10;
	//parameter integer ACCUM_EXTRA_BITS = 9;
	parameter integer ACCUM_EXTRA_BITS = 8;
	parameter integer FILTER_EXTRA_BITS = 4;

	parameter integer FINE_LOCK_THSH_MAX = 20;	//scale not sure
	parameter integer FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;	//scale not sure
	parameter integer CAPTURE_WIDTH = 25;

	parameter SSC_COUNT_WIDTH = 12;
	parameter SSC_ACCUM_WIDTH = 16;
	parameter SSC_MOD_WIDTH = 5;
	parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

	//=======================================================================
	// Local Parameters
	//=======================================================================

	// Sign bits
	localparam SIGN_BIT = 1;
	localparam EXTRA_SIGN_BIT = 1;
	
	// sigma-delta
	localparam SD_WIDTH=3;
	// TDC word sizes
	parameter EMBTDC_WIDTH = 5;
	parameter TDC_WIDTH = EMBTDC_WIDTH;
	// Reference accumulator control word sizes
	localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
	parameter FCW_FRAC_WIDTH = 9; // ble_test
	localparam TDC_ROUND_WIDTH = FCW_FRAC_WIDTH; // ble_test
	localparam TDC_SHIFT = FCW_FRAC_WIDTH-TDC_WIDTH; // ble_test
	localparam FCW_WIDTH = FCW_INT_WIDTH+FCW_FRAC_WIDTH; // ble_test

	// DCO control word sizes
	localparam DCO_CCW_BIN_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_BIN_WIDTH = func_clog2(DCO_FCW_MAX);

	// Reference accumulator size
	localparam REF_ACCUM_WIDTH = FCW_WIDTH + ACCUM_EXTRA_BITS;

	localparam signed PHASE_RAMP_ERROR_MAX = {1'b0, {REF_ACCUM_WIDTH-1{1'b1}}};
	localparam signed PHASE_RAMP_ERROR_MIN = {1'b1, {REF_ACCUM_WIDTH-1{1'b0}}};

	// Filter gain sizes
	localparam FILTER_GAIN_INT_WIDTH = func_MAX(KP_WIDTH-KP_FRAC_WIDTH,KI_WIDTH-KI_FRAC_WIDTH) + SIGN_BIT;
	localparam FILTER_GAIN_FRAC_WIDTH = func_MAX(KP_FRAC_WIDTH,KI_FRAC_WIDTH);
	localparam FILTER_GAIN_WIDTH = FILTER_GAIN_INT_WIDTH + FILTER_GAIN_FRAC_WIDTH;

	// Change the fractional width of the GAINED_ERROR_VALUES (just keep two decimal bits)
	localparam GAINED_ERROR_INT_WIDTH = REF_ACCUM_WIDTH + FILTER_GAIN_INT_WIDTH - EXTRA_SIGN_BIT;
	localparam GAINED_ERROR_FRAC_WIDTH = FILTER_GAIN_FRAC_WIDTH;
	localparam GAINED_ERROR_WIDTH = GAINED_ERROR_INT_WIDTH + GAINED_ERROR_FRAC_WIDTH;

	// Filter State sizes
	localparam FILTER_ACCUM_INT_WIDTH = func_MAX(GAINED_ERROR_INT_WIDTH, DCO_CCW_BIN_WIDTH+DCO_FCW_BIN_WIDTH+SIGN_BIT) + FILTER_EXTRA_BITS;
	localparam FILTER_ACCUM_FRAC_WIDTH = FILTER_GAIN_FRAC_WIDTH + TDC_ROUND_WIDTH; //km-test
	localparam FILTER_ACCUM_WIDTH = FILTER_ACCUM_INT_WIDTH + FILTER_ACCUM_FRAC_WIDTH;

	localparam signed FILTER_ACCUM_MAX = {1'b0, {FILTER_ACCUM_WIDTH-1{1'b1}}};
	localparam signed FILTER_ACCUM_MIN = {1'b1, {FILTER_ACCUM_WIDTH-1{1'b0}}};

	localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
	localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);
		
	localparam FILTER_OUT_FRAC = 6; 

	// freq lock limit
	localparam freq_lock_limit	= 16;

	// Ports
	input		 					CS_PLL_CTRL_OV; //  v 053121
	input reg [1:0] 					cs_pll_ctrl_user; //^
	input logic						CLKREF_RETIMED;
	input logic						RST;
	input logic	[FCW_INT_WIDTH-1:0] 			FCW_INT;
	input logic	[FCW_FRAC_WIDTH-1:0]			FCW_FRAC;  
	input logic	[DCO_CCW_BIN_WIDTH +
	      			 DCO_FCW_BIN_WIDTH-1:0]		DCO_OPEN_LOOP_CTRL;
	input logic						DCO_OPEN_LOOP_EN;
	input logic	[KP_WIDTH-1:0]				DLF_KP;
	input logic	[KI_WIDTH-1:0] 				DLF_KI;
	//input logic	[REF_ACCUM_WIDTH-
	//      				TDC_ROUND_WIDTH-1:0] 	COUNT_IN; // COUNT_IN[3] is going to drive sigma_delta
	input logic	[REF_ACCUM_WIDTH-
	      				FCW_FRAC_WIDTH-1:0] 	COUNT_IN; // ble_test: COUNT_IN[3] is going to drive sigma_delta
	input logic	[EMBTDC_WIDTH-1:0] 			FRAC_PHASE_IN;
	input signed	[FCW_WIDTH-1:0] 			FREQ_LOCK_THRESHOLD;
	input logic	[FINE_LOCK_COUNT_WIDTH-1:0]	 	FREQ_LOCK_COUNT;
	input logic					 	FREQ_LOCK_RST;
	input logic						FINE_LOCK_ENABLE;
	input signed	[FCW_WIDTH-1:0] 			FINE_LOCK_THRESHOLD;
	input logic	[FINE_LOCK_COUNT_WIDTH-1:0]	 	FINE_LOCK_COUNT;
	input logic					 	DITHER_EN;
	input logic					 	CLK_DITHER;
	input logic	[FCW_FRAC_WIDTH-1:0]			EMBTDC_OFFSET; 
	input logic	[3:0] 					CAPTURE_MUX_SEL;
	input 		[DCO_FCW_BIN_WIDTH-1:0]			DCO_FCW_MAX_LIMIT;	
	input	 						DCO_CCW_OV;
	//input 		[DCO_CCW_BIN_WIDTH-1:0]			DCO_CCW_OV_VAL;
	input 		[DCO_CCW_MAX-1:0]			DCO_CCW_OV_VAL; // thermal

	input logic						SSC_EN;
	input logic	[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
	input logic	[3:0]					SSC_STEP;
	input logic	[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

	output reg [1:0] 	cs_pll_ctrl; // 053121
	output logic	[FCW_FRAC_WIDTH-1:0]			ref_phase_ramp_frac;  // 053121 
	output logic	[DCO_CCW_MAX-1:0]	 		DCO_CCW_OUT;
	output logic	[DCO_FCW_MAX_H-1:0] 			DCO_FCW_OUT;
	output logic	[DCO_FCW_MAX_H-1:0] 			DCO_FCBW_OUT;
	output logic 						FINE_LOCK_DETECT;
	output logic 	[CAPTURE_WIDTH-1 :0]			CAPTURE_MUX_OUT;
	output logic						DCO_FCW_MAX_LIMIT_HIT;


//Internal Signals
	logic		[DCO_CCW_BIN_WIDTH-1:0] 		dco_ccw_bin; // 0602
	logic		[DCO_CCW_MAX-1:0] 			dco_ccw_therm;
	logic		[DCO_CCW_MAX-1:0] 			dco_ccw_therm_d;
	logic		[DCO_FCW_MAX-1:0] 			dco_fcw_therm;
	logic		[DCO_FCW_MAX-1:0] 			dco_fcw_max_limit_therm;
	logic		[DCO_FCW_MAX-1:0] 			dco_fcw_therm_latch;
	logic 		[FCW_WIDTH-1:0] 			frequency_control_word;
	logic 		[FCW_WIDTH-1:0] 			frequency_control_word_temp;
	logic 		[FCW_WIDTH-1:0]				frequency_control_word_d;
	logic		[TDC_ROUND_WIDTH-1:0]			tdc_round;

	logic 		[REF_ACCUM_WIDTH-1:0]			ref_phase_ramp;
	logic 		[REF_ACCUM_WIDTH-1:0]			ref_phase_ramp_shifted;
	logic 		[REF_ACCUM_WIDTH-1:0]			dco_phase_ramp;
	logic 		[REF_ACCUM_WIDTH-1:0]			count_in_shifted; // ble_test
	logic 		[REF_ACCUM_WIDTH:0]			dco_phase_ramp_d;
	logic 		[REF_ACCUM_WIDTH:0]			dco_phase_ramp_diff; // need to think about overflow

	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true;
	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true_d;
	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true_delta;


	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error;
	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_d;
	logic signed	[REF_ACCUM_WIDTH:0]			phase_ramp_error_temp;


	logic 							dlf_adjuest_en;
	logic 							dlf_adjuest_en_d;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_kp;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_kp_d;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_ki;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_ki_d;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			filter_kp_d;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			filter_ki_d;

	logic signed  [GAINED_ERROR_WIDTH-1:0]			error_proportional;
	logic signed  [GAINED_ERROR_WIDTH-1:0]			error_integral;

	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum;
	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum_d;
	logic signed	[FILTER_ACCUM_WIDTH:0]			filter_accum_temp; 


	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_out; 
	logic signed 	[FILTER_ACCUM_WIDTH-1:0]		filter_out_d;		
	logic signed	[FILTER_ACCUM_WIDTH:0]			filter_out_temp;


	//logic signed	[FILTER_ACCUM_INT_WIDTH-1:0]		filter_out_int; 
	//logic		[FILTER_ACCUM_INT_WIDTH-1:0]		dco_control_word;
	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_out_int; // test ble 
	logic		[FILTER_ACCUM_WIDTH-1:0]		dco_control_word; // test ble

	logic 		[DCO_CCW_MAX-1:0]			dco_ccw_fix_cand;
	logic 		[DCO_CCW_MAX-1:0]			dco_ccw_fix;

	logic 		[DCO_FCW_BIN_WIDTH-1:0]			dco_fcw_bin_final;		
	logic 		[DCO_FCW_BIN_WIDTH-1:0]			dco_fcw;		
	logic 		[DCO_FCW_BIN_WIDTH:0]			dco_fcw_filter; // -dither bit

	logic							dco_open_loop_en_d;
	logic			[DCO_CCW_BIN_WIDTH +
				 DCO_FCW_BIN_WIDTH-1:0]		dco_open_loop_ctrl_d;
	logic 		[DCO_CCW_BIN_WIDTH-1:0]			dco_ccw_open_loop;
	logic 		[DCO_FCW_BIN_WIDTH-1:0]			dco_fcw_open_loop;

	logic							fine_lock_detect;
	logic							freq_lock_detect;
	logic							freq_lock_zone;
	logic			[SSC_MOD_WIDTH-1:0]		ssc_value;
	logic		[8:0]					freq_lock_cnt;
	logic		[FINE_LOCK_COUNT_WIDTH-1:0]		fine_lock_cnt;

	logic 		[SD_WIDTH-1:0]				fine_dither_sd_in;
	logic 		[SD_WIDTH-1:0]				fine_dither_temp;
	logic 		[SD_WIDTH-1:0]				fine_dither_filter;
	logic 							fine_dither_out;
	logic 							dither_retimed;
//****************************************************************************************\\
//                              State machine                                             \\
//****************************************************************************************\\
  // FSMs
//  pll_fsm							ns_pll_ctrl,cs_pll_ctrl;
	reg [1:0]	ns_pll_ctrl;
//	output reg [1:0] 	cs_pll_ctrl; // 053121
	reg [1:0] 	cs_pll_ctrl_g;
	parameter 	PLL_INIT = 2'b00;
	parameter 	PLL_FREQ_TRACK = 2'b01;
	parameter	PLL_PHASE_TRACK = 2'b10;
	parameter	PLL_PHASE_LOCK = 2'b11;
`define PLL_INIT_STATE						(cs_pll_ctrl_g == PLL_INIT )
`define PLL_FREQ_TRACK_STATE             			(cs_pll_ctrl_g == PLL_FREQ_TRACK )
`define PLL_PHASE_TRACK_STATE					(cs_pll_ctrl_g == PLL_PHASE_TRACK )
`define PLL_PHASE_LOCK_STATE					(cs_pll_ctrl_g == PLL_PHASE_LOCK )

//==========================================================================================
//				Main fsm
//==========================================================================================
  always @(posedge CLKREF_RETIMED or posedge RST) begin 
    if (RST) begin 
      cs_pll_ctrl <= PLL_INIT;
    end else begin
      cs_pll_ctrl <= ns_pll_ctrl;
    end
  end 
  /// Combinational logic for next state

  always_comb begin 
    casex (cs_pll_ctrl)

	PLL_INIT:
	  ns_pll_ctrl = (DCO_CCW_OV==1)? PLL_PHASE_TRACK : PLL_FREQ_TRACK;	

	PLL_FREQ_TRACK:
	  ns_pll_ctrl = (freq_lock_detect==1)? PLL_PHASE_TRACK : PLL_FREQ_TRACK;
	
	PLL_PHASE_TRACK: // 052921 modified
	  ns_pll_ctrl = ((freq_lock_detect==1)||(DCO_CCW_OV==1))? PLL_PHASE_TRACK : PLL_FREQ_TRACK;
	default: 
	  ns_pll_ctrl = PLL_INIT;
	
    endcase // casez (cs_pll_ctrl)
  end

	assign	cs_pll_ctrl_g = (CS_PLL_CTRL_OV)? cs_pll_ctrl_user : cs_pll_ctrl;

//==========================================================================================
//				Generate phase-ramp signals	
//==========================================================================================
// Create the phase ramps and the error signal
  // Triangle Wave Generation for Spread Spectrum (SSC)
  ssc_generator #(
  	.COUNT_WIDTH(SSC_COUNT_WIDTH),
  	.ACCUM_WIDTH(SSC_ACCUM_WIDTH),
  	.MOD_WIDTH(SSC_MOD_WIDTH),
  	.SHIFT_WIDTH(SSC_SHIFT_WIDTH))
  	u_ssc_gen(
  		.CLKREF(CLKREF_RETIMED), 
  		.RST(RST),
  		.SSC_EN(SSC_EN),
  		.COUNT_LIM(SSC_REF_COUNT),
  		.STEP(SSC_STEP),
  		.SHIFT(SSC_SHIFT),
  		.MOD_OUT(ssc_value)
  );

  // accumulate the frequency control word 
  always @(posedge CLKREF_RETIMED or posedge RST) begin
    //if (`PLL_INIT_STATE) 
    if (RST) // km-test 
	begin
  	  ref_phase_ramp <= 0;
	  dco_phase_ramp_d <= 0;
  
  	  phase_ramp_error_d <= 0;
  	  phase_ramp_error_true_d <= 0;
  	end
    else
    if (`PLL_FREQ_TRACK_STATE)
	begin
  	  ref_phase_ramp <= frequency_control_word;

	  dco_phase_ramp_d <= dco_phase_ramp; //ble_test
  
  	  phase_ramp_error_d <= phase_ramp_error;
  	  phase_ramp_error_true_d <= phase_ramp_error_true;
  	end
    else
    if (`PLL_PHASE_TRACK_STATE)
  	begin
  	  //Add SSC here
  	  ref_phase_ramp <= ref_phase_ramp + frequency_control_word - ssc_value;
  	 
	// add edge_sel_offset 
	  //dco_phase_ramp_d <= {dco_phase_ramp_d[REF_ACCUM_WIDTH-1:FCW_FRAC_WIDTH],{FCW_FRAC_WIDTH{1'b0}}};
	  dco_phase_ramp_d <= {dco_phase_ramp_d[REF_ACCUM_WIDTH-1:FCW_FRAC_WIDTH],EMBTDC_OFFSET};

  	  phase_ramp_error_d <= phase_ramp_error;
  	  phase_ramp_error_true_d <= phase_ramp_error_true;
  	end
  end

  // generare the error signal
  always_comb begin
	tdc_round = (FRAC_PHASE_IN)<<TDC_SHIFT; // ble_test 
	dco_phase_ramp = {COUNT_IN,tdc_round}; // -5 for mid-rise tdc(assume DCO_OUT=sampled_phases[2]); COUNT_IN, tdc_round are synced with CLKREF_RETIMED, reset is taken care in tdc_counter
	dco_phase_ramp_diff=$signed(dco_phase_ramp)-$signed(dco_phase_ramp_d); // is this okay?
	ref_phase_ramp_shifted=ref_phase_ramp; // ble_test 
	phase_ramp_error_true = $signed(ref_phase_ramp_shifted)-$signed(dco_phase_ramp_diff);
	phase_ramp_error_true_delta = phase_ramp_error_true - phase_ramp_error_true_d;
	phase_ramp_error_temp = phase_ramp_error_true_delta + phase_ramp_error_d;
  end

	assign ref_phase_ramp_frac = ref_phase_ramp_shifted[FCW_FRAC_WIDTH-1:0];

//==========================================================================================
//			Overflow management for phase-ramp	
//==========================================================================================
  // build the frequecny control word and check limits
  always_comb begin
    //frequency_control_word_temp = FCW_INT;
    frequency_control_word_temp = {FCW_INT,FCW_FRAC}; // ble_test

    if (frequency_control_word_temp > FCW_MAX*2**(FCW_FRAC_WIDTH))
	begin
  	  frequency_control_word = FCW_MAX*2**(FCW_FRAC_WIDTH);
	end
    else if(frequency_control_word_temp < FCW_MIN*2**(FCW_FRAC_WIDTH))
	begin
       	  frequency_control_word = FCW_MIN*2**(FCW_FRAC_WIDTH);
	end
    else
	begin
	  frequency_control_word = frequency_control_word_temp;
	end
  end

  // After the system cycle slips enough, get back to the right error
  always_comb begin
    if(phase_ramp_error_temp > PHASE_RAMP_ERROR_MAX) 
  	begin
  		phase_ramp_error = PHASE_RAMP_ERROR_MAX;
  	end
    else if(phase_ramp_error_temp < PHASE_RAMP_ERROR_MIN) 
  	begin
  		phase_ramp_error = PHASE_RAMP_ERROR_MIN;
  	end
    else
  	begin
  		phase_ramp_error = phase_ramp_error_true;
  	end
  end

//==========================================================================================
//				Digital loop filter	
//==========================================================================================
  // Calculate the filter states
  always @* begin 
    //casex(cs_pll_ctrl) 
    casex(cs_pll_ctrl_g) // 060321 
    	PLL_PHASE_TRACK: begin
		error_proportional = phase_ramp_error*filter_kp_d;  // Nfrac = TDC_ROUND_WIDTH + KP_FRAC_wIDTH
		error_integral = phase_ramp_error*filter_ki_d;  // Nfrac = TDC_ROUND_WIDTH + KI_FRAC_WIDTH
	end
    	PLL_FREQ_TRACK: begin
		error_proportional = 0;
		error_integral = 0;
	end
    	PLL_INIT: begin
		error_proportional = 0;
		error_integral = 'b0;
	end
	default: begin
		error_proportional = 0;
		error_integral = 'b0;
	end
    endcase
  end

  // filter
  always_comb begin
    filter_out_temp = filter_accum + error_proportional;
    filter_accum_temp = filter_accum_d + error_integral;
  end

	// Latch the filter states
	always @(posedge CLKREF_RETIMED or posedge RST) begin
		if (RST) 
			begin 
				filter_out_d <= 0;
				//filter_accum_d <= 0;
				//filter_accum_d <= $unsigned(DCO_FCW_MAX/2)<<<(FILTER_ACCUM_FRAC_WIDTH +1 -TDC_WIDTH); // km-test
				//filter_accum_d <= $unsigned(DCO_FCW_MAX/2)<<<(FILTER_ACCUM_FRAC_WIDTH +1 -TDC_ROUND_WIDTH); // km-test
				//filter_accum_d <= $unsigned(DCO_FCW_MAX/2)<<<(FILTER_ACCUM_FRAC_WIDTH - FILTER_OUT_FRAC); // km-test
				//filter_accum_d <= $unsigned(DCO_FCW_MAX-DCO_FCW_MAX_Q-1)<<<(FILTER_ACCUM_FRAC_WIDTH - FILTER_OUT_FRAC + SD_WIDTH); // test v2 
				filter_accum_d <= $unsigned(DCO_FCW_MAX_Q)<<<(FILTER_ACCUM_FRAC_WIDTH - FILTER_OUT_FRAC + SD_WIDTH); // test v2 
			end
		else
			begin
				filter_out_d <= filter_out;
				filter_accum_d <= filter_accum;			
			end	
	end

//==========================================================================================
//			Overflow management for digital loop filter	
//==========================================================================================
  always_comb begin
    // Check filter output
    if (filter_out_temp > FILTER_ACCUM_MAX)
      begin
	filter_out = FILTER_ACCUM_MAX;
      end
    else if (filter_out_temp < FILTER_ACCUM_MIN)
      begin
    	filter_out = FILTER_ACCUM_MIN;
      end
    else
      begin
    	filter_out = filter_out_temp;
      end
    // Check filter accumulator
    if (filter_accum_temp > FILTER_ACCUM_MAX)
      begin
    	filter_accum = FILTER_ACCUM_MAX;
      end
    else if (filter_accum_temp < FILTER_ACCUM_MIN)
      begin
    	filter_accum = FILTER_ACCUM_MIN;
      end
    else
      begin
    	filter_accum = filter_accum_temp;
      end					
  end


//==========================================================================================
//			Generate dco control words	
//==========================================================================================

// Generate the DCO control words
	//Convert Filter Changes to changes in CC and FC	
	always @* begin
		// use the integer portion of the filter output
		filter_out_int = filter_out >>> (FILTER_ACCUM_FRAC_WIDTH - FILTER_OUT_FRAC); //km-test dsm

		// check for overflow in the DCO control word
		if (filter_out_int>>>SD_WIDTH >= 2**(DCO_CCW_BIN_WIDTH+DCO_FCW_BIN_WIDTH)-1 )
			begin
				dco_control_word = $unsigned(2**(DCO_CCW_BIN_WIDTH+DCO_FCW_BIN_WIDTH)-1);
			end
		else if (filter_out_int <= 0)
			begin
				dco_control_word = 0;
			end
		else
			begin
				dco_control_word = $unsigned(filter_out_int);
			end

		// seperate out the dco control words
		{dco_fcw_filter,fine_dither_filter} = dco_control_word[DCO_FCW_BIN_WIDTH+1+SD_WIDTH-1:0];

	end

	// dither clock retimer
	always @(posedge CLK_DITHER or posedge RST) begin
		if (RST) begin
			fine_dither_temp <= 0;
			dither_retimed <= 0;
		end else begin
			fine_dither_temp <= fine_dither_sd_in;
			dither_retimed <= CLKREF_RETIMED;
		end
	end
	// latch dither value with dither_retimed	
	assign fine_dither_sd_in = dither_retimed? fine_dither_filter : fine_dither_temp;

	sigma_delta #(.SD_WIDTH(SD_WIDTH)) u_sigma_delta (.clk_dither(CLK_DITHER), .dco_fine_frac(fine_dither_sd_in), .rst(RST), .dither_en(DITHER_EN), .o_fine_dither_bit(fine_dither_out));

	// coarse command word
	always_comb begin
		if (`PLL_INIT_STATE) begin
			dco_ccw_therm = {{DCO_CCW_MAX_H{1'b0}},{DCO_CCW_MAX_H{1'b1}}};
		end else if (`PLL_FREQ_TRACK_STATE) begin
			if ((phase_ramp_error<0) && (dco_ccw_therm>0) && (!freq_lock_zone)) begin
				dco_ccw_therm = {1'b0,dco_ccw_therm_d[DCO_CCW_MAX-1:1]};
			end else if ((phase_ramp_error>0) && (dco_ccw_therm[DCO_CCW_MAX-1]==0) && (!freq_lock_zone)) begin
				dco_ccw_therm = {dco_ccw_therm_d[DCO_CCW_MAX-2:0],1'b1};
			end else if (freq_lock_zone==1) begin
				dco_ccw_therm = dco_ccw_therm_d;
			end else begin
				dco_ccw_therm = dco_ccw_therm_d;
			end
		end else if (`PLL_PHASE_TRACK_STATE) begin
			dco_ccw_therm = dco_ccw_fix;
		end else begin
			dco_ccw_therm = {{DCO_CCW_MAX_H{1'b0}},{DCO_CCW_MAX_H{1'b1}}};
		end
	end 


	// detect overflow in fcw. get the open loop control words
	always @* begin
		dco_ccw_open_loop = dco_open_loop_ctrl_d[DCO_FCW_BIN_WIDTH+:DCO_CCW_BIN_WIDTH];
		dco_fcw_open_loop = dco_open_loop_ctrl_d[0+:DCO_FCW_BIN_WIDTH];

		//end
		if (dco_fcw_filter <0) begin
			dco_fcw_bin_final = 0;
		end else if (dco_fcw_filter >= DCO_FCW_MAX) begin
			dco_fcw_bin_final = DCO_FCW_MAX;
		end else begin
			dco_fcw_bin_final = dco_fcw_filter;
		end
	end


	// Latch the dco control words
	always @(posedge CLKREF_RETIMED or posedge RST) begin
//	always_ff @(negedge CLKREF_RETIMED or posedge RST) begin  // negedge test
		if (RST) begin // km-test 
			DCO_CCW_OUT <= {{DCO_CCW_MAX_H{1'b0}},{DCO_CCW_MAX_H{1'b1}}};
			dco_fcw_therm_latch <= {{DCO_FCW_MAX-DCO_FCW_MAX_Q-1{1'b0}},{DCO_FCW_MAX_Q{1'b1}}}; // more ones => less on 
			freq_lock_detect <= 0;
			freq_lock_zone <= 1'b0;
	  		freq_lock_cnt <= 0;
			fine_lock_detect <= 0;
	  		fine_lock_cnt <= 0;
			dco_ccw_fix <= 0;
			dco_ccw_fix_cand <= 0;
			dco_ccw_therm_d <= dco_ccw_therm;
		end else if (`PLL_FREQ_TRACK_STATE) begin
			if (DCO_CCW_OV) begin
				freq_lock_detect <= 1; // 052921
				DCO_CCW_OUT <= DCO_CCW_OV_VAL; // therm
			end else if (FREQ_LOCK_RST==1) begin
				freq_lock_detect <= 0;
				freq_lock_cnt <= 0;
				fine_lock_detect <= 0;
				fine_lock_cnt <= 0;
				freq_lock_zone <= 1'b0;
				dco_fcw_therm_latch <= {{DCO_FCW_MAX-DCO_FCW_MAX_Q-1{1'b0}},{DCO_FCW_MAX_Q{1'b1}}}; // more ones => less on 
			end else if (phase_ramp_error >= -FREQ_LOCK_THRESHOLD && phase_ramp_error <= FREQ_LOCK_THRESHOLD && (!FREQ_LOCK_RST)) begin
			// increment freq_lock_cnt
				freq_lock_zone <= 1'b1;
				freq_lock_cnt <= freq_lock_cnt+1;
				dco_ccw_fix_cand <= dco_ccw_therm_d;
			end else begin
				freq_lock_zone <= 1'b0;
				freq_lock_cnt <= 0;
			end
			// toggle freq_lock_detect
			//if (freq_lock_cnt >= freq_lock_limit && freq_lock_detect==0 && (!FREQ_LOCK_RST)) begin
			if (freq_lock_cnt >= FREQ_LOCK_COUNT && freq_lock_detect==0 && (!FREQ_LOCK_RST)) begin // 060221
				freq_lock_detect <= 1;
				dco_ccw_fix <= dco_ccw_fix_cand; 
			end
			DCO_CCW_OUT <= dco_ccw_therm;
			dco_ccw_therm_d <= dco_ccw_therm;
		end else if (`PLL_PHASE_TRACK_STATE) begin
			if (FREQ_LOCK_RST==1) begin
				freq_lock_detect <= 0;
				freq_lock_cnt <= 0;
				fine_lock_detect <= 0;
				fine_lock_cnt <= 0;
			end else if ((phase_ramp_error_d >= -FINE_LOCK_THRESHOLD) && (phase_ramp_error_d <=FINE_LOCK_THRESHOLD) && fine_lock_detect==0) begin
				fine_lock_cnt <= fine_lock_cnt+1;
			end
			if (fine_lock_cnt >= FINE_LOCK_COUNT && fine_lock_detect==0) begin
				fine_lock_detect <= 1;
			end
			if (DCO_CCW_OV) begin
				freq_lock_detect <= 1; // 052921
				DCO_CCW_OUT <= DCO_CCW_OV_VAL; // therm
			end else begin
				DCO_CCW_OUT <= dco_ccw_therm;
			end
			dco_ccw_therm_d <= dco_ccw_therm;
			dco_fcw_therm_latch <= dco_fcw_therm;
		end
	end
			

	always @(posedge CLKREF_RETIMED or posedge RST) begin
		if (RST) 
			begin
				dco_open_loop_ctrl_d <=0;
				dco_open_loop_en_d <=0;
			end
		else
			begin
				dco_open_loop_ctrl_d <= DCO_OPEN_LOOP_CTRL;
				dco_open_loop_en_d <= DCO_OPEN_LOOP_EN;
			end
	end

	// convert bin => therm
	bin2therm #(.NBIN(DCO_FCW_BIN_WIDTH),.NTHERM(DCO_FCW_MAX)) decFC(.binin(dco_fcw_bin_final), .thermout(dco_fcw_therm));
	bin2therm #(.NBIN(DCO_FCW_BIN_WIDTH),.NTHERM(DCO_FCW_MAX)) decFC_max_limit(.binin(DCO_FCW_MAX_LIMIT), .thermout(dco_fcw_max_limit_therm));
	therm2bin #(.NTHERM(DCO_CCW_MAX), .NBIN(DCO_CCW_BIN_WIDTH)) u_t2b1_ccw (.thermin(DCO_CCW_OUT), .binout(dco_ccw_bin)); // 060221
//	assign DCO_FCW_OUT = {dco_fcw_therm_latch,fine_dither_out};

	assign	DCO_FCW_MAX_LIMIT_HIT = (dco_fcw_therm_latch > dco_fcw_max_limit_therm)? 1 : 0;

	genvar i;
	generate
		for (i=0; i<DCO_FCW_MAX/2; i=i+1) begin
			assign DCO_FCBW_OUT[i] = dco_fcw_therm_latch[2*i+1];
			if (i==0) begin
				assign DCO_FCW_OUT[i] = ~fine_dither_out;
			end else begin
				assign DCO_FCW_OUT[i] = ~dco_fcw_therm_latch[2*i];
			end
		end
	endgenerate

//==========================================================================================
//			Filter adjustments
//==========================================================================================

	// keep track of the filter coefficients
	always @* begin
	
		dlf_kp = $signed({1'b0,DLF_KP})<<<(FILTER_GAIN_FRAC_WIDTH-KP_FRAC_WIDTH);
		dlf_ki = $signed({1'b0,DLF_KI})<<<(FILTER_GAIN_FRAC_WIDTH-KI_FRAC_WIDTH);

	end

	always @(posedge CLKREF_RETIMED or posedge RST) begin
		if (RST) 
			begin
				filter_kp_d <= 0;
				filter_ki_d <= 0;
			end
		else
			begin
				filter_kp_d <= dlf_kp;
				filter_ki_d <= dlf_ki;
			end
	end

//==========================================================================================
//			Mux out for debugging	
//==========================================================================================

	always @* begin
		FINE_LOCK_DETECT <= fine_lock_detect;
		case(CAPTURE_MUX_SEL)
			0: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, ref_phase_ramp};
			1: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_phase_ramp};
			2: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, phase_ramp_error_true};
			3: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, phase_ramp_error};
			4: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, error_proportional>>>GAINED_ERROR_FRAC_WIDTH};
			5: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, error_integral>>>GAINED_ERROR_FRAC_WIDTH};
			6: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, filter_out_d>>>FILTER_ACCUM_FRAC_WIDTH};
			7: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, filter_accum_d>>>FILTER_ACCUM_FRAC_WIDTH};
			8: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_fcw_bin_final};
			9: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_ccw_bin}; // 0602
			10:	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_phase_ramp_d}; // 0602
			default: 
			    CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_fcw};
		endcase
	end

endmodule


module sigma_delta  #( parameter SD_WIDTH = 5)  // resolution: 1/2^SD_WIDTH
  (
   input  logic 	clk_dither,
   input  logic [SD_WIDTH-1:0] 	dco_fine_frac,
   input  logic 	rst,
   
   input  logic 	dither_en,
   output logic         o_fine_dither_bit
   );

  logic [SD_WIDTH:0] 			    sum;
  logic [SD_WIDTH:0] 			    next_sum;
  logic 				    dsm_en;
 
// scan msb 
  assign o_fine_dither_bit = sum[SD_WIDTH] ; 
// Integrator
  
  assign next_sum = dither_en ? ({ 1'b0 , sum[(SD_WIDTH-1):0]} + { 1'b0, dco_fine_frac[SD_WIDTH-1:0]}) : {(SD_WIDTH + 1){1'b0}}; 

  always @(posedge clk_dither or posedge rst) 
    if (rst)
      sum <= {(SD_WIDTH+1){1'b0}};      
    else
      sum <= next_sum;

endmodule // adpll_dcodither
