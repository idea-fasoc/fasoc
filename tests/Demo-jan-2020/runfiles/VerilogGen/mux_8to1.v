module mux_8to1 (DATA_OUT, DATA_IN, DATA_SEL);
   parameter word_size = 32;
   parameter no_banks = 8;
   parameter banksel_bits = 3;
   output [word_size-1:0] DATA_OUT;
   input [word_size-1:0] DATA_IN [no_banks-1:0];
   input [banksel_bits-1:0] DATA_SEL;
   reg [word_size-1:0] DATA_OUT;
   always @(DATA_IN[0] or DATA_IN[1] or DATA_IN[2] or DATA_IN[3] or DATA_IN[4] or DATA_IN[5] or DATA_IN[6] or DATA_IN[7] or  DATA_SEL) begin
        case ( DATA_SEL )
                        3'b000: DATA_OUT = DATA_IN[0];
                        3'b001: DATA_OUT = DATA_IN[1];
                        3'b010: DATA_OUT = DATA_IN[2];
                        3'b011: DATA_OUT = DATA_IN[3];
                        3'b100: DATA_OUT = DATA_IN[4];
                        3'b101: DATA_OUT = DATA_IN[5];
                        3'b110: DATA_OUT = DATA_IN[6];
                        3'b111: DATA_OUT = DATA_IN[7];
                     default: DATA_OUT = 32'bxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx;
        endcase
     end
endmodule
