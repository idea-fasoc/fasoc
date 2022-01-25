
module ble_dco(PH_out, CC, FC, FCB, osc_en,clk, dum_in, dum_out, div_sel, RST); 
@@ parameter NSTG = @nM; 
@@ parameter NDRIV = @nD;
@@ parameter NFC = @nC;
@@ parameter NCC = @nF;
@@ parameter NDCC = @ND; // 2 per row
parameter NDECAP = 26; 
parameter p2_NDECAP = 8; 
// divider
parameter NUM_DIV = 8;  // slowest clock: 2^NUM_DIV
parameter NUM_BUF_STG = 2;
parameter NUM_BUF_START = 2;
parameter NUM_BUF_SEC_DIV_4 = 0.5;
parameter NUM_BUF_LAST = 2;



	input 	[NFC*NSTG-1:0] 		FC; 
	input 	[NFC*NSTG-1:0] 		FCB; 
	input 	[NCC*NSTG-1:0] 		CC; 
	input 				osc_en; 
	input 	[NUM_DIV:0]		div_sel; //one hot
	input				RST;

	output  [NSTG-1:0]		PH_out;
	wire 	[NSTG-1:0] 		PH;

	wire 		 		scpa_n0;
	wire 		 		scpa_n1;
	wire 		 		scpa_n2;
	wire 		 		scpa_n3;
	wire 		 		scpa_n4;
	wire 		 		clk_out_n0;
	wire 		 		clk_out_n1;
	wire 		 		clk_out_n2;
	wire 		 		clk_out_n3;
	wire 		 		clk_out_n4;

	wire	[1:0]		buf_net; // this is an floating output, used for attraction
	wire	[NUM_DIV:0]		buf_net_n; // this is an floating output, used for attraction
	wire	[NUM_DIV:0]		buf_net_n2; // this is an floating output, used for attraction
	wire	[NUM_DIV:0]		DIV_NODE;
	wire	[NUM_DIV:0]		int0DIV_NODE;  //added for hold time
	wire	[NUM_DIV:0]		int1DIV_NODE;  //added for hold time
	wire	[NUM_DIV:0]		nDIV_NODE;

//	output 				CLK_OUT; // set as power	
//	inout				SCPA_CLK; // set as power	


	// dummy clock and registers for synth & apr
	input		clk;  //dummy clk for synthesis	
	input		dum_in;  //dummy input for synthesis	
	reg dum_clk;
	output reg dum_out;
	always@(posedge clk)
		begin
			dum_clk <= ~dum_in;
			dum_out <= dum_in + dum_clk;
		end

	// Put down stages
	generate 
		genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<NSTG-1 ; i=i+1)
		begin:stg 
			for (j=0; j<NDCC; j=j+1)
			begin: dead 
	 		dco_CC_se_3st buff_driv ( .IN(PH[i]), .OUT(PH[i+1]), .EN(1'b0)); 
			end
			for (j=0; j<NDRIV; j=j+1)
			begin: driv 
	 		dco_CC_se_3st	 buff_driv ( .IN(PH[i]), .OUT(PH[i+1]), .EN(1'b1)); 
			end
			//Coarse Cells
			for (j=0; j<NCC; j=j+1)
			begin: cctrl 
			dco_CC_se_3st	 coarseCell ( .IN(PH[i]), .OUT(PH[i+1]), .EN(CC[i+j*NSTG])); 
			end
			//Fine Cells
			for (k=0; k<NFC; k=k+1)
			begin: fctrl 
	 		dco_FC_se2_half fineCell ( .IN(PH[i]), .EN(FC[i+k*NSTG]), .ENB(FCB[i+k*NSTG])); 
			end
			//output buffer
@@		@b8 Pout0_buf (.Y(PH_out[i]),.A(PH[i]));
		end

		//Last Stage Cells
		//off-Drivers
		for (j=0; j<NDCC; j=j+1)
		begin: stg_last__dead 
		dco_CC_se_3st buff_driv ( .IN(PH[NSTG-1]), .OUT(PH[0]), .EN(1'b0)); 
		end
		//Drivers
		for (j=0; j<NDRIV; j=j+1)
		begin: stg_last__driv 
		dco_CC_se_3st buff_driv ( .IN(PH[NSTG-1]), .OUT(PH[0]), .EN(osc_en)); 
		end
		//Driver for osc disable
		dco_CC_se_3st stg_last__buff_driv_disable  ( .IN(1'b1), .OUT(PH[0]), .EN(!osc_en)); 

		//Coarse Cells
		for (j=0; j<NCC; j=j+1)
		begin: stg_last__cctrl 
		dco_CC_se_3st coarseCell  ( .IN(PH[NSTG-1]), .OUT(PH[0]), .EN(CC[NSTG-1+j*NSTG])); 
		end
		//Fine Cells
		for (k=0; k<NFC; k=k+1)
		begin: stg_last__fctrl 
 		dco_FC_se2_half fineCell ( .IN(PH[NSTG-1]), .EN(FC[NSTG-1+k*NSTG]), .ENB(FCB[NSTG-1+k*NSTG])); 
		end
	endgenerate
	//last stage output buffers
@@	@B8 stg_last__Pout0_buf (.Y(PH_out[NSTG-1]),.A(PH[NSTG-1]));


	// clk_out buf
@@	@b2 clkout_buf0 (.Y(clk_out_n0), .A(PH_out[0]));
@@	@b4 clkout_buf1 (.Y(clk_out_n1), .A(clk_out_n0));
@@	@bt clkout_buf2 (.Y(clk_out_n2), .A(clk_out_n1));
	// scpa_clk buf
@@	@B2 scpa_buf0 (.Y(scpa_n0), .A(PH_out[0]));
@@	@B4 scpa_buf1 (.Y(scpa_n1), .A(scpa_n0));
@@	@BT scpa_buf2 (.Y(scpa_n2), .A(scpa_n1));

	//==================================================================================================
	// DIVIDER + buffer use VDD_BUF

	// direct connection without divider 
	dco_CC_se p2_direct_outbuf0 (.OUT(buf_net_n[0]),.IN(clk_out_n2),.EN(div_sel[0]));	
	dco_CC_se p2_direct_outbuf1 (.OUT(buf_net_n[0]),.IN(clk_out_n2),.EN(div_sel[0]));	
	dco_CC_se p2_direct_outbuf2 (.OUT(buf_net_n2[0]),.IN(buf_net_n[0]),.EN(div_sel[0]));	
	dco_CC_se p2_direct_outbuf3 (.OUT(buf_net_n2[0]),.IN(buf_net_n[0]),.EN(div_sel[0]));	
@@	@bT p2_direct_outbuf4 (.Y(clk_out_n3), .A(buf_net_n2[0]));

	assign DIV_NODE[0] = clk_out_n2;
	// always on buffers
	generate
		genvar i,j,k,l,m;
		// Divider
		for (i=0; i<NUM_DIV; i=i+1)
		begin: p2_div_stg
@@			@df dff (.Q(DIV_NODE[i+1]), .CK(DIV_NODE[0]), .D(nDIV_NODE[i]), .R(RST));	
@@			@i6 inv0 (.Y(nDIV_NODE[i]),.A(DIV_NODE[i+1]));  //added for hold time 0p6
			dco_CC_se buff0 (.OUT(buf_net_n[i+1]),.IN(DIV_NODE[0]),.EN(div_sel[i+1]));	
			dco_CC_se buff1 (.OUT(buf_net_n[i+1]),.IN(DIV_NODE[0]),.EN(div_sel[i+1]));	
			dco_CC_se buff2 (.OUT(buf_net_n2[i+1]),.IN(buf_net_n[i+1]),.EN(div_sel[i+1]));	
			dco_CC_se buff3 (.OUT(buf_net_n2[i+1]),.IN(buf_net_n[i+1]),.EN(div_sel[i+1]));	
@@			@Bt buff4 (.Y(clk_out_n3), .A(buf_net_n2[i+1]));
		end
	endgenerate	

	// clkout_buf on the right
@@	@BB p2_clkout_buf3 (.Y(clk_out_n4), .A(clk_out_n3));
@@	@Bb p2_clkout_buf4 (.Y(clk_out_n4), .A(clk_out_n3));
	BUFH_X14N_pwr p2_clkout_buf5 (.A(clk_out_n4));
	BUFH_X14N_pwr p2_clkout_buf6 (.A(clk_out_n4));
	BUFH_X14N_pwr p2_clkout_buf7 (.A(clk_out_n4));
	BUFH_X14N_pwr p2_clkout_buf8 (.A(clk_out_n4));
	BUFH_X14N_pwr p2_clkout_buf9 (.A(clk_out_n4));
	BUFH_X14N_pwr p2_clkout_buf10 (.A(clk_out_n4));

	// scpa_buf on the right
@@	@bf p2_scpa_buf3 (.Y(scpa_n3), .A(scpa_n2));
@@	@bF p2_scpa_buf4 (.Y(scpa_n3), .A(scpa_n2));
@@	@Bf p2_scpa_buf5 (.A(scpa_n3));
@@	@BF p2_scpa_buf6 (.A(scpa_n3));
@@	@bn p2_scpa_buf7 (.A(scpa_n3));
@@	@Bn p2_scpa_buf8 (.A(scpa_n3));

	// decap cells
	generate 
		genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<NDECAP ; i=i+1)
		begin:decap 
		       DCDC_CAP_UNIT unit ( );
		end
	endgenerate

	generate 
		genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<p2_NDECAP ; i=i+1)
		begin:p2_decap 
		       DCDC_CAP_UNIT unit ( );
		end
	endgenerate

endmodule 

  
