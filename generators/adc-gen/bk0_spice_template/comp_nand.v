module comp_nand_ver0 (clk_sar, vinn, vinp, outn, outp, vdd, vnw, vpw, vss); //vdd,vss,vnw,vpw power domain

input vinp;
input vinn;
input clk_sar;
inout vdd;
inout vnw;
inout vpw;
inout vss;
output outp;
output outn;

wire net10, net5, net12, net11, op, on;

INV_X0P6N_A10P5PP84TR_C14 i3 (.Y(outp), .A(net10), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));
INV_X0P6N_A10P5PP84TR_C14 i2 (.Y(outn), .A(net5), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));

INV_X0P6N_A10P5PP84TR_C14 i1 (.Y(net12), .A(op), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));
INV_X0P6N_A10P5PP84TR_C14 i0 (.Y(net11), .A(on), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));


NAND3_X2N_A10P5PP84TR_C14 i5 (.Y(op), .A(on), .B(clk_sar), .C(vinn), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));
NAND3_X2N_A10P5PP84TR_C14 i4 (.Y(on), .A(op), .B(clk_sar), .C(vinp), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));

NOR2_X2N_A10P5PP84TR_C14 i7 (.Y(net5), .A(net12), .B(net10), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));
NOR2_X2N_A10P5PP84TR_C14 i6 (.Y(net10), .A(net11), .B(net5), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));


endmodule
