// two-step tdc decoder + dco clock counter
`ifndef __TDC_COUNTER__
`define __TDC_COUNTER__


//`timescale 1ps/1ps


module tstdc_counter(
	CLKREF_IN, 
	SAMPLED_PH_CRS_IN, // from embedded TDC 
	SAMPLED_PH_FINE_IN, // from dltdc 
	DCO_OUTP,
	RST, 
	CLKREF_RETIMED_OUT,
	DCO_CLK_DIV4, 
	TDC_OUT,
	DLTDC_EDGE_SEL_OUT,
	DLTDC_NP_EDGE, 
	COUNT_ACCUM_OUT);

	// Functions

	// Parameters
		parameter TDC_MAX = 18;	
		parameter TDC_COUNT_ACCUM_WIDTH = 12;	
		parameter TDC_NUM_PHASE_LATCH = 2;
		//parameter TDC_NUM_RETIME_CYCLES = 3;
		parameter TDC_NUM_RETIME_CYCLES = 5;
		parameter TDC_NUM_RETIME_DELAYS = 2;
		parameter TDC_NUM_COUNTER_DIVIDERS = 3;
		parameter DLTDC_NUM_PH = 10;

	// Local Parameters
		//localparam EMBTDC_WIDTH = func_clog2(TDC_MAX);
		localparam EMBTDC_WIDTH = 5;
		localparam DCO_NUM_PH = (TDC_MAX/2+1)/2; // 5 (nstage) 
		//localparam DLTDC_WIDTH = func_clog2(TDC_FINE_MAX);
		localparam DLTDC_WIDTH = 5;
		localparam TDC_WIDTH = EMBTDC_WIDTH + DLTDC_WIDTH;

	// Ports
		input 						CLKREF_IN;
		input 		[DCO_NUM_PH-1:0] 		SAMPLED_PH_CRS_IN;	
		input 		[DLTDC_NUM_PH-1:0] 		SAMPLED_PH_FINE_IN;	
		input 						DCO_OUTP;
		input						RST;

		output reg 					CLKREF_RETIMED_OUT; 
		output reg 	[TDC_WIDTH-1:0] 		TDC_OUT;
		output reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]	COUNT_ACCUM_OUT;
		output						DCO_CLK_DIV4;	
		output reg	[DCO_NUM_PH-1:0]		DLTDC_EDGE_SEL_OUT; // one-hot
		output reg					DLTDC_NP_EDGE; // neg or posedge of DCO phase
	// Internal Signals
		wire 	[TDC_WIDTH-1:0] 			tdc_out_temp;

		reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_curr;
		reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_prev;
		reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_curr;
		reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_prev;
		reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_gray;
		reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_binary;
		reg 						dco_gray_accum_sel;

		wire						clkref_retimed;
		wire 						retime_edge_sel;
		wire 						retime_lag;

	// Variables 
		integer ii;


	// Encode the sampled phases in binary
		// Instantiate TDC enocder
		tstdc_encoder #(
				.TDC_MAX(TDC_MAX),
				.EMBTDC_WIDTH(EMBTDC_WIDTH),
				.DLTDC_WIDTH(DLTDC_WIDTH),
				.TDC_NUM_PHASE_LATCH(TDC_NUM_PHASE_LATCH))
			u_tdc_encoder(
				.CLKREF_IN(CLKREF_IN),
				.DCO_OUTP(DCO_OUTP),
				.RST(RST),
				.SAMPLED_PH_CRS_IN(SAMPLED_PH_CRS_IN), 
				.SAMPLED_PH_FINE_IN(SAMPLED_PH_FINE_IN), 
				.TDC_OUT(tdc_out_temp), 
				.RETIME_EDGE_SEL_OUT(retime_edge_sel), 
				.DLTDC_EDGE_SEL_OUT(DLTDC_EDGE_SEL_OUT),
				.DLTDC_NP_EDGE(DLTDC_NP_EDGE), 
				.RETIME_LAG_OUT(retime_lag)
		);

	// latch encoder on retimed edge
	always @(posedge clkref_retimed) begin
		TDC_OUT <= tdc_out_temp; 	
	end

	assign DCO_CLK_DIV4 = dco_accum_curr[1];
		always @(posedge DCO_OUTP or posedge RST) begin
			if (RST) begin
				dco_accum_curr <= 0;
				dco_accum_prev <= 0;
			end
			else begin
				dco_accum_curr <= dco_accum_curr + 1;
				dco_accum_prev <= dco_accum_curr;
			end
		end	

		// latch the counter on the retimed edge
			// get the gray code
			always @(posedge clkref_retimed) begin

				clkref_accum_curr <= dco_accum_curr;
				clkref_accum_prev <= dco_accum_prev;

				dco_gray_accum_sel <= retime_lag;
			end

			// convert back to binary
			always @* begin
				clkref_accum_binary = dco_gray_accum_sel ? clkref_accum_prev : clkref_accum_curr;
			end

			// assign the output
			always @* begin
				COUNT_ACCUM_OUT = clkref_accum_binary;
			end

	// Retime CLKREF
 		// Instantiate the retime synchronizer
		clkref_sync #(
				.TDC_NUM_RETIME_CYCLES(TDC_NUM_RETIME_CYCLES),
				.TDC_NUM_RETIME_DELAYS(TDC_NUM_RETIME_DELAYS))
			clkref_sync(
				.CLKREF_IN(CLKREF_IN),
				.DCO_OUTP(DCO_OUTP),
				.RETIME_EDGE_SEL_IN(retime_edge_sel),
				.CLKREF_RETIMED_OUT(clkref_retimed)
		);

		always @* begin
			CLKREF_RETIMED_OUT = clkref_retimed;
		end

endmodule

// new TDC_ENCODER: latch SAMPLED_PHASES_IN with DCO_OUTP
// assuming SAMPLED_PHASES_IN is sampled by CLKREF beforehand
// number of latchs should be less that retime cycle
module tstdc_encoder (
	CLKREF_IN,
	DCO_OUTP, //-km
	RST,
	SAMPLED_PH_CRS_IN, 
	SAMPLED_PH_FINE_IN, 
	TDC_OUT, 
	RETIME_EDGE_SEL_OUT,
	DLTDC_EDGE_SEL_OUT,
	DLTDC_NP_EDGE, 
	RETIME_LAG_OUT);

	// Functions

	// Parameters
		parameter TDC_CRS_MAX = 10;
		parameter TDC_FINE_MAX = 10;
		parameter TDC_MAX = TDC_CRS_MAX*TDC_FINE_MAX;
		parameter TDC_NUM_PHASE_LATCH = 2; 
		parameter DLTDC_NUM_PH = 10;
		parameter EMBTDC_WIDTH = 5;
		parameter DLTDC_WIDTH = 5;

	// Local Paramters
		localparam DCO_NUM_PH = (TDC_MAX/2+1)/2;
	//	localparam EMBTDC_WIDTH = func_clog2(TDC_CRS_MAX);
	//	localparam DLTDC_WIDTH = func_clog2(TDC_FINE_MAX);
		localparam TDC_WIDTH = EMBTDC_WIDTH + DLTDC_WIDTH;

	// Ports
		input				CLKREF_IN;
		input				DCO_OUTP;
		input				RST;
		input 	[DCO_NUM_PH-1:0] 	SAMPLED_PH_CRS_IN;  
		input 	[DLTDC_NUM_PH-1:0] 	SAMPLED_PH_FINE_IN;  
	
		output reg [EMBTDC_WIDTH+DLTDC_WIDTH-1:0] 	TDC_OUT;  
		output reg 			RETIME_EDGE_SEL_OUT;
		output reg [DCO_NUM_PH-1:0]	DLTDC_EDGE_SEL_OUT; // one-hot
		output reg 			RETIME_LAG_OUT;
		output reg			DLTDC_NP_EDGE; // neg or posedge of DCO phase
	// Internal Signals
		reg [(TDC_NUM_PHASE_LATCH-1)*DCO_NUM_PH-1:0]	sampled_phases_latch;  //-km
		reg [DCO_NUM_PH-1:0]				sampled_phases_curr;  //-km
		reg [EMBTDC_WIDTH-1:0]		embtdc_bin_tmp;
		reg 				retime_edge_sel;
		reg 				retime_lag;
		reg [DCO_NUM_PH-1:0]		dltdc_edge_sel_tmp; // one-hot
		reg				dltdc_np_edge_tmp; // neg or posedge of DCO phase
		reg [DLTDC_WIDTH-1:0]		dltdc_bin_tmp;

	// Variables
		integer ii;
	// Behavioral
		// latch the sampled phases through multiple DCO_OUTP latches:
		// this code works for only TDC_NUM_PHASE_LATCH >= 2
			//always @(posedge DCO_OUTP) begin	
			//	sampled_phases_latch[DCO_NUM_PH-1:0] <= SAMPLED_PH_CRS_IN;
			//	for(ii=1;ii<TDC_NUM_PHASE_LATCH-1;ii=ii+1) begin
			//		sampled_phases_latch[DCO_NUM_PH*(ii+1)-1 -:DCO_NUM_PH] <= sampled_phases_latch[DCO_NUM_PH*ii-1 -:DCO_NUM_PH];
 			//	end
			//	sampled_phases_curr=sampled_phases_latch[(TDC_NUM_PHASE_LATCH-1)*DCO_NUM_PH-1 -:DCO_NUM_PH];
			//end	
			always @(posedge DCO_OUTP) begin	
				sampled_phases_curr <= SAMPLED_PH_CRS_IN;
			end
		// Convert sampled phases to binary
			always @* begin 
				// coarse: single ended decoding
				case(sampled_phases_curr)
					// second version: linear approximated
					5'b00000: begin 	embtdc_bin_tmp <= 0; dltdc_edge_sel_tmp <= 5'b10000; dltdc_np_edge_tmp <= 0; end 
					5'b00001: begin 	embtdc_bin_tmp <= 3; dltdc_edge_sel_tmp <= 5'b00001; dltdc_np_edge_tmp <= 1; end    // -1 will be added in the pll_controller for mid-rise 
					5'b00011: begin 	embtdc_bin_tmp <= 6; dltdc_edge_sel_tmp <= 5'b00010; dltdc_np_edge_tmp <= 0; end 
					5'b00111: begin 	embtdc_bin_tmp <= 9; dltdc_edge_sel_tmp <= 5'b00100; dltdc_np_edge_tmp <= 1; end 
					5'b01111: begin 	embtdc_bin_tmp <= 12; dltdc_edge_sel_tmp <= 5'b01000; dltdc_np_edge_tmp <= 0; end
					5'b11111: begin 	embtdc_bin_tmp <= 15; dltdc_edge_sel_tmp <= 5'b10000; dltdc_np_edge_tmp <= 1; end
					5'b11110: begin 	embtdc_bin_tmp <= 18; dltdc_edge_sel_tmp <= 5'b00001; dltdc_np_edge_tmp <= 0; end
					5'b11100: begin 	embtdc_bin_tmp <= 22; dltdc_edge_sel_tmp <= 5'b00010; dltdc_np_edge_tmp <= 1; end
					5'b11000: begin 	embtdc_bin_tmp <= 25; dltdc_edge_sel_tmp <= 5'b00100; dltdc_np_edge_tmp <= 0; end
					5'b10000: begin 	embtdc_bin_tmp <= 28; dltdc_edge_sel_tmp <= 5'b01000; dltdc_np_edge_tmp <= 1; end
					default:
						begin 
						    embtdc_bin_tmp <= 0; dltdc_edge_sel_tmp <=5'b00001; dltdc_np_edge_tmp <= 1;
						end
				endcase
			end
			always @* begin 
				// fine
				case(SAMPLED_PH_FINE_IN)
					10'b00_0000_0000: begin dltdc_bin_tmp <= 0; end 
					10'b00_0000_0001: begin dltdc_bin_tmp <= 2; end 
					10'b00_0000_0011: begin dltdc_bin_tmp <= 5; end 
					10'b00_0000_0111: begin dltdc_bin_tmp <= 8; end 
					10'b00_0000_1111: begin dltdc_bin_tmp <= 11; end 
					10'b00_0001_1111: begin dltdc_bin_tmp <= 14; end 
					10'b00_0011_1111: begin dltdc_bin_tmp <= 17; end 
					10'b00_0111_1111: begin dltdc_bin_tmp <= 20; end 
					10'b00_1111_1111: begin dltdc_bin_tmp <= 23; end 
					10'b01_1111_1111: begin dltdc_bin_tmp <= 25; end 
					10'b11_1111_1111: begin dltdc_bin_tmp <= 28; end
					default: dltdc_bin_tmp <= 0; 
				endcase
			
		// Generate Retime Correction signals
				//Generation selection edge for reference retiming
				if ( (($unsigned(0) <= embtdc_bin_tmp ) && ( embtdc_bin_tmp <= $unsigned(7) )) || ( embtdc_bin_tmp >=$unsigned(27)) ) 
					retime_edge_sel = 0; // neg-edge
				else
					retime_edge_sel = 1; // pos-edge
				//Correction factor for retiming circuit
				//if (tdc_out_binary >= $unsigned(3*DCO_NUM_PH/4) ) 
				if (embtdc_bin_tmp >= $unsigned(27) ) 
					retime_lag = 1; // next negedge ( need to subtract 1 from count value )
				else
					retime_lag = 0;
			end
		// Latch all of the output signals
			//always @(posedge CLKREF_IN or posedge RST) begin
			always @* begin  //-km: to reduce edge selection latency 
				if (RST) 
					begin
						TDC_OUT <= {TDC_WIDTH{1'b0}};
						RETIME_EDGE_SEL_OUT <= 1'b0;
						RETIME_LAG_OUT <= 1'b0;
						DLTDC_EDGE_SEL_OUT <= 5'b00001;
						DLTDC_NP_EDGE <= 1;
						//sampled_phases_latch <= 0;
					end
				else
					begin
						TDC_OUT <= {embtdc_bin_tmp,dltdc_bin_tmp};
						RETIME_EDGE_SEL_OUT <= retime_edge_sel;
						RETIME_LAG_OUT <= retime_lag;
						DLTDC_EDGE_SEL_OUT <= dltdc_edge_sel_tmp;
						DLTDC_NP_EDGE <= dltdc_np_edge_tmp;
					end
			end

endmodule 

module clkref_sync(
	CLKREF_IN,
	DCO_OUTP,
	RETIME_EDGE_SEL_IN,
	CLKREF_RETIMED_OUT);

	// Parameters
		parameter TDC_NUM_RETIME_CYCLES = 2;
		parameter TDC_NUM_RETIME_DELAYS = 2;

	// Ports
		input			CLKREF_IN;
		input			DCO_OUTP;		
		input			RETIME_EDGE_SEL_IN;

		output reg 		CLKREF_RETIMED_OUT;


	// Interconnect
		reg 	[TDC_NUM_RETIME_CYCLES-1:0]		retime_posedge_path;
		reg 	[TDC_NUM_RETIME_CYCLES-1:0]		retime_negedge_path;
		reg 									retime_negedge_start;
		wire 									retime_sel_edge_mux;


		reg 	[TDC_NUM_RETIME_DELAYS-1:0]		retime_delays;


	// Variables
		integer ii;


	// Synchronization of CLKREF with DCO_OUTP

 		// positive edge path 

			always @(posedge DCO_OUTP) begin	

				retime_posedge_path[0] <= CLKREF_IN;
				for(ii=1;ii<TDC_NUM_RETIME_CYCLES;ii=ii+1) begin
					retime_posedge_path[ii] <= retime_posedge_path[ii-1];
 				end
			end	

		// negative edge path

			always @(negedge DCO_OUTP) begin
				retime_negedge_start <= CLKREF_IN;
			end


			always @(posedge DCO_OUTP) begin	

				retime_negedge_path[0] <= retime_negedge_start;
				for(ii=1;ii<TDC_NUM_RETIME_CYCLES;ii=ii+1) begin
					retime_negedge_path[ii] <= retime_negedge_path[ii-1];
				end
			end


		// retimne CLKREF
			
			// mux the negative and positve paths 
			assign retime_sel_edge_mux = RETIME_EDGE_SEL_IN ? 
				retime_posedge_path[TDC_NUM_RETIME_CYCLES-1] :
				retime_negedge_path[TDC_NUM_RETIME_CYCLES-1];


			// syncronize FREF after some delay
			always @(posedge DCO_OUTP) begin

				retime_delays[0] <= retime_sel_edge_mux;
				for(ii=1;ii<TDC_NUM_RETIME_DELAYS;ii=ii+1) begin
				
					retime_delays[ii] <= retime_delays[ii-1];
				end

				CLKREF_RETIMED_OUT <= retime_delays[TDC_NUM_RETIME_DELAYS-1];
			end

endmodule


`endif
