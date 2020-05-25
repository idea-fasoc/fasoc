// without PEDGE/NEDGE
@@ module @iN(PH_N_out, PH_P_out, CC, FC, osc_en, EDGE_SEL, CLK_OUT, clk, dum_in, dum_out); 
@@	parameter NSTG = @nM; 
@@	parameter NDRIV = @nD;
@@	parameter NFC = @nF;
@@	parameter NCC = @nC;
	//parameter NCC = 24;
	parameter Nintrp = 2;


	input 	[NFC*NSTG-1:0] 		FC; 
	input 	[NCC*NSTG-1:0] 		CC; 
	input 				osc_en; 
	output [Nintrp*NSTG-1:0]	PH_N_out, PH_P_out;
	wire [Nintrp*NSTG-1:0]	int_PH_N_out, int_PH_P_out;
	wire 	[NSTG-1:0] 		PH_N, PH_P;

	input [2*Nintrp*NSTG-1:0] 	EDGE_SEL;
	output 				CLK_OUT;	

	wire [2*Nintrp*NSTG-1:0] 	temp_clk_out;
	wire				p_clk_out;
	wire				n_clk_out;
	wire				pre_clk_out;

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
			for (j=0; j<NDRIV; j=j+1)
			begin: driv 
		 		dco_CC buff_driv ( .IN(PH_N[i]), .IP(PH_P[i]) , .ON(PH_N[i+1]), .OP(PH_P[i+1]),  .EN(1'b1)); 
			end
			//Coarse Cells
			for (j=0; j<NCC; j=j+1)
			begin: cctrl 
		 		dco_CC coarseCell ( .IN(PH_N[i]), .IP(PH_P[i]) , .ON(PH_N[i+1]), .OP(PH_P[i+1]),  .EN(CC[i+j*NSTG])); 
			end
			//Fine Cells
			for (k=0; k<NFC; k=k+1)
			begin: fctrl 
		 		dco_FC fineCell ( .IN(PH_N[i]), .IP(PH_P[i]) ,  .EN(FC[i+k*NSTG])); 
			end
			//Output Buffers
			synth_pll_dco_outbuff outbuffCell  ( .IN(PH_N[i]), .IP(PH_P[i]) , .ON(int_PH_P_out[2*i]), .OP(int_PH_N_out[2*i])); 
			//Interpolators
			synth_pll_dco_interp interpCell  ( .INA(PH_N[i]), .INB(PH_N[i+1]), .IPA(PH_P[i]), .IPB(PH_P[i+1]) ,  .ON(int_PH_P_out[1+2*i]), .OP(int_PH_N_out[1+2*i])); 
			//last output buffer
			BUFH_X2M_A9TR Pout0_buf (.Y(PH_P_out[2*i]),.A(int_PH_P_out[2*i]));
			BUFH_X2M_A9TR Nout0_buf (.Y(PH_N_out[2*i]),.A(int_PH_N_out[2*i]));
			BUFH_X2M_A9TR Pout1_buf (.Y(PH_P_out[1+2*i]),.A(int_PH_P_out[1+2*i]));
			BUFH_X2M_A9TR Nout1_buf (.Y(PH_N_out[1+2*i]),.A(int_PH_N_out[1+2*i]));
		end

		//Last Stage Cells
		
		//Drivers
		for (j=0; j<NDRIV; j=j+1)
		begin: stg_last__driv 
			dco_CC buff_driv ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P[0]), .OP(PH_N[0]),  .EN(osc_en)); 
		end
		//Driver for osc disable
		dco_CC stg_last__buff_driv_disable  ( .IN(1'b1), .IP(1'b0) , .ON(PH_P[0]), .OP(PH_N[0]),  .EN(!osc_en)); 

		//Coarse Cells
		for (j=0; j<NCC; j=j+1)
		begin: stg_last__cctrl 
			dco_CC coarseCell  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P[0]), .OP(PH_N[0]), .EN(CC[NSTG-1+j*NSTG])); 
		end
		//Fine Cells
		for (k=0; k<NFC; k=k+1)
		begin: stg_last__fctrl 
	 		dco_FC fineCell ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) ,  .EN(FC[NSTG-1+k*NSTG])); 
		end
		//Output Buffers
		synth_pll_dco_outbuff stg_last__outbuffCell  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(int_PH_P_out[2*(NSTG-1)]), .OP(int_PH_N_out[2*(NSTG-1)])); 
		//km: output switched for right TDC functionality: Interpolators
		synth_pll_dco_interp stg_last__interpCell  (  .INA(PH_N[NSTG-1]), .INB(PH_P[0]), .IPA(PH_P[NSTG-1]), .IPB(PH_N[0]), 
											.OP(int_PH_N_out[1+2*(NSTG-1)]), .ON(int_PH_P_out[1+2*(NSTG-1)])); 
											//.OP(PH_P_out[1+2*(NSTG-1)]), .ON(PH_N_out[1+2*(NSTG-1)])); //old 
		//last output buffers
		BUFH_X2M_A9TR last_Pout0_buf (.Y(PH_P_out[2*(NSTG-1)]),.A(int_PH_P_out[2*(NSTG-1)]));
		BUFH_X2M_A9TR last_Nout0_buf (.Y(PH_N_out[2*(NSTG-1)]),.A(int_PH_N_out[2*(NSTG-1)]));
		BUFH_X2M_A9TR last_Pout1_buf (.Y(PH_P_out[1+2*(NSTG-1)]),.A(int_PH_P_out[1+2*(NSTG-1)]));
		BUFH_X2M_A9TR last_Nout1_buf (.Y(PH_N_out[1+2*(NSTG-1)]),.A(int_PH_N_out[1+2*(NSTG-1)]));

		//Edge Selectors
		for (f=0; f<NSTG*Nintrp; f=f+1)
		begin: edge_sel
			BUFZ_X1M_A9TR Pedge_sel_buf (.Y(temp_clk_out[f]),.A(PH_P_out[f]),.OE(EDGE_SEL[f]));
			BUFZ_X4M_A9TR Pedge_sel_buf2 (.Y(pre_clk_out),.A(temp_clk_out[f]),.OE(EDGE_SEL[f]));

			BUFZ_X1M_A9TR Nedge_sel_buf (.Y(temp_clk_out[f+NSTG*Nintrp]),.A(PH_N_out[f]),.OE(EDGE_SEL[f+NSTG*Nintrp]));
			BUFZ_X4M_A9TR Nedge_sel_buf2 (.Y(pre_clk_out),.A(temp_clk_out[f+NSTG*Nintrp]),.OE(EDGE_SEL[f+NSTG*Nintrp]));
		end		
		//1st stage buffer before output: to suppress glitch
		BUFH_X9M_A9TR edge_sel_buf1_1 (.Y(CLK_OUT),.A(pre_clk_out));

	endgenerate 
endmodule 

  
