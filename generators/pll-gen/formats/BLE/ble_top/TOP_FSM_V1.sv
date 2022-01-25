//`timescale 1ns/1ps
module TOP_FSM_V1 (CLK_8M, RESET, TRANS_MODE, PLL_LOCKED, PLL_LOCKED_OV, MOD_ON, START_TX, DEBUG_MODE, PLL_CNT, PA_CNT, 
		   PLL_CAL_DONE, CONT_MOD, EN_PA, EN_PLL);

	input		CLK_8M;
	input		RESET;
	input		TRANS_MODE;
	input		PLL_LOCKED;
	input		PLL_LOCKED_OV;
	input		MOD_ON;
	input		START_TX;
	input		DEBUG_MODE;
	input [13:0]	PLL_CNT;	 
	input [9:0]	PA_CNT;	 
   

	output reg      PLL_CAL_DONE;		 
	output reg     	CONT_MOD;		 
	output reg     	EN_PA;		 
	output reg     	EN_PLL;		 

	wire		CLK_8M, RESET, TRANS_MODE, PLL_LOCKED, PLL_LOCKED_OV, MOD_ON,START_TX,DEBUG_MODE;

	reg [9:0]	T1;
	reg [9:0]	T2;
	reg 		TXF;


	localparam	STATE_0 = 3'd0 ,
			STATE_1 = 3'd1 ,
			STATE_2 = 3'd2 ,
			STATE_3 = 3'd3 ,
			STATE_4 = 3'd4 ,
			STATE_5 = 3'd5 ,
			STATE_6 = 3'd6 ,
			STATE_7 = 3'd7;



	reg [3:0]	pll_cal_done_cnt;
	reg [2:0]	CurrentState ;
	reg [2:0] 	NextState ;



	always@ ( posedge CLK_8M or posedge RESET) begin
		if ( RESET ) begin
			 CurrentState <= STATE_0 ;
			T1 <= 0;
			T2 <= 0;
			pll_cal_done_cnt <= 0;
		end else begin
			CurrentState <= NextState ;
			if ( CurrentState == STATE_2 ) begin
				T1 <= T1 + 1;
			end
			if ( CurrentState == STATE_3 ) begin
				T2 <= T2 + 1;
			end
			if ( CurrentState == STATE_4 ) begin
				pll_cal_done_cnt <= pll_cal_done_cnt + 1;
			end
			if ( CurrentState == STATE_5 ) begin
				pll_cal_done_cnt <= 0;
			end
		end
	end


	always@ ( * ) begin
		NextState = CurrentState ;
		case ( CurrentState )

			STATE_0 : begin
				TXF = 0;				
				NextState = STATE_1 ;
				EN_PA = 0;
				EN_PLL = 0;
				CONT_MOD =0;
				PLL_CAL_DONE =0;
			end

			STATE_1 : begin
				//T1=10'b0000000000 ;
				//T2=10'b0000000000 ;
				TXF = 0;				
				EN_PA = 0;
				EN_PLL = 0;
				CONT_MOD =0;
				PLL_CAL_DONE =0;
				if ( (START_TX && !TXF) || DEBUG_MODE) begin
					 NextState = STATE_2 ;
				end else begin 
					NextState = STATE_1 ;
				end
			end

			STATE_2 : begin
				TXF=1;
				EN_PA = 0;
				EN_PLL = 1;
				CONT_MOD =0;
				PLL_CAL_DONE =0;
				if (PLL_LOCKED || PLL_LOCKED_OV || (T1 >= PLL_CNT)) begin
					 NextState = STATE_3 ;
				end else begin
					NextState = STATE_2 ;
				end
			end

			STATE_3 : begin
				TXF=1;
				EN_PA = 1;
				EN_PLL = 1;
				CONT_MOD =0;
				PLL_CAL_DONE =0;
				if (T2 >= PA_CNT) begin 
					NextState = STATE_4 ;
				end else begin
					NextState = STATE_3 ;
				end
			end

			STATE_4 : begin
				TXF=1;
				EN_PA = 1;
				EN_PLL = 1;
				CONT_MOD = TRANS_MODE ;
				PLL_CAL_DONE = 1'b1 ;
				if (pll_cal_done_cnt == 4'b1011) begin
					NextState = STATE_5 ;
				end else begin
					NextState = STATE_4 ;
				end
			end

			STATE_5 : begin
				TXF=1;
				EN_PA = 1;
				EN_PLL = 1;
				CONT_MOD = TRANS_MODE ;
				PLL_CAL_DONE = 1'b0 ;				
				if ( !MOD_ON ) begin
					NextState = STATE_1 ;
				end else begin 
					NextState = STATE_5 ;
				end
			end

			STATE_6 : begin
				TXF=1;
				EN_PA = 1;
				EN_PLL = 1;
				CONT_MOD = TRANS_MODE ;
				PLL_CAL_DONE = 1'b0 ;				
				NextState = STATE_1 ;
			end

			STATE_7 : begin
				TXF=1;
				EN_PA = 1;
				EN_PLL = 1;
				CONT_MOD = TRANS_MODE ;
				PLL_CAL_DONE = 1'b0 ;				
				NextState = STATE_1 ;
			end
	

			// this default is needed for proper synthesis
			default: begin
				TXF = 0;
				EN_PA = 0;
				EN_PLL = 0;
				CONT_MOD =0;
				PLL_CAL_DONE =0;
				NextState = STATE_1 ;
			end
		
		endcase
	end

endmodule
