`ifndef __TDC_COUNTER__
`define __TDC_COUNTER__


`timescale 1ns/1ps


module TDC_COUNTER(
	CLKREF_IN, 
	SAMPLED_PHASES_IN, 
	DCO_OUTP,
	RST, 
	CLKREF_RETIMED_OUT, 
	TDC_OUT, 
	EDGE_SEL_ENABLE, 	//ff-km: enabling edge selection. [0] means chose PH_P_out[0]
	EDGE_SHIFT_MAX, 	//ff-km: maximum value of edge sel in binary: same value as TDC_MAX+1 
	EDGE_SEL_DEFAULT,		//ff-km: edge selection default value 
	EDGE_SEL_DEFAULT_BIN,		//ff-km: edge selection default value (binary) 
	EDGE_SEL_OUT,		//ff-km: edge selection output one hot	
	//PEDGE,			//ff-km
	//NEDGE,			//ff-km
	CAPTURE_MUX_SEL,	//ff-km	
	CAPTURE_MUX_OUT,	//ff-km	
	COUNT_ACCUM_OUT);


	// Functions
		`include "FUNCTIONS.v"

	// Parameters
		parameter TDC_MAX = 63;	
		parameter TDC_COUNT_ACCUM_WIDTH = 12;	
		parameter TDC_NUM_PHASE_LATCH = 2;
		parameter TDC_NUM_RETIME_CYCLES = 3;
		parameter TDC_NUM_RETIME_DELAYS = 2;

		parameter TDC_NUM_COUNTER_DIVIDERS = 3;

		parameter integer CAPTURE_WIDTH = 25;

	// Local Parameters
		localparam TDC_WIDTH = func_clog2(TDC_MAX);
		localparam DCO_NUM_PHASES = TDC_MAX+1;


	// Ports
		input 										CLKREF_IN;
		input 		[DCO_NUM_PHASES-1:0] 			SAMPLED_PHASES_IN;	
		input 										DCO_OUTP;
		input										RST;

		output reg 									CLKREF_RETIMED_OUT; 
		output reg 	[TDC_WIDTH-1:0] 				TDC_OUT;
		output reg 	[TDC_COUNT_ACCUM_WIDTH-1:0]		COUNT_ACCUM_OUT;
	
	// ff-km:muxing for test purpose
		input 		[2:0] 							CAPTURE_MUX_SEL;
		output reg 	[CAPTURE_WIDTH-1 :0]			CAPTURE_MUX_OUT;
	//edge_selection
		input							EDGE_SEL_ENABLE; //ff-km
		input		[TDC_WIDTH-1:0]				EDGE_SHIFT_MAX; //ff-km
		input		[TDC_MAX:0]				EDGE_SEL_DEFAULT;	//ff-km
		input		[TDC_WIDTH-1:0]				EDGE_SEL_DEFAULT_BIN;	//ff-km
		output reg	[TDC_MAX:0]				EDGE_SEL_OUT;	//ff-km
		wire		[TDC_MAX:0]				edge_sel_out_temp; //ff-km
		wire		[TDC_WIDTH-1:0]				edge_sel_temp_bin; //ff-km
		reg		[TDC_WIDTH-1:0]				edge_sel_d_bin; //ff-km
		wire							pedge_temp;//ff-km
		wire							nedge_temp;//ff-km
//		output	reg						PEDGE; //ff-km
//		output	reg						NEDGE; //ff-km
	
	// Internal Signals
		wire 		[TDC_WIDTH-1:0] 				tdc_out_temp;

		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_curr;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_accum_prev;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_curr;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_prev;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_gray;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		clkref_accum_binary;
		reg 										dco_gray_accum_sel;

		wire										clkref_retimed;
		wire 										retime_edge_sel;
		wire 										retime_lag;

	// Variables 
		integer ii;


	// Encode the sampled phases in binary

		// Instantiate TDC enocder
		TDC_ENCODER #(
				.TDC_MAX(TDC_MAX),
				.TDC_NUM_PHASE_LATCH(TDC_NUM_PHASE_LATCH))
			tdc_encoder(
				.CLKREF_IN(CLKREF_IN),
				.DCO_OUTP(DCO_OUTP),
				.RST(RST),
				.SAMPLED_PHASES_IN(SAMPLED_PHASES_IN), 
				.TDC_OUT(tdc_out_temp), 
				.EDGE_SEL_ENABLE(EDGE_SEL_ENABLE),  	//ff-km
				.EDGE_SHIFT_MAX(EDGE_SHIFT_MAX),		//ff-km	
				.EDGE_SEL_DEFAULT(EDGE_SEL_DEFAULT),		//ff-km
				.EDGE_SEL_OUT_TEMP(edge_sel_out_temp),		//ff-km
				.EDGE_SEL_D(edge_sel_d_bin),		//ff-km
				.EDGE_SEL_TEMP_BIN(edge_sel_temp_bin),		//ff-km
				//.PEDGE(pedge_temp),				//ff-km
				//.NEDGE(nedge_temp),				//ff-km
				.RETIME_EDGE_SEL_OUT(retime_edge_sel), 
				.RETIME_LAG_OUT(retime_lag)
		);

		// latch encoder on retimed edge
		always @(posedge clkref_retimed) begin
			TDC_OUT <= tdc_out_temp; 	
			//ff-km
			if (EDGE_SEL_ENABLE==0)begin
				EDGE_SEL_OUT <= EDGE_SEL_DEFAULT;    //ff-km
				edge_sel_d_bin   <= EDGE_SEL_DEFAULT_BIN;
				//PEDGE <= 1'b1;
				//NEDGE <= 1'b0;
			end else begin
				EDGE_SEL_OUT <= edge_sel_out_temp;
				edge_sel_d_bin   <= edge_sel_temp_bin;
				//PEDGE <= pedge_temp;
				//NEDGE <= nedge_temp;
			end
		end


	// Accumulate the DCO edges

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
		// get the gray code
		always @(posedge clkref_retimed or posedge RST) begin
			if (RST) begin
				clkref_accum_curr <= 0;
				clkref_accum_prev <= 0;
				dco_gray_accum_sel <= retime_lag;
			end 
			else begin
				clkref_accum_curr <= dco_accum_curr;
				clkref_accum_prev <= dco_accum_prev;
				dco_gray_accum_sel <= retime_lag;
			end
		end

		// select the right accum value 
		always @* begin
			clkref_accum_binary = dco_gray_accum_sel ? clkref_accum_prev : clkref_accum_curr;
		end

		// assign the output
		always @* begin
			COUNT_ACCUM_OUT = clkref_accum_binary;
		end


	// Retime CLKREF
 
 		// Instantiate the retime synchronizer
		CLKREF_SYNC #(
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

	// km: Build the capture system for signal selection (testing purpose)

		always @* begin
			case(CAPTURE_MUX_SEL)
				0: 	CAPTURE_MUX_OUT <= SAMPLED_PHASES_IN;
				1: 	CAPTURE_MUX_OUT <= edge_sel_d_bin;
				2: 	CAPTURE_MUX_OUT <= pedge_temp;
				3: 	CAPTURE_MUX_OUT <= nedge_temp;
				default: 
				    CAPTURE_MUX_OUT <= SAMPLED_PHASES_IN;
			endcase
		end


endmodule



// new TDC_ENCODER: latch SAMPLED_PHASES_IN with DCO_OUTP
// assuming SAMPLED_PHASES_IN is sampled by CLKREF beforehand
// number of latchs should be less that retime cycle
module TDC_ENCODER (
	CLKREF_IN,
	DCO_OUTP, //-km
	RST,
	SAMPLED_PHASES_IN, 
	TDC_OUT, 
	EDGE_SEL_ENABLE, 	//ff-km: enabling edge selection. [0] means chose PH_P_out[0]
	EDGE_SHIFT_MAX, 	//ff-km: maximum value of edge sel in binary: same value as TDC_MAX+1 
	EDGE_SEL_DEFAULT,		//ff-km: edge selection default value 
	EDGE_SEL_OUT_TEMP,		//ff-km: edge selection output one hot	
	EDGE_SEL_D,		//ff-km: edge selection output binary	
	EDGE_SEL_TEMP_BIN,		//ff-km: edge selection output binary	
	//PEDGE,			//ff-km
	//NEDGE,			//ff-km
	RETIME_EDGE_SEL_OUT, 
	RETIME_LAG_OUT);


	// Functions
		`include "FUNCTIONS.v"

	// Parameters
		parameter TDC_MAX = 31;
		parameter TDC_NUM_PHASE_LATCH = 2; 

	// Local Paramters
		localparam DCO_NUM_PHASES = TDC_MAX+1;
		localparam TDC_WIDTH = func_clog2(TDC_MAX);
	//ff-km: Threshold value of EDGE_SEL for P or N edge
		localparam EDGE_PN_TH = DCO_NUM_PHASES/2; 


	// Ports
		input								CLKREF_IN;
		input								DCO_OUTP;
		input								RST;
		input 		[DCO_NUM_PHASES-1:0] 	SAMPLED_PHASES_IN;  
	
		input							EDGE_SEL_ENABLE; //ff-km
		input signed	[TDC_WIDTH-1:0]				EDGE_SHIFT_MAX; //ff-km
		input		[TDC_MAX:0]				EDGE_SEL_DEFAULT;	//ff-km
		input 		[TDC_WIDTH-1:0]				EDGE_SEL_D;		//ff-km
		output		[TDC_MAX:0]				EDGE_SEL_OUT_TEMP;	//ff-km
		output		[TDC_WIDTH-1:0]				EDGE_SEL_TEMP_BIN;	//ff-km
//		output 							PEDGE; 			//ff-km
//		output 							NEDGE; 			//ff-km

		output reg 	[TDC_WIDTH-1:0] 		TDC_OUT;  
		output reg 							RETIME_EDGE_SEL_OUT;
		output reg 							RETIME_LAG_OUT;


	// Internal Signals
		reg 		[(TDC_NUM_PHASE_LATCH-1)*DCO_NUM_PHASES-1:0]	sampled_phases_latch;  //-km
		reg 		[DCO_NUM_PHASES-1:0]				sampled_phases_curr;  //-km
		reg 		[TDC_MAX:0] 			tdc_out_one_hot;
		reg 		[TDC_WIDTH-1:0]			tdc_out_binary;
		reg 								retime_edge_sel;
		reg 								retime_lag;


	// Variables
		integer ii;

	// edge selection related
		reg signed 	[TDC_WIDTH-1:0]				phase_shift; //ff-km
		reg signed	[TDC_WIDTH-1:0]				edge_sel_temp;
		reg 		[TDC_WIDTH-1:0]				edge_sel;

	//ff-km: edge selection
		// limit maximum shifting	
		always @* begin
			phase_shift =$signed(EDGE_SEL_D)-$signed(TDC_OUT);
			if ((phase_shift < EDGE_SHIFT_MAX+1) && (phase_shift > -(EDGE_SHIFT_MAX+1))) begin
				edge_sel_temp = TDC_OUT;
			end else if (EDGE_SEL_D > TDC_OUT) begin
				edge_sel_temp = $signed(EDGE_SEL_D)-$signed(EDGE_SHIFT_MAX);
			end else if (EDGE_SEL_D <= TDC_OUT) begin
				edge_sel_temp = $signed(EDGE_SEL_D)+$signed(EDGE_SHIFT_MAX);
			end
		end

		assign	EDGE_SEL_TEMP_BIN = $unsigned(edge_sel_temp);
		// select P or N edge according to the BIN value
//		assign PEDGE = (EDGE_SEL_TEMP_BIN < EDGE_PN_TH)? 1: 0;
//		assign NEDGE = (EDGE_SEL_TEMP_BIN < EDGE_PN_TH)? 0: 1;
		//convert tdc_in to onehot value
		generate
			genvar i;
			for(i=0; i<=TDC_MAX; i=i+1) begin: onehot_loop 
				assign EDGE_SEL_OUT_TEMP[i] = (EDGE_SEL_TEMP_BIN == i) ? 1: 0;
			end
		endgenerate


	// Behavioral

		// latch the sampled phases through multiple DCO_OUTP latches:
		// this code works for only TDC_NUM_PHASE_LATCH >= 2

			always @(posedge DCO_OUTP) begin	
				sampled_phases_latch[DCO_NUM_PHASES-1:0] <= SAMPLED_PHASES_IN;
				for(ii=1;ii<TDC_NUM_PHASE_LATCH-1;ii=ii+1) begin
					sampled_phases_latch[DCO_NUM_PHASES*(ii+1)-1 -:DCO_NUM_PHASES] <= sampled_phases_latch[DCO_NUM_PHASES*ii-1 -:DCO_NUM_PHASES];
 				end
				sampled_phases_curr=sampled_phases_latch[(TDC_NUM_PHASE_LATCH-1)*DCO_NUM_PHASES-1 -:DCO_NUM_PHASES];
			end	


		// Convert sampled phases to binary
			always @* begin 
		
				// convert sampled phases to one-hot with bubble suppression
				tdc_out_one_hot = {DCO_NUM_PHASES{1'b0}};
				for(ii=0;ii<DCO_NUM_PHASES;ii=ii+1)
				begin
					tdc_out_one_hot[ii] = 
						 sampled_phases_curr[(2*DCO_NUM_PHASES-ii-1) % DCO_NUM_PHASES] & 
						!sampled_phases_curr[(2*DCO_NUM_PHASES-ii-2) % DCO_NUM_PHASES] & 
						!sampled_phases_curr[(2*DCO_NUM_PHASES-ii-3) % DCO_NUM_PHASES];

				end

	
				//One hot to binary. Note: uses blocking assignments.
				tdc_out_binary = 0;
				for(ii=0;ii<DCO_NUM_PHASES;ii=ii+1) begin
					if (tdc_out_one_hot[ii] == 1'b1) begin
						tdc_out_binary = tdc_out_binary | $unsigned(ii);
					end
				end


		// Generate Retime Correction signals

				//Generation selection edge for reference retiming
				if ( ($unsigned(DCO_NUM_PHASES/4) <= tdc_out_binary )&( tdc_out_binary <= $unsigned(3*DCO_NUM_PHASES/4-1) ) ) 
					retime_edge_sel = 1;
				else
					retime_edge_sel = 0;


				//Correction factor for retiming circuit
				if (tdc_out_binary >= $unsigned(3*DCO_NUM_PHASES/4) ) 
					retime_lag = 1;
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
					end
				else
					begin
						TDC_OUT <= tdc_out_binary;
						RETIME_EDGE_SEL_OUT <= retime_edge_sel;
						RETIME_LAG_OUT <= retime_lag;
					end
			end

/*

			always @* begin
				TDC_OUT = tdc_out_binary;
				RETIME_EDGE_SEL_OUT = retime_edge_sel;
				RETIME_LAG_OUT = retime_lag;
			end
*/


endmodule 




module DCO_GRAY_ACCUMULATOR(
	DCO_OUTP,
	RST,
	DCO_ACCUM_OUT_CURR,
	DCO_ACCUM_OUT_PREV);


	// Parameters
		parameter TDC_NUM_COUNTER_DIVIDERS = 3;
		parameter TDC_COUNT_ACCUM_WIDTH = 12;


	// Ports
		input 										DCO_OUTP;
		input 										RST;

		output reg	[TDC_COUNT_ACCUM_WIDTH-1:0]		DCO_ACCUM_OUT_CURR;
		output reg	[TDC_COUNT_ACCUM_WIDTH-1:0]		DCO_ACCUM_OUT_PREV;


	// Internal Signals
		wire 		[TDC_NUM_COUNTER_DIVIDERS-1:0]	dco_binary_count_div;
		reg 		[TDC_NUM_COUNTER_DIVIDERS-1:0]	dco_binary_count_div_negedge;
		reg 		[TDC_COUNT_ACCUM_WIDTH-
					 TDC_NUM_COUNTER_DIVIDERS-1:0]	dco_binary_count_coarse;
		reg			[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_binary_count;

		reg		 	[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_gray_count;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_gray_count_curr;
		reg 		[TDC_COUNT_ACCUM_WIDTH-1:0]		dco_gray_count_prev;



	// Instatiate the binary count divider
		DCO_COUNT_DIVIDER 
				#(.NUM_COUNTER_DIVIDERS(TDC_NUM_COUNTER_DIVIDERS))
			dco_count_divider(
				.DCO_OUTP(DCO_OUTP),
				.RST(RST),
				.DCO_COUNT_DIV_OUT(dco_binary_count_div)
		);



	// run counter using the slowest divider output
		always @(negedge dco_binary_count_div[TDC_NUM_COUNTER_DIVIDERS-1] or posedge RST) begin
			if (RST)
				dco_binary_count_coarse <= 0;
			else 
				dco_binary_count_coarse <= dco_binary_count_coarse + 1 ;
		end

// -km : binary count coarse is already latched in posedge => this doesn't
//help metastability	
//		always @(negedge DCO_OUTP) begin
//			dco_binary_count_div_negedge <= dco_binary_count_div;
//		end



	// latch gray code counter ouputs

		// generate the binary and gray count
		always @* begin
			//dco_binary_count = {dco_binary_count_coarse, dco_binary_count_div_negedge};  //-km: eliminate negedge
			dco_binary_count = {dco_binary_count_coarse, dco_binary_count_div};
			dco_gray_count = dco_binary_count^(dco_binary_count>>1);
		end


		// latch the gray counts
		always @(posedge DCO_OUTP) begin
			dco_gray_count_curr <= dco_gray_count;
			dco_gray_count_prev <= dco_gray_count_curr;
		end


//-km: latch on posedge
		// retime to negegde to help with metastbility
		always @(negedge DCO_OUTP) begin
			DCO_ACCUM_OUT_CURR <= dco_gray_count_curr;
			DCO_ACCUM_OUT_PREV <= dco_gray_count_prev;
		end

endmodule



module DCO_COUNT_DIVIDER(
	DCO_OUTP,
	RST,
	DCO_COUNT_DIV_OUT);


	// Parameters
		parameter NUM_COUNTER_DIVIDERS = 3;


	// Ports
		input 										DCO_OUTP;
		input 										RST;
		output reg	[NUM_COUNTER_DIVIDERS-1:0]	DCO_COUNT_DIV_OUT;


	// Internal Signals
		reg 		[NUM_COUNTER_DIVIDERS-1:0]	dco_count_div;


	// Variables
		genvar genvar_ii;



	// generate the dividers to relax the counter speed

		generate
			for(genvar_ii=0; genvar_ii<NUM_COUNTER_DIVIDERS; genvar_ii=genvar_ii+1)
			begin : COUNT_DIVIDERS

				case(genvar_ii)
					
					0: begin : div0
						// first divider 
						always @(posedge DCO_OUTP or posedge RST) begin
							if (RST)
								dco_count_div[0] <= 1'b0;
							else
								dco_count_div[0] <= ~dco_count_div[0];
						end
					end

			// -km: commented out due to timing issue
			//		1: begin : div1
			//			// the second divider
			//			always @(posedge DCO_OUTP or posedge RST) begin
			//				if (RST)
			//					dco_count_div[genvar_ii] <= 1'b0;
			//				else
			//					dco_count_div[genvar_ii] <= 
			//						dco_count_div[genvar_ii] ^ dco_count_div[genvar_ii-1];
			//			end
			//		end

					default: begin :div2
						// the rest of the dividers
						always @(negedge dco_count_div[genvar_ii-1] or posedge RST) begin
							if (RST)
								dco_count_div[genvar_ii] <= 1'b0;
							else
								dco_count_div[genvar_ii] <= ~dco_count_div[genvar_ii];
						end
					end

				endcase

			end
		endgenerate



	// Assign the outputs

		always @* begin
			DCO_COUNT_DIV_OUT = dco_count_div;
		end


endmodule




module CLKREF_SYNC(
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


// TDC_ENCODER old version (edge selection has ref delay)
module old_TDC_ENCODER (
	CLKREF_IN,
	RST,
	SAMPLED_PHASES_IN, 
	TDC_OUT, 
	RETIME_EDGE_SEL_OUT, 
	RETIME_LAG_OUT);


	// Functions
		`include "FUNCTIONS.v"

	// Parameters
		parameter TDC_MAX = 31;


	// Local Paramters
		localparam DCO_NUM_PHASES = TDC_MAX+1;
		localparam TDC_WIDTH = func_clog2(TDC_MAX);


	// Ports
		input								CLKREF_IN;
		input								RST;
		input 		[DCO_NUM_PHASES-1:0] 	SAMPLED_PHASES_IN;  
	
		output reg 	[TDC_WIDTH-1:0] 		TDC_OUT;  
		output reg 							RETIME_EDGE_SEL_OUT;
		output reg 							RETIME_LAG_OUT;


	// Internal Signals
		reg 		[DCO_NUM_PHASES-1:0]	sampled_phases_curr;
		reg 		[TDC_MAX:0] 			tdc_out_one_hot;
		reg 		[TDC_WIDTH-1:0]			tdc_out_binary;
		reg 								retime_edge_sel;
		reg 								retime_lag;


	// Variables
		integer ii;


	// Behavioral

		// latch the sampled phases through multiple latches


			always @(posedge CLKREF_IN) begin
				sampled_phases_curr <= SAMPLED_PHASES_IN;
			end

/*
			always @* begin
				sampled_phases_curr = SAMPLED_PHASES_IN;
 			end
*/


		// Convert sampled phases to binary
			always @* begin 
		
				// convert sampled phases to one-hot with bubble suppression
				tdc_out_one_hot = {DCO_NUM_PHASES{1'b0}};
				for(ii=0;ii<DCO_NUM_PHASES;ii=ii+1)
				begin

					/*
					$display("%d\t%d\t%d\t%d", ii,
						(2*DCO_NUM_PHASES-ii-0) % DCO_NUM_PHASES,
						(2*DCO_NUM_PHASES-ii-1) % DCO_NUM_PHASES,
						(2*DCO_NUM_PHASES-ii-2) % DCO_NUM_PHASES );
					*/

					tdc_out_one_hot[ii] = 
						 sampled_phases_curr[(2*DCO_NUM_PHASES-ii-1) % DCO_NUM_PHASES] & 
						!sampled_phases_curr[(2*DCO_NUM_PHASES-ii-2) % DCO_NUM_PHASES] & 
						!sampled_phases_curr[(2*DCO_NUM_PHASES-ii-3) % DCO_NUM_PHASES];

				end

	
				//One hot to binary. Note: uses blocking assignments.
				tdc_out_binary = 0;
				for(ii=0;ii<DCO_NUM_PHASES;ii=ii+1) begin
					if (tdc_out_one_hot[ii] == 1'b1) begin
						tdc_out_binary = tdc_out_binary | $unsigned(ii);
					end
				end


		// Generate Retime Correction signals

				//Generation selection edge for reference retiming
				if ( ($unsigned(DCO_NUM_PHASES/4) <= tdc_out_binary )&( tdc_out_binary <= $unsigned(3*DCO_NUM_PHASES/4-1) ) ) 
					retime_edge_sel = 1;
				else
					retime_edge_sel = 0;


				//Correction factor for retiming circuit
				if (tdc_out_binary >= $unsigned(3*DCO_NUM_PHASES/4) ) 
					retime_lag = 1;
				else
					retime_lag = 0;

			end



		// Latch all of the output signals
			always @(posedge CLKREF_IN or posedge RST) begin

				if (RST) 
					begin
						TDC_OUT <= {TDC_WIDTH{1'b0}};
						RETIME_EDGE_SEL_OUT <= 1'b0;
						RETIME_LAG_OUT <= 1'b0;
					end
				else
					begin
						TDC_OUT <= tdc_out_binary;
						RETIME_EDGE_SEL_OUT <= retime_edge_sel;
						RETIME_LAG_OUT <= retime_lag;
					end
			end

/*

			always @* begin
				TDC_OUT = tdc_out_binary;
				RETIME_EDGE_SEL_OUT = retime_edge_sel;
				RETIME_LAG_OUT = retime_lag;
			end
*/


endmodule 


`endif

