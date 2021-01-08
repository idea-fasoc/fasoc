
module sar_logic ( clk_sar, en, sample, value, result_out, cmp, cmp_clk );
  output [7:0] value;
  output [7:0] result_out;
  input clk_sar, en, cmp;
  output sample, cmp_clk;
  wire   n104, n105, n106, n107, n108, n109, n110, n111, state_1_, N58, N61,
         n1, n2, n3, n4, n7, n8, n9, n10, n11, n12, n13, n30, n31, n32, n33,
         n34, n36, n37, n38, n39, n40, n41, n42, n43, n44, n45, n46, n47, n48,
         n49, n50, n51, n52, n53, n54, n55, n56, n57, n59, n61, n63, n65, n67,
         n69, n71, n80, n81, n82, n83, n84, n85, n86, n87, n88, n90, n92, n93,
         n94, n95, n96, n97, n98, n99, n100, n101, n102, n103, n112;
  wire   [7:0] result;

  DFFQN_X3M_A9TR mask_reg_0_ ( .D(n47), .CK(clk_sar), .QN(n3) );
  DFFQN_X3M_A9TR state_reg_0_ ( .D(n45), .CK(clk_sar), .QN(n2) );
  A2DFFQ_X4M_A9TR state_reg_1_ ( .A(n1), .B(n112), .CK(clk_sar), .Q(state_1_)
         );
  DFFQN_X3M_A9TR mask_reg_6_ ( .D(n38), .CK(clk_sar), .QN(n8) );
  DFFQN_X3M_A9TR mask_reg_5_ ( .D(n39), .CK(clk_sar), .QN(n9) );
  DFFQN_X3M_A9TR mask_reg_4_ ( .D(n40), .CK(clk_sar), .QN(n10) );
  DFFQN_X3M_A9TR mask_reg_3_ ( .D(n41), .CK(clk_sar), .QN(n11) );
  DFFQN_X3M_A9TR mask_reg_2_ ( .D(n42), .CK(clk_sar), .QN(n12) );
  DFFQN_X3M_A9TR mask_reg_1_ ( .D(n43), .CK(clk_sar), .QN(n13) );
  DFFQ_X4M_A9TR result_reg_7_ ( .D(n30), .CK(clk_sar), .Q(result[7]) );
  DFFQ_X4M_A9TR result_reg_6_ ( .D(n31), .CK(clk_sar), .Q(result[6]) );
  DFFQ_X4M_A9TR result_reg_5_ ( .D(n32), .CK(clk_sar), .Q(result[5]) );
  DFFQ_X4M_A9TR result_reg_4_ ( .D(n33), .CK(clk_sar), .Q(result[4]) );
  DFFQ_X4M_A9TR result_reg_3_ ( .D(n34), .CK(clk_sar), .Q(result[3]) );
  DFFQ_X4M_A9TR result_reg_1_ ( .D(n36), .CK(clk_sar), .Q(result[1]) );
  DFFQ_X4M_A9TR result_reg_0_ ( .D(n37), .CK(clk_sar), .Q(result[0]) );
  INV_X16B_A9TR I_1 ( .A(clk_sar), .Y(N61) );
  DFFNQ_X2M_A9TR result_out_reg_7_ ( .D(result[7]), .CKN(en), .Q(n104) );
  DFFNQ_X2M_A9TR result_out_reg_6_ ( .D(result[6]), .CKN(n52), .Q(n105) );
  DFFNQ_X2M_A9TR result_out_reg_5_ ( .D(result[5]), .CKN(en), .Q(n106) );
  DFFNQ_X2M_A9TR result_out_reg_4_ ( .D(result[4]), .CKN(n52), .Q(n107) );
  DFFNQ_X2M_A9TR result_out_reg_3_ ( .D(result[3]), .CKN(en), .Q(n108) );
  DFFNQ_X2M_A9TR result_out_reg_2_ ( .D(result[2]), .CKN(n52), .Q(n109) );
  DFFNQ_X2M_A9TR result_out_reg_1_ ( .D(result[1]), .CKN(en), .Q(n110) );
  DFFNQ_X2M_A9TR result_out_reg_0_ ( .D(result[0]), .CKN(n52), .Q(n111) );
  A2DFFQN_X3M_A9TR mask_reg_7_ ( .A(n50), .B(n44), .CK(clk_sar), .QN(n7) );
  A2DFFQN_X3M_A9TR result_reg_2_ ( .A(n50), .B(n51), .CK(clk_sar), .QN(
        result[2]) );
  A2DFFQN_X3M_A9TR value_rst_reg_0_ ( .A(n50), .B(n46), .CK(clk_sar), .QN(n4)
         );
  INV_X7P5M_A9TR U52 ( .A(n56), .Y(n52) );
  NAND2_X8M_A9TR U53 ( .A(N61), .B(n52), .Y(n87) );
  NOR3_X1A_A9TR U54 ( .A(state_1_), .B(n2), .C(n55), .Y(n92) );
  NAND2_X1A_A9TR U55 ( .A(n92), .B(cmp), .Y(n93) );
  INV_X1M_A9TR U56 ( .A(n92), .Y(n94) );
  OA22_X0P5M_A9TR U57 ( .A0(n98), .A1(n55), .B0(n12), .B1(n93), .Y(n51) );
  NAND2_X0P5M_A9TR U58 ( .A(en), .B(N58), .Y(n48) );
  OAI21_X0P5M_A9TR U59 ( .A0(n7), .A1(n95), .B0(n48), .Y(n44) );
  OAI31_X0P5M_A9TR U60 ( .A0(n3), .A1(state_1_), .A2(n2), .B0(n52), .Y(n49) );
  AOI21_X0P5M_A9TR U61 ( .A0(state_1_), .A1(n2), .B0(n49), .Y(n45) );
  TIEHI_X1M_A9TR U62 ( .Y(n50) );
  INV_X16B_A9TR U63 ( .A(n87), .Y(cmp_clk) );
  INV_X4M_A9TR U64 ( .A(n53), .Y(n54) );
  INV_X4M_A9TR U65 ( .A(n4), .Y(n53) );
  INV_X13M_A9TR U66 ( .A(en), .Y(n56) );
  AND3_X2M_A9TR U67 ( .A(n3), .B(n4), .C(n96), .Y(n86) );
  OAI22_X1M_A9TR U68 ( .A0(n3), .A1(n95), .B0(n13), .B1(n94), .Y(n47) );
  OAI22_X1M_A9TR U69 ( .A0(n13), .A1(n95), .B0(n12), .B1(n94), .Y(n43) );
  NAND3_X2M_A9TR U70 ( .A(n10), .B(n54), .C(n100), .Y(n83) );
  OAI22_X1M_A9TR U71 ( .A0(n10), .A1(n93), .B0(n55), .B1(n100), .Y(n33) );
  NAND3_X2M_A9TR U72 ( .A(n13), .B(n4), .C(n97), .Y(n80) );
  OAI22_X1M_A9TR U73 ( .A0(n11), .A1(n93), .B0(n55), .B1(n99), .Y(n34) );
  OAI22_X1M_A9TR U74 ( .A0(n7), .A1(n93), .B0(n55), .B1(n103), .Y(n30) );
  OAI22_X1M_A9TR U75 ( .A0(n11), .A1(n95), .B0(n10), .B1(n94), .Y(n41) );
  OAI22_X1M_A9TR U76 ( .A0(n8), .A1(n93), .B0(n55), .B1(n102), .Y(n31) );
  OAI22_X1M_A9TR U77 ( .A0(n8), .A1(n95), .B0(n7), .B1(n94), .Y(n38) );
  OAI22_X1M_A9TR U78 ( .A0(n13), .A1(n93), .B0(n55), .B1(n97), .Y(n36) );
  OAI22_X1M_A9TR U79 ( .A0(n9), .A1(n95), .B0(n8), .B1(n94), .Y(n39) );
  OAI22_X1M_A9TR U80 ( .A0(n9), .A1(n93), .B0(n56), .B1(n101), .Y(n32) );
  NAND3_X2M_A9TR U81 ( .A(n12), .B(n4), .C(n98), .Y(n81) );
  NAND3_X2M_A9TR U82 ( .A(n7), .B(n54), .C(n103), .Y(n88) );
  NAND3_X2M_A9TR U83 ( .A(n11), .B(n54), .C(n99), .Y(n82) );
  NAND3_X2M_A9TR U84 ( .A(n9), .B(n54), .C(n101), .Y(n84) );
  OAI22_X1M_A9TR U85 ( .A0(n12), .A1(n95), .B0(n11), .B1(n94), .Y(n42) );
  OAI22_X1M_A9TR U86 ( .A0(n10), .A1(n95), .B0(n9), .B1(n94), .Y(n40) );
  NAND3_X2M_A9TR U87 ( .A(n8), .B(n54), .C(n102), .Y(n85) );
  OAI22_X1M_A9TR U88 ( .A0(n3), .A1(n93), .B0(n96), .B1(n55), .Y(n37) );
  INV_X1M_A9TR U89 ( .A(result[3]), .Y(n99) );
  NOR2B_X2M_A9TR U90 ( .AN(n2), .B(state_1_), .Y(N58) );
  INV_X1M_A9TR U91 ( .A(result[4]), .Y(n100) );
  INV_X1M_A9TR U92 ( .A(result[1]), .Y(n97) );
  INV_X1M_A9TR U93 ( .A(result[6]), .Y(n102) );
  INV_X1M_A9TR U94 ( .A(result[5]), .Y(n101) );
  INV_X1M_A9TR U95 ( .A(result[7]), .Y(n103) );
  INV_X1M_A9TR U96 ( .A(result[2]), .Y(n98) );
  INV_X1M_A9TR U97 ( .A(result[0]), .Y(n96) );
  INV_X1M_A9TR U98 ( .A(en), .Y(n55) );
  INV_X0P5B_A9TR U99 ( .A(n111), .Y(n57) );
  INV_X16M_A9TR U100 ( .A(n57), .Y(result_out[0]) );
  INV_X0P5B_A9TR U101 ( .A(n110), .Y(n59) );
  INV_X16M_A9TR U102 ( .A(n59), .Y(result_out[1]) );
  INV_X0P5B_A9TR U103 ( .A(n109), .Y(n61) );
  INV_X16M_A9TR U104 ( .A(n61), .Y(result_out[2]) );
  INV_X0P5B_A9TR U105 ( .A(n108), .Y(n63) );
  INV_X16M_A9TR U106 ( .A(n63), .Y(result_out[3]) );
  INV_X0P5B_A9TR U107 ( .A(n107), .Y(n65) );
  INV_X16M_A9TR U108 ( .A(n65), .Y(result_out[4]) );
  INV_X0P5B_A9TR U109 ( .A(n106), .Y(n67) );
  INV_X16M_A9TR U110 ( .A(n67), .Y(result_out[5]) );
  INV_X0P5B_A9TR U111 ( .A(n105), .Y(n69) );
  INV_X16M_A9TR U112 ( .A(n69), .Y(result_out[6]) );
  INV_X0P5B_A9TR U113 ( .A(n104), .Y(n71) );
  INV_X16M_A9TR U114 ( .A(n71), .Y(result_out[7]) );
  INV_X16M_A9TR U115 ( .A(n86), .Y(value[0]) );
  BUF_X16M_A9TR U116 ( .A(n80), .Y(value[1]) );
  BUF_X16M_A9TR U117 ( .A(n81), .Y(value[2]) );
  BUF_X16M_A9TR U118 ( .A(n82), .Y(value[3]) );
  BUF_X16M_A9TR U119 ( .A(n83), .Y(value[4]) );
  BUF_X16M_A9TR U120 ( .A(n84), .Y(value[5]) );
  BUF_X16M_A9TR U121 ( .A(n85), .Y(value[6]) );
  BUF_X16M_A9TR U122 ( .A(n88), .Y(value[7]) );
  INV_X16M_A9TR U123 ( .A(n90), .Y(sample) );
  INV_X4M_A9TR U124 ( .A(N58), .Y(n90) );
  OAI21_X0P5M_A9TR U125 ( .A0(N58), .A1(n4), .B0(n52), .Y(n46) );
  NAND2_X0P5M_A9TR U126 ( .A(state_1_), .B(n52), .Y(n95) );
  OAI21B_X1M_A9TR U127 ( .A0(n3), .A1(n2), .B0N(state_1_), .Y(n1) );
  BUFH_X1M_A9TR U128 ( .A(en), .Y(n112) );
endmodule

