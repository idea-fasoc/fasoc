

//module sw_input (in0l, in0r, in1, out, sw0, sw1);
//
//input in0l, in0r, in1; // Analog input
//input sw0, sw1; // Digital switch control input
//output out; // Analog output
//
//endmodule
//
//
//
//
//
//
//module sw_vcm (in, out, sw_ctrl);
//
//input in; // Analog input
//input sw_ctrl; // Digital switch control input
//
//output out; // Analog output
//
//endmodule
//
//
//
//
//
//
//module unit_cap (top, bot);
//
//inout top; // Capacitor top node, analog in/out
//inout bot; // Capacitor bottom node, analog in/out
//
//endmodule


module cap_1b (inout top, inout bot);

unit_cap u_unitcap (.top(top), .bot(bot));

endmodule

module cap_2b (inout top, inout bot);

unit_cap u_unitcap[1:0] (.top(top), .bot(bot));

endmodule

module cap_3b (inout top, inout bot);

unit_cap u_unitcap[3:0] (.top(top), .bot(bot));

endmodule

module cap_4b (inout top, inout bot);

unit_cap u_unitcap[7:0] (.top(top), .bot(bot));

endmodule

module cap_5b (inout top, inout bot);

unit_cap u_unitcap[15:0] (.top(top), .bot(bot));

endmodule

module cap_6b (inout top, inout bot);

unit_cap u_unitcap[31:0] (.top(top), .bot(bot));

endmodule

module cap_7b (inout top, inout bot);

unit_cap u_unitcap[63:0] (.top(top), .bot(bot));

endmodule

module cap_8b (inout top, inout bot);

unit_cap u_unitcap[127:0] (.top(top), .bot(bot));

endmodule



module cdac (vcm_p, vcm_n, vin_p, vin_n, vrefh, vrefl, vtop_p, vtop_n, sample, value);

input vcm_p;
input vcm_n;
input vin_p;
input vin_n;
input vrefh;
input vrefl;

input sample;

input [@NBIT-1:0] value;

output vtop_p;
output vtop_n;

wire [@NBIT-1:0] vbot_p;
wire [@NBIT-1:0] vbot_n;
wire cm_up_p, cm_up_n;


//bit0 @in sw_input u_sw_in_p0@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[0]), .sw0(sample), .sw1(value[0]));
//bit1 @in sw_input u_sw_in_p1@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[1]), .sw0(sample), .sw1(value[1]));
//bit2 @in sw_input u_sw_in_p2@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[2]), .sw0(sample), .sw1(value[2]));
//bit3 @in sw_input u_sw_in_p3@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[3]), .sw0(sample), .sw1(value[3]));
//bit4 @in sw_input u_sw_in_p4@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[4]), .sw0(sample), .sw1(value[4]));
//bit5 @in sw_input u_sw_in_p5@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[5]), .sw0(sample), .sw1(value[5]));
//bit6 @in sw_input u_sw_in_p6@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[6]), .sw0(sample), .sw1(value[6]));
//bit7 @in sw_input u_sw_in_p7@ (.in0l(vrefh), .in0r(vin_p), .in1(vrefl), .out(vbot_p[7]), .sw0(sample), .sw1(value[7]));

//bit0 @in sw_input u_sw_in_n0@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[0]), .sw0(sample), .sw1(value[0]));
//bit1 @in sw_input u_sw_in_n1@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[1]), .sw0(sample), .sw1(value[1]));
//bit2 @in sw_input u_sw_in_n2@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[2]), .sw0(sample), .sw1(value[2]));
//bit3 @in sw_input u_sw_in_n3@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[3]), .sw0(sample), .sw1(value[3]));
//bit4 @in sw_input u_sw_in_n4@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[4]), .sw0(sample), .sw1(value[4]));
//bit5 @in sw_input u_sw_in_n5@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[5]), .sw0(sample), .sw1(value[5]));
//bit6 @in sw_input u_sw_in_n6@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[6]), .sw0(sample), .sw1(value[6]));
//bit7 @in sw_input u_sw_in_n7@ (.in0l(vrefl), .in0r(vin_n), .in1(vrefh), .out(vbot_n[7]), .sw0(sample), .sw1(value[7]));


//bit0 @cv cap_1b u_cap1b_p0@ (.top(vtop_p), .bot(vbot_p[0]));
//bit1 @cv cap_2b u_cap2b_p1@ (.top(vtop_p), .bot(vbot_p[1]));
//bit2 @cv cap_3b u_cap3b_p2@ (.top(vtop_p), .bot(vbot_p[2]));
//bit3 @cv cap_4b u_cap4b_p3@ (.top(vtop_p), .bot(vbot_p[3]));
//bit4 @cv cap_5b u_cap5b_p4@ (.top(vtop_p), .bot(vbot_p[4]));
//bit5 @cv cap_6b u_cap6b_p5@ (.top(vtop_p), .bot(vbot_p[5]));
//bit6 @cv cap_7b u_cap7b_p6@ (.top(vtop_p), .bot(vbot_p[6]));
//bit7 @cv cap_8b u_cap8b_p7@ (.top(vtop_p), .bot(vbot_p[7]));

//bit0 @cv cap_1b u_cap1b_n0@ (.top(vtop_n), .bot(vbot_n[0]));
//bit1 @cv cap_2b u_cap2b_n1@ (.top(vtop_n), .bot(vbot_n[1]));
//bit2 @cv cap_3b u_cap3b_n2@ (.top(vtop_n), .bot(vbot_n[2]));
//bit3 @cv cap_4b u_cap4b_n3@ (.top(vtop_n), .bot(vbot_n[3]));
//bit4 @cv cap_5b u_cap5b_n4@ (.top(vtop_n), .bot(vbot_n[4]));
//bit5 @cv cap_6b u_cap6b_n5@ (.top(vtop_n), .bot(vbot_n[5]));
//bit6 @cv cap_7b u_cap7b_n6@ (.top(vtop_n), .bot(vbot_n[6]));
//bit7 @cv cap_8b u_cap8b_n7@ (.top(vtop_n), .bot(vbot_n[7]));


@cm sw_vcm u_sw_vcmp@ (.in(vcm_p), .out(vtop_p), .sw_ctrl(sample));
@cm sw_vcm u_sw_vcmn@ (.in(vcm_n), .out(vtop_n), .sw_ctrl(sample));

@cv INV_X2B_A9TR u_inv_cm_up_p@ (.Y(cm_up_p), .A(sample));
@cv INV_X2B_A9TR u_inv_cm_up_n@ (.Y(cm_up_n), .A(sample));

//bit0 @cv cap_1b u_cm_up_p0@ (.top(vtop_p), .bot(cm_up_p));
//bit1 @cv cap_1b u_cm_up_p1@ (.top(vtop_p), .bot(cm_up_p));
//bit2 @cv cap_1b u_cm_up_p2@ (.top(vtop_p), .bot(cm_up_p));
//bit3 @cv cap_2b u_cm_up_p3@ (.top(vtop_p), .bot(cm_up_p));
//bit4 @cv cap_3b u_cm_up_p4@ (.top(vtop_p), .bot(cm_up_p));
//bit5 @cv cap_4b u_cm_up_p5@ (.top(vtop_p), .bot(cm_up_p));
//bit6 @cv cap_5b u_cm_up_p6@ (.top(vtop_p), .bot(cm_up_p));
//bit7 @cv cap_6b u_cm_up_p7@ (.top(vtop_p), .bot(cm_up_p));

//bit0 @cv cap_1b u_cm_up_n0@ (.top(vtop_n), .bot(cm_up_n));
//bit1 @cv cap_1b u_cm_up_n1@ (.top(vtop_n), .bot(cm_up_n));
//bit2 @cv cap_1b u_cm_up_n2@ (.top(vtop_n), .bot(cm_up_n));
//bit3 @cv cap_2b u_cm_up_n3@ (.top(vtop_n), .bot(cm_up_n));
//bit4 @cv cap_3b u_cm_up_n4@ (.top(vtop_n), .bot(cm_up_n));
//bit5 @cv cap_4b u_cm_up_n5@ (.top(vtop_n), .bot(cm_up_n));
//bit6 @cv cap_5b u_cm_up_n6@ (.top(vtop_n), .bot(cm_up_n));
//bit7 @cv cap_6b u_cm_up_n7@ (.top(vtop_n), .bot(cm_up_n));

endmodule





