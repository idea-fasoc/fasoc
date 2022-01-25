// delay difference-based DLTDC model
`timescale 1ps/1ps

module lpdtc_v2 (	dtc_in,
			dtc_out,
			CC,
			FC
			);

	// design parameters
	parameter NSTG = 6;
	parameter NSTG_CC_TUNE = 2; // # of coarse tunable stages
	parameter NCC_TUNE = 2; // # of tunable CCs of tunable stages 
	parameter NCC_TUNE_BASE = 3; // # of always-on CCs of tunable stages 
	parameter NCC_BASE = 2;  // NCC of every stage except 1. TUNE_CCs, 2. Last stage
	parameter NCC_OUT = 4; // NCC of last stage
	parameter NFC = 63; // number of FC + 1 
	parameter N_STG_FC = 5; // number of FC + 1 

	localparam N_STG_TUNE_START_tmp = NSTG - 1 - (NSTG_CC_TUNE-1); // 4
	localparam N_STG_FC_first = N_STG_FC < N_STG_TUNE_START_tmp; // 0
	localparam N_STG_TUNE_START = N_STG_FC_first? N_STG_TUNE_START_tmp : N_STG_TUNE_START_tmp-1;


	parameter BASE_3st = 1; // number of FC + 1 
	parameter TUNE_BASE_3st = 1; // number of FC + 1 
	parameter TUNE_TUNE_3st = 0; // number of FC + 1 
	parameter OUTBUF_3st = 0; // number of FC + 1 

//	parameter FC_WIDTH = func_clog2(NFC);
	parameter FC_WIDTH = 5;

	input				dtc_in;
	output				dtc_out;
	input	[NCC_TUNE*NSTG_CC_TUNE-1:0]	CC;
	//input	[FC_WIDTH-1:0]		FC;
	input	[NFC-1:0]		FC;
//	// dummy
//	input		clk;  //dummy clk for synthesis	
//	input		dum_in;  //dummy input for synthesis	
//	output	reg	dum_out;  //dummy input for synthesis	
//	reg dum_clk;
//	always@(posedge clk) begin
//		dum_clk <= ~dum_in;
//		dum_out <= dum_in + dum_clk;
//	end

	logic	[NSTG:0]		int_node;

//	logic	[NFC-1:0]		FCB; // test with dco_FC_half
//	assign FCB = ~FC;

	assign int_node[0] = dtc_in;
//	assign int_node[NSTG] = dtc_out;

	// Selection pins
	generate 
		genvar i,j,k,f,l,m,n; 
		for (i=0; i<NSTG ; i=i+1)
		begin:stg_dtc
			if ((i != N_STG_FC-1)&&(i < N_STG_TUNE_START)) begin: notune // not tunable stage
				for (j=0; j<NCC_BASE; j=j+1)
				begin: base 
					if (BASE_3st==1) begin	 
						dco_CC_se_3st drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(1'b1));
					end else begin
						dco_CC_se drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(1'b1));
					end
				end
			end else if ((i == N_STG_FC-1)||((i>= N_STG_TUNE_START)&&(i<NSTG-1))) begin: tune // tunable stage
				for (k=0; k<NCC_BASE; k=k+1)
				begin: base // base 
					if (TUNE_BASE_3st==1) begin	 
						dco_CC_se_3st drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(1'b1));
					end else begin
						dco_CC_se drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(1'b1));
					end
				end
				for (f=0; f<NCC_TUNE; f=f+1)
				begin: tunable // tunable CCs
					if (TUNE_TUNE_3st==1) begin
						if (N_STG_FC_first) begin
							if (i==N_STG_FC-1) begin 
								dco_CC_se_3st drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(CC[f]));
							end else begin
								dco_CC_se_3st drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(CC[(i-N_STG_TUNE_START+1)*NCC_TUNE+f]));
							end
						end else begin
							dco_CC_se_3st drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(CC[(i-N_STG_TUNE_START)*NCC_TUNE+f]));
						end
					end else begin
						if (N_STG_FC_first) begin
							if (i==N_STG_FC-1) begin 
								dco_CC_se drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(CC[f]));
							end else begin
								dco_CC_se drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(CC[(i-N_STG_TUNE_START+1)*NCC_TUNE+f]));
							end
						end else begin
							dco_CC_se drv(.IN(int_node[i]), .OUT(int_node[i+1]), .EN(CC[(i-(NSTG-(NSTG_CC_TUNE+1)))*NCC_TUNE+f]));
						end
					end
				end
				if  (i==N_STG_FC-1) begin: finetune // tunable FCs only in 1 stage
					for (l=0; l<NFC; l=l+1)
					begin: tunable
						//dco_FC_se2_pnc cap(.IN(int_node[i+1]), .EN(FC[l]));
						dco_FC_se2 cap(.IN(int_node[i+1]), .EN(FC[l])); // 050821
						//dco_FC_se2_half cap(.IN(int_node[i+1]), .EN(FC[l]), .ENB(FCB[l]));
					end
				end
			end else if (i==NSTG-1) begin: last // last stage
				for (m=0; m<NCC_OUT; m=m+1)
				begin:	outbuf
					if (OUTBUF_3st==1) begin	 
						dco_CC_se_3st drv(.IN(int_node[i]), .OUT(dtc_out), .EN(1'b1));
					end else begin
						dco_CC_se drv(.IN(int_node[i]), .OUT(dtc_out), .EN(1'b1));
					end
				end
			end
		end
	endgenerate
	// Put down CLKREF path stages



endmodule 

  
