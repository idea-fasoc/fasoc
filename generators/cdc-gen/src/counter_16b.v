module counter_16b(CLK_SENS, RESET_COUNTERn, DOUT);
	input RESET_COUNTERn;
	input CLK_SENS;

	output reg [15:0] DOUT;

//	reg [15:0] DOUT;
	wire clk_sens_in;
	//reg WAKE;
	//reg WAKE_pre;
	

//	assign clk_sens_in = done_sens && CLK_SENS;
//	assign clk_ref_in = done_ref && CLK_REF;
//	assign done_pre = ~doneb;
//	assign done_sens = WAKE_pre &&  doneb;
//	assign done_ref = WAKE && doneb;
	BUFX2HVT	Buf_DONE(.A(CLK_SENS), .Y(clk_sens_in));
	//assign RESET_CLK_REF = ~q1; 

//	always @ (*) begin
//		case (done_pre)
//			1'd0:	DOUT = 24'd0;
//			1'd1:	DOUT = DOUT;
//		endcase
//	end
	
//	always @ (negedge RESET_COUNTERn or posedge CLK_REF) begin
//		if (~RESET_COUNTERn) begin	WAKE <= 1'd0;
//						WAKE_pre <= 1'd0;
//		end
//		else if (WAKE_pre == 0)		WAKE_pre <= 1'd1;
//		else 				WAKE <= WAKE_pre;
//	end
	// CLK_Sens DIV count
	always @ (negedge RESET_COUNTERn or posedge clk_sens_in) begin
		if (~RESET_COUNTERn)	DOUT[0] <= 1'd0; 
		else 			DOUT[0] <= ~DOUT[0];
	end

	genvar j;
	generate
		for (j=1; j<16; j=j+1) begin
			always @ (negedge RESET_COUNTERn or negedge DOUT[j-1]) begin
				if (~RESET_COUNTERn)		DOUT[j] <=  1'd0; 
				else 				DOUT[j] <= ~DOUT[j];
			end
		end
	endgenerate
endmodule
