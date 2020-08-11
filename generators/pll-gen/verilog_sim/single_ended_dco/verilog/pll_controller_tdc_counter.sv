// verilog


`timescale 1ns/1ps

//`include "pll_controller.sv"
//`include "tdc_counter.v"
module pll_controller_tdc_counter(
	SAMPLED_PHASES_IN,	// DCO phases sampledby reference clock
	DCO_OUTP,			// DCO positive output
	CLKREF,				// reference clk   
	RST,				// active high reset 
	FCW_INT,			// integer FCW to the PLL 
//	FCW_FRAC,			// fractional FCW to the PLL, not tested yet 
	DCO_OPEN_LOOP_EN,	// switch between open and close loop
	DCO_OPEN_LOOP_CC,	// open loop oscillator coarse control
	DCO_OPEN_LOOP_FC,	// open loop oscillator fine control
	DLF_ADJUST_EN,		// enable for loop filter fast and slow mode adjustment
	DLF_LOCK_KP,		// loop filter Kp for slow mode 
	DLF_LOCK_KI,		// loop filter Ki for slow mode
	DLF_TRACK_KP,		// loop filter Kp for fast mode
	DLF_TRACK_KI,		// loop filter Ki for fast mode 
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,
	CAPTURE_MUX_SEL,	// Select among different internal signals to view for testing purposes.
	CLK_DITHER,
	DITHER_EN,
	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,
	CLKREF_RETIMED,
	DCO_CCW_OUT,		// OUTPUT: coarse CW to the DCO   
	DCO_FCW_OUT,		// OUTPUT: fine CW to the DCO
	FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode. 
	CAPTURE_MUX_OUT);	// OUTPUT: The internal signal selected to view as an output. 



	// Functions
//	`include "functions.v"


	//Parameters
		// dco
		parameter DCO_CCW_MAX = 44;
		parameter DCO_FCW_MAX = 384;

		// CONTROLLER
		parameter TDC_MAX = 18; 
		parameter FCW_MAX = 100;
		parameter FCW_MIN = 10;
		parameter KP_WIDTH = 12;
		parameter KP_FRAC_WIDTH = 6;
		parameter KI_WIDTH = 12;
		parameter KI_FRAC_WIDTH = 10;
		parameter ACCUM_EXTRA_BITS = 9;
		parameter FILTER_EXTRA_BITS = 4;
		
		parameter FINE_LOCK_THSH_MAX = 127;
		parameter FINE_LOCK_COUNT_MAX = 127;
		parameter CAPTURE_WIDTH = 25;

		parameter SSC_COUNT_WIDTH = 12;
		parameter SSC_ACCUM_WIDTH = 16;
		parameter SSC_MOD_WIDTH = 5;
		parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

		// TDC_COUNTER
		parameter TDC_NUM_RETIME_CYCLES = 2;
		parameter TDC_NUM_RETIME_DELAYS = 2;
		parameter TDC_NUM_COUNTER_DIVIDERS = 3;


	// Local Parameters

		// DCO parameter
		localparam DCO_NUM_PHASES = (TDC_MAX/2+1)/2;

		// Controller TDC parameters
		localparam TDC_WIDTH = func_clog2(TDC_MAX);
		localparam TDC_BIT_MAX = 2**TDC_WIDTH;// only used in next line
		localparam TDC_ROUND_WIDTH = TDC_WIDTH;

		// Controller control word sizes
		localparam FCW_FRAC_WIDTH = TDC_WIDTH;
		localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
		localparam FCW_WIDTH = FCW_INT_WIDTH;

	
		// Controller DCO control word sizes
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);

		// Controller reference accumulator sizes
		localparam REF_ACCUM_WIDTH = FCW_WIDTH + ACCUM_EXTRA_BITS;

		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

	

	// Ports
		input 	[DCO_NUM_PHASES-1:0]			SAMPLED_PHASES_IN;
		input						DCO_OUTP;
		input 						CLKREF;
		input 						RST;
		input	[FCW_INT_WIDTH-1:0] 			FCW_INT;
//		input	[FCW_FRAC_WIDTH-1:0] 			FCW_FRAC;

		input 						DCO_OPEN_LOOP_EN;
		input 	[DCO_CCW_WIDTH-1:0]			DCO_OPEN_LOOP_CC;
		input 	[DCO_FCW_WIDTH-1:0] 			DCO_OPEN_LOOP_FC;

		input 						DLF_ADJUST_EN;
		input 	[KP_WIDTH-1:0] 				DLF_LOCK_KP;
		input 	[KI_WIDTH-1:0] 				DLF_LOCK_KI;
		input 	[KP_WIDTH-1:0] 				DLF_TRACK_KP;
		input 	[KI_WIDTH-1:0] 				DLF_TRACK_KI;

		input 						FINE_LOCK_ENABLE;
		input 	[FINE_LOCK_THSH_WIDTH-1:0] 		FINE_LOCK_THRESHOLD;
		input 	[FINE_LOCK_COUNT_WIDTH-1:0] 		FINE_LOCK_COUNT;

		input 	[3:0]					CAPTURE_MUX_SEL;

		input 						CLK_DITHER;
		input 						DITHER_EN;
		input 						SSC_EN;
		input 	[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
		input 	[3:0]					SSC_STEP;
		input	[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

		output						CLKREF_RETIMED;
		output	[DCO_CCW_MAX-1:0]			DCO_CCW_OUT;
		output	[DCO_FCW_MAX-1:0]			DCO_FCW_OUT;

		output 						FINE_LOCK_DETECT;
		output	[CAPTURE_WIDTH-1:0]			CAPTURE_MUX_OUT;


	// Internal Signals
		wire						clkref_retimed;
		wire 	[DCO_FCW_WIDTH + 
				 	DCO_CCW_WIDTH-1:0]	dco_open_loop_cw;
		wire 	[TDC_WIDTH-1:0] 			tdc_out;
		wire 	[REF_ACCUM_WIDTH-
				 	TDC_ROUND_WIDTH-1:0] 	count_accum;
	
		logic	[DCO_CCW_MAX-1:0]			dco_ccw_outn;
		logic	[DCO_FCW_MAX-1:0]			dco_fcw_outn;
	
	// Concatinate the open loop control word
		assign dco_open_loop_cw = {DCO_OPEN_LOOP_CC, DCO_OPEN_LOOP_FC}; 
		assign CLKREF_RETIMED = clkref_retimed;


	// Structural
		pll_controller #(
				.TDC_MAX(TDC_MAX),
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
				.SSC_COUNT_WIDTH(SSC_COUNT_WIDTH),
				.SSC_ACCUM_WIDTH(SSC_ACCUM_WIDTH),
				.SSC_MOD_WIDTH(SSC_MOD_WIDTH),
				.SSC_SHIFT_WIDTH(SSC_SHIFT_WIDTH),
				.CAPTURE_WIDTH(CAPTURE_WIDTH))
			u_pll_controller (
				.CLKREF_RETIMED(clkref_retimed), 
				.RST(RST), 
				.FCW_INT(FCW_INT), 
				.FCW_FRAC( {FCW_FRAC_WIDTH{1'b0}} ), 
				.DCO_OPEN_LOOP_EN(DCO_OPEN_LOOP_EN), 				
				.DCO_OPEN_LOOP_CTRL(dco_open_loop_cw),
				.DLF_ADJUST_EN(DLF_ADJUST_EN),
				.DLF_LOCK_KP(DLF_LOCK_KP), 
				.DLF_LOCK_KI(DLF_LOCK_KI), 
				.DLF_TRACK_KP(DLF_TRACK_KP), 
				.DLF_TRACK_KI(DLF_TRACK_KI), 
				.COUNT_IN(count_accum),
				.TDC_IN(tdc_out),
				.FINE_LOCK_ENABLE(FINE_LOCK_ENABLE),
				.FINE_LOCK_THRESHOLD(FINE_LOCK_THRESHOLD),
				.FINE_LOCK_COUNT(FINE_LOCK_COUNT),
				.CAPTURE_MUX_SEL(CAPTURE_MUX_SEL),
				.CLK_DITHER(clk_div4),
				.DITHER_EN(DITHER_EN),

				.SSC_EN(SSC_EN),
				.SSC_REF_COUNT(SSC_REF_COUNT),
				.SSC_STEP(SSC_STEP),
				.SSC_SHIFT(SSC_SHIFT),

				.DCO_CCW_OUT(DCO_CCW_OUT),
				.DCO_CCW_OUTN(dco_ccw_outn),
				.DCO_FCW_OUT(DCO_FCW_OUT),
				.DCO_FCW_OUTN(dco_fcw_outn),
				.FINE_LOCK_DETECT(FINE_LOCK_DETECT),
				.CAPTURE_MUX_OUT(CAPTURE_MUX_OUT)
		);



	tdc_counter	#(
			.TDC_MAX(TDC_MAX),
			.TDC_COUNT_ACCUM_WIDTH(REF_ACCUM_WIDTH-TDC_ROUND_WIDTH),
			.TDC_NUM_RETIME_CYCLES(TDC_NUM_RETIME_CYCLES),
			.TDC_NUM_RETIME_DELAYS(TDC_NUM_RETIME_DELAYS),
			.TDC_NUM_COUNTER_DIVIDERS(TDC_NUM_COUNTER_DIVIDERS))
		u_tdc_counter (
			.CLKREF_IN(CLKREF),
			.SAMPLED_PHASES_IN(SAMPLED_PHASES_IN),
			.DCO_OUTP(DCO_OUTP),
			.RST(RST),
			.CLKREF_RETIMED_OUT(clkref_retimed),
			.DCO_CLK_DIV4(clk_div4),
			.TDC_OUT(tdc_out),
			.COUNT_ACCUM_OUT(count_accum)
	);


endmodule


