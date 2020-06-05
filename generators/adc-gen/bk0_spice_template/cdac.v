

//module SW_INPUT (in0l, in0r, in1, out, sw0, sw1, vdd, vnw, vpw, vss);
//
//input in0l, in0r, in1; // Analog input
//input sw0, sw1; // Digital switch control input
//inout vdd;
//inout vnw;
//inout vpw;
//inout vss;
//output out; // Analog output
//
//endmodule
//
//




//module SW_VCM (in, out, sw_ctrl, vdd, vnw, vpw, vss);
//
//input in; // Analog input
//input sw_ctrl; // Digital switch control input
//inout vdd;
//inout vnw;
//inout vpw;
//inout vss;
//output out; // Analog output
//
//endmodule






//module UNIT_CAP (top, bot);
//
//inout top; // Capacitor top node, analog in/out
//inout bot; // Capacitor bottom node, analog in/out
//
//endmodule


module cap_x1 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap (.top(top), .bot(bot));

endmodule

module cap_x2 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[1:0] (.top(top), .bot(bot));

endmodule

module cap_x4 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[3:0] (.top(top), .bot(bot));

endmodule

module cap_x8 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[7:0] (.top(top), .bot(bot));

endmodule

module cap_x16 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[15:0] (.top(top), .bot(bot));

endmodule

module cap_x32 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[31:0] (.top(top), .bot(bot));

endmodule

module cap_x64 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[63:0] (.top(top), .bot(bot));

endmodule

module cap_x128 (top, bot);
inout top; // Capacitor top node, analog in/out
inout bot; // Capacitor bottom node, analog in/out


UNIT_CAP u_unitcap[127:0] (.top(top), .bot(bot));

endmodule



module cdac (vcm_p, vcm_n, vin_p, vin_n, vrefh, vrefl, vtop_p, vtop_n, sample, value, vdd, vnw, vpw, vss);

inout vcm_p;
inout vcm_n;
input vin_p;
input vin_n;
input vrefh;
input vrefl;
inout vdd;
inout vnw;
inout vpw;
inout vss;
input sample;

output [@NBIT-1:0] value;

output vtop_p;
output vtop_n;

wire [@NBIT-1:0] vbot_p;
wire [@NBIT-1:0] vbot_n;
wire cm_up_p, cm_up_n;


//bit0 @in SW_INPUT u_sw_in_p0@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[0]), .sw0(sample), .sw1(value[0]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit1 @in SW_INPUT u_sw_in_p1@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[1]), .sw0(sample), .sw1(value[1]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit2 @in SW_INPUT u_sw_in_p2@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[2]), .sw0(sample), .sw1(value[2]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit3 @in SW_INPUT u_sw_in_p3@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[3]), .sw0(sample), .sw1(value[3]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit4 @in SW_INPUT u_sw_in_p4@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[4]), .sw0(sample), .sw1(value[4]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit5 @in SW_INPUT u_sw_in_p5@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[5]), .sw0(sample), .sw1(value[5]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit6 @in SW_INPUT u_sw_in_p6@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[6]), .sw0(sample), .sw1(value[6]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit7 @in SW_INPUT u_sw_in_p7@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[7]), .sw0(sample), .sw1(value[7]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//
//bit0 @in SW_INPUT u_sw_in_n0@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[0]), .sw0(sample), .sw1(value[0]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit1 @in SW_INPUT u_sw_in_n1@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[1]), .sw0(sample), .sw1(value[1]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit2 @in SW_INPUT u_sw_in_n2@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[2]), .sw0(sample), .sw1(value[2]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit3 @in SW_INPUT u_sw_in_n3@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[3]), .sw0(sample), .sw1(value[3]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit4 @in SW_INPUT u_sw_in_n4@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[4]), .sw0(sample), .sw1(value[4]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit5 @in SW_INPUT u_sw_in_n5@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[5]), .sw0(sample), .sw1(value[5]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit6 @in SW_INPUT u_sw_in_n6@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[6]), .sw0(sample), .sw1(value[6]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
//bit7 @in SW_INPUT u_sw_in_n7@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[7]), .sw0(sample), .sw1(value[7]), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));


//bit0 @cv cap_x1 u_cap1b_p0@ (.top(vtop_p), .bot(vbot_p[0]));
//bit1 @cv cap_x2 u_cap2b_p1@ (.top(vtop_p), .bot(vbot_p[1]));
//bit2 @cv cap_x4 u_cap3b_p2@ (.top(vtop_p), .bot(vbot_p[2]));
//bit3 @cv cap_x8 u_cap4b_p3@ (.top(vtop_p), .bot(vbot_p[3]));
//bit4 @cv cap_x16 u_cap5b_p4@ (.top(vtop_p), .bot(vbot_p[4]));
//bit5 @cv cap_x32 u_cap6b_p5@ (.top(vtop_p), .bot(vbot_p[5]));
//bit6 @cv cap_x64 u_cap7b_p6@ (.top(vtop_p), .bot(vbot_p[6]));
//bit7 @cv cap_x128 u_cap8b_p7@ (.top(vtop_p), .bot(vbot_p[7]));
//
//bit0 @cv cap_x1 u_cap1b_n0@ (.top(vtop_n), .bot(vbot_n[0]));
//bit1 @cv cap_x2 u_cap2b_n1@ (.top(vtop_n), .bot(vbot_n[1]));
//bit2 @cv cap_x4 u_cap3b_n2@ (.top(vtop_n), .bot(vbot_n[2]));
//bit3 @cv cap_x8 u_cap4b_n3@ (.top(vtop_n), .bot(vbot_n[3]));
//bit4 @cv cap_x16 u_cap5b_n4@ (.top(vtop_n), .bot(vbot_n[4]));
//bit5 @cv cap_x32 u_cap6b_n5@ (.top(vtop_n), .bot(vbot_n[5]));
//bit6 @cv cap_x64 u_cap7b_n6@ (.top(vtop_n), .bot(vbot_n[6]));
//bit7 @cv cap_x128 u_cap8b_n7@ (.top(vtop_n), .bot(vbot_n[7]));


@cm SW_VCM u_SW_VCMp@ (.in(vcm_p), .out(vtop_p), .sw_ctrl(sample), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));
@cm SW_VCM u_SW_VCMn@ (.in(vcm_n), .out(vtop_n), .sw_ctrl(sample), .vdd(vdd), .vnw(vnw), .vpw(vpw), .vss(vss));

@cv INV_X4N_A10P5PP84TR_C14 u_inv_cm_up_p@ (.Y(cm_up_p), .A(sample), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));
@cv INV_X4N_A10P5PP84TR_C14 u_inv_cm_up_n@ (.Y(cm_up_n), .A(sample), .VDD(vdd), .VNW(vnw), .VPW(vpw), .VSS(vss));

//bit0 @cv cap_x1 u_cm_up_p0@ (.top(vtop_p), .bot(cm_up_p));
//bit1 @cv cap_x1 u_cm_up_p1@ (.top(vtop_p), .bot(cm_up_p));
//bit2 @cv cap_x1 u_cm_up_p2@ (.top(vtop_p), .bot(cm_up_p));
//bit3 @cv cap_x2 u_cm_up_p3@ (.top(vtop_p), .bot(cm_up_p));
//bit4 @cv cap_x4 u_cm_up_p4@ (.top(vtop_p), .bot(cm_up_p));
//bit5 @cv cap_x8 u_cm_up_p5@ (.top(vtop_p), .bot(cm_up_p));
//bit6 @cv cap_x16 u_cm_up_p6@ (.top(vtop_p), .bot(cm_up_p));
//bit7 @cv cap_x32 u_cm_up_p7@ (.top(vtop_p), .bot(cm_up_p));
//
//bit0 @cv cap_x1 u_cm_up_n0@ (.top(vtop_n), .bot(cm_up_n));
//bit1 @cv cap_x1 u_cm_up_n1@ (.top(vtop_n), .bot(cm_up_n));
//bit2 @cv cap_x1 u_cm_up_n2@ (.top(vtop_n), .bot(cm_up_n));
//bit3 @cv cap_x2 u_cm_up_n3@ (.top(vtop_n), .bot(cm_up_n));
//bit4 @cv cap_x4 u_cm_up_n4@ (.top(vtop_n), .bot(cm_up_n));
//bit5 @cv cap_x8 u_cm_up_n5@ (.top(vtop_n), .bot(cm_up_n));
//bit6 @cv cap_x16 u_cm_up_n6@ (.top(vtop_n), .bot(cm_up_n));
//bit7 @cv cap_x32 u_cm_up_n7@ (.top(vtop_n), .bot(cm_up_n));

endmodule
