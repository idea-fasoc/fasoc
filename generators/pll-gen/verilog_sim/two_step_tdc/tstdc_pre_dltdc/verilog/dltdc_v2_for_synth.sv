// delay difference-based DLTDC model
`timescale 1ps/1ps

module dltdc_v2	(	tdc_out,
			DCO_RAW_PH,
			pre_CC_fb,
			pre_CC_ref,
			npath_CC_fb,
			ppath_CC_fb,
			CC_fb,
			FC_fb,
			CC_ref,
			FC_ref,
			CLK_REF,
			RST,
			smpl_edge_sel,
			clk,
			dum_in,
			dum_out);
	// pre-dltdc 
	parameter pre_NDRV_fb = 1;
	parameter pre_NDRV_ref = 2;
	parameter pre_NCC_fb = 4;
	parameter pre_NCC_ref = 2;
	
	parameter npath_NDRV = 4;
	parameter ppath_NDRV = 2;
	
	parameter npath_NCC = 4;
	parameter ppath_NCC = 6;

	// dltdc delay line	
	parameter NSTG = 10; 
	parameter NFC_fb = 6;
	parameter NFC_ref = 6;
	parameter NDRV_fb = 1;
	parameter NDRV_ref = 2;
	parameter NCC_fb = 4;
	parameter NCC_ref = 2;
	parameter DCO_NUM_PH = 5;

	// DFF char 
	parameter dff_su_time = 20e-12;

	// pre-dltdc delay lines
	parameter pre_ref_delay = 17e-12;
	parameter pre_NSTG_ref_ls = 1; // latch edge sel @ 17*4 = 68ps 
	parameter pre_NSTG_ref = 10; // dltdc ref in @ 17*6 = 102ps

	parameter pre_fb_delay = 17e-12;
	parameter pre_NSTG_fb = 4; // edge arrives @ 17*1 = 17ps

	parameter npath_delay = 22.7e-12;   
	parameter npath_NSTG = 3; // npath Tdly=(npath_NSTG)*delay
	//parameter npath_NSTG = 3; // npath Tdly=(npath_NSTG)*delay

	parameter ppath_delay = 17e-12;   
	parameter ppath_NSTG = 4; // ppath (ppath_NSTG)*delay
	//parameter ppath_NSTG = 4; // ppath (ppath_NSTG)*delay
	 
	parameter fmux_delay = 17e-12; 

	// dltdc delay lines
	parameter dltdc_fb_delay = 26e-12;
	parameter dltdc_ref_delay = 17e-12; 
	
	real TIME_SCALE=1e-12;

	input 				CLK_REF;
	input 				RST;
	
	input	[DCO_NUM_PH-1:0]		DCO_RAW_PH;

	input 	[pre_NCC_fb*pre_NSTG_fb-1:0] 		pre_CC_fb; 
	input 	[pre_NCC_ref*pre_NSTG_ref-1:0] 		pre_CC_ref; 

	input 	[npath_NCC*(npath_NSTG-1)-1:0] 		npath_CC_fb; 
	input 	[ppath_NCC*(ppath_NSTG-1)-1:0] 		ppath_CC_fb; 


	input 	[NFC_fb*NSTG-1:0] 		FC_fb; 
	input 	[NCC_fb*NSTG-1:0] 		CC_fb; 
	input 	[NFC_ref*NSTG-1:0] 		FC_ref; 
	input 	[NCC_ref*NSTG-1:0] 		CC_ref; 
	output  [NSTG-1:0]			tdc_out;
	output	[DCO_NUM_PH-1:0]		smpl_edge_sel; // timing check-point 1
	output	[DCO_NUM_PH-1:0]		pre_PH_fb_out; // test purpose 
	output					pre_dltdc_in_fb; // test purpose

	logic 	[DCO_NUM_PH-1:0] [pre_NSTG_fb:0]	pre_PH_fb;
	logic 	[pre_NSTG_ref:0] 		pre_clk_ref;
	logic 	[NSTG:0] 		PH_fb;
	logic 	[NSTG:0] 		PH_fb_tmp;
	logic 	[NSTG:0] 		PH_ref;
	logic 	[NSTG:0] 		PH_ref_tmp;
	logic	[DCO_NUM_PH-1:0]		edge_sel;
	logic	[DCO_NUM_PH-1:0]		embtdc_out;
	logic	[npath_NSTG:0]		npath_fb;
	logic	[ppath_NSTG:0]		ppath_fb;
	logic					np_edge;
	logic					np_edge_off;
	logic				npath_fb_tmp;
	logic				ppath_fb_tmp;
//	logic	[DCO_NUM_PH-1:0]		smpl_edge_sel; // test purpose
//	logic				pre_dltdc_in_fb; // test purpose
	// timing check points
	logic	[DCO_NUM_PH-1:0]	check_pnt_2;
	logic	[1:0]			check_pnt_3;

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

	//===============================================================================
	// pre-DLTDC 
	//===============================================================================

	// Selection pins
	generate 
		genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<DCO_NUM_PH ; i=i+1)
		begin:stg
			DFFQ_X1N_A10P5PP84TR_C14 #(.su_time(dff_su_time)) embtdc_dff (.Q(embtdc_out[i]), .CK(CLK_REF), .D(DCO_RAW_PH[i]));
			if (i<DCO_NUM_PH-1) begin
				assign	edge_sel[i] = ~(embtdc_out[i]^embtdc_out[i+1]);
			end else if (i==DCO_NUM_PH-1) begin
				assign  edge_sel[i] = ~(embtdc_out[i]^embtdc_out[0]);
			end
		// latch edge_sel
		//	DFFQ_X1N_A10P5PP84TR_C14 edge_sel_dff(.Q(smpl_edge_sel[i]), .CK(pre_clk_ref[pre_NSTG_ref-1]), .D(edge_sel[i]));
		end
	endgenerate

	// latch edge_sel: this needs to be fast. check what synthesis uses here
	always @(negedge pre_clk_ref[pre_NSTG_ref_ls] or negedge CLK_REF) begin
		if (~CLK_REF) begin
			smpl_edge_sel <= 0;
		end else begin 
			smpl_edge_sel <= edge_sel;
		end
	end

	// np_edge (logical)
	always @* begin		
		case (edge_sel)
			5'b00001: begin	np_edge = embtdc_out[0]; end	
			5'b00010: begin	np_edge = embtdc_out[1]; end	
			5'b00100: begin	np_edge = embtdc_out[2]; end	
			5'b01000: begin	np_edge = embtdc_out[3]; end	
			5'b10000: begin	np_edge = embtdc_out[4]; end
			default: begin np_edge = 1; end
		endcase
	end	

	// Put down CLKREF path stages
	generate 
		//genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<pre_NSTG_ref ; i=i+1)
		begin:pre_stg_ref
			// Driver Cells 
			for (j=0; j<pre_NDRV_ref; j=j+1)
			begin: driv_ref 
		 	      dco_CC_se DRV_ref ( .IN(pre_clk_ref[i]), .OUT(pre_clk_ref[i+1]), .EN(1'b1));
			end 
			//Coarse Cells
			for (j=0; j<pre_NCC_ref; j=j+1)
			begin: cctrl_ref 
		 		dco_CC_se CC_ref ( .IN(pre_clk_ref[i]), .OUT(pre_clk_ref[i+1]), .EN(pre_CC_ref[i+j*pre_NSTG_ref]));
			end 
		end
	endgenerate
	assign pre_clk_ref[0]=CLK_REF;
	assign PH_ref[0] = pre_clk_ref[pre_NSTG_ref]; // clkref input to dltdc
	assign pre_PH_fb[0][0] = DCO_RAW_PH[0];
	assign pre_PH_fb[1][0] = DCO_RAW_PH[1];
	assign pre_PH_fb[2][0] = DCO_RAW_PH[2];
	assign pre_PH_fb[3][0] = DCO_RAW_PH[3];
	assign pre_PH_fb[4][0] = DCO_RAW_PH[4];
	//----------------------------------------------------------
	// test purpose
	assign pre_PH_fb_out[0] = pre_PH_fb[0][pre_NSTG_fb];
	assign pre_PH_fb_out[1] = pre_PH_fb[1][pre_NSTG_fb];
	assign pre_PH_fb_out[2] = pre_PH_fb[2][pre_NSTG_fb];
	assign pre_PH_fb_out[3] = pre_PH_fb[3][pre_NSTG_fb];
	assign pre_PH_fb_out[4] = pre_PH_fb[4][pre_NSTG_fb];
	//----------------------------------------------------------

	// Put down DCO_RAW_PH path stages
	generate 
		//genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<pre_NSTG_fb ; i=i+1)
		begin:pre_stg_fb
			// Driver Cells 
			for (j=0; j<pre_NDRV_fb-1; j=j+1)
			begin: driv_fb 
				for (k=0; k<DCO_NUM_PH-1; k=k+1)
				begin: ph 
		 	      		dco_CC_se #(.CC_delay(pre_fb_delay)) DRV_fb ( .IN(pre_PH_fb[k][i]), .OUT(pre_PH_fb[k][i+1]), .EN(1'b1));
				end 
			end
			//Coarse Cells
			for (j=0; j<pre_NCC_fb; j=j+1)
			begin: cctrl_fb 
				for (k=0; k<DCO_NUM_PH-1; k=k+1)
				begin: ph 
		 			dco_CC_se #(.CC_delay(pre_fb_delay)) CC_fb ( .IN(pre_PH_fb[k][i]), .OUT(pre_PH_fb[k][i+1]), .EN(pre_CC_fb[i+j*pre_NSTG_fb]));
				end 
			end
		end
	endgenerate

	// n/p path beginning
//---------------------------------------------------
// code for sim - 1: n/p path sel 
//	always @* begin
//		if (np_edge_off) begin
//			npath_fb[0] = 1'b1;
//			ppath_fb[0] = 1'b0;
//			//npath_fb[0] = 1'b0;
//			//ppath_fb[0] = 1'b1;
//		end else begin
//			case(smpl_edge_sel)
//				5'b00001: begin npath_fb_tmp = pre_PH_fb[0][pre_NSTG_fb]; ppath_fb_tmp = pre_PH_fb[0][pre_NSTG_fb]; end
//				5'b00010: begin npath_fb_tmp = pre_PH_fb[1][pre_NSTG_fb]; ppath_fb_tmp = pre_PH_fb[1][pre_NSTG_fb]; end
//				5'b00100: begin npath_fb_tmp = pre_PH_fb[2][pre_NSTG_fb]; ppath_fb_tmp = pre_PH_fb[2][pre_NSTG_fb]; end
//				5'b01000: begin npath_fb_tmp = pre_PH_fb[3][pre_NSTG_fb]; ppath_fb_tmp = pre_PH_fb[3][pre_NSTG_fb]; end
//				5'b10000: begin npath_fb_tmp = pre_PH_fb[4][pre_NSTG_fb]; ppath_fb_tmp = pre_PH_fb[4][pre_NSTG_fb]; end
//			endcase
//		end
//	end
//
//	always @(posedge npath_fb_tmp or negedge npath_fb_tmp) begin
//		npath_fb[0] <= npath_fb_tmp;
//	end
//		 
//	always @(posedge ppath_fb_tmp or negedge ppath_fb_tmp) begin
//		ppath_fb[0] <= ppath_fb_tmp;
//	end
//---------------------------------------------------
// code for synth - 1: n/p path sel
	generate 
		//genvar i,j,k,f; 
		for (i=0; i<DCO_NUM_PH; i=i+1)
		begin: npsel_begin
			for (k=0; k<npath_NCC; k=k+1)
			begin: npath_sel 
				dco_CC_se CC ( .IN(pre_PH_fb[i][pre_NSTG_fb]), .OUT(npath_fb[0]), .EN(smpl_edge_sel[i]));
			end 
			for (k=0; k<ppath_NCC; k=k+1)
			begin: ppath_sel 
				dco_CC_se CC ( .IN(pre_PH_fb[i][pre_NSTG_fb]), .OUT(ppath_fb[0]), .EN(smpl_edge_sel[i]));
			end
		end 
	endgenerate

	assign np_edge_off = ~(smpl_edge_sel[1]|smpl_edge_sel[2]|smpl_edge_sel[3]|smpl_edge_sel[4]|smpl_edge_sel[0]); 

	dco_CC_se npath_tie_hi ( .IN(1'b1), .OUT(npath_fb[0]), .EN(np_edge_off));
	dco_CC_se ppath_tie_lo ( .IN(1'b0), .OUT(ppath_fb[0]), .EN(np_edge_off));
	
	// n/p path delay
	generate 
		//genvar i,j,k,f; 
		for (i=0; i<npath_NSTG-2 ; i=i+1)
		begin: npath_dl
			// Driver Cells 
			for (j=0; j<npath_NDRV; j=j+1)
			begin: driv 
		 		dco_CC_se DRV_fb ( .IN(npath_fb[i]), .OUT(npath_fb[i+1]), .EN(1'b1));
			end 
			//Coarse Cells
			for (j=0; j<npath_NCC; j=j+1)
			begin: cctrl 
		 		dco_CC_se CC_fb ( .IN(npath_fb[i]), .OUT(npath_fb[i+1]), .EN(npath_CC_fb[i+j*(npath_NSTG-1)]));
			end 
		end
	endgenerate

	generate 
		//genvar i,j,k,f; 
		for (i=0; i<ppath_NSTG-2 ; i=i+1)
		begin: ppath_dl
			// Driver Cells 
			for (j=0; j<ppath_NDRV; j=j+1)
			begin: driv 
		 		dco_CC_se DRV_fb ( .IN(ppath_fb[i]), .OUT(ppath_fb[i+1]), .EN(1'b1));
			end 
			//Coarse Cells
			for (j=0; j<ppath_NCC; j=j+1)
			begin: cctrl 
		 		dco_CC_se CC_fb ( .IN(ppath_fb[i]), .OUT(ppath_fb[i+1]), .EN(ppath_CC_fb[i+j*(ppath_NSTG-1)]));
			end 
		end
	endgenerate

//-------------------------------------------------------------
// code for sim - 2: final mux
//
//	//always @(posedge ppath_fb[ppath_NSTG-2] or negedge ppath_fb[ppath_NSTG-2] or posedge np_edge_off or posedge npath_fb[npath_NSTG-2] or negedge npath_fb[npath_NSTG-2] ) begin
//	always @(posedge ppath_fb[ppath_NSTG-2] or posedge np_edge_off or posedge npath_fb[npath_NSTG-2]) begin
//		if (np_edge && (~np_edge_off)) begin
//			pre_dltdc_in_fb <= #(ppath_delay/TIME_SCALE) ~ppath_fb[ppath_NSTG-2];
//		end else if ((~np_edge) && (~np_edge_off)) begin 
//			pre_dltdc_in_fb <= #(npath_delay/TIME_SCALE) ~npath_fb[npath_NSTG-2];
//		end else if (np_edge_off) begin
//			pre_dltdc_in_fb <= #(fmux_delay/TIME_SCALE) 1;
//		end
//	end
//	always @(posedge pre_dltdc_in_fb or negedge pre_dltdc_in_fb) begin
//		PH_fb[0] <= #(2*fmux_delay/TIME_SCALE) ~pre_dltdc_in_fb;
//	end

//-------------------------------------------------------------
// code for synth - 2: final mux
	// final mux
	// ppath
	for (j=0; j<ppath_NCC; j=j+1)
	begin: ppath_final
		dco_CC_se CC_fb ( .IN(ppath_fb[ppath_NSTG-1]), .OUT(pre_dltdc_in_fb), .EN(np_edge));
	end
	// npath 
	for (j=0; j<npath_NCC; j=j+1)
	begin: npath_final 
		dco_CC_se CC_fb ( .IN(npath_fb[npath_NSTG-1]), .OUT(pre_dltdc_in_fb), .EN(~np_edge));
	end 
	// tie-lo	
	dco_CC_se tie_lo_CC_fb ( .IN(1'b1), .OUT(pre_dltdc_in_fb), .EN(~np_edge_off));

	dco_CC_se buf_pre_dltdc1 ( .IN(pre_dltdc_in_fb), .OUT(PH_fb[0]), .EN(1'b1));
	dco_CC_se buf_pre_dltdc2 ( .IN(pre_dltdc_in_fb), .OUT(PH_fb[0]), .EN(1'b1));
	dco_CC_se buf_pre_dltdc3 ( .IN(pre_dltdc_in_fb), .OUT(PH_fb[0]), .EN(1'b1));
	//===============================================================================
	// diff-based DLTDC 
	//===============================================================================

	// Put down clk_fb path stages
	generate 
		//genvar i,j,k,f; 
		//Loop across first N-1 Stages
		for (i=0; i<NSTG ; i=i+1)
		begin:stg_dltdc
			// Driver Cells 
			for (j=0; j<NDRV_fb; j=j+1)
			begin: driv_fb 
		 		dco_CC_se #(.CC_delay(dltdc_fb_delay))  DRV_fb_1 ( .IN(PH_fb[i]), .OUT(PH_fb_tmp[i]), .EN(1'b1)); 
		 		dco_CC_se #(.CC_delay(dltdc_fb_delay))  DRV_fb_2 ( .IN(PH_fb_tmp[i]), .OUT(PH_fb[i+1]), .EN(1'b1)); 
			end
			for (j=0; j<NDRV_ref; j=j+1)
			begin: driv_ref 
		 		dco_CC_se #(.CC_delay(dltdc_ref_delay))  DRV_ref_1 ( .IN(PH_ref[i]), .OUT(PH_ref_tmp[i]), .EN(1'b1));
		 		dco_CC_se #(.CC_delay(dltdc_ref_delay))  DRV_ref_2 ( .IN(PH_ref_tmp[i]), .OUT(PH_ref[i+1]), .EN(1'b1));
			end 
			//Coarse Cells
			for (j=0; j<NCC_fb; j=j+1)
			begin: cctrl_fb 
		 		dco_CC_se #(.CC_delay(dltdc_fb_delay))  CC_fb_1 ( .IN(PH_fb[i]), .OUT(PH_fb_tmp[i]), .EN(CC_fb[i+j*NSTG])); 
		 		dco_CC_se #(.CC_delay(dltdc_fb_delay))  CC_fb_2 ( .IN(PH_fb_tmp[i]), .OUT(PH_fb[i+1]), .EN(CC_fb[i+j*NSTG])); 
			end
			for (j=0; j<NCC_ref; j=j+1)
			begin: cctrl_ref 
		 		dco_CC_se #(.CC_delay(dltdc_ref_delay))  CC_ref_1 ( .IN(PH_ref[i]), .OUT(PH_ref_tmp[i]), .EN(CC_ref[i+j*NSTG]));
		 		dco_CC_se #(.CC_delay(dltdc_ref_delay))  CC_ref_2 ( .IN(PH_ref_tmp[i]), .OUT(PH_ref[i+1]), .EN(CC_ref[i+j*NSTG]));
			end 
			//Fine Cells
			for (k=0; k<NFC_fb; k=k+1)
			begin: fctrl_fb 
		 		dco_FC_se2 FC_fb ( .IN(PH_fb[i]), .EN(FC_fb[i+k*NSTG])); 
			end
			for (k=0; k<NFC_ref; k=k+1)
			begin: fctrl_ref 
		 		dco_FC_se2 FC_ref ( .IN(PH_ref[i]), .EN(FC_ref[i+k*NSTG]));
			end 
			//output buffer
			DFFQ_X1N_A10P5PP84TR_C14 #(.su_time(dff_su_time)) tdc_dff(.Q(tdc_out[i]), .CK(PH_ref[i]), .D(PH_fb[i]));
		end
	endgenerate

endmodule 

  
