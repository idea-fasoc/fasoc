//`timescale 1ns/1ps
//`include "dco_FC.v"
//`include "dco_CC.v"
module dco_8stg (PH_N_out, PH_P_out, CC, FC, osc_en, clk); 
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
	input		clk;  //dummy clk for synthesis	


	// Put down stages
	generate 
		genvar i,j,k; 
		//Loop across first N-1 Stages
		for (i=0; i<NSTG-1 ; i=i+1)
		begin:stg 
			//Drivers
			//dco_CC buff_driva  ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_N[i+1]), .op(PH_P[i+1]),  .en(1'b1)); 
			//dco_CC buff_drivb  ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_N[i+1]), .op(PH_P[i+1]),  .en(1'b1)); 
			//dco_CC buff_drivc  ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_N[i+1]), .op(PH_P[i+1]),  .en(1'b1)); 
			//dco_CC buff_drivd  ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_N[i+1]), .op(PH_P[i+1]),  .en(1'b1)); 
			for (j=0; j<NDRIV; j=j+1)
			begin: driv 
		 		dco_CC buff_driv ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_N[i+1]), .op(PH_P[i+1]),  .en(1'b1)); 
			end
			//Coarse Cells
			for (j=0; j<NCC; j=j+1)
			begin: cctrl 
		 		dco_CC coarseCell ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_N[i+1]), .op(PH_P[i+1]),  .en(CC[i+j*NSTG])); 
			end
			//Fine Cells
			for (k=0; k<NFC; k=k+1)
			begin: fctrl 
		 		dco_FC fineCell ( .in(PH_N[i]), .ip(PH_P[i]) ,  .en(FC[i+k*NSTG])); 
			end
			//Output Buffers
			synth_pll_dco_outbuff outbuffCell  ( .in(PH_N[i]), .ip(PH_P[i]) , .on(PH_P_out[2*i]), .op(PH_N_out[2*i])); 
			//Interpolators
			synth_pll_dco_interp interpCell  ( .inA(PH_N[i]), .inB(PH_N[i+1]), .ipA(PH_P[i]), .ipB(PH_P[i+1]) ,  .on(PH_P_out[1+2*i]), .op(PH_N_out[1+2*i])); 
		end

		//Last Stage Cells
		
		//Drivers
		//dco_CC stg_last__buff_driva  ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P[0]), .op(PH_N[0]),  .en(osc_en)); 
		//dco_CC stg_last__buff_drivb  ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P[0]), .op(PH_N[0]),  .en(osc_en)); 
		//dco_CC stg_last__buff_drivc  ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P[0]), .op(PH_N[0]),  .en(osc_en)); 
		//dco_CC stg_last__buff_drivd  ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P[0]), .op(PH_N[0]),  .en(osc_en)); 
		for (j=0; j<NDRIV; j=j+1)
		begin: stg_last__driv 
			dco_CC buff_driv ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P[0]), .op(PH_N[0]),  .en(osc_en)); 
		end
		//Driver for osc disable
		dco_CC stg_last__buff_driv_disable  ( .in(1'b1), .ip(1'b0) , .on(PH_P[0]), .op(PH_N[0]),  .en(!osc_en)); 

		//Coarse Cells
		for (j=0; j<NCC; j=j+1)
		begin: stg_last__cctrl 
			dco_CC coarseCell  ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P[0]), .op(PH_N[0]), .en(CC[NSTG-1+j*NSTG])); 
		end
		//Fine Cells
		for (k=0; k<NFC; k=k+1)
		begin: stg_last__fctrl 
	 		dco_FC fineCell ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) ,  .en(FC[NSTG-1+k*NSTG])); 
		end
		//Output Buffers
		synth_pll_dco_outbuff stg_last__outbuffCell  ( .in(PH_N[NSTG-1]), .ip(PH_P[NSTG-1]) , .on(PH_P_out[2*(NSTG-1)]), .op(PH_N_out[2*(NSTG-1)])); 
		//Interpolators
		synth_pll_dco_interp stg_last__interpCell  (  .inA(PH_N[NSTG-1]), .inB(PH_P[0]), .ipA(PH_P[NSTG-1]), .ipB(PH_N[0]), 
											.op(PH_P_out[1+2*(NSTG-1)]), .on(PH_N_out[1+2*(NSTG-1)])); 
	endgenerate 
endmodule 

  
