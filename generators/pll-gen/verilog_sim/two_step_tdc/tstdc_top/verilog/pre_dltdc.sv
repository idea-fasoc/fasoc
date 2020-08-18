// pre-dltdc block
// pre-delay should be in this block
// 1st muxing between the gnd and edges should be done before the pre-delay to prevent wrong (faster) edges going in dltdc
// 2nd muxing should be done right before the dlktdc to prevent the wrong (slower) edges going in the dltdc
//`timescale 1ps/1ps

module pre_dltdc (
	DCO_RAW_PH,
	CLK_REF,
	DCO_EDGE_SEL,
	CLK_REF_OUT,
	DLTDC_NP_EDGE,
	RST,
	CLK_FB_OUT);

    // Parameters
	parameter DLTDC_NUM_PH = 10;
	parameter DCO_NUM_PH = 5; // 5 (nstage)
	parameter FB_PRE_MUX_DLY = 60e-12; 
	parameter REF_PRE_MUX_DLY = 15e-12; 
	parameter FB_POST_MUX_DLY_NEG = 30e-12; 
	parameter FB_POST_MUX_DLY_POS = 30e-12; 

	localparam FB_PATH_TOTAL_DLY = FB_PRE_MUX_DLY + FB_POST_MUX_DLY_NEG;
	localparam REF_PATH_DLY = FB_PATH_TOTAL_DLY + 10e-12;

	input	[DCO_NUM_PH-1:0]	DCO_RAW_PH;
	input 				CLK_REF;
	input 				DLTDC_NP_EDGE;
	input 				RST;
	input	[DCO_NUM_PH-1:0]	DCO_EDGE_SEL; // one-hot
	output	reg			CLK_REF_OUT;
	output				CLK_FB_OUT;

	logic	[DCO_NUM_PH-1:0]	dco_ph_mux1_in_pre;
	logic	[DCO_NUM_PH-1:0]	dco_ph_mux1_in;
	logic				dco_ph_mux2_in_neg;
	logic				dco_ph_mux2_in_pos;
	logic				dco_ph_mux1_out_neg;
	logic				dco_ph_mux1_out_pos;
	logic	[DCO_NUM_PH-1:0]	dco_ph_mux2_in;
	logic	[DCO_NUM_PH-1:0]	mux1_edge_sel; // one-hot
	
	logic				clk_ref_mux1_in;
	logic				final_mux_en;

	real TIME_SCALE=1e-12;
	// delay the raw phases
	genvar iph;
	generate
		for (iph=0; iph<DCO_NUM_PH; iph=iph+1) begin: GEN_PHASE
			always @(posedge DCO_RAW_PH[iph] or negedge DCO_RAW_PH[iph]) begin // 1. raw phases
				 dco_ph_mux1_in[iph] <= #(FB_PRE_MUX_DLY/TIME_SCALE) DCO_RAW_PH[iph];
			end
		end
	endgenerate

	always @(posedge CLK_REF or negedge CLK_REF) begin
		clk_ref_mux1_in = #(REF_PRE_MUX_DLY/TIME_SCALE) CLK_REF;
	end
	always @(posedge CLK_REF or negedge CLK_REF) begin
		CLK_REF_OUT = #(REF_PATH_DLY/TIME_SCALE) CLK_REF;
	end

	// latch the mux1 with delayed clk_ref to prevent wrong previous edge going in
	always @(posedge clk_ref_mux1_in or negedge clk_ref_mux1_in or posedge RST) begin
		if (RST | ~clk_ref_mux1_in) begin
			mux1_edge_sel <= 0;
		end else if (clk_ref_mux1_in) begin
			mux1_edge_sel <= DCO_EDGE_SEL;
		end
	end

	// edge selection for neg & pos path
	always @* begin
		case(mux1_edge_sel)
			5'b00000: begin dco_ph_mux1_out_neg = 1'b1;			dco_ph_mux1_out_pos = 1'b0; end	
			5'b00001: begin dco_ph_mux1_out_neg = dco_ph_mux1_in[0];	dco_ph_mux1_out_pos = dco_ph_mux1_in[0]; end 
			5'b00010: begin dco_ph_mux1_out_neg = dco_ph_mux1_in[1];	dco_ph_mux1_out_pos = dco_ph_mux1_in[1]; end
			5'b00100: begin dco_ph_mux1_out_neg = dco_ph_mux1_in[2];	dco_ph_mux1_out_pos = dco_ph_mux1_in[2]; end
			5'b01000: begin dco_ph_mux1_out_neg = dco_ph_mux1_in[3];	dco_ph_mux1_out_pos = dco_ph_mux1_in[3]; end
			5'b10000: begin dco_ph_mux1_out_neg = dco_ph_mux1_in[4];	dco_ph_mux1_out_pos = dco_ph_mux1_in[4]; end
			default: begin dco_ph_mux1_out_neg = 1'b1;			dco_ph_mux1_out_pos = 1'b0; end
		endcase
	end	

	// delay mux outputs	
	always @(posedge dco_ph_mux1_out_neg or negedge dco_ph_mux1_out_neg) begin // 2. mux outputs 
		 dco_ph_mux2_in_neg <= #(FB_POST_MUX_DLY_NEG/TIME_SCALE) ~dco_ph_mux1_out_neg;
	end
	always @(posedge dco_ph_mux1_out_pos or posedge dco_ph_mux1_out_pos) begin // 2. mux outputs 
		 dco_ph_mux2_in_pos <= #(FB_POST_MUX_DLY_POS/TIME_SCALE) dco_ph_mux1_out_pos;
	end

	// final mux en 
	//always @(negedge CLK_FB_OUT or posedge CLK_REF or RST) begin
	//	if (RST | ~CLK_FB_OUT) begin
	always @(posedge CLK_REF or negedge CLK_REF or RST) begin
		if (RST | ~CLK_REF) begin
			final_mux_en <= 0;
		end else if (CLK_REF) begin
			final_mux_en <= 1;
		end
	end	

	// final mux
	assign CLK_FB_OUT = final_mux_en? (DLTDC_NP_EDGE? dco_ph_mux2_in_pos:dco_ph_mux2_in_neg) : 0;
	
endmodule	
