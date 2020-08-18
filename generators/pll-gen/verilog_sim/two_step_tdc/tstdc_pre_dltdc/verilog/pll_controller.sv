`timescale 1ns/1ps

//`include "pll_fsm_define.sv"
//`include "ssc_generator.v"
//`include "functions.v"
module pll_controller(
	CLKREF_RETIMED,	// retimed reference clk   
	RST,				// active high reset 
	FCW_INT,			// integer FCW to the PLL 
	FCW_FRAC,			// fractional FCW to the PLL, not tested yet 
	DCO_OPEN_LOOP_CTRL,	// combined CW to the DCO, only valid in open loop    
	DCO_OPEN_LOOP_EN,	// switch between open and close loop
	DLF_ADJUST_EN,		// enable for loop filter fast and slow mode adjustment
	DLF_LOCK_KP,		// loop filter Kp for slow mode 
	DLF_LOCK_KI,		// loop filter Ki for slow mode
	DLF_TRACK_KP,		// loop filter Kp for fast mode
	DLF_TRACK_KI,		// loop filter Ki for fast mode 
	COUNT_IN,			// retimed clkref sampled counter input(this is the coarse DCO phase) 
	TDC_IN,				// retimed clkref sampled TDC output(this is the fine DCO phase)  
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,
	CAPTURE_MUX_SEL,	// Select among different internal signals to view for testing purposes.
	DITHER_EN,
	CLK_DITHER,

	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,

	DCO_CCW_OUT,		// OUTPUT: coarse CW to the DCO  (thermal) 
	DCO_CCW_OUTN,		// OUTPUT: coarse CW to the DCO  (thermal) 
	DCO_FCW_OUT,		// OUTPUT: fine CW to the DCO (thermal)
	DCO_FCW_OUTN,		// OUTPUT: fine CW to the DCO (thermal)
	FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode. 
	CAPTURE_MUX_OUT);	// OUTPUT: The internal signal selected to view as an output. 
						
	// Functions
//	`include "functions.v"
	//=======================================================================
	// Parameters to tweak. sync with higher level blocks
	//=======================================================================
	// dco parameters
	parameter integer DCO_CCW_MAX = 44;
	parameter integer DCO_FCW_MAX = 384;

	parameter integer DCO_CCW_MAX_H = DCO_CCW_MAX/2;
	parameter integer DCO_FCW_MAX_H = DCO_FCW_MAX/2;
	// controller parameters
	parameter integer TDC_MAX = 18;
	parameter integer FCW_MAX = 100;
	parameter integer FCW_MIN = 10;
	parameter integer KP_WIDTH = 12;
	parameter integer KP_FRAC_WIDTH = 6;
	parameter integer KI_WIDTH = 12;
	parameter integer KI_FRAC_WIDTH = 10;
	parameter integer ACCUM_EXTRA_BITS = 9;
	parameter integer FILTER_EXTRA_BITS = 4;

	parameter integer FINE_LOCK_THSH_MAX = 127;
	parameter integer FINE_LOCK_COUNT_MAX = 127;
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
	//localparam SD_WIDTH=5;
	localparam SD_WIDTH=3;
	// TDC word sizes
	//localparam TDC_WIDTH = func_clog2(TDC_MAX);
	localparam TDC_WIDTH = func_clog2(TDC_MAX);
	//localparam TDC_ROUND_WIDTH = TDC_WIDTH;

	// Reference accumulator control word sizes
	//localparam FCW_FRAC_WIDTH = TDC_WIDTH;
	localparam FCW_FRAC_WIDTH = 9; // ble_test
	localparam TDC_ROUND_WIDTH = FCW_FRAC_WIDTH; // ble_test
	localparam TDC_SHIFT = FCW_FRAC_WIDTH-TDC_WIDTH; // ble_test
	localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
//	localparam FCW_WIDTH = FCW_INT_WIDTH;
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

	// Gained error sizes
	//localparam GAINED_ERROR_INT_WIDTH = REF_ACCUM_WIDTH + FILTER_GAIN_INT_WIDTH - EXTRA_SIGN_BIT;
	//localparam GAINED_ERROR_FRAC_WIDTH = FILTER_GAIN_FRAC_WIDTH;
	//localparam GAINED_ERROR_WIDTH = GAINED_ERROR_INT_WIDTH + GAINED_ERROR_FRAC_WIDTH;

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

	// freq lock limit
	localparam freq_lock_limit	= 1;

	// Ports
	input logic						CLKREF_RETIMED;
	input logic						RST;
	input logic	[FCW_INT_WIDTH-1:0] 			FCW_INT;
	input logic	[FCW_FRAC_WIDTH-1:0]			FCW_FRAC;  

	input logic	[DCO_CCW_BIN_WIDTH +
	      			 DCO_FCW_BIN_WIDTH-1:0]		DCO_OPEN_LOOP_CTRL;
	input logic						DCO_OPEN_LOOP_EN;
	input logic						DLF_ADJUST_EN;
	input logic	[KP_WIDTH-1:0]				DLF_LOCK_KP;
	input logic	[KI_WIDTH-1:0] 				DLF_LOCK_KI;
	input logic	[KP_WIDTH-1:0] 				DLF_TRACK_KP;
	input logic	[KI_WIDTH-1:0] 				DLF_TRACK_KI;

	//input logic	[REF_ACCUM_WIDTH-
	//      				TDC_ROUND_WIDTH-1:0] 	COUNT_IN; // COUNT_IN[3] is going to drive sigma_delta
	input logic	[REF_ACCUM_WIDTH-
	      				FCW_FRAC_WIDTH-1:0] 	COUNT_IN; // ble_test: COUNT_IN[3] is going to drive sigma_delta
	input logic	[TDC_WIDTH-1:0] 			TDC_IN;


	input logic						FINE_LOCK_ENABLE;
	input logic	[FINE_LOCK_THSH_WIDTH-1:0] 		FINE_LOCK_THRESHOLD;
	input logic	[FINE_LOCK_COUNT_WIDTH-1:0]	 	FINE_LOCK_COUNT;
	input logic					 	DITHER_EN;
	input logic					 	CLK_DITHER;

	input logic	[3:0] 					CAPTURE_MUX_SEL;

	input logic						SSC_EN;
	input logic	[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
	input logic	[3:0]					SSC_STEP;
	input logic	[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

	output logic	[DCO_CCW_MAX-1:0]	 		DCO_CCW_OUT;
	output logic	[DCO_CCW_MAX-1:0]	 		DCO_CCW_OUTN;
	output logic	[DCO_FCW_MAX-1:0] 			DCO_FCW_OUT;
	output logic	[DCO_FCW_MAX-1:0] 			DCO_FCW_OUTN;

	output logic 						FINE_LOCK_DETECT;
	output logic 	[CAPTURE_WIDTH-1 :0]			CAPTURE_MUX_OUT;


//Internal Signals
	logic		[DCO_CCW_MAX-1:0] 			dco_ccw_therm;
	logic		[DCO_CCW_MAX-1:0] 			dco_ccw_therm_d;
	logic		[DCO_FCW_MAX-1-1:0] 			dco_fcw_therm;
	logic		[DCO_FCW_MAX-1-1:0] 			dco_fcw_therm_latch;
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

	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_lock_kp;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_track_kp;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_kp;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_lock_kp_d;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_track_kp_d;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_kp_d;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_lock_ki;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_track_ki;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_ki;		
	
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_lock_ki_d;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_track_ki_d;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_ki_d;		

	logic signed	[FILTER_GAIN_WIDTH-1:0]			filter_kp;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			filter_kp_d;

	logic signed	[FILTER_GAIN_WIDTH-1:0]			filter_ki;
	logic signed	[FILTER_GAIN_WIDTH-1:0]			filter_ki_d;

	logic signed  [GAINED_ERROR_WIDTH-1:0]			error_proportional;
	logic signed  [GAINED_ERROR_WIDTH-1:0]			error_integral;

	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum;
	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum_d;
	logic signed	[FILTER_ACCUM_WIDTH:0]			filter_accum_temp; 


	logic signed	[FILTER_ACCUM_WIDTH-1:0]		filter_out; 
	logic signed 	[FILTER_ACCUM_WIDTH-1:0]		filter_out_d;		
	logic signed	[FILTER_ACCUM_WIDTH:0]			filter_out_temp;


	logic signed	[FILTER_ACCUM_INT_WIDTH-1:0]		filter_out_int; 
	logic		[FILTER_ACCUM_INT_WIDTH-1:0]		dco_control_word;

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
	logic			[SSC_MOD_WIDTH-1:0]		ssc_value;
	logic		[3:0]					freq_lock_cnt;

	logic 		[SD_WIDTH-1:0]				fine_dither_sd_in;
	logic 		[SD_WIDTH-1:0]				fine_dither_temp;
	logic 		[SD_WIDTH-1:0]				fine_dither_filter;
	logic 							fine_dither_out;
	logic 							dither_retimed;
//****************************************************************************************\\
//                              State machine                                             \\
//****************************************************************************************\\
  // FSMs
//  pll_fsm							ns_pll,cs_pll;
	reg [1:0]	ns_pll;
	reg [1:0] 	cs_pll;
	parameter 	PLL_INIT = 2'b00;
	parameter 	PLL_FREQ_TRACK = 2'b01;
	parameter	PLL_PHASE_TRACK = 2'b10;
	parameter	PLL_PHASE_LOCK = 2'b11;
`define PLL_INIT_STATE						(cs_pll == PLL_INIT )
`define PLL_FREQ_TRACK_STATE             			(cs_pll == PLL_FREQ_TRACK )
`define PLL_PHASE_TRACK_STATE					(cs_pll == PLL_PHASE_TRACK )
`define PLL_PHASE_LOCK_STATE					(cs_pll == PLL_PHASE_LOCK )

//==========================================================================================
//				Main fsm
//==========================================================================================
  always_ff @(posedge CLKREF_RETIMED or posedge RST) begin 
    if (RST) begin 
      cs_pll <= PLL_INIT;
    end else begin
      cs_pll <= ns_pll;
    end
  end 
  /// Combinational logic for next state

  always_comb begin 
    casex (cs_pll)

	PLL_INIT:
	  ns_pll = PLL_FREQ_TRACK;	

	PLL_FREQ_TRACK:
	  ns_pll = (freq_lock_detect==1)? PLL_PHASE_TRACK : PLL_FREQ_TRACK;
	
	PLL_PHASE_TRACK:
	  ns_pll = (freq_lock_detect==1)? PLL_PHASE_TRACK : PLL_FREQ_TRACK;
	
    endcase // casez (cs_pll)
  end

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
  always_ff @(posedge CLKREF_RETIMED or posedge RST) begin
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

	  //dco_phase_ramp_d <= dco_phase_ramp; 
	  //dco_phase_ramp_d <= dco_phase_ramp-$unsigned(6'b100000); //test: to check when count missed
	  //dco_phase_ramp_d <= dco_phase_ramp-$unsigned(10'b10_0000_0000); //ble_test
	  dco_phase_ramp_d <= dco_phase_ramp; //ble_test
  
  	  phase_ramp_error_d <= phase_ramp_error;
  	  phase_ramp_error_true_d <= phase_ramp_error_true;
  	end
    else
    if (`PLL_PHASE_TRACK_STATE)
  	begin
  	  //Add SSC here
  	  ref_phase_ramp <= ref_phase_ramp + frequency_control_word - ssc_value;
  	  
	  dco_phase_ramp_d <= dco_phase_ramp_d;

  	  phase_ramp_error_d <= phase_ramp_error;
  	  phase_ramp_error_true_d <= phase_ramp_error_true;
  	end
  end

	// generare the error signal
  always_comb begin
	//tdc_round = TDC_IN; // generate TDC rounded value
	tdc_round = TDC_IN<<<TDC_SHIFT; // ble_test 
	dco_phase_ramp = {COUNT_IN,tdc_round}; // -5 for mid-rise tdc(assume DCO_OUT=sampled_phases[2]); COUNT_IN, tdc_round are synced with CLKREF_RETIMED, reset is taken care in tdc_counter
	//dco_phase_ramp_diff=$signed(dco_phase_ramp)-$signed(dco_phase_ramp_d)-$unsigned(5)<<<TDC_SHIFT; // is this okay?
	dco_phase_ramp_diff=$signed(dco_phase_ramp)-$signed(dco_phase_ramp_d); // is this okay?
	//ref_phase_ramp_shifted=ref_phase_ramp<<TDC_WIDTH; // subtract ssc_value to downspread freq
	ref_phase_ramp_shifted=ref_phase_ramp; // ble_test 
	phase_ramp_error_true = $signed(ref_phase_ramp_shifted)-$signed(dco_phase_ramp_diff);
	phase_ramp_error_true_delta = phase_ramp_error_true - phase_ramp_error_true_d;
	phase_ramp_error_temp = phase_ramp_error_true_delta + phase_ramp_error_d;
  end

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
    casex(cs_pll) 
    	PLL_PHASE_TRACK: begin
		error_proportional = phase_ramp_error*filter_kp_d;
		error_integral = phase_ramp_error*filter_ki_d;
	end
    	PLL_FREQ_TRACK: begin
		error_proportional = 0;
		error_integral = 0;
	end
    	PLL_INIT: begin
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
				filter_accum_d <= $unsigned(DCO_FCW_MAX/2)<<<(FILTER_ACCUM_FRAC_WIDTH +1 -TDC_WIDTH); // km-test
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
		//filter_out_int = filter_out>>>(FILTER_ACCUM_FRAC_WIDTH+1-TDC_WIDTH); //km-test
		filter_out_int = filter_out>>>(FILTER_ACCUM_FRAC_WIDTH+1-TDC_WIDTH-SD_WIDTH); //km-test dsm

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
	always_ff @(posedge CLK_DITHER or posedge RST) begin
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
	always @* begin
		if (`PLL_INIT_STATE) begin
			dco_ccw_therm = {{DCO_CCW_MAX_H{1'b0}},{DCO_CCW_MAX_H{1'b1}}};
		end
		if (`PLL_FREQ_TRACK_STATE) begin
			if ((phase_ramp_error<0) && (dco_ccw_therm>0)) begin
				dco_ccw_therm = {1'b0,dco_ccw_therm_d[DCO_CCW_MAX-1:1]};
			end else if ((phase_ramp_error>0) && (dco_ccw_therm[DCO_CCW_MAX-1]==0)) begin
				dco_ccw_therm = {dco_ccw_therm_d[DCO_CCW_MAX-2:0],1'b1};
			end
		end else if (`PLL_PHASE_TRACK_STATE) begin
			dco_ccw_therm = dco_ccw_fix;
		end
	end 

	// Latch the dco control words
	always_ff @(posedge CLKREF_RETIMED or posedge RST) begin
		//if (`PLL_INIT_STATE) begin 
		if (RST) begin // km-test 
			DCO_CCW_OUT <= {{DCO_CCW_MAX_H{1'b0}},{DCO_CCW_MAX_H{1'b1}}};
			dco_fcw_therm_latch <= {{DCO_FCW_MAX_H-1{1'b0}},{DCO_FCW_MAX_H{1'b1}}};
			freq_lock_detect <= 0;
	  		freq_lock_cnt <= 0;
			dco_ccw_fix <= 0;
			dco_ccw_fix_cand <= 0;
			dco_ccw_therm_d <= dco_ccw_therm;
		end else if (`PLL_FREQ_TRACK_STATE) begin
		//	if (phase_ramp_error >= -2**(TDC_WIDTH+1) && phase_ramp_error <=2**(TDC_WIDTH+1)) begin
			//if (phase_ramp_error >= -32 && phase_ramp_error <=32) begin
			if (phase_ramp_error >= -32*2**(TDC_SHIFT-1) && phase_ramp_error <=32*2**(TDC_SHIFT-1)) begin
			//if (phase_ramp_error ==0 ) begin
				freq_lock_cnt <= freq_lock_cnt+1;
				dco_ccw_fix_cand <= dco_ccw_therm_d;
			end
			if (freq_lock_cnt >= freq_lock_limit && freq_lock_detect==0) begin
				freq_lock_detect <= 1;
				dco_ccw_fix <= dco_ccw_fix_cand; 
			end
			DCO_CCW_OUT <= dco_ccw_therm;
			dco_ccw_therm_d <= dco_ccw_therm;
		end else if (`PLL_PHASE_TRACK_STATE) begin
			DCO_CCW_OUT <= dco_ccw_therm;
			dco_fcw_therm_latch <= dco_fcw_therm;
		end
	end

	// detecet overflow in fcw. get the open loop control words
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

	always_ff @(posedge CLKREF_RETIMED or posedge RST) begin
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
	bin2therm #(.NBIN(DCO_FCW_BIN_WIDTH),.NTHERM(DCO_FCW_MAX-1)) decFC(.binin(dco_fcw_bin_final), .thermout(dco_fcw_therm));
	assign DCO_FCW_OUT = {dco_fcw_therm_latch,fine_dither_out};
	assign DCO_CCW_OUTN = ~DCO_CCW_OUT; 
	assign DCO_FCW_OUTN = ~DCO_FCW_OUT; 
//==========================================================================================
//			Filter adjustments
//==========================================================================================

	// Instatiate the fine lock controller
	fine_lock_controller #(
			.FCW_WIDTH(FCW_WIDTH),
			.PHASE_RAMP_ERROR_WIDTH(REF_ACCUM_WIDTH),
			.FINE_LOCK_THSH_MAX(FINE_LOCK_THSH_MAX),
			.FINE_LOCK_COUNT_MAX(FINE_LOCK_COUNT_MAX))
		u_fine_lock_controller(
			.FCW_IN(frequency_control_word),
			.PHASE_RAMP_ERROR(phase_ramp_error),
			.FINE_LOCK_ENABLE(FINE_LOCK_ENABLE),
			.FINE_LOCK_THRESHOLD(FINE_LOCK_THRESHOLD),
			.FINE_LOCK_COUNT(FINE_LOCK_COUNT),
			.CK(CLKREF_RETIMED),
			.RST(RST),
			.FINE_LOCK_DETECT(fine_lock_detect)
	);

	// keep track of the filter coefficients
	always @* begin

		dlf_adjuest_en = DLF_ADJUST_EN;
	
		dlf_lock_kp = $signed({1'b0,DLF_LOCK_KP})<<<(FILTER_GAIN_FRAC_WIDTH-KP_FRAC_WIDTH);
		dlf_track_kp = $signed({1'b0,DLF_TRACK_KP})<<<(FILTER_GAIN_FRAC_WIDTH-KP_FRAC_WIDTH);

		dlf_lock_ki = $signed({1'b0,DLF_LOCK_KI})<<<(FILTER_GAIN_FRAC_WIDTH-KI_FRAC_WIDTH);
		dlf_track_ki = $signed({1'b0,DLF_TRACK_KI})<<<(FILTER_GAIN_FRAC_WIDTH-KI_FRAC_WIDTH);

	end

	always_ff @(posedge CLKREF_RETIMED or posedge RST) begin
		if (RST) 
			begin
				dlf_adjuest_en_d <= 0;

				dlf_lock_kp_d <= 0;
				dlf_track_kp_d <= 0;
	
				dlf_lock_ki_d <= 0;
				dlf_track_ki_d <= 0;
			end
		else
			begin
				dlf_adjuest_en_d <= dlf_adjuest_en;

				dlf_lock_kp_d <= dlf_lock_kp;
				dlf_track_kp_d <= dlf_track_kp;
	
				dlf_lock_ki_d <= dlf_lock_ki;
				dlf_track_ki_d <= dlf_track_ki;
			end
	end

	// adjust the filter coefficients for different modes
	always @* begin
		if (dlf_adjuest_en == 1'b1) 
			begin
				if (fine_lock_detect == 1'b0)
					begin
						filter_kp = dlf_track_kp_d;
						filter_ki = dlf_track_ki_d;
					end
				else
					begin
						filter_kp = dlf_lock_kp_d;
						filter_ki = dlf_lock_ki_d;
					end
			end 
		else 
			begin
				filter_kp = dlf_lock_kp_d;
				filter_ki = dlf_lock_ki_d;
			end
	end

	always_ff @(posedge CLKREF_RETIMED or posedge RST) begin
		if (RST) 
			begin
				filter_kp_d <= 0;
				filter_ki_d <= 0;
			end
		else
			begin
				filter_kp_d <= filter_kp;
				filter_ki_d <= filter_ki;
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
			8: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_fcw};
			9: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, filter_kp_d};
			10:	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, filter_ki_d};
			
			default: 
			    CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_fcw};
		endcase
	end

endmodule
	


module fine_lock_controller(
		FCW_IN,
		PHASE_RAMP_ERROR,

		FINE_LOCK_ENABLE,
		FINE_LOCK_THRESHOLD,
		FINE_LOCK_COUNT,

		CK,
		RST,
	
		FINE_LOCK_DETECT);


// Functions


// Parameters
	parameter FCW_WIDTH = 13;
	parameter PHASE_RAMP_ERROR_WIDTH = 10;
	parameter FINE_LOCK_THSH_MAX = 127;
	parameter FINE_LOCK_COUNT_MAX = 127;



// Local parameters
	localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
	localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

	
// Ports
	input 		[FCW_WIDTH-1:0] 		FCW_IN;
	input 		[PHASE_RAMP_ERROR_WIDTH-1:0]	PHASE_RAMP_ERROR;

	input 						FINE_LOCK_ENABLE;
	input 		[FINE_LOCK_THSH_WIDTH-1:0]   	FINE_LOCK_THRESHOLD;
	input 		[FINE_LOCK_COUNT_WIDTH-1:0] 	FINE_LOCK_COUNT;

	input 						CK;
	input 						RST;

	output reg					FINE_LOCK_DETECT;

		
// Interconnects
	reg 		[FCW_WIDTH-1:0] 		frequency_control_word;
	reg 		[FCW_WIDTH-1:0] 		frequency_control_word_d;

	reg signed	[PHASE_RAMP_ERROR_WIDTH-1:0] 	phase_ramp_error;
	reg signed	[PHASE_RAMP_ERROR_WIDTH-1:0] 	phase_ramp_error_d;

	reg 						fine_lock_enable;
	reg 						fine_lock_enable_d;

	reg 		[FINE_LOCK_THSH_WIDTH-1:0] 	fine_lock_threshold;
	reg 		[FINE_LOCK_THSH_WIDTH-1:0] 	fine_lock_threshold_d;

	reg 		[FINE_LOCK_COUNT_WIDTH-1:0] 	fine_lock_count;
	reg 		[FINE_LOCK_COUNT_WIDTH-1:0] 	fine_lock_count_d;

	reg 		[FINE_LOCK_COUNT_WIDTH:0]	fine_lock_accum;
	reg 		[FINE_LOCK_COUNT_WIDTH:0]	fine_lock_accum_d;

	reg 						fine_lock_detect;
	reg 						fine_lock_detect_d;



// Detect whether the PLL is fine locked

	// Keep track of some of the inputs
	always @* begin
		frequency_control_word = FCW_IN;
		phase_ramp_error = $signed(PHASE_RAMP_ERROR);

		fine_lock_enable = FINE_LOCK_ENABLE;
		fine_lock_threshold = (FINE_LOCK_THRESHOLD > FINE_LOCK_THSH_MAX) ? FINE_LOCK_THSH_MAX : FINE_LOCK_THRESHOLD;
		fine_lock_count = (FINE_LOCK_COUNT > FINE_LOCK_COUNT_MAX) ? FINE_LOCK_COUNT_MAX : FINE_LOCK_COUNT;
	end


	always @(posedge CK or posedge RST) begin

		if (RST)
			begin
				frequency_control_word_d <= 0;
				phase_ramp_error_d <= 0;

				fine_lock_enable_d <= 0;
				fine_lock_threshold_d <= 0;
				fine_lock_count_d <= 0;
			end
		else
			begin
				frequency_control_word_d <= frequency_control_word;
				phase_ramp_error_d <= phase_ramp_error;

				fine_lock_enable_d <= fine_lock_enable;
				fine_lock_threshold_d <= fine_lock_threshold;
				fine_lock_count_d <= fine_lock_count;
			end

	end


	// Run the fine lock accumulator when no fine lock is detected
	// and reset the value when appropriate
	always @* begin
		if (frequency_control_word != frequency_control_word_d) 
			begin
				// only reset the counter when the control word changes
				fine_lock_accum = 0;
			end
		else if ((fine_lock_enable_d == 1'b1) && (fine_lock_detect_d == 1'b0))
			begin
				if ( (phase_ramp_error > -$signed({1'b0,fine_lock_threshold})) && 
					(phase_ramp_error < $signed({1'b0,fine_lock_threshold})) )
					begin
						// increment the counter when the lock detect is off 
						// and the ramp error is bounded
						fine_lock_accum = fine_lock_accum_d + 1;
					end
				else
					begin
						// otherwise restart the counter
						fine_lock_accum = 0;
					end
			end
		else
			begin
				fine_lock_accum = fine_lock_accum_d;
			end
	end

	always @(posedge CK or posedge RST) begin
		if (RST)
			fine_lock_accum_d <= 0;
		else
			fine_lock_accum_d <= fine_lock_accum;
	end

	// Check for a coarse lock
	always @* begin
		fine_lock_detect = (fine_lock_accum_d > fine_lock_count_d) ? 1'b1 : 1'b0;
	end

	always @(posedge CK or posedge RST) begin
		if (RST)
			fine_lock_detect_d <= 1'b0;
		else
			fine_lock_detect_d <= fine_lock_detect;
	end
	// Build the outputs
	always @* begin
		FINE_LOCK_DETECT = fine_lock_detect_d;
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
  
  //assign next_sum = dither_en ? ({ 1'b0 , sum[(SD_WIDTH-1):0]} + { 1'b0, dco_fine_frac[SD_WIDTH:(4-SD_WIDTH+1)]}) : {(SD_WIDTH + 1){1'b0}}; 
  assign next_sum = dither_en ? ({ 1'b0 , sum[(SD_WIDTH-1):0]} + { 1'b0, dco_fine_frac[SD_WIDTH-1:0]}) : {(SD_WIDTH + 1){1'b0}}; 

  always_ff @(posedge clk_dither or posedge rst) 
    if (rst)
      sum <= {(SD_WIDTH+1){1'b0}};      
    else
      sum <= next_sum;

endmodule // adpll_dcodither
