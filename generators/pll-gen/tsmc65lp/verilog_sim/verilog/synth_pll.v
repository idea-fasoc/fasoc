module synth_pll(
	CLKREF,
	RST,
	OSC_EN,
	FCW_INT,
	DCO_OPEN_LOOP_EN,
	DCO_OPEN_LOOP_CC,
	DCO_OPEN_LOOP_FC,
	DLF_KP,
	DLF_KI,
	FINE_LOCK_ENABLE,
	FINE_LOCK_THRESHOLD,
	FINE_LOCK_COUNT,
	CAPTURE_MUX_SEL,
	SSC_EN,
	SSC_REF_COUNT,
	SSC_STEP,
	SSC_SHIFT,
	FINE_LOCK_DETECT,
	CAPTURE_MUX_OUT,
	CLKREF_RETIMED,
	PHASES,
	CLK_OUT
	);

	// Functions
		`include "FUNCTIONS.v"

	// DCO design parameters - km
	parameter NSTG = 18; 
	parameter NDRIV = 10;
	parameter NFC = 30;
	parameter NCC = 10;
		parameter Nintrp = 2;

	//parameters
		parameter TDC_MAX = NSTG*Nintrp*2-1;	//-km	
		parameter FCW_MAX = 55;
		parameter FCW_MIN = 10;
		parameter DCO_CCW_MAX = NSTG*NCC-1;	//scale
		parameter DCO_FCW_MAX = NSTG*NFC-1;	//scale
		parameter KP_WIDTH = 12;
		parameter KP_FRAC_WIDTH = 2;
		parameter KI_WIDTH = 12;
		parameter KI_FRAC_WIDTH = 6;

		parameter TDC_EXTRA_BITS = 1; 
		parameter ACCUM_EXTRA_BITS = 1;
		parameter FILTER_EXTRA_BITS = 1;
		
		parameter NUM_COARSE_LOCK_REGIONS = 5;
		parameter COARSE_LOCK_THSH_MAX = DCO_CCW_MAX/4;
		parameter COARSE_LOCK_COUNT_MAX = DCO_CCW_MAX;
		parameter FINE_LOCK_THSH_MAX = DCO_FCW_MAX/4;
		parameter FINE_LOCK_COUNT_MAX = DCO_FCW_MAX;

		parameter CAPTURE_WIDTH = 25;

		parameter SSC_COUNT_WIDTH = 12;
		parameter SSC_ACCUM_WIDTH = 16;
		parameter SSC_MOD_WIDTH = 5;
		parameter SSC_SHIFT_WIDTH = func_clog2(SSC_ACCUM_WIDTH-1);

		// Local parameters
		localparam FINE_LOCK_THSH_WIDTH = func_clog2(FINE_LOCK_THSH_MAX);
		localparam FINE_LOCK_COUNT_WIDTH = func_clog2(FINE_LOCK_COUNT_MAX);
		localparam DCO_CCW_WIDTH = func_clog2(DCO_CCW_MAX);
		localparam DCO_FCW_WIDTH = func_clog2(DCO_FCW_MAX);
		localparam FCW_INT_WIDTH = func_clog2(FCW_MAX);
		localparam DCO_NUM_PHASES = TDC_MAX+1;
		
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
		input 		[3:0]							CAPTURE_MUX_SEL;
		input 										SSC_EN;
		input 		[SSC_COUNT_WIDTH-1:0]			SSC_REF_COUNT;
		input 		[3:0]							SSC_STEP;
		input		[SSC_SHIFT_WIDTH-1:0]			SSC_SHIFT;

		output 										FINE_LOCK_DETECT;
		output 		[CAPTURE_WIDTH-1:0]				CAPTURE_MUX_OUT;
		output										CLKREF_RETIMED;
		output reg	[DCO_NUM_PHASES/2-1:0]			PHASES;
		output 										CLK_OUT;


		wire 		[DCO_NUM_PHASES-1:0]			sampled_phases;
		wire 		[DCO_NUM_PHASES-1:0]			phases;
		wire		[(DCO_NUM_PHASES/2)-1:0]		PH_P_out;
		wire		[(DCO_NUM_PHASES/2)-1:0]		PH_N_out;
		//wire		[2**DCO_CCW_WIDTH-1:0]			CC_dec;
		wire		[DCO_CCW_MAX-1:0]			CC_dec;
		//wire		[2**DCO_FCW_WIDTH-1:0]			FC_dec;
		wire		[DCO_FCW_MAX-1:0]			FC_dec;
		wire		[DCO_CCW_WIDTH-1:0]				dco_ccw_out;
		wire		[DCO_FCW_WIDTH-1:0]				dco_fcw_out;


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
				.CAPTURE_WIDTH(CAPTURE_WIDTH))
			pll_controller_tdc_counter (
				.SAMPLED_PHASES_IN(sampled_phases),
				.DCO_OUTP(phases[0]),
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
				.COARSE_LOCK_ENABLE(1'b0),
				.COARSE_LOCK_REGION_SEL(3'b0),
				.COARSE_LOCK_THRESHOLD(5'b0),
				.COARSE_LOCK_COUNT(7'b0),
				.FINE_LOCK_ENABLE(FINE_LOCK_ENABLE),
				.FINE_LOCK_THRESHOLD(FINE_LOCK_THRESHOLD),
				.FINE_LOCK_COUNT(FINE_LOCK_COUNT),
				.CAPTURE_MUX_SEL(CAPTURE_MUX_SEL),
				.SSC_EN(SSC_EN),
				.SSC_REF_COUNT(SSC_REF_COUNT),
				.SSC_STEP(SSC_STEP),
				.SSC_SHIFT(SSC_SHIFT),
				.CLKREF_RETIMED(CLKREF_RETIMED),
				.DCO_CCW_OUT(dco_ccw_out),
				.DCO_FCW_OUT(dco_fcw_out),
				.FINE_LOCK_DETECT(FINE_LOCK_DETECT),
				.CAPTURE_MUX_OUT(CAPTURE_MUX_OUT)
		);

		//Control Decoders
		bin2therm #(.NBIN(DCO_CCW_WIDTH)) decCC(.binin(dco_ccw_out), .thermout(CC_dec));
		bin2therm #(.NBIN(DCO_FCW_WIDTH)) decFC(.binin(dco_fcw_out), .thermout(FC_dec));
		//DCO
		synth_dco #(	.NSTG(NSTG),
				.NDRIV(NDRIV),
				.NFC(NFC),
				.NCC(NCC),
				.Nintrp(Nintrp))
 		dco(.PH_N_out(PH_N_out),.PH_P_out(PH_P_out), .CC(CC_dec), .FC(FC_dec), .osc_en(OSC_EN));

		assign phases = {PH_P_out, PH_N_out};
		assign CLK_OUT = phases[0];

		//Get uninterpolate phases for CDR
		integer j;
		always @* begin
			for (j = 0; j < DCO_NUM_PHASES/2; j = j + 1) begin
				PHASES[j] <= phases[2*j];
			end
		end
		//assign PHASES = phases;

		//TDC
		generate
			genvar i;
			for (i=0; i<DCO_NUM_PHASES; i=i+1)
			begin: tdcstg
				//DFCNQD1BWP12T tdc_dff(.Q(sampled_phases[i]), .CP(CLKREF), .D(phases[i]), .CDN(~RST));
				DFFRPQ_X0P5M_A9TR tdc_dff(.Q(sampled_phases[i]), .CK(CLKREF), .D(phases[i]), .R(~RST));
			end
		endgenerate

endmodule

module bin2therm (binin, thermout);
	parameter NBIN = 4;
	parameter NTHERM = (1<<NBIN);
	input [NBIN-1:0] binin;
	output [NTHERM-1:0] thermout;

	generate
		genvar i;
		for(i=0; i<=NTHERM-1; i=i+1) begin: thermloop
			assign thermout[i] = (binin > i) ? 1: 0;
		end
	endgenerate

endmodule
