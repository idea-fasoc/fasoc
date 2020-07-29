`timescale 1ns / 1ns
`include "decoder_3to8.v"
`include "mux_8to1.v"


module memory2 (DOUT, ADDR, CLK, DBE, CEN, DIN, WE);
   parameter address_size = 12;
   parameter no_banks = 8;
   parameter bank_address_size = 9;
   parameter word_size    = 32;
   input  CLK, CEN,  WE;
   input [3:0]  DBE;
   input [address_size-1:0]  ADDR;
   input [word_size-1:0]  DIN;
   output [word_size-1:0]  DOUT;
   wire  [no_banks-1:0]  DATA_REQ;
   wire [word_size-1:0] DATA_SRAM_BANK_OUT [no_banks-1:0];
   decoder_3to8 DI (.DATA_REQ(DATA_REQ), .ADDR(ADDR[address_size-1:bank_address_size]), .DATA_REQIN(CEN));
   SRAM_2KB SR0 ( .DOUT(DATA_SRAM_BANK_OUT[0]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[0]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR1 ( .DOUT(DATA_SRAM_BANK_OUT[1]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[1]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR2 ( .DOUT(DATA_SRAM_BANK_OUT[2]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[2]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR3 ( .DOUT(DATA_SRAM_BANK_OUT[3]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[3]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR4 ( .DOUT(DATA_SRAM_BANK_OUT[4]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[4]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR5 ( .DOUT(DATA_SRAM_BANK_OUT[5]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[5]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR6 ( .DOUT(DATA_SRAM_BANK_OUT[6]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[6]), .DIN(DIN), .WE_IN(WE));
   SRAM_2KB SR7 ( .DOUT(DATA_SRAM_BANK_OUT[7]), .ADDR_IN(ADDR[bank_address_size-1:0]), .CLK_IN(CLK), .DATA_BE_IN(DBE), .DATA_REQ_IN(DATA_REQ[7]), .DIN(DIN), .WE_IN(WE));
   mux_8to1 MI (.DATA_OUT(DOUT), .DATA_IN(DATA_SRAM_BANK_OUT), .DATA_SEL(ADDR[address_size-1:bank_address_size]));
endmodule
