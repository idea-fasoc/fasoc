@@ module @iN(
	CLKREF,
	RST,
	OSC_EN,
	FCW_INT,
	DCO_OPEN_LOOP_EN,
	DCO_OPEN_LOOP_CC,
	DCO_OPEN_LOOP_FC,
	DLF_KP,
	DLF_KI,
	EDGE_SEL_ENABLE, 	//ff-km: enabling edge selection. [0] means chose PH_P_out[0]
	EDGE_SHIFT_MAX, 	//ff-km: maximum value of edge sel in binary: same value as TDC_MAX+1 
	EDGE_SEL_DEFAULT,		//ff-km: edge selection default value 
	EDGE_SEL_DEFAULT_BIN,		//ff-km
	//EDGE_SEL_CLK_OUT,		//ff-km: edge selection clock output	
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,
	CAPTURE_MUX_SEL_CONT,	//ff-km
	CAPTURE_MUX_SEL_TDC,	//ff-km
	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,
	FINE_LOCK_DETECT,
	CAPTURE_MUX_OUT_CONT,  	//ff-km
	CAPTURE_MUX_OUT_TDC,  	//ff-km
	CLKREF_RETIMED,
	DIV_SEL,
	BUF_SWITCH,
	//PHASES,
	CLK_OUT
	);

	// Functions
		`include "FUNCTIONS.v"

	// DCO design parameters - km
@@	parameter NSTG = @nM; 
@@	parameter NDRIV = @nD;
@@	parameter NFC = @nF;
@@	parameter NCC = @nC;
	parameter Nintrp = 2;

	//parameters
		parameter TDC_MAX = NSTG*Nintrp*2-1;	//-km	
		//parameter FCW_MAX = 65;
		parameter FCW_MAX = 65;
		parameter FCW_MIN = 10;
		parameter DCO_CCW_MAX = NSTG*NCC-1;	//scale
		parameter DCO_FCW_MAX = NSTG*NFC-1;	//scale
		parameter KP_WIDTH = 12;
		parameter KP_FRAC_WIDTH = 2;
		parameter KI_WIDTH = 12;
		parameter KI_FRAC_WIDTH = 6;

		parameter TDC_EXTRA_BITS = 1; 
		parameter ACCUM_EXTRA_BITS = 4;
		parameter FILTER_EXTRA_BITS = 4;
		
		parameter NUM_COARSE_LOCK_REGIONS = 5;
		parameter COARSE_LOCK_THSH_MAX = DCO_CCW_MAX/4;
		parameter COARSE_LOCK_COUNT_MAX = DCO_CCW_MAX;
		parameter FINE_LOCK_THSH_MAX = DCO_FCW_MAX/4;
		parameter FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;

		//ff-km:capture width
		//parameter CAPTURE_WIDTH_CONT = 37;
		parameter CAPTURE_WIDTH_CONT = 32; //max width = 32 
		parameter CAPTURE_WIDTH_TDC = 32;

		parameter SSC_COUNT_WIDTH = 12;
		parameter SSC_ACCUM_WIDTH = 16;
		parameter SSC_MOD_WIDTH = 5;
		parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

		// Local parameters
		localparam COARSE_LOCK_REGION_WIDTH = func_clog2(NUM_COARSE_LOCK_REGIONS);
		localparam COARSE_LOCK_THSH_WIDTH = func_clog2(COARSE_LOCK_THSH_MAX);
		localparam COARSE_LOCK_COUNT_WIDTH = func_clog2(COARSE_LOCK_COUNT_MAX);
		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
		localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
		localparam DCO_NUM_PHASES = TDC_MAX+1;
		
		localparam TDC_WIDTH = func_clog2(TDC_MAX);
		//inputs
		input 										CLKREF;
		input 										RST;
		input										OSC_EN;
		input 		[FCW_INT_WIDTH-1:0]				FCW_INT;
		input 										DCO_OPEN_LOOP_EN;
		input 		[DCO_CCW_WIDTH-1:0]				DCO_OPEN_LOOP_CC;
		input 		[DCO_FCW_WIDTH-1:0]				DCO_OPEN_LOOP_FC;
		input 		[KP_WIDTH-1:0]					DLF_KP;
		input 		[KI_WIDTH-1:0]					DLF_KI;
		input 										FINE_LOCK_ENABLE;
		input 		[FINE_LOCK_THSH_WIDTH-1:0]		FINE_LOCK_THRESHOLD;
		input 		[FINE_LOCK_COUNT_WIDTH-1:0]		FINE_LOCK_COUNT;
		//ff-km: capture sel
		input 	[3:0]								CAPTURE_MUX_SEL_CONT;
		input 	[2:0]								CAPTURE_MUX_SEL_TDC;

		input 										SSC_EN;
		input 		[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
		input 		[3:0]							SSC_STEP;
		input		[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

		input							EDGE_SEL_ENABLE; //ff-km
		input		[TDC_WIDTH-1:0]				EDGE_SHIFT_MAX; //ff-km
		input		[TDC_MAX:0]				EDGE_SEL_DEFAULT;	//ff-km
		input		[TDC_WIDTH-1:0]				EDGE_SEL_DEFAULT_BIN;	//ff-km
//		output 							EDGE_SEL_CLK_OUT;	//ff-km
		wire							EDGE_SEL_CLK_OUT;

		input		[6:0]					DIV_SEL;
		input		[3:0]					BUF_SWITCH;
		
		output 									FINE_LOCK_DETECT;

		output	[CAPTURE_WIDTH_CONT-1:0]					CAPTURE_MUX_OUT_CONT;
		output	[CAPTURE_WIDTH_TDC-1:0]					CAPTURE_MUX_OUT_TDC;

		output										CLKREF_RETIMED;
//		output reg	[DCO_NUM_PHASES/2-1:0]			PHASES;
		output 										CLK_OUT;


		wire 		[DCO_NUM_PHASES-1:0]			sampled_phases;
		wire 		[DCO_NUM_PHASES-1:0]			phases;
		wire		[(DCO_NUM_PHASES/2)-1:0]		PH_P_out;
		wire		[(DCO_NUM_PHASES/2)-1:0]		PH_N_out;
		//wire		[2**DCO_CCW_WIDTH-1:0]			CC_dec;
		wire		[DCO_CCW_MAX:0]			CC_dec;
		//wire		[2**DCO_FCW_WIDTH-1:0]			FC_dec;
		wire		[DCO_FCW_MAX:0]			FC_dec;
		wire		[DCO_CCW_WIDTH-1:0]				dco_ccw_out;
		wire		[DCO_FCW_WIDTH-1:0]				dco_fcw_out;

		wire		[TDC_MAX:0]				edge_sel_out; //ff-km
//		wire							PEDGE; //ff-km
//		wire							NEDGE; //ff-km
		
		wire 			dum_clk;
		wire 			dum_in;
		wire 			dum_out;

		wire 			dum_clk2;
		wire 			dum_in2;
		wire 			dum_out2;
		wire			[1:0] dum_buf_net;
		//wire			[2:0] dum_buf_net;
		//wire			[3:0] dum_buf_net;
			
		wire							clkref_buf1;
		wire							clkref_buf2;
		wire							clkout_buf1;
	
		PLL_CONTROLLER_TDC_COUNTER #(
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
				.CAPTURE_WIDTH_CONT(CAPTURE_WIDTH_CONT), //ff-km
				.CAPTURE_WIDTH_TDC(CAPTURE_WIDTH_TDC))  //ff-km
			pll_controller_tdc_counter (
				.SAMPLED_PHASES_IN(sampled_phases),
				.DCO_OUTP(clkout_buf1),
				.CLKREF(CLKREF),
				.RST(RST),
				.FCW_INT(FCW_INT),
				.DCO_OPEN_LOOP_EN(DCO_OPEN_LOOP_EN),
				.DCO_OPEN_LOOP_CC(DCO_OPEN_LOOP_CC),
				.DCO_OPEN_LOOP_FC(DCO_OPEN_LOOP_FC),
				.DLF_ADJUST_EN(1'b0),
				.DLF_SLOW_KP(DLF_KP),
				.DLF_SLOW_KI(DLF_KI),
				.DLF_FAST_KP(12'b0),
				.DLF_FAST_KI(12'b0),
				.DLF_SLEW_KP(12'b0),
				.DLF_SLEW_KI(12'b0),
				.EDGE_SEL_ENABLE(EDGE_SEL_ENABLE),  	//ff-km
				.EDGE_SHIFT_MAX(EDGE_SHIFT_MAX),		//ff-km	
				.EDGE_SEL_DEFAULT(EDGE_SEL_DEFAULT),		//ff-km
				.EDGE_SEL_DEFAULT_BIN(EDGE_SEL_DEFAULT_BIN),		//ff-km
				.EDGE_SEL_OUT(edge_sel_out),		//ff-km
				//.PEDGE(PEDGE),			//ff-km	
				//.NEDGE(NEDGE),			//ff-km	
				.FINE_LOCK_ENABLE(FINE_LOCK_ENABLE),
				.FINE_LOCK_THRESHOLD(FINE_LOCK_THRESHOLD),
				.FINE_LOCK_COUNT(FINE_LOCK_COUNT),
				.CAPTURE_MUX_SEL_CONT(CAPTURE_MUX_SEL_CONT),
				.CAPTURE_MUX_SEL_TDC(CAPTURE_MUX_SEL_TDC),
				.SSC_EN(SSC_EN),
				.SSC_REF_COUNT(SSC_REF_COUNT),
				.SSC_STEP(SSC_STEP),
				.SSC_SHIFT(SSC_SHIFT),
				.CLKREF_RETIMED(CLKREF_RETIMED),
				.DCO_CCW_OUT(dco_ccw_out),
				.DCO_FCW_OUT(dco_fcw_out),
				.FINE_LOCK_DETECT(FINE_LOCK_DETECT),
				.CAPTURE_MUX_OUT_CONT(CAPTURE_MUX_OUT_CONT),
				.CAPTURE_MUX_OUT_TDC(CAPTURE_MUX_OUT_TDC)
		);

		//Control Decoders
		bin2therm #(.NBIN(DCO_CCW_WIDTH),.NTHERM(DCO_CCW_MAX+1)) decCC(.binin(dco_ccw_out), .thermout(CC_dec));
		bin2therm #(.NBIN(DCO_FCW_WIDTH),.NTHERM(DCO_FCW_MAX+1)) decFC(.binin(dco_fcw_out), .thermout(FC_dec));
		//DCO
@@		@dN #(	.NSTG(NSTG),
				.NDRIV(NDRIV),
				.NFC(NFC),
				.NCC(NCC),
				.Nintrp(Nintrp))
 		dco(.PH_N_out(PH_N_out),.PH_P_out(PH_P_out), .CC(CC_dec), .FC(FC_dec), .osc_en(OSC_EN), .EDGE_SEL(edge_sel_out), .CLK_OUT(EDGE_SEL_CLK_OUT),.clk(dum_clk),.dum_in(dum_in),.dum_out(dum_out));

		//PHASE MAP
		//assign phases = {PH_P_out, PH_N_out}; //old
		//assign phases = {PH_N_out, PH_P_out}; //old2: ff-km: sequence changed for right functionality
		// sequence changed for correct propagating direction
		generate
			genvar ph;
			for (ph=0; ph<DCO_NUM_PHASES/2; ph=ph+1)
			begin: phase_map
				assign phases[ph]			=PH_N_out[DCO_NUM_PHASES/2-1-ph];	
				assign phases[ph+DCO_NUM_PHASES/2]	=PH_P_out[DCO_NUM_PHASES/2-1-ph];
			end
		endgenerate	

		//CLKREF Buffers
		BUFH_X0P8M_A9TR ref_buf(.Y(clkref_buf1),.A(CLKREF));	
		BUFH_X0P8M_A9TR ref_buf2(.Y(clkref_buf2),.A(clkref_buf1));	
		BUFH_X0P8M_A9TR ref_buf21(.Y(clkref_buf2),.A(clkref_buf1));	
		BUFH_X0P8M_A9TR ref_buf22(.Y(clkref_buf2),.A(clkref_buf1));	
		//DCO_OUTP Buffers : phases[0]=PH_N_out[15]
		BUFH_X0P8M_A9TR out_buf(.Y(clkout_buf1),.A(phases[0]));	
		BUFH_X0P8M_A9TR out_buf1(.Y(clkout_buf1),.A(phases[0]));	

		//output buffers
		outbuff_div I_outbuff_div (.CLK_IN(EDGE_SEL_CLK_OUT), .CLK_OUT(CLK_OUT), .div_sel(DIV_SEL),.buf_switch(BUF_SWITCH),.clk(dum_clk2),.dum_in(dum_in2),.dum_out(dum_out2),.RST(RST),.buf_net(dum_buf_net));

		//TDC
		generate
			genvar i;
			for (i=0; i<DCO_NUM_PHASES; i=i+1)
			begin: tdcstg
				//DFCNQD1BWP12T tdc_dff(.Q(sampled_phases[i]), .CP(CLKREF), .D(phases[i]), .CDN(~RST));
				DFFRPQ_X0P5M_A9TR tdc_dff(.Q(sampled_phases[i]), .CK(clkref_buf2), .D(phases[i]), .R(RST));
			end
		endgenerate

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
