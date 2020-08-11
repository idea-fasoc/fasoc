//`timescale 1ns/1ps
//`include "dco_FC.v"
//`include "dco_CC.v"
module dco_8stg (PH_N_out, PH_P_out, CC, FC, osc_en, clk, dum_in, dum_out); 
	 parameter NSTG = 8; 
	 parameter NDRIV = 8;
	 parameter NFC = 8;
	 parameter NCC = 16;
	 parameter Nintrp = 2;


	 input 	[NFC*NSTG-1:0] 		FC; 
	 input 	[NCC*NSTG-1:0] 		CC; 
	 input 						osc_en; 
	 output [Nintrp*NSTG-1:0]	PH_N_out, PH_P_out;
	 wire 	[NSTG-1:0] 			PH_N, PH_P;
	 //output 	[NSTG-1:0] 			PH_N, PH_P;  //testing for functionality

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
		genvar i,j,k; 
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
			synth_pll_dco_outbuff outbuffCell  ( .IN(PH_N[i]), .IP(PH_P[i]) , .ON(PH_P_out[2*i]), .OP(PH_N_out[2*i])); 
			//Interpolators
			synth_pll_dco_interp interpCell  ( .INA(PH_N[i]), .INB(PH_N[i+1]), .IPA(PH_P[i]), .IPB(PH_P[i+1]) ,  .ON(PH_P_out[1+2*i]), .OP(PH_N_out[1+2*i])); 
		end

		//Last Stage Cells
		
		//Drivers
		//dco_CC stg_last__buff_driva  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P[0]), .OP(PH_N[0]),  .EN(osc_en)); 
		//dco_CC stg_last__buff_drivb  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P[0]), .OP(PH_N[0]),  .EN(osc_en)); 
		//dco_CC stg_last__buff_drivc  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P[0]), .OP(PH_N[0]),  .EN(osc_en)); 
		//dco_CC stg_last__buff_drivd  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P[0]), .OP(PH_N[0]),  .EN(osc_en)); 
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
		synth_pll_dco_outbuff stg_last__outbuffCell  ( .IN(PH_N[NSTG-1]), .IP(PH_P[NSTG-1]) , .ON(PH_P_out[2*(NSTG-1)]), .OP(PH_N_out[2*(NSTG-1)])); 
		//Interpolators
		synth_pll_dco_interp stg_last__interpCell  (  .INA(PH_N[NSTG-1]), .INB(PH_P[0]), .IPA(PH_P[NSTG-1]), .IPB(PH_N[0]), 
											.OP(PH_P_out[1+2*(NSTG-1)]), .ON(PH_N_out[1+2*(NSTG-1)])); 
	endgenerate 
endmodule 

  
