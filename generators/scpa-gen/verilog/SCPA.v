module SCPA(
   input         dum_clk,
   input         dum_in,
   output logic  dum_out,
   input 	 clk,
   input [31:0]   cap_sel,
   output	 cap_out
);

   parameter integer ARRSZ = 32;
   logic [ARRSZ-1:0] cap_bot_in;

   logic dum_inter;

   always_ff @ (posedge dum_clk) begin
      dum_inter <= ~dum_in;
      dum_out <= dum_inter + dum_in;
   end

  genvar i;
  generate 
     for (i = 0; i < ARRSZ; i = i + 1) begin
         CLK_DRIVER clk_drv (.rf(clk), .sel(cap_sel[i]), .vout(cap_bot_in[i])); 
         SCPA_MIMCAP_new cap_array (.TOP(cap_out), .BOT(cap_bot_in[i]));

     end
  endgenerate


endmodule
