// verilog

`ifndef __PLL_CONTROLLER_TDC_COUNTER__
`define __PLL_CONTROLLER_TDC_COUNTER__

`include "PLL_CONTROLLER.v"
`include "TDC_COUNTER.v"


`timescale 1ns/1ps

module PLL_CONTROLLER_TDC_COUNTER(
	SAMPLED_PHASES_IN,	// DCO phases sampledby reference clock
	DCO_OUTP,			// DCO positive output

	CLKREF,				// reference clk   
	RST,				// active high reset 

	FCW_INT,			// integer FCW to the PLL 

	DCO_OPEN_LOOP_EN,	// switch between open and close loop
	DCO_OPEN_LOOP_CC,	// open loop oscillator coarse control
	DCO_OPEN_LOOP_FC,	// open loop oscillator fine control

	DLF_ADJUST_EN,		// enable for loop filter fast and slow mode adjustment
	DLF_SLOW_KP,		// loop filter Kp for slow mode 
	DLF_SLOW_KI,		// loop filter Ki for slow mode
	DLF_FAST_KP,		// loop filter Kp for fast mode
	DLF_FAST_KI,		// loop filter Ki for fast mode 
	DLF_SLEW_KP,		// loop filter Kp for slew mode
	DLF_SLEW_KI,		// loop filter Ki for slew mode 

	EDGE_SEL_ENABLE, 	//ff-km: enabling edge selection. [0] means chose PH_P_out[0]
	EDGE_SHIFT_MAX, 	//ff-km: maximum value of edge sel in binary: same value as TDC_MAX+1 
	EDGE_SEL_DEFAULT,		//ff-km: edge selection default value 
	EDGE_SEL_DEFAULT_BIN,		//ff-km
	EDGE_SEL_OUT,		//ff-km: edge selection output one hot	
	//PEDGE,			//ff-km	
	//NEDGE,			//ff-km	
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,

	CAPTURE_MUX_SEL_CONT,	// Select among different internal signals to view for testing purposes(PLL_CONTROLLER).
	CAPTURE_MUX_SEL_TDC,	// Select among different internal signals to view for testing purposes(TDC_COUNTER).

	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,

	CLKREF_RETIMED,
	DCO_CCW_OUT,		// OUTPUT: coarse CW to the DCO   
	DCO_FCW_OUT,		// OUTPUT: fine CW to the DCO
	FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode. 
	CAPTURE_MUX_OUT_CONT,	// OUTPUT: The internal signal selected to view as an output(PLL_CONTROLLER). 
	CAPTURE_MUX_OUT_TDC);	// OUTPUT: The internal signal selected to view as an output(TDC_COUNTER). 



	// Functions
		`include "FUNCTIONS.v"


	//Parameters
	// DCO design parameters - km
	parameter NSTG = 8; 
	parameter NDRIV = 4;
	parameter NFC = 32;
	parameter NCC = 16;
		parameter Nintrp = 2;

		// CONTROLLER
		parameter TDC_MAX = NSTG*Nintrp*2-1;	//-km	
		parameter TDC_EXTRA_BITS = 1; // 
		parameter FCW_MAX = 55;
		parameter FCW_MIN = 10;
		parameter DCO_CCW_MAX = NSTG*NCC-1;	//scale
		parameter DCO_FCW_MAX = NSTG*NFC-1;	//scale
		parameter KP_WIDTH = 12;
		parameter KP_FRAC_WIDTH = 2;
		parameter KI_WIDTH = 12;
		parameter KI_FRAC_WIDTH = 6;
		parameter ACCUM_EXTRA_BITS = 1;
		parameter FILTER_EXTRA_BITS = 1;
		
		parameter NUM_COARSE_LOCK_REGIONS = 2;
		parameter COARSE_LOCK_THSH_MAX = DCO_CCW_MAX/4;
		parameter COARSE_LOCK_COUNT_MAX = DCO_CCW_MAX;
		parameter FINE_LOCK_THSH_MAX = DCO_FCW_MAX/4;
		parameter FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;

		parameter CAPTURE_WIDTH_CONT = 37;
		parameter CAPTURE_WIDTH_TDC = 32;

		parameter SSC_COUNT_WIDTH = 12;
		parameter SSC_ACCUM_WIDTH = 16;
		parameter SSC_MOD_WIDTH = 5;
		parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

		// TDC_COUNTER
		parameter TDC_NUM_PHASE_LATCH = 2;
		parameter TDC_NUM_RETIME_CYCLES = 4;
		parameter TDC_NUM_RETIME_DELAYS = 2;
		parameter TDC_NUM_COUNTER_DIVIDERS = 3;


	// Local Parameters

		// DCO parameter
		localparam DCO_NUM_PHASES = TDC_MAX+1;

		// Controller TDC parameters
		localparam TDC_WIDTH = func_clog2(TDC_MAX);
		localparam TDC_BIT_MAX = 2**TDC_WIDTH;// only used in next line
		localparam TDC_SCALE = (TDC_BIT_MAX << TDC_EXTRA_BITS)/(TDC_MAX+1);
		localparam TDC_ROUND_WIDTH = TDC_WIDTH + TDC_EXTRA_BITS;

		// Controller control word sizes
		localparam FCW_FRAC_WIDTH = TDC_WIDTH;
		localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
		localparam FCW_WIDTH = FCW_INT_WIDTH + TDC_ROUND_WIDTH;

	
		// Controller DCO control word sizes
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);

		// Controller reference accumulator sizes
		localparam REF_ACCUM_WIDTH = FCW_WIDTH + ACCUM_EXTRA_BITS;

		// Lock detection sizes
		localparam COARSE_LOCK_REGION_WIDTH = func_clog2(NUM_COARSE_LOCK_REGIONS);
		localparam COARSE_LOCK_THSH_WIDTH = func_clog2(COARSE_LOCK_THSH_MAX);
		localparam COARSE_LOCK_COUNT_WIDTH = func_clog2(COARSE_LOCK_COUNT_MAX);

		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);

	

	// Ports
		input 	[DCO_NUM_PHASES-1:0]				SAMPLED_PHASES_IN;
		input										DCO_OUTP;
		input 										CLKREF;
		input 										RST;
		input	[FCW_INT_WIDTH-1:0] 				FCW_INT;
//		input	[FCW_FRAC_WIDTH-1:0] 				FCW_FRAC;

		input 										DCO_OPEN_LOOP_EN;
		input 	[DCO_CCW_WIDTH-1:0]					DCO_OPEN_LOOP_CC;
		input 	[DCO_FCW_WIDTH-1:0] 				DCO_OPEN_LOOP_FC;

		input 										DLF_ADJUST_EN;
		input 	[KP_WIDTH-1:0] 						DLF_SLOW_KP;
		input 	[KI_WIDTH-1:0] 						DLF_SLOW_KI;
		input 	[KP_WIDTH-1:0] 						DLF_FAST_KP;
		input 	[KI_WIDTH-1:0] 						DLF_FAST_KI;
		input 	[KP_WIDTH-1:0] 						DLF_SLEW_KP;
		input 	[KI_WIDTH-1:0] 						DLF_SLEW_KI;

		//input 						COARSE_LOCK_ENABLE;
		//input 	[COARSE_LOCK_REGION_WIDTH-1:0] 		COARSE_LOCK_REGION_SEL;
		//input 	[COARSE_LOCK_THSH_WIDTH-1:0] 		COARSE_LOCK_THRESHOLD;
		//input 	[COARSE_LOCK_COUNT_WIDTH-1:0] 		COARSE_LOCK_COUNT;

		input 										FINE_LOCK_ENABLE;
		input 	[FINE_LOCK_THSH_WIDTH-1:0] 			FINE_LOCK_THRESHOLD;
		input 	[FINE_LOCK_COUNT_WIDTH-1:0] 		FINE_LOCK_COUNT;

		input 	[3:0]								CAPTURE_MUX_SEL_CONT;
		input 	[2:0]								CAPTURE_MUX_SEL_TDC;

		input 										SSC_EN;
		input 	[SSC_COUNT_WIDTH-1:0]				SSC_REF_COUNT;
		input 	[3:0]								SSC_STEP;
		input	[SSC_SHIFT_WIDTH-1:0]				SSC_SHIFT;

		input							EDGE_SEL_ENABLE; //ff-km
		input		[TDC_WIDTH-1:0]				EDGE_SHIFT_MAX; //ff-km
		input		[TDC_MAX:0]				EDGE_SEL_DEFAULT;	//ff-km
		input		[TDC_WIDTH-1:0]				EDGE_SEL_DEFAULT_BIN;	//ff-km
		output reg	[TDC_MAX:0]				EDGE_SEL_OUT;	//ff-km
//		output							PEDGE;    	//ff-km
//		output							NEDGE;    	//ff-km

		output										CLKREF_RETIMED;
		output	[DCO_CCW_WIDTH-1:0]					DCO_CCW_OUT;
		output	[DCO_FCW_WIDTH-1:0]					DCO_FCW_OUT;

		output 										FINE_LOCK_DETECT;
		output	[CAPTURE_WIDTH_CONT-1:0]					CAPTURE_MUX_OUT_CONT;
		output	[CAPTURE_WIDTH_TDC-1:0]					CAPTURE_MUX_OUT_TDC;


	// Internal Signals
		wire										clkref_retimed;
		wire 	[DCO_FCW_WIDTH + 
				 	DCO_CCW_WIDTH-1:0]				dco_open_loop_cw;
		wire 	[TDC_WIDTH-1:0] 					tdc_out;
		wire 	[REF_ACCUM_WIDTH-
				 	TDC_ROUND_WIDTH-1:0] 			count_accum;
	
	
	// Concatinate the open loop control word
		assign dco_open_loop_cw = {DCO_OPEN_LOOP_CC, DCO_OPEN_LOOP_FC}; 
		assign CLKREF_RETIMED = clkref_retimed;


	// Structural
		PLL_CONTROLLER #(
				.TDC_MAX(TDC_MAX),
				.TDC_EXTRA_BITS(TDC_EXTRA_BITS),
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
				.NUM_COARSE_LOCK_REGIONS(NUM_COARSE_LOCK_REGIONS),
				.COARSE_LOCK_THSH_MAX(COARSE_LOCK_THSH_MAX),
				.COARSE_LOCK_COUNT_MAX(COARSE_LOCK_COUNT_MAX),
				.FINE_LOCK_THSH_MAX(FINE_LOCK_THSH_MAX),
				.FINE_LOCK_COUNT_MAX(FINE_LOCK_COUNT_MAX),
				.SSC_COUNT_WIDTH(SSC_COUNT_WIDTH),
				.SSC_ACCUM_WIDTH(SSC_ACCUM_WIDTH),
				.SSC_MOD_WIDTH(SSC_MOD_WIDTH),
				.SSC_SHIFT_WIDTH(SSC_SHIFT_WIDTH),
				.CAPTURE_WIDTH(CAPTURE_WIDTH_CONT))
			pll_controller (
				.CLKREF_RETIMED(clkref_retimed), 
				.RST(RST), 
				.FCW_INT(FCW_INT), 
				.FCW_FRAC( {FCW_FRAC_WIDTH{1'b0}} ), 
				.DCO_OPEN_LOOP_EN(DCO_OPEN_LOOP_EN), 				
				.DCO_OPEN_LOOP_CTRL(dco_open_loop_cw),
				.DLF_ADJUST_EN(DLF_ADJUST_EN),
				.DLF_SLOW_KP(DLF_SLOW_KP), 
				.DLF_SLOW_KI(DLF_SLOW_KI), 
				.DLF_FAST_KP(DLF_FAST_KP), 
				.DLF_FAST_KI(DLF_FAST_KI), 
				.DLF_SLEW_KP(DLF_SLEW_KP), 
				.DLF_SLEW_KI(DLF_SLEW_KI), 
				.COUNT_IN(count_accum),
				.TDC_IN(tdc_out),
//				.COARSE_LOCK_ENABLE(COARSE_LOCK_ENABLE),
//				.COARSE_LOCK_REGION_SEL(COARSE_LOCK_REGION_SEL),
//				.COARSE_LOCK_THRESHOLD(COARSE_LOCK_THRESHOLD),
//				.COARSE_LOCK_COUNT(COARSE_LOCK_COUNT),
				.FINE_LOCK_ENABLE(FINE_LOCK_ENABLE),
				.FINE_LOCK_THRESHOLD(FINE_LOCK_THRESHOLD),
				.FINE_LOCK_COUNT(FINE_LOCK_COUNT),
				.CAPTURE_MUX_SEL(CAPTURE_MUX_SEL_CONT),
				.SSC_EN(SSC_EN),
				.SSC_REF_COUNT(SSC_REF_COUNT),
				.SSC_STEP(SSC_STEP),
				.SSC_SHIFT(SSC_SHIFT),
				.DCO_CCW_OUT(DCO_CCW_OUT),
				.DCO_FCW_OUT(DCO_FCW_OUT),
				.FINE_LOCK_DETECT(FINE_LOCK_DETECT),
				.CAPTURE_MUX_OUT(CAPTURE_MUX_OUT_CONT)
		);



	TDC_COUNTER	#(
			.TDC_MAX(TDC_MAX),
			.TDC_COUNT_ACCUM_WIDTH(REF_ACCUM_WIDTH-TDC_ROUND_WIDTH),
			.TDC_NUM_PHASE_LATCH(TDC_NUM_PHASE_LATCH),
			.TDC_NUM_RETIME_CYCLES(TDC_NUM_RETIME_CYCLES),
			.TDC_NUM_RETIME_DELAYS(TDC_NUM_RETIME_DELAYS),
			.TDC_NUM_COUNTER_DIVIDERS(TDC_NUM_COUNTER_DIVIDERS),
			.CAPTURE_WIDTH(CAPTURE_WIDTH_TDC))
		tdc_counter (
			.CLKREF_IN(CLKREF),
			.SAMPLED_PHASES_IN(SAMPLED_PHASES_IN),
			.DCO_OUTP(DCO_OUTP),
			.RST(RST),
			.EDGE_SEL_ENABLE(EDGE_SEL_ENABLE),  	//ff-km
			.EDGE_SHIFT_MAX(EDGE_SHIFT_MAX),		//ff-km	
			.EDGE_SEL_DEFAULT(EDGE_SEL_DEFAULT),		//ff-km
			.EDGE_SEL_DEFAULT_BIN(EDGE_SEL_DEFAULT_BIN),		//ff-km
			.EDGE_SEL_OUT(EDGE_SEL_OUT),		//ff-km
			//.PEDGE(PEDGE),				//ff-km
			//.NEDGE(NEDGE),				//ff-km
			.CAPTURE_MUX_SEL(CAPTURE_MUX_SEL_TDC),	//ff-km
			.CAPTURE_MUX_OUT(CAPTURE_MUX_OUT_TDC),	//ff-km
			.CLKREF_RETIMED_OUT(clkref_retimed),
			.TDC_OUT(tdc_out),
			.COUNT_ACCUM_OUT(count_accum)
	);


endmodule


`endif

