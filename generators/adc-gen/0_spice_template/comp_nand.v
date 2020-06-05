module comp_nand_ver0 (	input clk_sar, 
						input vinn, 
						input vinp, 
						output outn, 
						output outp);

//input vinp;
//input vinn;
//input clk_sar;
//output outp;
//output outn;

wire net10, net5, net12, net11, op, on;

INV_X0P6N_A10P5PP84TR_C14 i3 (.Y(outp), .A(net10));
INV_X0P6N_A10P5PP84TR_C14 i2 (.Y(outn), .A(net5));

INV_X0P6N_A10P5PP84TR_C14 i1 (.Y(net12), .A(op));
INV_X0P6N_A10P5PP84TR_C14 i0 (.Y(net11), .A(on));


NAND3_X2N_A10P5PP84TR_C14 i5 (.Y(op), .A(on), .B(clk_sar), .C(vinn));
NAND3_X2N_A10P5PP84TR_C14 i4 (.Y(on), .A(op), .B(clk_sar), .C(vinp));

NOR2_X2N_A10P5PP84TR_C14 i7 (.Y(net5), .A(net12), .B(net10));
NOR2_X2N_A10P5PP84TR_C14 i6 (.Y(net10), .A(net11), .B(net5));


endmodule
