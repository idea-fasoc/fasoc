module CLK_DRIVER(
           input rf,
           input sel,
           output vout
);
   logic w0, w1, w2, w3;
   NAND2_X1N_A10P5PP84TR_C14 nand1 (.A(sel), .B(rf), .Y(w0));
   INV_X2N_A10P5PP84TR_C14 inv1 (.A(w0), .Y(w1));
   INV_X4N_A10P5PP84TR_C14 inv2 (.A(w1), .Y(w2));
   INV_X8N_A10P5PP84TR_C14 inv3 (.A(w2), .Y(w3));
   INV_X16N_A10P5PP84TR_C14 inv4 (.A(w3), .Y(vout));

endmodule


