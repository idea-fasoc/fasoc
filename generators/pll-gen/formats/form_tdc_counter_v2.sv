// two-step tdc decoder + dco clock counter

//`timescale 1ps/1ps



module tdc_counter(
	CLKREF_IN, 
	DCO_RAW_PH,
	RST,
	CLKREF_RETIMED_OUT,
	DCO_CLK_DIV4, 
	EMBTDC_BIN_OUT,
	EMBTDC_LUT,
	retime_lag, // test
	retime_edge_sel, // test
	embtdc_bin_tmp, // test
	COUNT_ACCUM_OUT);

	`ifndef BEH_SIM
		// Functions
		`include "FUNCTIONS.v"
	`endif

	// Parameters
	parameter NDECAP = 26; 
	// DFF char 
	parameter dff_su_time = 20e-12;

	parameter dff_delay = 60e-12;
	parameter fmux_delay = 17e-12; 
	parameter TIME_SCALE = 1e-12;

	// embtdc
	parameter TDC_COUNT_ACCUM_WIDTH = 15;	
	parameter TDC_NUM_PHASE_LATCH = 2;
	//parameter TDC_NUM_RETIME_CYCLES = 3;
	parameter TDC_NUM_RETIME_CYCLES = 5;
	parameter TDC_NUM_RETIME_DELAYS = 2;
	parameter TDC_NUM_COUNTER_DIVIDERS = 3;
	// dco
@@		parameter NSTG=@ns;
	parameter DCO_NUM_PH = NSTG;

	// Local Parameters
	parameter EMBTDC_WIDTH = 5;
		localparam TDC_WIDTH = EMBTDC_WIDTH;

	// Ports
		input 						CLKREF_IN;
		input 						RST;
		input	[DCO_NUM_PH-1:0]			DCO_RAW_PH;
		input	[DCO_NUM_PH*2-1:0][TDC_WIDTH-1:0]		EMBTDC_LUT;

		// outputs
		output  					CLKREF_RETIMED_OUT; 
		output logic 	[TDC_WIDTH-1:0] 		EMBTDC_BIN_OUT;
		output logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]	COUNT_ACCUM_OUT;
		output						DCO_CLK_DIV4;	
		output 						retime_edge_sel;
		output 						retime_lag;
		output 	[TDC_WIDTH-1:0] 			embtdc_bin_tmp; //test

	// Internal Signals
		logic						dco_outp;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_curr;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_prev;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_curr;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_prev;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_gray;
		logic 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_binary;
		logic 						dco_gray_accum_sel;
		logic						clkref_retimed;

		logic	[DCO_NUM_PH-1:0]			embtdc_raw_out;

		logic						CLKREF_IN_buf0;
		logic						CLKREF_IN_buf;
		logic						CLKREF_IN_buf_sync;

	// Variables 
		integer ii;

	
	`ifndef BEH_SIM	
		BUFH_X4N_A10P5PP84TR_C14 clkref_buf1 (.Y(CLKREF_IN_buf0), .A(CLKREF_IN)); // 050921 
		BUFH_X8N_A10P5PP84TR_C14 clkref_buf2 (.Y(CLKREF_IN_buf), .A(CLKREF_IN_buf0)); // 050921 
		BUFH_X2N_A10P5PP84TR_C14 clkref_buf_3 (.Y(CLKREF_IN_buf_sync),.A(CLKREF_IN_buf)); // 053121	
		BUFH_X2N_A10P5PP84TR_C14 clkref_buf_4 (.Y(CLKREF_IN_buf_sync),.A(CLKREF_IN_buf));
	`else
		assign CLKREF_IN_buf0 = CLKREF_IN;
		assign CLKREF_IN_buf = CLKREF_IN_buf0;
		assign CLKREF_IN_buf_sync = CLKREF_IN_buf;
	`endif

	// EMBTDC
	// Selection pins
	`ifndef BEH_SIM 
		generate 
			genvar i,j,k,f; 
			//Loop across first N-1 Stages
			for (i=0; i<DCO_NUM_PH ; i=i+1)
			begin:stg_emb
				DFFQ_X1N_A10P5PP84TR_C14 embtdc_dff (.Q(embtdc_raw_out[i]), .CK(CLKREF_IN_buf), .D(DCO_RAW_PH[i]));
	  			//XNOR2_X0P6N_A10P5PP84TR_C14 xnor_edge_sel ( .A(embtdc_out[i%DCO_NUM_PH]), .B(embtdc_out[(i+1)%DCO_NUM_PH]), .Y(edge_sel_tmp[i]) );
			end
		endgenerate
	`else
		always @(posedge CLKREF_IN_buf) begin
			embtdc_raw_out <= DCO_RAW_PH;
		end
	`endif


	tdc_encoder	#(
			.EMBTDC_WIDTH	(EMBTDC_WIDTH		),
			.DCO_NUM_PH	(DCO_NUM_PH		))
	 u_tdc_encoder(
		.DCO_OUTP		(dco_outp		), //-km
		.RST			(RST			),
		.EMBTDC_RAW_OUT		(embtdc_raw_out		),
		.EMBTDC_OUT		(embtdc_bin_tmp		), 
		.EMBTDC_LUT		(EMBTDC_LUT		),// LUT test 
		.RETIME_EDGE_SEL_OUT	(retime_edge_sel	),
		.RETIME_LAG_OUT		(retime_lag		));


	// Encode the sampled phases in binary
	// latch encoder on retimed edge
	always @(posedge clkref_retimed or posedge RST) begin
		if (RST) begin
			// tdc val
			EMBTDC_BIN_OUT <= 0;
			// count val
			clkref_accum_curr <= 0;
			clkref_accum_prev <= 0;
			dco_gray_accum_sel <= 0;
		end else begin
			`ifdef BEH_SIM
				#(dff_delay/TIME_SCALE);
			`endif
			// tdc val
			EMBTDC_BIN_OUT <= embtdc_bin_tmp;
			// count val
			clkref_accum_curr <= dco_accum_curr;
			clkref_accum_prev <= dco_accum_prev;
			dco_gray_accum_sel <= retime_lag;
		end	
	end


	always @(posedge dco_outp or posedge RST) begin
		if (RST) begin
			dco_accum_curr <= 0;
			dco_accum_prev <= 0;
		end
		else begin
			`ifdef BEH_SIM
				#(dff_delay/TIME_SCALE);
			`endif
			dco_accum_curr <= dco_accum_curr + 1;
			dco_accum_prev <= dco_accum_curr;
		end
	end	

	// combinational
	assign dco_outp = DCO_RAW_PH[0];
	assign DCO_CLK_DIV4 = dco_accum_curr[1];

	// convert back to binary
	assign	clkref_accum_binary = dco_gray_accum_sel ? clkref_accum_prev : clkref_accum_curr;

	// assign the output
	assign	COUNT_ACCUM_OUT = clkref_accum_binary;

	assign	CLKREF_RETIMED_OUT = clkref_retimed;

	// Retime CLKREF
 		// Instantiate the retime synchronizer
		clkref_sync #(
				.TDC_NUM_RETIME_CYCLES(TDC_NUM_RETIME_CYCLES),
				.TDC_NUM_RETIME_DELAYS(TDC_NUM_RETIME_DELAYS))
			u_clkref_sync(
				.CLKREF_IN(CLKREF_IN_buf_sync), // 053121
				.DCO_OUTP(dco_outp),
				.RETIME_EDGE_SEL_IN(retime_edge_sel),
				.CLKREF_RETIMED_OUT(clkref_retimed));



	//// decap cells
	//generate 
	//	genvar i,j,k,f; 
	//	//Loop across first N-1 Stages
	//	for (i=0; i<NDECAP ; i=i+1)
	//	begin:decap 
	//	       DCDC_CAP_UNIT unit ( );
	//	end
	//endgenerate


endmodule

module clkref_sync(
	CLKREF_IN,
	DCO_OUTP,
	RETIME_EDGE_SEL_IN,
	CLKREF_RETIMED_OUT);

	// Parameters
		parameter TDC_NUM_RETIME_CYCLES = 5;
		parameter TDC_NUM_RETIME_DELAYS = 2;

	// Ports
		input			CLKREF_IN;
		input			DCO_OUTP;		
		input			RETIME_EDGE_SEL_IN;

		output reg 		CLKREF_RETIMED_OUT;


	// Interconnect
		reg 	[TDC_NUM_RETIME_CYCLES-1:0]		retime_posedge_path;
		reg 	[TDC_NUM_RETIME_CYCLES-1:0]		retime_negedge_path;
		reg 						retime_negedge_start;
		wire 						retime_sel_edge_mux;


		reg 	[TDC_NUM_RETIME_DELAYS-1:0]		retime_delays;


	// Variables
		integer ii;


	// Synchronization of CLKREF with DCO_OUTP

 		// positive edge path 

			always @(posedge DCO_OUTP) begin
				// posedge path	
				retime_posedge_path[0] <= CLKREF_IN;
				for(ii=1;ii<TDC_NUM_RETIME_CYCLES;ii=ii+1) begin
					retime_posedge_path[ii] <= retime_posedge_path[ii-1];
 				end
				// negedge path
				retime_negedge_path[0] <= retime_negedge_start;
				for(ii=1;ii<TDC_NUM_RETIME_CYCLES;ii=ii+1) begin
					retime_negedge_path[ii] <= retime_negedge_path[ii-1];
				end
				// retime delay
				retime_delays[0] <= retime_sel_edge_mux;
				for(ii=1;ii<TDC_NUM_RETIME_DELAYS;ii=ii+1) begin
				
					retime_delays[ii] <= retime_delays[ii-1];
				end
				CLKREF_RETIMED_OUT <= retime_delays[TDC_NUM_RETIME_DELAYS-1];
			end	

		// negative edge path start

			always @(negedge DCO_OUTP) begin
				retime_negedge_start <= CLKREF_IN;
			end



		// retimne CLKREF
			
			// mux the negative and positve paths 
			assign retime_sel_edge_mux = RETIME_EDGE_SEL_IN ? 
				retime_posedge_path[TDC_NUM_RETIME_CYCLES-1] :
				retime_negedge_path[TDC_NUM_RETIME_CYCLES-1];


endmodule

// 100% combinational
module tdc_encoder (
	DCO_OUTP, //-km
	RST,
	EMBTDC_RAW_OUT,
	EMBTDC_OUT, 
	EMBTDC_LUT,
	RETIME_EDGE_SEL_OUT,
	RETIME_LAG_OUT);

	// Functions

	// Parameters
		parameter TDC_CRS_MAX = 10;
		parameter TDC_FINE_MAX = 10;
		parameter TDC_NUM_PHASE_LATCH = 2; 
		parameter EMBTDC_WIDTH = 5;

	// Local Paramters
		localparam DCO_NUM_PH = 5;
		localparam TDC_WIDTH = EMBTDC_WIDTH;

	// Ports
		input				DCO_OUTP;
		input				RST;
		input [DCO_NUM_PH-1:0]		EMBTDC_RAW_OUT;
		input reg [DCO_NUM_PH*2-1:0][TDC_WIDTH-1:0] EMBTDC_LUT;  
	
		output reg [TDC_WIDTH-1:0] 	EMBTDC_OUT;  
		output reg 			RETIME_EDGE_SEL_OUT;
		output reg 			RETIME_LAG_OUT;
	// Internal Signals
		reg [(TDC_NUM_PHASE_LATCH-1)*DCO_NUM_PH-1:0]	sampled_phases_latch;  //-km
		reg [DCO_NUM_PH-1:0]				sampled_phases_curr;  //-km
		reg [TDC_WIDTH-1:0]		embtdc_bin_tmp;
		reg 				retime_edge_sel;
		reg 				retime_lag;
		reg [TDC_WIDTH-1:0]		embtdc_idx;

	// Variables
		integer ii;
	// Behavioral

		// Convert sampled phases to binary
			//	    (CK2Q)	  (comb)
			// DCO_RAW_PH => embtdc_out => embtdc_idx should be less than retime delay(=Tdco*TDC_NUM_RETIME_CYCLES)! 
			always @* begin		
				case (EMBTDC_RAW_OUT)
@@						@Ns'b@er: begin	embtdc_idx = @ei; retime_edge_sel <= @re; retime_lag <= @rl; end	
					default: begin embtdc_idx = 0; retime_edge_sel <= 0; retime_lag <= 1; end
				endcase
			end	

		// assign output signals
		assign EMBTDC_OUT = EMBTDC_LUT[embtdc_idx];
		assign RETIME_EDGE_SEL_OUT = retime_edge_sel;
		assign RETIME_LAG_OUT = retime_lag;

endmodule 

//`ifndef BEH_SIM
//	module bin2therm (binin, thermout);
//		parameter NBIN = 4;
//		parameter NTHERM = 16;
//		input [NBIN-1:0] binin;
//		output [NTHERM-1:0] thermout;
//	
//		generate
//			genvar i;
//			for(i=0; i<=NTHERM-1; i=i+1) begin: thermloop
//				assign thermout[i] = (binin > i) ? 1: 0;
//			end
//		endgenerate
//	
//	endmodule
//`endif
