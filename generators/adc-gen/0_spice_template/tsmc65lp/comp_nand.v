module comp_nand (clk_sar, vinn, vinp, outn, outp); //vdd,vss power domain

input vinp;
input vinn;
input clk_sar;

output outp;
output outn;

wire net018, net024, net026, net027, op, on;

INV_X0P5B_A9TR i11 (.Y(outp), .A(net018));
INV_X0P5B_A9TR i10 (.Y(outn), .A(net024));

INV_X0P5B_A9TR i7 (.Y(net026), .A(op));
INV_X0P5B_A9TR i4 (.Y(net027), .A(on));


NAND3_X2A_A9TR i1 (.Y(op), .A(on), .B(clk_sar), .C(vinn));
NAND3_X2A_A9TR i0 (.Y(on), .A(op), .B(clk_sar), .C(vinp));

NOR2_X0P5A_A9TR i6 (.Y(net024), .A(net018), .B(net026));
NOR2_X0P5A_A9TR i5 (.Y(net018), .A(net027), .B(net024));


endmodule
