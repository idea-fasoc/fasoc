
`include "ssc_generator.v"
`include "functions.v"
module tb_pll_controller();

	//Parameters
	parameter integer TDC_MAX = 18;
	parameter integer NTDC = TDC_MAX+2; 
	parameter integer TDC_EXTRA_BITS = 1; // 
	parameter integer FCW_MAX = 31;
	parameter integer FCW_MIN = 3;
	parameter integer DCO_CCW_MAX = 127;
	parameter integer DCO_FCW_MAX = 511;
	parameter integer KP_WIDTH = 12;
	parameter integer KP_FRAC_WIDTH = 2;
	parameter integer KI_WIDTH = 12;
	parameter integer KI_FRAC_WIDTH = 6;
	parameter integer ACCUM_EXTRA_BITS = 9;
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
	localparam TDC_ROUND_WIDTH = TDC_WIDTH;

	// Reference accumulator control word sizes
	localparam FCW_FRAC_WIDTH = TDC_WIDTH;
	localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
	localparam FCW_WIDTH = FCW_INT_WIDTH;


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
	localparam FILTER_ACCUM_FRAC_WIDTH = FILTER_GAIN_FRAC_WIDTH + TDC_ROUND_WIDTH; //km-test
	localparam FILTER_ACCUM_WIDTH = FILTER_ACCUM_INT_WIDTH + FILTER_ACCUM_FRAC_WIDTH;

	localparam signed FILTER_ACCUM_MAX = {1'b0, {FILTER_ACCUM_WIDTH-1{1'b1}}};
	localparam signed FILTER_ACCUM_MIN = {1'b1, {FILTER_ACCUM_WIDTH-1{1'b0}}};

	localparam COARSE_LOCK_REGION_WIDTH = func_clog2(NUM_COARSE_LOCK_REGIONS);
	localparam COARSE_LOCK_THSH_WIDTH = func_clog2(COARSE_LOCK_THSH_MAX);
	localparam COARSE_LOCK_COUNT_WIDTH = func_clog2(COARSE_LOCK_COUNT_MAX);

	localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
	localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

	// freq lock limit
	localparam flock_limit	= 4;

	// Ports
	logic						CLKREF_RETIMED;
	logic						RST;
	logic	[FCW_INT_WIDTH-1:0] 			FCW_INT;
	logic	[FCW_FRAC_WIDTH-1:0]			FCW_FRAC;  

	logic	[DCO_CCW_WIDTH +
				 DCO_FCW_WIDTH-1:0]		DCO_OPEN_LOOP_CTRL;
	logic						DCO_OPEN_LOOP_EN;
	logic						DLF_ADJUST_EN;
	logic	[KP_WIDTH-1:0]				DLF_SLOW_KP;
	logic	[KI_WIDTH-1:0] 				DLF_SLOW_KI;
	logic	[KP_WIDTH-1:0] 				DLF_FAST_KP;
	logic	[KI_WIDTH-1:0] 				DLF_FAST_KI;
	logic	[KP_WIDTH-1:0] 				DLF_SLEW_KP;
	logic	[KI_WIDTH-1:0] 				DLF_SLEW_KI;

	logic	[REF_ACCUM_WIDTH-
					TDC_ROUND_WIDTH-1:0] 	COUNT_IN;
	logic	[TDC_WIDTH-1:0] 			TDC_IN;


	logic						FINE_LOCK_ENABLE;
	logic	[FINE_LOCK_THSH_WIDTH-1:0] 		FINE_LOCK_THRESHOLD;
	logic	[FINE_LOCK_COUNT_WIDTH-1:0]	 	FINE_LOCK_COUNT;

	logic	[3:0] 					CAPTURE_MUX_SEL;

	logic						SSC_EN;
	logic	[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
	logic	[3:0]					SSC_STEP;
	logic	[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

	logic	[DCO_CCW_WIDTH-1:0]	 		DCO_CCW_OUT;
	logic	[DCO_FCW_WIDTH-1:0] 			DCO_FCW_OUT;

	logic 						FINE_LOCK_DETECT;
	logic 	[CAPTURE_WIDTH-1 :0]			CAPTURE_MUX_OUT;


//Internal Signals
	reg 		[FCW_WIDTH-1:0] 			frequency_control_word;
	reg 		[FCW_WIDTH-1:0] 			frequency_control_word_temp;
	reg 		[FCW_WIDTH-1:0]				frequency_control_word_d;
	reg		[TDC_ROUND_WIDTH-1:0]			tdc_round;


	reg 		[REF_ACCUM_WIDTH-1:0]			ref_phase_ramp;
	reg 		[REF_ACCUM_WIDTH-1:0]			ref_phase_ramp_shifted;
	reg 		[REF_ACCUM_WIDTH-1:0]			dco_phase_ramp;
	reg 		[REF_ACCUM_WIDTH:0]			dco_phase_ramp_d;
	reg 		[REF_ACCUM_WIDTH:0]			dco_phase_ramp_diff; // need to think about overflow

	reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true;
	reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true_d;
	reg signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_true_delta;


	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error;
	logic signed	[REF_ACCUM_WIDTH-1:0]			phase_ramp_error_d;
	logic signed	[REF_ACCUM_WIDTH:0]			phase_ramp_error_temp;


	reg 							dlf_adjuest_en;
	reg 							dlf_adjuest_en_d;

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


	logic signed  [GAINED_ERROR_WIDTH-1:0]			error_proportional;
	logic signed  [GAINED_ERROR_WIDTH-1:0]			error_integral;


	reg signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum;
	reg signed	[FILTER_ACCUM_WIDTH-1:0]		filter_accum_d;
	reg	signed	[FILTER_ACCUM_WIDTH:0]			filter_accum_temp; 


	reg signed	[FILTER_ACCUM_WIDTH-1:0]		filter_out; 
	reg signed 	[FILTER_ACCUM_WIDTH-1:0]		filter_out_d;		
	reg	signed	[FILTER_ACCUM_WIDTH:0]			filter_out_temp;


	reg	signed	[FILTER_ACCUM_INT_WIDTH-1:0]		filter_out_int; 
	reg		[FILTER_ACCUM_INT_WIDTH-1:0]		dco_control_word;

	reg 		[DCO_CCW_WIDTH-1:0]			dco_ccw;
	reg 		[DCO_CCW_WIDTH-1:0]			dco_ccw_fix;
	reg 		[DCO_CCW_WIDTH-1:0]			dco_ccw_filter;
	wire 		[DCO_CCW_WIDTH-1:0]			dco_ccw_coarse_lock_ctrl;

	reg 		[DCO_FCW_WIDTH-1:0]			dco_fcw;		
	reg 		[DCO_FCW_WIDTH-1:0]			dco_fcw_filter;
	wire 		[DCO_FCW_WIDTH-1:0]			dco_fcw_coarse_lock_ctrl;

	reg							dco_open_loop_en_d;
	reg			[DCO_CCW_WIDTH +
				 DCO_FCW_WIDTH-1:0]		dco_open_loop_ctrl_d;
	reg 		[DCO_CCW_WIDTH-1:0]			dco_ccw_open_loop;
	reg 		[DCO_FCW_WIDTH-1:0]			dco_fcw_open_loop;

	wire 							fine_lock_detect;
	logic							freq_lock_detect;
	reg			[SSC_MOD_WIDTH-1:0]		ssc_value;
	reg							flock_cnt;
//****************************************************************************************\\
//                              State machine                                             \\
//****************************************************************************************\\
  // FSMs
//  pll_fsm							ns_pll,cs_pll;
	reg [1:0]	ns_pll;
	reg [1:0] 	cs_pll;
	parameter 	PLL_INIT = 2'b00;
	parameter 	PLL_FREQ_TRACK = 2'b01;
	parameter	PLL_PHASE_TRACK = 2'b11;
`define PLL_INIT_STATE						(cs_pll == PLL_INIT )
`define PLL_FREQ_TRACK_STATE             			(cs_pll == PLL_FREQ_TRACK )
`define PLL_PHASE_TRACK_STATE					(cs_pll == PLL_PHASE_TRACK )

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


	// build the frequecny control word and check limits
  always_comb begin
    frequency_control_word_temp = FCW_INT;

    if (frequency_control_word_temp > FCW_MAX)
	begin
  	  frequency_control_word = FCW_MAX;
	end
    else if(frequency_control_word_temp < FCW_MIN)
	begin
       	  frequency_control_word = FCW_MIN;
	end
    else
	begin
	  frequency_control_word = frequency_control_word_temp;
	end
  end

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
    if (`PLL_INIT_STATE) 
	begin
  	  ref_phase_ramp <= 0;
	  flock_cnt <= 0;
	  freq_lock_detect<=0;
	  dco_phase_ramp_d <= 0;
  
  	  phase_ramp_error_d <= 0;
  	  phase_ramp_error_true_d <= 0;
  	end
    else
    if (`PLL_FREQ_TRACK_STATE)
	begin
  	  ref_phase_ramp <= frequency_control_word;

	  dco_phase_ramp_d <= dco_phase_ramp;
  
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
	tdc_round = TDC_IN; // generate TDC rounded value
	dco_phase_ramp = {COUNT_IN,tdc_round}-9; // -9 for mid-rise tdc; COUNT_IN, tdc_round are synced with CLKREF_RETIMED, reset is taken care in tdc_counter
	dco_phase_ramp_diff=$signed(dco_phase_ramp)-$signed(dco_phase_ramp_d); // is this okay?
	ref_phase_ramp_shifted=ref_phase_ramp<<TDC_WIDTH; // subtract ssc_value to downspread freq
	phase_ramp_error_true = $signed(ref_phase_ramp_shifted)-$signed(dco_phase_ramp_diff);
	phase_ramp_error_true_delta = phase_ramp_error_true - phase_ramp_error_true_d;
	phase_ramp_error_temp = phase_ramp_error_true_delta + phase_ramp_error_d;
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

  //always @* begin 
  //      error_proportional = phase_ramp_error*filter_kp_d;
  //      error_integral = phase_ramp_error*filter_ki_d;
  //end
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

  // start stimulus
	initial
	begin
		CLKREF_RETIMED=1'b0;
		RST=1'b0;
		#3;
		RST=1'b1;
		#3;
		RST=1'b0;
		#100;
		$finish;
	end

	always	begin
	#3	CLKREF_RETIMED<=~CLKREF_RETIMED;
	end
endmodule	
