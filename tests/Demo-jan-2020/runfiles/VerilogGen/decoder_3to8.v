module decoder_3to8 (DATA_REQ, ADDR, DATA_REQIN);
   parameter no_banks = 8;
   parameter banksel_bits = 3;
   output [no_banks-1:0] DATA_REQ;
   input  [banksel_bits-1:0] ADDR;
   input DATA_REQIN;
   reg [no_banks-1:0] DATA_REQ;
   always @(DATA_REQIN or ADDR) begin
     if (DATA_REQIN == 1'b1)
         case (ADDR)
               3'b000: DATA_REQ = 8'b00000001;
               3'b001: DATA_REQ = 8'b00000010;
               3'b010: DATA_REQ = 8'b00000100;
               3'b011: DATA_REQ = 8'b00001000;
               3'b100: DATA_REQ = 8'b00010000;
               3'b101: DATA_REQ = 8'b00100000;
               3'b110: DATA_REQ = 8'b01000000;
               3'b111: DATA_REQ = 8'b10000000;
         endcase
     else if (DATA_REQIN == 0)
         DATA_REQ = 8'b00000000;
   end
endmodule
