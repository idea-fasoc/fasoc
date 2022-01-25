// delay difference-based DLTDC model
`timescale 1ps/1ps

module dltdc_v3	(	clkref_retimed,
			tdc_out,
			DCO_RAW_PH,
			pre_ls_ref_CC, 
			pre_ls_ref_FC, 
			post_ls_ref_CC, 
			post_ls_ref_FC, 
			pre_es_fb_CC, 
			pre_es_fb_FC, 
			post_es_fb_CC, 
			post_es_fb_FC,
			CC_fb,
			FC_fb,
			CC_ref,
			FC_ref,
			CLK_REF,
			smpl_edge_sel_out, // test
			edge_sel,
			edge_sel_idx,
			pre_PH_fb_out, //test
			pre_dltdc_in_fb_out, //test
			pre_dltdc_in_ref_out, //test
			np_edge, 
			post_es_fb_out,
			embtdc_out_out,
			edge_fb_idx,
			es_check, // edge_sel calibration check 04/14/21
			clk_ref_ls_out // 041821
			);

	// pre-dltdc 
@@		parameter pre_ls_ref_NSTG	=@pl; // 18 
	//parameter pre_ls_ref_NSTG	=16; // 042221
@@		parameter pre_ls_ref_NSTG_CC_TUNE=@rM; // 2 
@@		parameter pre_ls_ref_NCC_TUNE 	=@rC; // 2
	parameter pre_ls_ref_NCC_TUNE_BASE=3; 
	parameter pre_ls_ref_NCC_BASE	=2;  
	parameter pre_ls_ref_NCC_OUT	=4; 
@@		parameter pre_ls_ref_NFC	=@rF; // 63
	parameter pre_ls_ref_BASE_3st	=1; 
	parameter pre_ls_ref_TUNE_BASE_3st=1; 
	parameter pre_ls_ref_TUNE_TUNE_3st=0; 
	parameter pre_ls_ref_OUTBUF_3st	=0; 
	localparam NUM_pre_ls_ref_CC = pre_ls_ref_NSTG_CC_TUNE*pre_ls_ref_NCC_TUNE; 
	localparam NUM_pre_ls_ref_FC = pre_ls_ref_NFC; 

	// post latch edge sel path for ref
	//parameter post_ls_ref_NSTG	=4;
@@		parameter post_ls_ref_NSTG	=@Pl; // 6
@@		parameter post_ls_ref_NSTG_CC_TUNE=@RM; // 2
@@		parameter post_ls_ref_NCC_TUNE	=@RC; // 2
	parameter post_ls_ref_NCC_TUNE_BASE=1; // 041921
	parameter post_ls_ref_NCC_BASE	=1; // 041921
	parameter post_ls_ref_NCC_OUT	=4;
	parameter post_ls_ref_NFC	=pre_ls_ref_NFC;
	parameter post_ls_ref_BASE_3st	=1; 
	parameter post_ls_ref_TUNE_BASE_3st=1; 
	parameter post_ls_ref_TUNE_TUNE_3st=0; 
	parameter post_ls_ref_OUTBUF_3st   =0; 
	localparam NUM_post_ls_ref_CC = post_ls_ref_NSTG_CC_TUNE*post_ls_ref_NCC_TUNE; 
	localparam NUM_post_ls_ref_FC = post_ls_ref_NFC; 

	// pre edge sel path for fb
	//parameter pre_es_fb_NSTG	=6;
@@		parameter pre_es_fb_NSTG	=@fN; // 8
@@		parameter pre_es_fb_NSTG_CC_TUNE=@ft; // 2
@@		parameter pre_es_fb_NCC_TUNE	=@fC; // 2
	parameter pre_es_fb_NCC_TUNE_BASE=2;
	parameter pre_es_fb_NCC_BASE	=2;
	parameter pre_es_fb_NCC_OUT	=4;
	parameter pre_es_fb_NFC		= pre_ls_ref_NFC;
	parameter pre_es_fb_BASE_3st	=1; 
	parameter pre_es_fb_TUNE_BASE_3st=1; 
	parameter pre_es_fb_TUNE_TUNE_3st=1; 
	parameter pre_es_fb_OUTBUF_3st	=1; 
	localparam NUM_pre_es_fb_CC = pre_es_fb_NSTG_CC_TUNE*pre_es_fb_NCC_TUNE; 
	localparam NUM_pre_es_fb_FC = pre_es_fb_NFC; 

	// post edge sel path for fb
@@		parameter post_es_fb_NSTG	=@FN; // 4
	//parameter post_es_fb_NSTG	=2; // 041921
@@		parameter post_es_fb_NSTG_CC_TUNE=@FT; // 2
@@		parameter post_es_fb_NCC_TUNE	=@FC; // 2
	parameter post_es_fb_NCC_TUNE_BASE=2;
	parameter post_es_fb_NCC_BASE	=2;
	parameter post_es_fb_NCC_OUT	=4;
	parameter post_es_fb_NFC	= pre_ls_ref_NFC;
	parameter post_es_fb_BASE_3st	=1; 
	parameter post_es_fb_TUNE_BASE_3st=1; 
	parameter post_es_fb_TUNE_TUNE_3st=0; 
	parameter post_es_fb_OUTBUF_3st	=0;
	localparam NUM_post_es_fb_CC = post_es_fb_NSTG_CC_TUNE*post_es_fb_NCC_TUNE; 
	localparam NUM_post_es_fb_FC = post_es_fb_NFC; 

	//parameter fm_NCC = 2; // final mux
	parameter fm_NCC = 4; // 041921 

	// dltdc delay line version 2	
@@		parameter NSTG = @dM; // 10 
@@		parameter NFC_fb = @ff; // 4
@@		parameter NFC_ref = @fr; // 4
@@		parameter NDRV_fb = @df; // 2
@@		parameter NDRV_ref = @dr; // 2
@@		parameter NCC_fb = @cf; // 2 
@@		parameter NCC_ref = @cr; // 2
	parameter DCO_NUM_PH = 5;

	// DFF char 
	parameter dff_su_time = 20e-12;

	parameter fmux_delay = 17e-12; 
	// dltdc delay lines
	parameter dltdc_fb_delay = 26e-12;
	parameter dltdc_ref_delay = 17e-12; 

	input				clkref_retimed;	
	input 				CLK_REF;
	input	[DCO_NUM_PH-1:0]		DCO_RAW_PH;
	// delay control signals for pre-dltdc DTCs
	input 	[NUM_pre_ls_ref_CC-1:0] 	pre_ls_ref_CC; 
	input 	[NUM_pre_ls_ref_FC-1:0] 	pre_ls_ref_FC; 
	input 	[NUM_post_ls_ref_CC-1:0] 	post_ls_ref_CC; 
	input 	[NUM_post_ls_ref_FC-1:0] 	post_ls_ref_FC; 
	input	[DCO_NUM_PH-1:0][NUM_pre_es_fb_CC-1:0]	pre_es_fb_CC;					
	input	[DCO_NUM_PH-1:0][NUM_pre_es_fb_FC-1:0]	pre_es_fb_FC;					
	input 	[NUM_post_es_fb_CC-1:0] 	post_es_fb_CC; 
	input 	[NUM_post_es_fb_FC-1:0]		post_es_fb_FC;

	// delay control signals for DLTDC 
	input 	[NFC_fb*NSTG-1:0] 		FC_fb; 
	input 	[NCC_fb*NSTG-1:0] 		CC_fb; 
	input 	[NFC_ref*NSTG-1:0] 		FC_ref; 
	input 	[NCC_ref*NSTG-1:0] 		CC_ref;

	// other signals 
	output  [NSTG-1:0]			tdc_out;
	output	[DCO_NUM_PH-1:0]		smpl_edge_sel_out; // timing check-point 1
	output	[DCO_NUM_PH-1:0]		edge_sel;
	output logic	[2:0]			edge_sel_idx;
	output logic	[2:0]			edge_fb_idx;
	logic	[DCO_NUM_PH-1:0]		edge_sel_out;
	output	[DCO_NUM_PH-1:0]		pre_PH_fb_out; // test purpose 
	output					pre_dltdc_in_fb_out; // test purpose
	output					pre_dltdc_in_ref_out; // test purpose
	output	reg				np_edge;
	output					post_es_fb_out;
	logic					np_edge_fb;
	logic					np_edge_gated; // test purpose
	output	[DCO_NUM_PH-1:0]		embtdc_out_out;
	output	[DCO_NUM_PH-1:0]		es_check;
	output					clk_ref_ls_out; // 041821

	// pre-dltdc wires/regs
	logic	[DCO_NUM_PH-1:0]			pre_es_fb_PH;					
	logic						post_es_fb;
	logic						clk_ref_ls;
	logic						pre_dltdc_fb; 
	logic						pre_final_fb; 
	logic						pre_dltdc_ref;
	logic						clk_ref_b;
	logic						edge_sel_off; // (<= np_edge_off) 
	logic						final_fb_pass;

	// dltdc
	logic 	[NSTG:0] 				PH_fb;
	logic 	[NSTG:0] 				PH_fb_tmp;
	logic 	[NSTG:0] 				PH_ref;
	logic 	[NSTG:0] 				PH_ref_tmp;
	logic	[DCO_NUM_PH-1:0]			edge_sel;
	logic	[DCO_NUM_PH-1:0]			edge_fb;
	logic	[DCO_NUM_PH-1:0]			edge_sel_tmp;
	logic	[DCO_NUM_PH-1:0]			edge_fb_tmp;
	logic	[DCO_NUM_PH-1:0]			embtdc_out;
	logic	[DCO_NUM_PH-1:0]			smpl_ph_fb;
	logic	[DCO_NUM_PH-1:0]			smpl_edge_sel; // test purpose

	// CLK_REF_BUF
@@		@X2 clk_ref_buf_0 (.Y(clk_ref_b),.A(CLK_REF)); // BUFH 2X	
@@		@Xt clk_ref_buf_1 (.Y(clk_ref_b),.A(CLK_REF)); // BUFH 2X

@@		@xt clk_ref_ls_buf (.Y(clk_ref_ls_out),.A(clk_ref_ls)); // BUF 2X 
	// initial clocks	
	assign PH_ref[0] = pre_dltdc_ref; // clkref input to dltdc

	//===============================================================================
	// pre-DLTDC 
	//===============================================================================

	// Selection pins
	generate 
		genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<DCO_NUM_PH ; i=i+1)
		begin:stg_emb
@@				@Df embtdc_dff (.Q(embtdc_out[i]), .CK(clk_ref_b), .D(DCO_RAW_PH[i])); // DFFQ X1
@@	  			@xn xnor_edge_sel ( .A(embtdc_out[i%DCO_NUM_PH]), .B(embtdc_out[(i+1)%DCO_NUM_PH]), .Y(edge_sel_tmp[i]) ); // XNOR2 X0p6
@@				@DF edge_fb_dff (.Q(smpl_ph_fb[i]), .CK(clk_ref_ls), .D(pre_PH_fb_out[i])); // DFFQ X1
@@	  			@Xn xnor_edge_fb ( .A(smpl_ph_fb[i%DCO_NUM_PH]), .B(smpl_ph_fb[(i+1)%DCO_NUM_PH]), .Y(edge_fb_tmp[i]) ); // XNOR2 X0p6
		end
	endgenerate

	// np_edge (logical)
	always @* begin		
		case (edge_sel_tmp)
			5'b00001: begin	np_edge = embtdc_out[0]; end	
			5'b00010: begin	np_edge = embtdc_out[1]; end	
			5'b00100: begin	np_edge = embtdc_out[2]; end	
			5'b01000: begin	np_edge = embtdc_out[3]; end	
			5'b10000: begin	np_edge = embtdc_out[4]; end
			default: begin np_edge = 1; end
		endcase
	end	

	assign edge_sel[0] = np_edge? edge_sel_tmp[0] : edge_sel_tmp[1];
	assign edge_sel[1] = np_edge? edge_sel_tmp[1] : edge_sel_tmp[2];
	assign edge_sel[2] = np_edge? edge_sel_tmp[2] : edge_sel_tmp[3];
	assign edge_sel[3] = np_edge? edge_sel_tmp[3] : edge_sel_tmp[4];
	assign edge_sel[4] = np_edge? edge_sel_tmp[4] : edge_sel_tmp[0];
	// np_edge for pre_fb calib
	always @* begin		
		case (edge_fb_tmp)
			5'b00001: begin	np_edge_fb = smpl_ph_fb[0]; end	
			5'b00010: begin	np_edge_fb = smpl_ph_fb[1]; end	
			5'b00100: begin	np_edge_fb = smpl_ph_fb[2]; end	
			5'b01000: begin	np_edge_fb = smpl_ph_fb[3]; end	
			5'b10000: begin	np_edge_fb = smpl_ph_fb[4]; end
			default: begin np_edge_fb = 1; end
		endcase
	end	

	assign edge_fb[0] = np_edge_fb? edge_fb_tmp[0] : edge_fb_tmp[1];
	assign edge_fb[1] = np_edge_fb? edge_fb_tmp[1] : edge_fb_tmp[2];
	assign edge_fb[2] = np_edge_fb? edge_fb_tmp[2] : edge_fb_tmp[3];
	assign edge_fb[3] = np_edge_fb? edge_fb_tmp[3] : edge_fb_tmp[4];
	assign edge_fb[4] = np_edge_fb? edge_fb_tmp[4] : edge_fb_tmp[0];

	// latch edge_sel: 04/04/2021: reset on clkref_retimed to save power.
@@		@rp dff_smpl_edge_sel_0 (.Q(smpl_edge_sel[0]),.CK(clk_ref_ls), .D(edge_sel[0]), .R(clkref_retimed)); // DFFRPQ X3
@@		@rP dff_smpl_edge_sel_1 (.Q(smpl_edge_sel[1]),.CK(clk_ref_ls), .D(edge_sel[1]), .R(clkref_retimed));
@@		@Rp dff_smpl_edge_sel_2 (.Q(smpl_edge_sel[2]),.CK(clk_ref_ls), .D(edge_sel[2]), .R(clkref_retimed));
@@		@RP dff_smpl_edge_sel_3 (.Q(smpl_edge_sel[3]),.CK(clk_ref_ls), .D(edge_sel[3]), .R(clkref_retimed));
@@		@pq dff_smpl_edge_sel_4 (.Q(smpl_edge_sel[4]),.CK(clk_ref_ls), .D(edge_sel[4]), .R(clkref_retimed));

@@		@pQ dff_es_check_0 (.Q(es_check[0]),.CK(smpl_edge_sel[0]), .D(pre_es_fb_PH[0]), .R(~clk_ref_b));
@@		@Pq dff_es_check_1 (.Q(es_check[1]),.CK(smpl_edge_sel[1]), .D(pre_es_fb_PH[1]), .R(~clk_ref_b));
@@		@PQ dff_es_check_2 (.Q(es_check[2]),.CK(smpl_edge_sel[2]), .D(pre_es_fb_PH[2]), .R(~clk_ref_b));
@@		@rq dff_es_check_3 (.Q(es_check[3]),.CK(smpl_edge_sel[3]), .D(pre_es_fb_PH[3]), .R(~clk_ref_b));
@@		@Rq dff_es_check_4 (.Q(es_check[4]),.CK(smpl_edge_sel[4]), .D(pre_es_fb_PH[4]), .R(~clk_ref_b));


	// edge_sel_idx
	always @* begin		
		case (edge_sel)
			5'b00001: begin	edge_sel_idx = 0; end	
			5'b00100: begin	edge_sel_idx = 1; end	
			5'b10000: begin	edge_sel_idx = 2; end	
			5'b00010: begin	edge_sel_idx = 3; end	
			5'b01000: begin	edge_sel_idx = 4; end
			default: begin edge_sel_idx = 0; end
		endcase
	end	
	always @* begin		
		case (edge_fb)
			5'b00001: begin	edge_fb_idx = 0; end	
			5'b00100: begin	edge_fb_idx = 1; end	
			5'b10000: begin	edge_fb_idx = 2; end	
			5'b00010: begin	edge_fb_idx = 3; end	
			5'b01000: begin	edge_fb_idx = 4; end
			default: begin edge_fb_idx = 0; end
		endcase
	end	

	// Put down CLKREF path stages
	// pre-latch edge sel path for ref
	lpdtc_v2 
		#(	.NSTG		(pre_ls_ref_NSTG	),
			.NSTG_CC_TUNE	(pre_ls_ref_NSTG_CC_TUNE), 
			.NCC_TUNE	(pre_ls_ref_NCC_TUNE	),
			.NCC_TUNE_BASE	(pre_ls_ref_NCC_TUNE_BASE), 
			.NCC_BASE	(pre_ls_ref_NCC_BASE	),  
			.NCC_OUT	(pre_ls_ref_NCC_OUT	), 
			.NFC		(pre_ls_ref_NFC		),
			.N_STG_FC	(pre_ls_ref_NSTG-1	),
			.BASE_3st 	(pre_ls_ref_BASE_3st 	),
			.TUNE_BASE_3st	(pre_ls_ref_TUNE_BASE_3st),
			.TUNE_TUNE_3st	(pre_ls_ref_TUNE_TUNE_3st),
			.OUTBUF_3st	(pre_ls_ref_OUTBUF_3st	)) 
	u_pre_ls_ref_dtc (.dtc_in(clk_ref_b), .dtc_out(clk_ref_ls), .CC(pre_ls_ref_CC), .FC(pre_ls_ref_FC));	

	// post latch edge sel path for ref
	lpdtc_v2 
		#(	.NSTG		(post_ls_ref_NSTG	),
			.NSTG_CC_TUNE	(post_ls_ref_NSTG_CC_TUNE),
			.NCC_TUNE	(post_ls_ref_NCC_TUNE	),
			.NCC_TUNE_BASE	(post_ls_ref_NCC_TUNE_BASE),
			.NCC_BASE	(post_ls_ref_NCC_BASE	),
			.NCC_OUT	(post_ls_ref_NCC_OUT	),
			.NFC		(post_ls_ref_NFC	),
			.N_STG_FC	(post_ls_ref_NSTG-1	),
			.BASE_3st 	(post_ls_ref_BASE_3st 	),
			.TUNE_BASE_3st	(post_ls_ref_TUNE_BASE_3st),
			.TUNE_TUNE_3st	(post_ls_ref_TUNE_TUNE_3st),
			.OUTBUF_3st	(post_ls_ref_OUTBUF_3st	)) 
	u_post_ls_ref_dtc (.dtc_in(clk_ref_ls), .dtc_out(pre_dltdc_ref), .CC(post_ls_ref_CC), .FC(post_ls_ref_FC));	

	//----------------------------------------------------------
	// analog test purpose
	assign pre_PH_fb_out[0] = pre_es_fb_PH[0];
	assign pre_PH_fb_out[1] = pre_es_fb_PH[1];
	assign pre_PH_fb_out[2] = pre_es_fb_PH[2];
	assign pre_PH_fb_out[3] = pre_es_fb_PH[3];
	assign pre_PH_fb_out[4] = pre_es_fb_PH[4];
	
@@	@b2 embtdc_out_buf_0 (.Y(embtdc_out_out[0]),.A(embtdc_out[0])); // BUFH X2	
@@	@B2 embtdc_out_buf_1 (.Y(embtdc_out_out[1]),.A(embtdc_out[1]));	
@@	@2b embtdc_out_buf_2 (.Y(embtdc_out_out[2]),.A(embtdc_out[2]));	
@@	@2B embtdc_out_buf_3 (.Y(embtdc_out_out[3]),.A(embtdc_out[3]));	
@@	@be embtdc_out_buf_4 (.Y(embtdc_out_out[4]),.A(embtdc_out[4]));	
		
@@	@bE pp_buf (.Y(post_es_fb_out),.A(post_es_fb));

@@	@Be edge_sel_buf_0 (.Y(edge_sel_out[0]),.A(edge_sel[0]));	
@@	@BE edge_sel_buf_1 (.Y(edge_sel_out[1]),.A(edge_sel[1]));	
@@	@bt edge_sel_buf_2 (.Y(edge_sel_out[2]),.A(edge_sel[2]));	
@@	@bT edge_sel_buf_3 (.Y(edge_sel_out[3]),.A(edge_sel[3]));	
@@	@Bt edge_sel_buf_4 (.Y(edge_sel_out[4]),.A(edge_sel[4]));	
		
@@	@BT smpl_edge_sel_buf_0 (.Y(smpl_edge_sel_out[0]),.A(smpl_edge_sel[0]));	
@@	@Bd smpl_edge_sel_buf_1 (.Y(smpl_edge_sel_out[1]),.A(smpl_edge_sel[1]));	
@@	@BD smpl_edge_sel_buf_2 (.Y(smpl_edge_sel_out[2]),.A(smpl_edge_sel[2]));	
@@	@bd smpl_edge_sel_buf_3 (.Y(smpl_edge_sel_out[3]),.A(smpl_edge_sel[3]));	
@@	@bD smpl_edge_sel_buf_4 (.Y(smpl_edge_sel_out[4]),.A(smpl_edge_sel[4]));	
		
@@	@Db pre_dltdc_in_ref_buf (.Y(pre_dltdc_in_ref_out),.A(PH_ref[0]));

	//----------------------------------------------------------
	// Put down DCO_RAW_PH path stages

	generate 
		//genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<DCO_NUM_PH ; i=i+1)
		begin:u_pre_es_fb_ph
			lpdtc_v2 
				#(	.NSTG		(pre_es_fb_NSTG	),
					.NSTG_CC_TUNE	(pre_es_fb_NSTG_CC_TUNE),
					.NCC_TUNE	(pre_es_fb_NCC_TUNE	),
					.NCC_TUNE_BASE	(pre_es_fb_NCC_TUNE_BASE),
					.NCC_BASE	(pre_es_fb_NCC_BASE	),
					.NCC_OUT	(pre_es_fb_NCC_OUT	),
					.NFC		(pre_es_fb_NFC		),
					.N_STG_FC	(pre_es_fb_NSTG-1-i%2	),
					//.N_STG_FC	(pre_es_fb_NSTG-2	), // 04/15/21:  this didn't work: dtcs up/down connected
					.BASE_3st 	(pre_es_fb_BASE_3st 	),
					.TUNE_BASE_3st	(pre_es_fb_TUNE_BASE_3st),
					.TUNE_TUNE_3st	(pre_es_fb_TUNE_TUNE_3st),
					.OUTBUF_3st	(pre_es_fb_OUTBUF_3st	)) 
			dtc (.dtc_in(DCO_RAW_PH[i]), .dtc_out(pre_es_fb_PH[i]), .CC(pre_es_fb_CC[i]), .FC(pre_es_fb_FC[i]));	
		end
	endgenerate

//---------------------------------------------------
// code for synth - 1: n/p path sel
	generate 
		//genvar i,j,k,f; 
		for (i=0; i<DCO_NUM_PH; i=i+1)
		begin: phase_sel 
			dco_CC_se CC ( .IN(pre_es_fb_PH[i]), .OUT(post_es_fb), .EN(smpl_edge_sel[i]));
		end 
	endgenerate

	assign edge_sel_off = ~(smpl_edge_sel[1]|smpl_edge_sel[2]|smpl_edge_sel[3]|smpl_edge_sel[4]|smpl_edge_sel[0]); 

	dco_CC_se post_ls_tie_hi ( .IN(1'b0), .OUT(post_es_fb), .EN(edge_sel_off));


	// n/p path delay
	lpdtc_v2 
		#(	.NSTG		(post_es_fb_NSTG	),
			.NSTG_CC_TUNE	(post_es_fb_NSTG_CC_TUNE), 
			.NCC_TUNE	(post_es_fb_NCC_TUNE	),
			.NCC_TUNE_BASE	(post_es_fb_NCC_TUNE_BASE), 
			.NCC_BASE	(post_es_fb_NCC_BASE	),  
			.NCC_OUT	(post_es_fb_NCC_OUT	), 
			.NFC		(post_es_fb_NFC		),
			.N_STG_FC	(post_es_fb_NSTG-1	),
			.BASE_3st 	(post_es_fb_BASE_3st 	),
			.TUNE_BASE_3st	(post_es_fb_TUNE_BASE_3st),
			.TUNE_TUNE_3st	(post_es_fb_TUNE_TUNE_3st),
			.OUTBUF_3st	(post_es_fb_OUTBUF_3st	))
	u_post_es_fb_dtc (.dtc_in(post_es_fb), .dtc_out(pre_final_fb), .CC(post_es_fb_CC), .FC(post_es_fb_FC));	

//-------------------------------------------------------------
// code for synth - 2: final mux
	assign final_fb_pass = edge_sel_off? 0 : 1;
	// final mux
	for (j=0; j<fm_NCC; j=j+1)
		begin: final_mux_fb
			dco_CC_se CC_fb ( .IN(pre_final_fb), .OUT(pre_dltdc_fb), .EN(final_fb_pass));
		end
	// tie-lo	
	dco_CC_se tie_lo_CC_fb ( .IN(1'b1), .OUT(pre_dltdc_fb), .EN(edge_sel_off));

	assign PH_fb[0] = pre_dltdc_fb;
@@	@x2 pre_dltdc_in_fb_buf (.Y(pre_dltdc_in_fb_out),.A(PH_fb[0])); // BUFH X2

	//===============================================================================
	// delay-diff based DLTDC 
	//===============================================================================
	generate 
		//genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<NSTG ; i=i+1)
		begin:stg
			// Driver Cells 
			for (j=0; j<NDRV_fb; j=j+1)
			begin: driv_fb 
		 		dco_CC_se DRV_fb_1 ( .IN(PH_fb[i]), .OUT(PH_fb_tmp[i]), .EN(1'b1)); 
		 		dco_CC_se DRV_fb_2 ( .IN(PH_fb_tmp[i]), .OUT(PH_fb[i+1]), .EN(1'b1)); 
			end
			for (j=0; j<NDRV_ref; j=j+1)
			begin: driv_ref 
		 		dco_CC_se DRV_ref_1 ( .IN(PH_ref[i]), .OUT(PH_ref_tmp[i]), .EN(1'b1));
		 		dco_CC_se DRV_ref_2 ( .IN(PH_ref_tmp[i]), .OUT(PH_ref[i+1]), .EN(1'b1));
			end 
			//Coarse Cells
			for (j=0; j<NCC_fb; j=j+1)
			begin: cctrl_fb 
		 		dco_CC_se CC_fb_1 ( .IN(PH_fb[i]), .OUT(PH_fb_tmp[i]), .EN(CC_fb[i+j*NSTG])); 
		 		dco_CC_se CC_fb_2 ( .IN(PH_fb_tmp[i]), .OUT(PH_fb[i+1]), .EN(CC_fb[i+j*NSTG])); 
			end
			for (j=0; j<NCC_ref; j=j+1)
			begin: cctrl_ref 
		 		dco_CC_se CC_ref_1 ( .IN(PH_ref[i]), .OUT(PH_ref_tmp[i]), .EN(CC_ref[i+j*NSTG]));
		 		dco_CC_se CC_ref_2 ( .IN(PH_ref_tmp[i]), .OUT(PH_ref[i+1]), .EN(CC_ref[i+j*NSTG]));
			end 
			//Fine Cells
			for (k=0; k<NFC_fb; k=k+1)
			begin: fctrl_fb 
		 		dco_FC_se2 fineCell_fb ( .IN(PH_fb[i]), .EN(FC_fb[i+k*NSTG])); // 050821 
		 		//dco_FC_se2_pnc fineCell_fb ( .IN(PH_fb[i]), .EN(FC_fb[i+k*NSTG])); 
			end
			for (j=0; j<NFC_ref; j=j+1)
			begin: fctrl_ref 
		 		dco_FC_se2 fineCell_ref ( .IN(PH_ref[i]), .EN(FC_ref[i+j*NSTG])); // 050821
		 		//dco_FC_se2_pnc fineCell_ref ( .IN(PH_ref[i]), .EN(FC_ref[i+j*NSTG]));
			end 
			//output buffer
@@				@fq tdc_dff(.Q(tdc_out[i]), .CK(PH_ref[i]), .D(PH_fb[i])); // DFFQ
		end
	endgenerate

endmodule 

  
