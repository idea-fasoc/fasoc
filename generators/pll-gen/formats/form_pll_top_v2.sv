// pll_top
// Functions as an arbiter between pll_controller <=> tstdc_counter
// wraps pll_controller, tstdc_counter, ble_dco

//`define TDC_APR
//`define DCO_FC_HALF


@@ module @iN(
	// inputs
		CLK_REF,
		RST,
		EMBTDC_LUT,

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
		CS_PLL_OV, // v 0531
		cs_pll_user,
		CS_PLL_CTRL_OV,
		cs_pll_ctrl_user,

	// outputs
		cs_pll,
		cs_pll_ctrl, // ^ 053121
		ns_pll,
		DCO_FCW_MAX_LIMIT_HIT, 		// valid range of FCW
		FINE_LOCK_DETECT,	// OUTPUT: lock detect, goes high when error is within lock_thsh, also if goes high, PLL switches to slow mode.
		PLL_LOCKED, 
		CAPTURE_MUX_OUT,	// OUTPUT: The internal signal selected to view as an output.
		CLK_OUT,

	// dco
		OSC_EN,
		SCPA_CLK_EN, 
		CLK_OUT_EN, 
		DIV_SEL);

// Functions
	`ifndef BEH_SIM
		`include "FUNCTIONS.v"
	`endif
	parameter TIME_SCALE = 1e-12;

// DCO parameters
@@	parameter NSTG=@nM;
	parameter DCO_NUM_PH = NSTG;
@@	parameter NCC=@nC;
	//parameter NFC=16; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
@@	parameter NFC=@nF; // this is (N(one-hot) x N(thermal)) (3 x 112) because FSTEP is the one-hot value, and we want the same effective range 
	parameter DCO_CCW_MAX = NCC*NSTG;	//scale
	`ifdef DCO_FC_HALF
		parameter DCO_FCW_MAX = NFC*NSTG*2;	// *2 for *_half operation
	`else
		parameter DCO_FCW_MAX = NFC*NSTG*1;	// *2 for *_half operation
	`endif
	parameter DCO_FCW_MAX_H = NFC*NSTG*1;	//scale
// ANALOG CORE
@@		parameter DCO_CENTER_FREQ = @CF;	//scale
@@		parameter DCO_FBASE = @FB;	//scale
	parameter DCO_OFFSET = 0;
@@		parameter DCO_CSTEP = @CS;	// ble_test 
@@		parameter DCO_FSTEP = @FS;	// ble_test 

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
	parameter TDC_NUM_PHASE_LATCH = 2;
	parameter TDC_NUM_RETIME_CYCLES = 5;
	parameter TDC_NUM_RETIME_DELAYS = 2;
	parameter TDC_NUM_COUNTER_DIVIDERS = 3;
@@		localparam EMBTDC_WIDTH = @ew;
	localparam TDC_WIDTH = EMBTDC_WIDTH;

// Local Parameters
	localparam DCO_CCW_BIN_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_BIN_WIDTH = func_clog2(DCO_FCW_MAX);
	localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
	localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
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

	// user values
	input [DCO_NUM_PH*2-1:0][TDC_WIDTH-1:0] 	EMBTDC_LUT;  

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
	input		 	CS_PLL_OV; // v 053121
	input reg [2:0] 	cs_pll_user;
	input		 	CS_PLL_CTRL_OV;
	input reg [1:0] 	cs_pll_ctrl_user;
	input	[FCW_FRAC_WIDTH-1:0]			embtdc_offset_user; // v 060121
	input						EMBTDC_OFFSET_OV; // 

	// outputs
	output logic [1:0] 				cs_pll_ctrl;
	output reg [2:0]	ns_pll;
	output reg [2:0] 	cs_pll;
	output logic					DCO_FCW_MAX_LIMIT_HIT;
	output						FINE_LOCK_DETECT;	// OUTPUT: lock detect; goes high when error is within lock_thsh; also if goes high; PLL switches to slow mode. 
	output						PLL_LOCKED;	        // high when OPERATE state & FINE_LOCK_DETECT 
	output logic 	[CAPTURE_WIDTH-1 :0]		CAPTURE_MUX_OUT;
	output						CLK_OUT; // output clock 

	// dco
	input						OSC_EN;
   	input 						SCPA_CLK_EN;
   	input 						CLK_OUT_EN;
   	input [8:0] 					DIV_SEL;

	// logics
	logic [2:0] 					cs_pll_g;// ^
	logic						clkref_retimed; // main clock

	logic						freq_lock_rst;
	logic	[FCW_FRAC_WIDTH-1:0]			embtdc_offset;
	logic	[FCW_FRAC_WIDTH-1:0]			embtdc_offset_final;

	// pll_controller
	logic	[FCW_FRAC_WIDTH-1:0] 			pll_fcw_frac; // ble_test
	logic 	[TDC_WIDTH-1:0]				embtdc_out;
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
	logic						pll_ctrl_rst;
	logic	[FCW_FRAC_WIDTH-1:0]			ref_phase_ramp_frac;  // 053121 


	// tdc_counter
	logic 						CLKREF_IN;
	logic 						RST;	
	logic	[DCO_NUM_PH-1:0]			DCO_RAW_PH;
	logic	[DCO_NUM_PH*2*TDC_WIDTH-1:0] 			embtdc_lut_2d;
	// outputs
	logic  						CLKREF_RETIMED_OUT; 
	logic 	[TDC_WIDTH-1:0] 			EMBTDC_BIN_OUT;
	logic						dco_clk_div4;	
	logic 						retime_edge_sel;
	logic 						retime_lag;
	logic 	[TDC_WIDTH-1:0] 			embtdc_bin_tmp; //test

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
	  ns_pll = PLL_OPERATE; // calib=0 => need to be able to diagnose tstdc status

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
			freq_lock_rst <= 0;
			pll_ctrl_rst <= 1'b1;

		end else if (`PLL_IDLE_STATE) begin // PLL_INIT?
			// do nothing? below is place-holder	
			freq_lock_rst <= 0;
			pll_ctrl_rst <= 1'b1;

		end else if (`PLL_OPERATE_STATE) begin
			pll_ctrl_rst <= 1'b0;
			freq_lock_rst <= 1'b0;
		end
	end



//========================================================================================
//			 main function: combinational			
//========================================================================================
	bin2therm #(.NBIN(DCO_CCW_BIN_WIDTH),.NTHERM(DCO_CCW_MAX)) b2t_dco_ccw_ov (.binin(DCO_CCW_OV_VAL), .thermout(DCO_CCW_OV_VAL_therm));
	bin2therm #(.NBIN(DCO_FCW_BIN_WIDTH),.NTHERM(DCO_FCW_MAX)) b2t_dco_fcw_ov (.binin(DCO_FCW_OV_VAL), .thermout(DCO_FCW_OV_VAL_therm));

	genvar i;
	generate // 060221
		for (i=0; i<DCO_FCW_MAX/2; i=i+1) begin
			assign DCO_FCBW_OV_VAL_therm_p[i] = DCO_FCW_OV_VAL_therm[2*i+1]; // processed
			assign DCO_FCW_OV_VAL_therm_p[i] = ~DCO_FCW_OV_VAL_therm[2*i];
		end
	endgenerate

	// map the luts
	generate
		for (i=0; i<DCO_NUM_PH*2; i=i+1) begin
			assign embtdc_lut_2d[TDC_WIDTH*(i+1)-1:TDC_WIDTH*i] = EMBTDC_LUT[i];
		end
	endgenerate


//==========================================================================================
//				Signal gating
//==========================================================================================

assign pll_fcw_frac = (`PLL_OPERATE_STATE)? FCW_FRAC : 0;
assign pll_frac_phase_in = EMBTDC_BIN_OUT;
assign PLL_LOCKED = (`PLL_OPERATE_STATE)? FINE_LOCK_DETECT : 0;
assign FINE_LOCK_DETECT = fine_lock_detect; 
assign embtdc_offset_final = embtdc_offset_user; 

assign dco_fcw_g = (DCO_FCW_OV)? DCO_FCW_OV_VAL_therm_p : dco_fcw; // 060221 update 
assign dco_fcbw_g = (DCO_FCW_OV)? DCO_FCBW_OV_VAL_therm_p : dco_fcbw; // 060221 update 

//==========================================================================================
//				Define submodules	
//==========================================================================================

	pll_controller 
		`ifndef SYNorAPR
			#(
				.NSTG(NSTG),
				.NCC(NCC),	
				.NFC(NFC),
				.EMBTDC_WIDTH(EMBTDC_WIDTH),	
				.FCW_FRAC_WIDTH(FCW_FRAC_WIDTH),	
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

	assign CLKREF_IN = CLK_REF;
	

	tdc_counter
			#(.EMBTDC_WIDTH		(EMBTDC_WIDTH		))
	 u_tdc_counter(
			.CLKREF_IN		(CLK_REF		), 
			.DCO_RAW_PH		(DCO_RAW_PH		),
			.RST			(RST			),
			.CLKREF_RETIMED_OUT	(clkref_retimed		),
			.DCO_CLK_DIV4		(dco_clk_div4		), 
			.EMBTDC_BIN_OUT		(EMBTDC_BIN_OUT		),
			`ifndef TDC_APR
				.EMBTDC_LUT	(EMBTDC_LUT	),
			`else
				.EMBTDC_LUT	(embtdc_lut_2d		),
			`endif
			.retime_lag		(retime_lag		), // test
			.retime_edge_sel	(retime_edge_sel	), // test
			.embtdc_bin_tmp		(embtdc_bin_tmp		), // test
			.COUNT_ACCUM_OUT	(count_accum_out	));

@@	@dN
	`ifdef BEH_SIM 
		#(
			.NSTG			(NSTG			),
			.NCC 			(NCC			),
			.NFC 			(NFC			),
			.DCO_CENTER_FREQ	(DCO_CENTER_FREQ	),
			.DCO_FBASE		(DCO_FBASE		),	//scale
			.DCO_CSTEP		(DCO_CSTEP		),	// ble_test 
			.DCO_FSTEP		(DCO_FSTEP		))	// ble_test
	`endif
	u_dco	( 
			.PH_out		(DCO_RAW_PH	), 
			.CC		(dco_ccw	), 
			.FC		(dco_fcw_g	), // 060221 
			.FCB		(dco_fcbw_g	), // 060221 
			.osc_en		(OSC_EN	), 
			.CLK_OUT	(CLK_OUT	), 
//			.SCPA_CLK	(SCPA_OUT	), 
			.clk		(dco_clk	), 
			.dum_in		(dco_dum_in	), 
			.dum_out	(dco_dum_out	));

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
//
