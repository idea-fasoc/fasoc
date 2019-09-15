`ifndef __PLL_CONTROLLLER__
`define __PLL_CONTROLLLER__


`include "SSC_GENERATOR.v"
///////////////////////////////////////////////////////////////////////
//
//	PLL_CONTROLLER -- REVIVION LIST
//
//	
//	VER 0.1
//		Author:		Jeffrey Fredenburg	
//		Date:		11-16-2015
//
//		
//		The number of gates needed to contrust the filter is way too big. In a 28nm process, 
//		the path delay from TDC output to the DCO control words was 12ns. Need to reduce the
//		delay of this path since clock frequencies can be on the order of 5ns (200Mhz). The
//		potential stategies to reduce this delay include:
//
//			(1) 	Reduce the number of fractional bits used by the controller. Currently all 
//					fractional bits are used throughout the filter. The fractional bits will be
//					contrained on the gained error values and the filter values.
//				
//			(2)		Implement an alternative overflow/underflow error check. In this version
//					every signal is check for overflow in the critical filter path. Since 
//					overflow/underflow errors only become a problem durnig locking, a few
//					overflow/underflow errors can be tolerated. As long as the PLL moves in
//					the right direction on average, some errors can go through
//
//			(3)		
//
//
//
//
//




`timescale 1ns/1ps

module PLL_CONTROLLER(
	CLKREF_RETIMED,	// retimed reference clk   
	RST,				// active high reset 
	FCW_INT,			// integer FCW to the PLL 
	FCW_FRAC,			// fractional FCW to the PLL, not tested yet 
	DCO_OPEN_LOOP_CTRL,	// combined CW to the DCO, only valid in open loop    
	DCO_OPEN_LOOP_EN,	// switch between open and close loop
	DLF_ADJUST_EN,		// enable for loop filter fast and slow mode adjustment
	DLF_SLOW_KP,		// loop filter Kp for slow mode 
	DLF_SLOW_KI,		// loop filter Ki for slow mode
	DLF_FAST_KP,		// loop filter Kp for fast mode
	DLF_FAST_KI,		// loop filter Ki for fast mode 
	DLF_SLEW_KP,		// loop filter Kp for slewing mode
	DLF_SLEW_KI,		// loop filter Ki for slewing mode 
	COUNT_IN,			// retimed clkref sampled counter input(this is the coarse DCO phase) 
	TDC_IN,				// retimed clkref sampled TDC output(this is the fine DCO phase)  

	//COARSE_LOCK_ENABLE,
	//COARSE_LOCK_REGION_SEL,
	//COARSE_LOCK_THRESHOLD,
	//COARSE_LOCK_COUNT,
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,

	CAPTURE_MUX_SEL,	// Select among different internal signals to view for testing purposes.

	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,

	DCO_CCW_OUT,		// OUTPUT: coarse CW to the DCO   
	DCO_FCW_OUT,		// OUTPUT: fine CW to the DCO
	FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode. 
	CAPTURE_MUX_OUT);	// OUTPUT: The internal signal selected to view as an output. 
						

	// Functions
		`include "FUNCTIONS.v"


	//Parameters
		parameter integer TDC_MAX = 63; 
		parameter integer TDC_EXTRA_BITS = 1; // 
		parameter integer FCW_MAX = 31;
		parameter integer FCW_MIN = 3;
		parameter integer DCO_CCW_MAX = 127;
		parameter integer DCO_FCW_MAX = 511;
		parameter integer KP_WIDTH = 12;
		parameter integer KP_FRAC_WIDTH = 2;
		parameter integer KI_WIDTH = 12;
		parameter integer KI_FRAC_WIDTH = 6;
		parameter integer ACCUM_EXTRA_BITS = 4;
		parameter integer FILTER_EXTRA_BITS = 2;

		parameter integer NUM_COARSE_LOCK_REGIONS = 3;
		parameter integer COARSE_LOCK_THSH_MAX = 127;
		parameter integer COARSE_LOCK_COUNT_MAX = 127;
		parameter integer FINE_LOCK_THSH_MAX = 127;
		parameter integer FINE_LOCK_COUNT_MAX = 127;

		parameter integer CAPTURE_WIDTH = 25;

		parameter SSC_COUNT_WIDTH = 12;
		parameter SSC_ACCUM_WIDTH = 16;
		parameter SSC_MOD_WIDTH = 5;
		parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

	// Local Parameters

		// Sign bits
		localparam SIGN_BIT = 1;
		localparam EXTRA_SIGN_BIT = 1;

		// TDC word sizes
		//localparam TDC_WIDTH = func_clog2(TDC_MAX);
		localparam TDC_WIDTH = func_clog2(TDC_MAX);
		localparam TDC_BIT_MAX = 2**TDC_WIDTH;// only used in next line
		localparam TDC_SCALE = (TDC_BIT_MAX << TDC_EXTRA_BITS)/(TDC_MAX+1);
		localparam TDC_ROUND_WIDTH = TDC_WIDTH + TDC_EXTRA_BITS;

		// Reference accumulator control word sizes
		localparam FCW_FRAC_WIDTH = TDC_WIDTH;
		localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
		localparam FCW_WIDTH = FCW_INT_WIDTH + TDC_ROUND_WIDTH;

	
		// DCO control word sizes
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);


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
		localparam FILTER_ACCUM_INT_WIDTH = func_MAX(GAINED_ERROR_INT_WIDTH, DCO_CCW_WIDTH+DCO_FCW_WIDTH+SIGN_BIT) + FILTER_EXTRA_BITS;
		localparam FILTER_ACCUM_FRAC_WIDTH = FILTER_GAIN_FRAC_WIDTH + TDC_ROUND_WIDTH;
		localparam FILTER_ACCUM_WIDTH = FILTER_ACCUM_INT_WIDTH + FILTER_ACCUM_FRAC_WIDTH;

		localparam signed FILTER_ACCUM_MAX = {1'b0, {FILTER_ACCUM_WIDTH-1{1'b1}}};
		localparam signed FILTER_ACCUM_MIN = {1'b1, {FILTER_ACCUM_WIDTH-1{1'b0}}};

		localparam COARSE_LOCK_REGION_WIDTH = func_clog2(NUM_COARSE_LOCK_REGIONS);
		localparam COARSE_LOCK_THSH_WIDTH = func_clog2(COARSE_LOCK_THSH_MAX);
		localparam COARSE_LOCK_COUNT_WIDTH = func_clog2(COARSE_LOCK_COUNT_MAX);

		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);



	// Ports
		input 										CLKREF_RETIMED;
		input 										RST;
		input 		[FCW_INT_WIDTH-1:0] 			FCW_INT;
		input 		[FCW_FRAC_WIDTH-1:0]			FCW_FRAC;  

		input 		[DCO_CCW_WIDTH +
					 DCO_FCW_WIDTH-1:0]				DCO_OPEN_LOOP_CTRL;
		input 										DCO_OPEN_LOOP_EN;
		input 										DLF_ADJUST_EN;
		input 		[KP_WIDTH-1:0]					DLF_SLOW_KP;
		input 		[KI_WIDTH-1:0] 					DLF_SLOW_KI;
		input 		[KP_WIDTH-1:0] 					DLF_FAST_KP;
		input 		[KI_WIDTH-1:0] 					DLF_FAST_KI;
		input 		[KP_WIDTH-1:0] 					DLF_SLEW_KP;
		input 		[KI_WIDTH-1:0] 					DLF_SLEW_KI;

		input 		[REF_ACCUM_WIDTH-
						TDC_ROUND_WIDTH-1:0] 		COUNT_IN;
		input 		[TDC_WIDTH-1:0] 				TDC_IN;

//		input 										COARSE_LOCK_ENABLE;
//		input 		[COARSE_LOCK_REGION_WIDTH-1:0] 	COARSE_LOCK_REGION_SEL;
//		input 		[COARSE_LOCK_THSH_WIDTH-1:0]    COARSE_LOCK_THRESHOLD;
//		input 		[COARSE_LOCK_COUNT_WIDTH-1:0] 	COARSE_LOCK_COUNT;

		input 										FINE_LOCK_ENABLE;
		input 		[FINE_LOCK_THSH_WIDTH-1:0] 		FINE_LOCK_THRESHOLD;
		input 		[FINE_LOCK_COUNT_WIDTH-1:0] 	FINE_LOCK_COUNT;

		input 		[3:0] 							CAPTURE_MUX_SEL;

		input 										SSC_EN;
		input 		[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
		input 		[3:0]							SSC_STEP;
		input		[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

		output reg	[DCO_CCW_WIDTH-1:0]	 			DCO_CCW_OUT;
		output reg	[DCO_FCW_WIDTH-1:0] 			DCO_FCW_OUT;

		output reg 									FINE_LOCK_DETECT;
		output reg 	[CAPTURE_WIDTH-1 :0]			CAPTURE_MUX_OUT;


	//Internal Signals
		reg 		[FCW_WIDTH-1:0] 				frequency_control_word;
		reg 		[FCW_WIDTH-1:0] 				frequency_control_word_temp;
		reg 		[FCW_WIDTH-1:0]					frequency_control_word_d;
		reg			[TDC_ROUND_WIDTH-1:0]			tdc_round;


		reg 		[REF_ACCUM_WIDTH-1:0]			ref_phase_ramp;
		reg 		[REF_ACCUM_WIDTH-1:0]			dco_phase_ramp;

		reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true;
		reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true_d;
		reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true_delta;


		reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error;
		reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_d;
		reg signed	[REF_ACCUM_WIDTH:0]				phase_ramp_error_temp;


		reg 										dlf_adjuest_en;
		reg 										dlf_adjuest_en_d;

		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slow_kp;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_fast_kp;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_kp;

		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slow_kp_d;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_fast_kp_d;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_kp_d;

		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slow_ki;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_fast_ki;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_ki;		
		
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slow_ki_d;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_fast_ki_d;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			dlf_slew_ki_d;		


		reg signed	[FILTER_GAIN_WIDTH-1:0]			filter_kp;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			filter_kp_d;


		reg signed	[FILTER_GAIN_WIDTH-1:0]			filter_ki;
		reg signed	[FILTER_GAIN_WIDTH-1:0]			filter_ki_d;


		reg signed  [GAINED_ERROR_WIDTH-1:0]		error_proportional;
		reg signed  [GAINED_ERROR_WIDTH-1:0]		error_integral;


		reg signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum;
		reg signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum_d;
		reg	signed	[FILTER_ACCUM_WIDTH:0]			filter_accum_temp; 


		reg signed	[FILTER_ACCUM_WIDTH-1:0]		filter_out; 
		reg signed 	[FILTER_ACCUM_WIDTH-1:0]		filter_out_d;		
		reg	signed	[FILTER_ACCUM_WIDTH:0]			filter_out_temp;


		reg	signed	[FILTER_ACCUM_INT_WIDTH-1:0]	filter_out_int; 
		reg			[FILTER_ACCUM_INT_WIDTH-1:0]	dco_control_word;

		reg 		[DCO_CCW_WIDTH-1:0]				dco_ccw;
		reg 		[DCO_CCW_WIDTH-1:0]				dco_ccw_filter;
		wire 		[DCO_CCW_WIDTH-1:0]				dco_ccw_coarse_lock_ctrl;

		reg 		[DCO_FCW_WIDTH-1:0]				dco_fcw;		
		reg 		[DCO_FCW_WIDTH-1:0]				dco_fcw_filter;
		wire 		[DCO_FCW_WIDTH-1:0]				dco_fcw_coarse_lock_ctrl;

		reg											dco_open_loop_en_d;
		reg			[DCO_CCW_WIDTH +
					 DCO_FCW_WIDTH-1:0]				dco_open_loop_ctrl_d;
		reg 		[DCO_CCW_WIDTH-1:0]				dco_ccw_open_loop;
		reg 		[DCO_FCW_WIDTH-1:0]				dco_fcw_open_loop;

		wire 										fine_lock_detect;

		reg			[SSC_MOD_WIDTH-1:0]				ssc_value;
	

	// Create the phase ramps and the error signal

		// build the frequecny control word and check limits
		always @* begin
			frequency_control_word_temp = {FCW_INT, FCW_FRAC, {TDC_EXTRA_BITS{1'b0}}};

			if (frequency_control_word_temp > {FCW_MAX, {TDC_ROUND_WIDTH{1'b0}}})
				begin
					frequency_control_word = {FCW_MAX, {TDC_ROUND_WIDTH{1'b0}}};
				end
			else if(frequency_control_word_temp < {FCW_MIN, {TDC_ROUND_WIDTH{1'b0}}})
				begin
					frequency_control_word = {FCW_MIN, {TDC_ROUND_WIDTH{1'b0}}};
				end
			else
				begin
					frequency_control_word = frequency_control_word_temp;
				end
		end


		// Triangle Wave Generation for Spread Spectrum (SSC)
		SSC_GENERATOR #(
			.COUNT_WIDTH(SSC_COUNT_WIDTH),
			.ACCUM_WIDTH(SSC_ACCUM_WIDTH),
			.MOD_WIDTH(SSC_MOD_WIDTH),
			.SHIFT_WIDTH(SSC_SHIFT_WIDTH))
			ssc_gen(
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
			if (RST) 
				begin
					ref_phase_ramp <= 0;

					phase_ramp_error_d <= 0;
					phase_ramp_error_true_d <= 0;
				end
			else
				begin
					//Add SSC here
					ref_phase_ramp <= ref_phase_ramp + frequency_control_word - ssc_value;//subtract ssc_value to downspread freq
					
					phase_ramp_error_d <= phase_ramp_error;
					phase_ramp_error_true_d <= phase_ramp_error_true;
				end
		end



		// generare the error signal
		always @* begin

			// concatinate the dco couter output to get the dco phase ramp
			tdc_round = TDC_IN*TDC_SCALE; // generate TDC rounded value
			dco_phase_ramp = {COUNT_IN,tdc_round}; // concatenate counter and tdc to get dco phase


			// generate a test error signal using modulus arithmetic
			// need the bit width of the error signal to match the bit width of the phase ramps
			phase_ramp_error_true = $signed(ref_phase_ramp)-$signed(dco_phase_ramp);
			phase_ramp_error_true_delta = phase_ramp_error_true - phase_ramp_error_true_d;

			phase_ramp_error_temp = phase_ramp_error_true_delta + phase_ramp_error_d;

		end


		// After the system cycle slips enough, get back to the right error
		always @* begin

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


	//Filter Stuff
	
		// Calculate the filter states
		always @(*) begin
			error_proportional = phase_ramp_error*filter_kp_d;
			error_integral = phase_ramp_error*filter_ki_d;

			filter_out_temp = filter_accum + error_proportional;
			filter_accum_temp = filter_accum_d + error_integral;
		end


		// Check for overflow
		always @* begin

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




		// Latch the filter states
		always @(posedge CLKREF_RETIMED or posedge RST) begin
			if (RST) 
				begin 
					filter_out_d <= 0;
					filter_accum_d <= 0;
				end
			else
				begin
					filter_out_d <= filter_out;
					filter_accum_d <= filter_accum;			
				end	
		end




	// Generate the DCO control words


		//Convert Filter Changes to changes in CC and FC	
		always @* begin

			// use the integer portion of the filter output
			filter_out_int = filter_out>>>(FILTER_ACCUM_FRAC_WIDTH+1);


			// check for overflow in the DCO control word
			if (filter_out_int >= 2**(DCO_CCW_WIDTH+DCO_FCW_WIDTH)-1 )
				begin
					dco_control_word = $unsigned(2**(DCO_CCW_WIDTH+DCO_FCW_WIDTH)-1);
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
			{dco_ccw_filter,dco_fcw_filter} = dco_control_word;

		end



		// Instantiate the coarse lock controller
//		COARSE_LOCK_CONTROLLER #(
//				.DCO_CCW_MAX(DCO_CCW_MAX),
//				.DCO_FCW_MAX(DCO_FCW_MAX),
//				.FCW_WIDTH(FCW_WIDTH),
//				.PHASE_RAMP_ERROR_WIDTH(REF_ACCUM_WIDTH),
//				.NUM_COARSE_LOCK_REGIONS(NUM_COARSE_LOCK_REGIONS),
//				.COARSE_LOCK_THSH_MAX(COARSE_LOCK_THSH_MAX),
//				.COARSE_LOCK_COUNT_MAX(COARSE_LOCK_COUNT_MAX))
//			coarse_lock_controller(
//				.DCO_CCW_IN(dco_ccw_filter),
//				.DCO_FCW_IN(dco_fcw_filter),
//				.FCW_IN(frequency_control_word),
//				.PHASE_RAMP_ERROR(phase_ramp_error),
//				.COARSE_LOCK_ENABLE(COARSE_LOCK_ENABLE),
//				.COARSE_LOCK_REGION_SEL(COARSE_LOCK_REGION_SEL),
//				.COARSE_LOCK_THRESHOLD(COARSE_LOCK_THRESHOLD),
//				.COARSE_LOCK_COUNT(COARSE_LOCK_COUNT),
//				.CK(CLKREF_RETIMED),
//				.RST(RST),
//				.DCO_CCW_OUT(dco_ccw_coarse_lock_ctrl),
//				.DCO_FCW_OUT(dco_fcw_coarse_lock_ctrl)
//		);




		// Latch the dco control words
		always @(posedge CLKREF_RETIMED or posedge RST) begin
			if (RST) 
				begin
					dco_ccw <= $unsigned(DCO_CCW_MAX/2);
					dco_fcw <= $unsigned(DCO_FCW_MAX/2);
				end
			else
				begin
					//dco_ccw <= dco_open_loop_en_d ? dco_ccw_open_loop : dco_ccw_coarse_lock_ctrl;
					//dco_fcw <= dco_open_loop_en_d ? dco_fcw_open_loop : dco_fcw_coarse_lock_ctrl;	
					dco_ccw <= dco_open_loop_en_d ? dco_ccw_open_loop : dco_ccw_filter;
					dco_fcw <= dco_open_loop_en_d ? dco_fcw_open_loop : dco_fcw_filter;	
				end
		end


		// get the open loop control words
		always @* begin
			dco_ccw_open_loop = dco_open_loop_ctrl_d[DCO_FCW_WIDTH+:DCO_CCW_WIDTH];
			dco_fcw_open_loop = dco_open_loop_ctrl_d[0+:DCO_FCW_WIDTH];


			DCO_CCW_OUT = dco_ccw;
			DCO_FCW_OUT = dco_fcw;
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



	// Additional Filter Adjustments


		// Instatiate the fine lock controller
		FINE_LOCK_CONTROLLER #(
				.FCW_WIDTH(FCW_WIDTH),
				.PHASE_RAMP_ERROR_WIDTH(REF_ACCUM_WIDTH),
				.FINE_LOCK_THSH_MAX(FINE_LOCK_THSH_MAX),
				.FINE_LOCK_COUNT_MAX(FINE_LOCK_COUNT_MAX))
			fine_lock_controller(
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
		
			dlf_slow_kp = $signed({1'b0,DLF_SLOW_KP})<<<(FILTER_GAIN_FRAC_WIDTH-KP_FRAC_WIDTH);
			dlf_fast_kp = $signed({1'b0,DLF_FAST_KP})<<<(FILTER_GAIN_FRAC_WIDTH-KP_FRAC_WIDTH);
			dlf_slew_kp = $signed({1'b0,DLF_SLEW_KP})<<<(FILTER_GAIN_FRAC_WIDTH-KP_FRAC_WIDTH);
	
			dlf_slow_ki = $signed({1'b0,DLF_SLOW_KI})<<<(FILTER_GAIN_FRAC_WIDTH-KI_FRAC_WIDTH);
			dlf_fast_ki = $signed({1'b0,DLF_FAST_KI})<<<(FILTER_GAIN_FRAC_WIDTH-KI_FRAC_WIDTH);
			dlf_slew_ki = $signed({1'b0,DLF_SLEW_KI})<<<(FILTER_GAIN_FRAC_WIDTH-KI_FRAC_WIDTH);

		end


		always @(posedge CLKREF_RETIMED or posedge RST) begin

			if (RST) 
				begin
					dlf_adjuest_en_d <= 0;

					dlf_slow_kp_d <= 0;
					dlf_fast_kp_d <= 0;
					dlf_slew_kp_d <= 0;
		
					dlf_slow_ki_d <= 0;
					dlf_fast_ki_d <= 0;
					dlf_slew_ki_d <= 0;
				end
			else
				begin
					dlf_adjuest_en_d <= dlf_adjuest_en;

					dlf_slow_kp_d <= dlf_slow_kp;
					dlf_fast_kp_d <= dlf_fast_kp;
					dlf_slew_kp_d <= dlf_slew_kp;
		
					dlf_slow_ki_d <= dlf_slow_ki;
					dlf_fast_ki_d <= dlf_fast_ki;
					dlf_slew_ki_d <= dlf_slew_ki;
				end


		end


		// adjust the filter coefficients for different modes
		always @* begin

			if (dlf_adjuest_en == 1'b1) 
				begin
					if ((phase_ramp_error == PHASE_RAMP_ERROR_MAX) || (phase_ramp_error == PHASE_RAMP_ERROR_MIN))
						begin
							filter_kp = dlf_slew_kp_d;
							filter_ki = dlf_slew_ki_d;
						end
					else if (fine_lock_detect == 1'b0)
						begin
							filter_kp = dlf_fast_kp_d;
							filter_ki = dlf_fast_ki_d;
						end
					else
						begin
							filter_kp = dlf_slow_kp_d;
							filter_ki = dlf_slow_ki_d;
						end
				end 
			else 
				begin
					filter_kp = dlf_slow_kp_d;
					filter_ki = dlf_slow_ki_d;
				end
		end


		always @(posedge CLKREF_RETIMED or posedge RST) begin
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



	// Build the capture system for signal selection (testing purpose)

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
				8: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_ccw, dco_fcw};
				9: 	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, filter_kp_d};
				10:	CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, filter_ki_d};
				
				default: 
				    CAPTURE_MUX_OUT <= {FINE_LOCK_DETECT, dco_ccw, dco_fcw};
			endcase
		end






endmodule
	




module COARSE_LOCK_CONTROLLER(
		DCO_CCW_IN,
		DCO_FCW_IN,
		FCW_IN,
		PHASE_RAMP_ERROR,

		COARSE_LOCK_ENABLE,
		COARSE_LOCK_REGION_SEL,
		COARSE_LOCK_THRESHOLD,
		COARSE_LOCK_COUNT,

		CK,
		RST,
	
		DCO_CCW_OUT,
		DCO_FCW_OUT);



	// Functions
		`include "FUNCTIONS.v"


	// Parameters
		parameter DCO_CCW_MAX = 15;
		parameter DCO_FCW_MAX = 1023;
		parameter FCW_WIDTH = 13;
		parameter PHASE_RAMP_ERROR_WIDTH = 10;
		parameter NUM_COARSE_LOCK_REGIONS = 3;
		parameter COARSE_LOCK_THSH_MAX = 127;
		parameter COARSE_LOCK_COUNT_MAX = 127;




	// Local parameters
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
		localparam COARSE_LOCK_REGION_WIDTH = func_clog2(NUM_COARSE_LOCK_REGIONS);
		localparam COARSE_LOCK_THSH_WIDTH = func_clog2(COARSE_LOCK_THSH_MAX);
		localparam COARSE_LOCK_COUNT_WIDTH = func_clog2(COARSE_LOCK_COUNT_MAX);

		localparam signed COARSE_LOCK_REGION_SEL_MAX = NUM_COARSE_LOCK_REGIONS/2;
		localparam signed COARSE_LOCK_REGION_SEL_MIN = -NUM_COARSE_LOCK_REGIONS/2;
		localparam signed COARSE_LOCK_REGION_SCALE = DCO_FCW_MAX/2/NUM_COARSE_LOCK_REGIONS;


	// Ports
		input 		[DCO_CCW_WIDTH-1:0]				DCO_CCW_IN;
		input 		[DCO_FCW_WIDTH-1:0]				DCO_FCW_IN;
		input 		[FCW_WIDTH-1:0] 				FCW_IN;

		input 		[PHASE_RAMP_ERROR_WIDTH-1:0]	PHASE_RAMP_ERROR;

		input 										COARSE_LOCK_ENABLE;
		input 		[COARSE_LOCK_REGION_WIDTH-1:0] 	COARSE_LOCK_REGION_SEL;
		input 		[COARSE_LOCK_THSH_WIDTH-1:0]    COARSE_LOCK_THRESHOLD;
		input 		[COARSE_LOCK_COUNT_WIDTH-1:0] 	COARSE_LOCK_COUNT;

		input 										CK;
		input 										RST;

		output reg 	[DCO_CCW_WIDTH-1:0]				DCO_CCW_OUT;
		output reg	[DCO_FCW_WIDTH-1:0]				DCO_FCW_OUT;


			
	// Interconnects
		reg 		[FCW_WIDTH-1:0] 				frequency_control_word;
		reg 		[FCW_WIDTH-1:0] 				frequency_control_word_d;

		reg signed	[PHASE_RAMP_ERROR_WIDTH-1:0] 	phase_ramp_error;
		reg signed	[PHASE_RAMP_ERROR_WIDTH-1:0] 	phase_ramp_error_d;

		reg 										coarse_lock_enable;
		reg 										coarse_lock_enable_d;

		reg signed 	[COARSE_LOCK_REGION_WIDTH-1:0] 	coarse_lock_region_sel;
		reg signed 	[COARSE_LOCK_REGION_WIDTH-1:0] 	coarse_lock_region_sel_d;

		reg 		[COARSE_LOCK_THSH_WIDTH-1:0] 	coarse_lock_threshold;
		reg 		[COARSE_LOCK_THSH_WIDTH-1:0] 	coarse_lock_threshold_d;

		reg 		[COARSE_LOCK_COUNT_WIDTH-1:0] 	coarse_lock_count;
		reg 		[COARSE_LOCK_COUNT_WIDTH-1:0] 	coarse_lock_count_d;

		reg 		[COARSE_LOCK_COUNT_WIDTH:0]		coarse_lock_accum;
		reg 		[COARSE_LOCK_COUNT_WIDTH:0]		coarse_lock_accum_d;

		reg 										coarse_lock_detect;
		reg 										coarse_lock_detect_d;

		reg 		[DCO_FCW_WIDTH-1:0] 			coarse_lock_region_upper_bound_fcw;
		reg 	 	[DCO_FCW_WIDTH-1:0] 			coarse_lock_region_lower_bound_fcw;

		reg 		[DCO_CCW_WIDTH-1:0]				dco_ccw_out;
		reg 		[DCO_CCW_WIDTH-1:0]				dco_ccw_out_temp;
		
		reg 		[DCO_FCW_WIDTH-1:0]				dco_fcw_out;
		reg 		[DCO_FCW_WIDTH-1:0]				dco_fcw_out_temp;





	// Detect whether the PLL is coase locked
	
		// Keep track of some of the inputs
		always @* begin
			frequency_control_word = FCW_IN;
			phase_ramp_error = $signed(PHASE_RAMP_ERROR);


			coarse_lock_enable = COARSE_LOCK_ENABLE;
			coarse_lock_region_sel = 
				($signed(COARSE_LOCK_REGION_SEL) > COARSE_LOCK_REGION_SEL_MAX) ? COARSE_LOCK_REGION_SEL_MAX :
				($signed(COARSE_LOCK_REGION_SEL) < COARSE_LOCK_REGION_SEL_MIN) ? COARSE_LOCK_REGION_SEL_MIN : $signed(COARSE_LOCK_REGION_SEL);

			coarse_lock_threshold = (COARSE_LOCK_THRESHOLD > COARSE_LOCK_THSH_MAX) ? COARSE_LOCK_THSH_MAX : COARSE_LOCK_THRESHOLD;
			coarse_lock_count = (COARSE_LOCK_COUNT > COARSE_LOCK_COUNT_MAX) ? COARSE_LOCK_COUNT_MAX : COARSE_LOCK_COUNT;
		end


		always @(posedge CK or posedge RST) begin

			if (RST)
				begin
					
					frequency_control_word_d <= 0;
					phase_ramp_error_d <= 0;

					coarse_lock_enable_d <= 0;
					coarse_lock_region_sel_d <= 0;
					coarse_lock_threshold_d <= 0;
					coarse_lock_count_d <= 0;

				end
			else
				begin
					frequency_control_word_d <= frequency_control_word;
					phase_ramp_error_d <= phase_ramp_error;

					coarse_lock_enable_d <= coarse_lock_enable;
					coarse_lock_region_sel_d <= coarse_lock_region_sel;
					coarse_lock_threshold_d <= coarse_lock_threshold;
					coarse_lock_count_d <= coarse_lock_count;
				end

		end


		// Run the coarse lock accumulator when no coarse lock is detected
		// and reset the value when appropriate
		always @* begin

			if (frequency_control_word != frequency_control_word_d) 
				begin
					
					// only reset the counter when the control word changes
					coarse_lock_accum = 0;

				end
			else if ((coarse_lock_enable_d == 1'b1) && (coarse_lock_detect_d == 1'b0))
				begin

					if ( (phase_ramp_error > -$signed({1'b0,coarse_lock_threshold})) && 
						(phase_ramp_error < $signed({1'b0,coarse_lock_threshold})) )
						begin
								
							// increment the counter when the lock detect is off 
							// and the ramp error is bounded
							coarse_lock_accum = coarse_lock_accum_d + 1;

						end
					else
						begin

							// otherwise restart the counter
							coarse_lock_accum = 0;

						end
				end
			else
				begin
					coarse_lock_accum = coarse_lock_accum_d;
				end


		end


		always @(posedge CK or posedge RST) begin
			if (RST)
				coarse_lock_accum_d <= 0;
			else
				coarse_lock_accum_d <= coarse_lock_accum;
		end



		// Check for a coarse lock
		always @* begin

			coarse_lock_detect = (coarse_lock_accum_d > coarse_lock_count_d) ? 1'b1 : 1'b0;

		end



		always @(posedge CK or posedge RST) begin
			if (RST)
				coarse_lock_detect_d <= 1'b0;
			else
				coarse_lock_detect_d <= coarse_lock_detect;
		end




	// Calculate the dco fine code ranges for the coarse lock 
	

		generate


				if(NUM_COARSE_LOCK_REGIONS%2 == 0)
					begin : NUM_COARSE_LOCK_PARITY
		

						// number of regions are even
						always @* begin

							if (coarse_lock_region_sel_d == 0)
								begin
									coarse_lock_region_upper_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(NUM_COARSE_LOCK_REGIONS+1));
									coarse_lock_region_lower_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(NUM_COARSE_LOCK_REGIONS-1));
								end
							else if (coarse_lock_region_sel_d > 0)
								begin	
									coarse_lock_region_upper_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(NUM_COARSE_LOCK_REGIONS+2*(coarse_lock_region_sel_d-0)));
									coarse_lock_region_lower_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(NUM_COARSE_LOCK_REGIONS+2*(coarse_lock_region_sel_d-1)));
								end
							else
								begin	
									coarse_lock_region_upper_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(NUM_COARSE_LOCK_REGIONS+2*(coarse_lock_region_sel_d+1)));
									coarse_lock_region_lower_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(NUM_COARSE_LOCK_REGIONS+2*(coarse_lock_region_sel_d+0)));
							end

						end
					end
				else
					begin  : NUM_COARSE_LOCK_PARITY

						// number of regions are odd
						always @* begin	

							coarse_lock_region_upper_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(coarse_lock_region_sel_d+COARSE_LOCK_REGION_SEL_MAX+1)<<<1);
							coarse_lock_region_lower_bound_fcw = $unsigned(COARSE_LOCK_REGION_SCALE*(coarse_lock_region_sel_d+COARSE_LOCK_REGION_SEL_MAX+0)<<<1);

						end
					end
			

		endgenerate



	// Map the dco control codes to restricted values when needed for a coarse lock
		always @* begin

			if ( (coarse_lock_detect_d == 1'b1) || (coarse_lock_enable_d == 1'b0) )
				begin
					dco_ccw_out = DCO_CCW_IN;
					dco_fcw_out = DCO_FCW_IN;
				end

			else 
				begin

					if (DCO_FCW_IN >= coarse_lock_region_upper_bound_fcw)
						begin
							dco_ccw_out = (DCO_CCW_IN < DCO_CCW_MAX) ? DCO_CCW_IN+1 : DCO_CCW_IN;
							dco_fcw_out = coarse_lock_region_lower_bound_fcw;
						end
					else if (DCO_FCW_IN <= coarse_lock_region_lower_bound_fcw)
						begin
							dco_ccw_out = (DCO_CCW_IN > 0) ? DCO_CCW_IN-1 : DCO_CCW_IN;
							dco_fcw_out = coarse_lock_region_upper_bound_fcw;
						end
					else
						begin
							dco_ccw_out = DCO_CCW_IN;
							dco_fcw_out = DCO_FCW_IN;
						end

				end


			DCO_CCW_OUT = dco_ccw_out;
			DCO_FCW_OUT = dco_fcw_out;

		end

endmodule



module FINE_LOCK_CONTROLLER(
		FCW_IN,
		PHASE_RAMP_ERROR,

		FINE_LOCK_ENABLE,
		FINE_LOCK_THRESHOLD,
		FINE_LOCK_COUNT,

		CK,
		RST,
	
		FINE_LOCK_DETECT);


	// Functions
		`include "FUNCTIONS.v"


	// Parameters
		parameter FCW_WIDTH = 13;
		parameter PHASE_RAMP_ERROR_WIDTH = 10;
		parameter FINE_LOCK_THSH_MAX = 127;
		parameter FINE_LOCK_COUNT_MAX = 127;



	// Local parameters
		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

		
	// Ports
		input 		[FCW_WIDTH-1:0] 				FCW_IN;
		input 		[PHASE_RAMP_ERROR_WIDTH-1:0]	PHASE_RAMP_ERROR;

		input 										FINE_LOCK_ENABLE;
		input 		[FINE_LOCK_THSH_WIDTH-1:0]   	FINE_LOCK_THRESHOLD;
		input 		[FINE_LOCK_COUNT_WIDTH-1:0] 	FINE_LOCK_COUNT;

		input 										CK;
		input 										RST;

		output reg									FINE_LOCK_DETECT;

			
	// Interconnects
		reg 		[FCW_WIDTH-1:0] 				frequency_control_word;
		reg 		[FCW_WIDTH-1:0] 				frequency_control_word_d;

		reg signed	[PHASE_RAMP_ERROR_WIDTH-1:0] 	phase_ramp_error;
		reg signed	[PHASE_RAMP_ERROR_WIDTH-1:0] 	phase_ramp_error_d;

		reg 										fine_lock_enable;
		reg 										fine_lock_enable_d;

		reg 		[FINE_LOCK_THSH_WIDTH-1:0] 		fine_lock_threshold;
		reg 		[FINE_LOCK_THSH_WIDTH-1:0] 		fine_lock_threshold_d;

		reg 		[FINE_LOCK_COUNT_WIDTH-1:0] 	fine_lock_count;
		reg 		[FINE_LOCK_COUNT_WIDTH-1:0] 	fine_lock_count_d;

		reg 		[FINE_LOCK_COUNT_WIDTH:0]		fine_lock_accum;
		reg 		[FINE_LOCK_COUNT_WIDTH:0]		fine_lock_accum_d;

		reg 										fine_lock_detect;
		reg 										fine_lock_detect_d;



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


`endif
