
@@ module @iN(PH_out, CC, FC, FCB, osc_en,clk, dum_in, dum_out, CLK_OUT); 
@@ parameter NSTG = @nM; 
@@ parameter NDRIV = @nD;
@@ parameter NCC = @nC;
@@ parameter NFC = @nF;
@@ parameter NDCC = @ND; // 2 per row
//parameter NDECAP = 26; 
	//parameter NCC = 24;
	parameter Nintrp = 2;

	input 	[NFC*NSTG-1:0] 		FC; 
	input 	[NFC*NSTG-1:0] 		FCB; 
	input 	[NCC*NSTG-1:0] 		CC; 
	input 				osc_en; 
	output  [NSTG-1:0]		PH_out;
	wire 	[NSTG-1:0] 		PH;

	wire 		 		clk_out_n0;
	wire 		 		clk_out_n1;
	wire 		 		clk_out_n2;
	wire 		 		clk_out_n3;
	wire 		 		clk_out_n4;

	output 				CLK_OUT; // set as power	

	wire [2*Nintrp*NSTG-1:0] 	temp_clk_out;
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
			for (j=0; j<NDCC; j=j+1)
			begin: dead 
@@	 			@cN buff_driv ( .IN(PH[i]), .OUT(PH[i+1]), .EN(1'b0)); 
			end
			for (j=0; j<NDRIV; j=j+1)
			begin: driv 
@@	 			@Cn	 buff_driv ( .IN(PH[i]), .OUT(PH[i+1]), .EN(1'b1)); 
			end
			//Coarse Cells
			for (j=0; j<NCC; j=j+1)
			begin: cctrl 
@@				@CN	 coarseCell ( .IN(PH[i]), .OUT(PH[i+1]), .EN(CC[i+j*NSTG])); 
			end
			//Fine Cells
			for (k=0; k<NFC; k=k+1)
			begin: fctrl 
@@	 			@fN fineCell ( .IN(PH[i]), .EN(FC[i+k*NSTG]), .ENB(FCB[i+k*NSTG])); 
			end
			//output buffer
@@			@b1 Pout0_buf (.Y(PH_out[i]),.A(PH[i]));
		//BUFH_X8N_A10P5PP84TR_C14 Pout0_buf (.Y(PH_out[i]),.A(PH[i]));
		end

		//Last Stage Cells
		//off-Drivers
		for (j=0; j<NDCC; j=j+1)
		begin: stg_last__dead 
@@			@dn buff_driv ( .IN(PH[NSTG-1]), .OUT(PH[0]), .EN(1'b0)); 
		end
		//Drivers
		for (j=0; j<NDRIV; j=j+1)
		begin: stg_last__driv 
@@			@Dn buff_driv ( .IN(PH[NSTG-1]), .OUT(PH[0]), .EN(osc_en)); 
		end
		//Driver for osc disable
@@			@dN stg_last__buff_driv_disable  ( .IN(1'b1), .OUT(PH[0]), .EN(!osc_en)); 

		//Coarse Cells
		for (j=0; j<NCC; j=j+1)
		begin: stg_last__cctrl 
@@			@DN coarseCell  ( .IN(PH[NSTG-1]), .OUT(PH[0]), .EN(CC[NSTG-1+j*NSTG])); 
		end
		//Fine Cells
		for (k=0; k<NFC; k=k+1)
		begin: stg_last__fctrl 
@@ 			@FN fineCell ( .IN(PH[NSTG-1]), .EN(FC[NSTG-1+k*NSTG]), .ENB(FCB[NSTG-1+k*NSTG])); 
		end
	endgenerate

	//last stage output buffers
	//BUFH_X8N_A10P5PP84TR_C14 stg_last__Pout0_buf (.Y(PH_out[NSTG-1]),.A(PH[NSTG-1]));
@@		@b2 stg_last__Pout0_buf (.Y(PH_out[NSTG-1]),.A(PH[NSTG-1]));
	// clk_out buf
@@		@b3 clkout_buf0 (.Y(clk_out_n0), .A(PH_out[0]));
@@		@b4 clkout_buf1 (.Y(clk_out_n1), .A(clk_out_n0));
@@		@b5 clkout_buf2 (.Y(CLK_OUT), .A(clk_out_n1));

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

  
