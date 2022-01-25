//`timescale 1ns/1ps
//module GFSK_CTRL_V2 (CLK_8M,RESET, PLL_CAL_DONE, EN_OV,GFSK_EN,VC_CTRL_INIT,CONT_MOD,PKT_LENGTH, DATA_INIT, DATA, VC_MOD,MOD_ON                  
module GFSK_CTRL_V2 (CLK_8M,RESET, PLL_CAL_DONE, EN_OV,GFSK_EN,VC_CTRL_INIT,CONT_MOD,PKT_LENGTH, DATA_INIT, DATA, VC_CTRL,MOD_ON                  
		     ,MOD_0_0,MOD_0_1,MOD_0_2,MOD_0_3,MOD_0_4,MOD_0_5,MOD_0_6,MOD_0_7
		     ,MOD_1_0,MOD_1_1,MOD_1_2,MOD_1_3,MOD_1_4,MOD_1_5,MOD_1_6,MOD_1_7
		     ,MOD_2_0,MOD_2_1,MOD_2_2,MOD_2_3,MOD_2_4,MOD_2_5,MOD_2_6,MOD_2_7
		     ,MOD_3_0,MOD_3_1,MOD_3_2,MOD_3_3,MOD_3_4,MOD_3_5,MOD_3_6,MOD_3_7
		     ,MOD_4_0,MOD_4_1,MOD_4_2,MOD_4_3,MOD_4_4,MOD_4_5,MOD_4_6,MOD_4_7
		     ,MOD_5_0,MOD_5_1,MOD_5_2,MOD_5_3,MOD_5_4,MOD_5_5,MOD_5_6,MOD_5_7
		     ,MOD_6_0,MOD_6_1,MOD_6_2,MOD_6_3,MOD_6_4,MOD_6_5,MOD_6_6,MOD_6_7
		     ,MOD_7_0,MOD_7_1,MOD_7_2,MOD_7_3,MOD_7_4,MOD_7_5,MOD_7_6,MOD_7_7
		     );

   parameter VC_BITS = 9;
   parameter VC_BITS_D = 64;
   // parameter VC_CTRL_INIT = 6'b011111;

   input						CLK_8M;
   input						RESET;
   input						PLL_CAL_DONE; // from PLL
   input						EN_OV; // from top 
   input						GFSK_EN; // from top 
   input						CONT_MOD; // from top 
   input [8:0] 						VC_CTRL_INIT; // from top 
   input [8:0] 						PKT_LENGTH;
   input [1:0] 						DATA_INIT;
   input [511:0] 					DATA;



   output      						MOD_ON;		 
   output reg [VC_BITS-1:0] 				VC_CTRL;
//   output  reg [VC_BITS_D-1:0] 				VC_MOD;		 

   input [VC_BITS-1:0] 					MOD_0_0;			
   input [VC_BITS-1:0] 					MOD_0_1;			
   input [VC_BITS-1:0] 					MOD_0_2;			
   input [VC_BITS-1:0] 					MOD_0_3;			
   input [VC_BITS-1:0] 					MOD_0_4;			
   input [VC_BITS-1:0] 					MOD_0_5;			
   input [VC_BITS-1:0] 					MOD_0_6;			
   input [VC_BITS-1:0] 					MOD_0_7;			
   input [VC_BITS-1:0] 					MOD_1_0;			
   input [VC_BITS-1:0] 					MOD_1_1;			
   input [VC_BITS-1:0] 					MOD_1_2;			
   input [VC_BITS-1:0] 					MOD_1_3;			
   input [VC_BITS-1:0] 					MOD_1_4;			
   input [VC_BITS-1:0] 					MOD_1_5;			
   input [VC_BITS-1:0] 					MOD_1_6;			
   input [VC_BITS-1:0] 					MOD_1_7;			
   input [VC_BITS-1:0] 					MOD_2_0;			
   input [VC_BITS-1:0] 					MOD_2_1;			
   input [VC_BITS-1:0] 					MOD_2_2;			
   input [VC_BITS-1:0] 					MOD_2_3;			
   input [VC_BITS-1:0] 					MOD_2_4;			
   input [VC_BITS-1:0] 					MOD_2_5;			
   input [VC_BITS-1:0] 					MOD_2_6;			
   input [VC_BITS-1:0] 					MOD_2_7;			
   input [VC_BITS-1:0] 					MOD_3_0;			
   input [VC_BITS-1:0] 					MOD_3_1;			
   input [VC_BITS-1:0] 					MOD_3_2;			
   input [VC_BITS-1:0] 					MOD_3_3;			
   input [VC_BITS-1:0] 					MOD_3_4;			
   input [VC_BITS-1:0] 					MOD_3_5;			
   input [VC_BITS-1:0] 					MOD_3_6;			
   input [VC_BITS-1:0] 					MOD_3_7;			
   input [VC_BITS-1:0] 					MOD_4_0;			
   input [VC_BITS-1:0] 					MOD_4_1;			
   input [VC_BITS-1:0] 					MOD_4_2;			
   input [VC_BITS-1:0] 					MOD_4_3;			
   input [VC_BITS-1:0] 					MOD_4_4;			
   input [VC_BITS-1:0] 					MOD_4_5;			
   input [VC_BITS-1:0] 					MOD_4_6;			
   input [VC_BITS-1:0] 					MOD_4_7;			
   input [VC_BITS-1:0] 					MOD_5_0;			
   input [VC_BITS-1:0] 					MOD_5_1;			
   input [VC_BITS-1:0] 					MOD_5_2;			
   input [VC_BITS-1:0] 					MOD_5_3;			
   input [VC_BITS-1:0] 					MOD_5_4;			
   input [VC_BITS-1:0] 					MOD_5_5;			
   input [VC_BITS-1:0] 					MOD_5_6;			
   input [VC_BITS-1:0] 					MOD_5_7;			
   input [VC_BITS-1:0] 					MOD_6_0;			
   input [VC_BITS-1:0] 					MOD_6_1;			
   input [VC_BITS-1:0] 					MOD_6_2;			
   input [VC_BITS-1:0] 					MOD_6_3;			
   input [VC_BITS-1:0] 					MOD_6_4;			
   input [VC_BITS-1:0] 					MOD_6_5;			
   input [VC_BITS-1:0] 					MOD_6_6;			
   input [VC_BITS-1:0] 					MOD_6_7;			
   input [VC_BITS-1:0] 					MOD_7_0;			
   input [VC_BITS-1:0] 					MOD_7_1;			
   input [VC_BITS-1:0] 					MOD_7_2;			
   input [VC_BITS-1:0] 					MOD_7_3;			
   input [VC_BITS-1:0] 					MOD_7_4;			
   input [VC_BITS-1:0] 					MOD_7_5;			
   input [VC_BITS-1:0] 					MOD_7_6;			
   input [VC_BITS-1:0] 					MOD_7_7;			
   

   //wire 						CLK_8M;
   wire 						CLK_8M_155M;
   wire 						CLK_8M_1240M;
   reg 							en_0;
   reg 							en_1;
   reg [2:0] 						os_cnt;
   reg [8:0] 						b_cnt; 
   reg [2:0] 						data_seq;
//   reg [VC_BITS_D-1:0] 					vc_mod_wire;



   always @(posedge CLK_8M or posedge RESET) begin
      if (RESET) begin
	 en_0 <= 0;
	 en_1 <= 0;
      end
      else begin
	 en_0 <= (PLL_CAL_DONE|EN_OV);
	 en_1 <= en_0;
      end
   end
   assign MOD_ON =(en_0 && en_1) | (b_cnt >0) | CONT_MOD;
   always @(posedge CLK_8M or posedge RESET) begin
      if (RESET) begin
	 os_cnt <= 0;
	 b_cnt  <= 0;
	 VC_CTRL <= VC_CTRL_INIT;
         //VC_MOD <= vc_mod_wire;
      end
      else begin
	 if ((en_0 && en_1) | (b_cnt >0) | CONT_MOD) begin	//level trigger
            os_cnt <= os_cnt + 1;
            b_cnt <= ((b_cnt == PKT_LENGTH)&&(os_cnt == 7))?0:
						(os_cnt == 7)? (b_cnt + 1) : b_cnt;
            //VC_MOD <= vc_mod_wire;
            if(GFSK_EN) begin 
               case ({data_seq,os_cnt})

		 {3'b000,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_0;	//-28
		 {3'b000,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_1;	//-28
		 {3'b000,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_2;	//-28
		 {3'b000,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_3;	//-28
		 {3'b000,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_4;	//-28
		 {3'b000,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_5;	//-28
		 {3'b000,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_6;	//-28
		 {3'b000,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_0_7;	//-28

		 {3'b001,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_0;	//-28
		 {3'b001,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_1;	//-28
		 {3'b001,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_2;	//-28
		 {3'b001,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_3;	//-27
		 {3'b001,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_4;	//-25
		 {3'b001,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_5;	//-21
		 {3'b001,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_6;	//-15
		 {3'b001,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_1_7;	//-5

		 {3'b010,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_0;		//5
		 {3'b010,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_1;		//15
		 {3'b010,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_2;		//21
		 {3'b010,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_3;		//24
		 {3'b010,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_4;		//24
		 {3'b010,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_5;		//21
		 {3'b010,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_6;		//15
		 {3'b010,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_2_7;		//5

		 {3'b011,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_0;		//5
		 {3'b011,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_1;		//15
		 {3'b011,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_2;		//21
		 {3'b011,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_3;		//25
		 {3'b011,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_4;		//27
		 {3'b011,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_5;		//28
		 {3'b011,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_6;		//28
		 {3'b011,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_3_7;		//28

		 {3'b100,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_0;	//-5
		 {3'b100,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_1;	//-15
		 {3'b100,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_2;	//-21
		 {3'b100,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_3;	//-25
		 {3'b100,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_4;	//-27
		 {3'b100,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_5;	//-28
		 {3'b100,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_6;	//-28
		 {3'b100,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_4_7;	//-28

		 {3'b101,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_0;	//-5
		 {3'b101,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_1;	//-15
		 {3'b101,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_2;	//-21
		 {3'b101,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_3;	//-24
		 {3'b101,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_4;	//-24
		 {3'b101,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_5;	//-21
		 {3'b101,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_6;	//-15
		 {3'b101,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_5_7;	//-5

		 {3'b110,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_0;		//28
		 {3'b110,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_1;		//28
		 {3'b110,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_2;		//28
		 {3'b110,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_3;		//27
		 {3'b110,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_4;		//25
		 {3'b110,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_5;		//21
		 {3'b110,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_6;		//15
		 {3'b110,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_6_7;		//5

		 {3'b111,3'b000}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_0;		//28
		 {3'b111,3'b001}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_1;		//28
		 {3'b111,3'b010}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_2;		//28
		 {3'b111,3'b011}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_3;		//28
		 {3'b111,3'b100}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_4;		//28
		 {3'b111,3'b101}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_5;		//28
		 {3'b111,3'b110}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_6;		//28
		 {3'b111,3'b111}:	VC_CTRL <= VC_CTRL_INIT + MOD_7_7;		//28

		 default:		VC_CTRL <= VC_CTRL_INIT;
               endcase
	       
	    end else begin
               case (DATA[b_cnt])
		 {1'b0}:	VC_CTRL <=  MOD_0_0;	//-28
		 {1'b1}:	VC_CTRL <=  MOD_7_7;	//28
		 default:	VC_CTRL <= VC_CTRL_INIT;
               endcase
	    end
	 end else begin
	    os_cnt  <= os_cnt;
	    b_cnt  	<= b_cnt;
	    VC_CTRL <= VC_CTRL_INIT;
	 end
      end
   end

   always @(*) begin
      if (RESET) begin
	 data_seq <= 3'b000;
      end
      else begin
	 case (b_cnt)
           0: 	 data_seq <= {DATA_INIT[0],DATA_INIT[1],DATA[0]};
           1: 	 data_seq <= {DATA_INIT[1],DATA[0],DATA[1]};
           default: data_seq <= {DATA[b_cnt-2],DATA[b_cnt-1],DATA[b_cnt]};
	 endcase  
      end
   end

   //binary to thermometer code
 //  integer i;

 //  always @(*) begin
 //     for (i=0; i<VC_BITS_D; i=i+1) begin
 //        if (i<=VC_CTRL)  vc_mod_wire[i] = 1;
 //        else             vc_mod_wire[i] = 0;                 
 //     end
 //  end

endmodule
