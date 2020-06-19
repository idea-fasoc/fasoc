/////////////////////////////////////////////////////////////
// Created by: Synopsys DC Expert(TM) in wire load mode
// Version   : O-2018.06
// Date      : Thu May 28 21:03:26 2020
/////////////////////////////////////////////////////////////


module sar_logic ( clk_sar, en, sample, value, result_out, cmp, cmp_clk, VSS, VDD, VNW, VPW);
  inout VSS;
  inout VDD;
  inout VNW;
  inout VPW;
  output [7:0] value;
  output [7:0] result_out;
  input clk_sar, en, cmp;
  output sample, cmp_clk;
  wire   netlg_59, netsm_27, netsm_28, netsm_29, netsm_30, netsm_31, netsm_32, netsm_33, netsm_34, netsm_35, netsm_36, netsm_37, netsm_38, netsm_39,
         netsm_40, netsm_41, netsm_42, netsm_43, netsm_44, netsm_45, netsm_46, netsm_47, netsm_48, netsm_49, netsm_50, netsm_51, netsm_52, netsm_53,
         netsm_54, netsm_55, netsm_56, netsm_57, netsm_58, netsm_59, netsm_60, netsm_61, netsm_62, netsm_63, netsm_64, netsm_65, netsm_66, netsm_67,
         netsm_68, netsm_69, netsm_70, netsm_71, netsm_72, netsm_73;
  wire   [1:0] state;
  wire   [7:0] mask;
  wire   [7:0] result;

  DFFQ_X1N_A10P5PP84TR_C14 state_reg_0_ ( .D(netsm_28), .CK(clk_sar), .Q(state[0])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_7_ ( .D(netsm_43), .CK(clk_sar), .Q(result[7]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_6_ ( .D(netsm_42), .CK(clk_sar), .Q(result[6]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_5_ ( .D(netsm_41), .CK(clk_sar), .Q(result[5]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_4_ ( .D(netsm_40), .CK(clk_sar), .Q(result[4]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_3_ ( .D(netsm_39), .CK(clk_sar), .Q(result[3]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_2_ ( .D(netsm_38), .CK(clk_sar), .Q(result[2]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_1_ ( .D(netsm_37), .CK(clk_sar), .Q(result[1]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 result_reg_0_ ( .D(netsm_45), .CK(clk_sar), .Q(result[0]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_7_ ( .D(result[7]), .CKN(en), .Q(
        result_out[7]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_6_ ( .D(result[6]), .CKN(netsm_46), .Q(
        result_out[6]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_5_ ( .D(result[5]), .CKN(en), .Q(
        result_out[5]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_4_ ( .D(result[4]), .CKN(netsm_46), .Q(
        result_out[4]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_3_ ( .D(result[3]), .CKN(en), .Q(
        result_out[3]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_2_ ( .D(result[2]), .CKN(netsm_46), .Q(
        result_out[2]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_1_ ( .D(result[1]), .CKN(en), .Q(
        result_out[1]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFNQ_X1N_A10P5PP84TR_C14 result_out_reg_0_ ( .D(result[0]), .CKN(netsm_46), .Q(
        result_out[0]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 state_reg_1_ ( .D(netsm_27), .CK(clk_sar), .Q(state[1])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_7_ ( .D(netsm_29), .CK(clk_sar), .Q(mask[7]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_6_ ( .D(netsm_30), .CK(clk_sar), .Q(mask[6]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_5_ ( .D(netsm_31), .CK(clk_sar), .Q(mask[5]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_4_ ( .D(netsm_32), .CK(clk_sar), .Q(mask[4]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_3_ ( .D(netsm_33), .CK(clk_sar), .Q(mask[3]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_2_ ( .D(netsm_34), .CK(clk_sar), .Q(mask[2]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_1_ ( .D(netsm_35), .CK(clk_sar), .Q(mask[1]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQ_X1N_A10P5PP84TR_C14 mask_reg_0_ ( .D(netsm_36), .CK(clk_sar), .Q(mask[0]), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 I_1 ( .A(clk_sar), .Y(netlg_59), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  DFFQN_X1N_A10P5PP84TR_C14 value_rst_reg_0_ ( .D(netsm_44), .CK(clk_sar), .QN(netsm_73)
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  AND2_X0P6N_A10P5PP84TR_C14 U57 ( .A(netlg_59), .B(netsm_46), .Y(cmp_clk), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  BUF_X0P6R_A10P5PP84TR_C14 U58 ( .A(en), .Y(netsm_46), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  BUF_X0P6R_A10P5PP84TR_C14 U59 ( .A(netsm_52), .Y(netsm_47), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  BUF_X0P6R_A10P5PP84TR_C14 U60 ( .A(netsm_73), .Y(netsm_48), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NOR2_X0P4N_A10P5PP84TR_C14 U61 ( .A(state[0]), .B(state[1]), .Y(sample), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI21_X0P4N_A10P5PP84TR_C14 U62 ( .A0(sample), .A1(netsm_48), .B0(netsm_46), .Y(netsm_44)
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND2_X0P4N_A10P5PP84TR_C14 U63 ( .A(en), .B(state[0]), .Y(netsm_51), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U64 ( .A(mask[0]), .Y(netsm_72), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND2_X0P4N_A10P5PP84TR_C14 U65 ( .A(netsm_46), .B(state[1]), .Y(netsm_52), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI21_X0P4N_A10P5PP84TR_C14 U66 ( .A0(netsm_51), .A1(netsm_72), .B0(netsm_47), .Y(netsm_27), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U67 ( .A(mask[7]), .Y(netsm_70), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND2_X0P4N_A10P5PP84TR_C14 U68 ( .A(en), .B(sample), .Y(netsm_49), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI21_X0P4N_A10P5PP84TR_C14 U69 ( .A0(netsm_52), .A1(netsm_70), .B0(netsm_49), .Y(netsm_29), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  AO21A1AI2_X0P4N_A10P5PP84TR_C14 U70 ( .A0(state[0]), .A1(state[1]), .B0(
        sample), .C0(netsm_46), .Y(netsm_50), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI21_X0P4N_A10P5PP84TR_C14 U71 ( .A0(mask[0]), .A1(netsm_51), .B0(netsm_50), .Y(netsm_28)
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NOR2_X0P4N_A10P5PP84TR_C14 U72 ( .A(state[1]), .B(netsm_51), .Y(netsm_54), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U73 ( .A(netsm_54), .Y(netsm_53), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U74 ( .A(mask[1]), .Y(netsm_58), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U75 ( .A0(netsm_72), .A1(netsm_52), .B0(netsm_53), .B1(netsm_58), 
        .Y(netsm_36), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U76 ( .A(mask[2]), .Y(netsm_68), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U77 ( .A0(netsm_53), .A1(netsm_68), .B0(netsm_58), .B1(netsm_52), 
        .Y(netsm_35), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U78 ( .A(mask[6]), .Y(netsm_62), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U79 ( .A(mask[5]), .Y(netsm_60), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U80 ( .A0(netsm_53), .A1(netsm_62), .B0(netsm_60), .B1(netsm_52), 
        .Y(netsm_31), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U81 ( .A0(netsm_53), .A1(netsm_70), .B0(netsm_62), .B1(netsm_52), 
        .Y(netsm_30), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U82 ( .A(mask[3]), .Y(netsm_64), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U83 ( .A0(netsm_53), .A1(netsm_64), .B0(netsm_68), .B1(netsm_52), 
        .Y(netsm_34), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U84 ( .A(mask[4]), .Y(netsm_66), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U85 ( .A0(netsm_53), .A1(netsm_66), .B0(netsm_64), .B1(netsm_52), 
        .Y(netsm_33), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U86 ( .A0(netsm_53), .A1(netsm_60), .B0(netsm_66), .B1(netsm_47), 
        .Y(netsm_32), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U87 ( .A(en), .Y(netsm_55), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U88 ( .A(result[7]), .Y(netsm_69), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND2_X0P4N_A10P5PP84TR_C14 U89 ( .A(netsm_54), .B(cmp), .Y(netsm_56), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U90 ( .A0(netsm_55), .A1(netsm_69), .B0(netsm_56), .B1(netsm_70), 
        .Y(netsm_43), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U91 ( .A(result[6]), .Y(netsm_61), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U92 ( .A0(netsm_55), .A1(netsm_61), .B0(netsm_56), .B1(netsm_62), 
        .Y(netsm_42), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U93 ( .A(result[5]), .Y(netsm_59), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U94 ( .A0(netsm_55), .A1(netsm_59), .B0(netsm_56), .B1(netsm_60), 
        .Y(netsm_41), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U95 ( .A(result[3]), .Y(netsm_63), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U96 ( .A0(netsm_55), .A1(netsm_63), .B0(netsm_56), .B1(netsm_64), 
        .Y(netsm_39), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U97 ( .A(result[4]), .Y(netsm_65), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U98 ( .A0(netsm_55), .A1(netsm_65), .B0(netsm_56), .B1(netsm_66), 
        .Y(netsm_40), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U99 ( .A(result[1]), .Y(netsm_57), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U100 ( .A0(netsm_55), .A1(netsm_57), .B0(netsm_56), .B1(netsm_58), 
        .Y(netsm_37), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U101 ( .A(result[2]), .Y(netsm_67), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U102 ( .A0(netsm_55), .A1(netsm_67), .B0(netsm_56), .B1(netsm_68), 
        .Y(netsm_38), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  INVP_X0P6F_A10P5PP84TR_C14 U103 ( .A(result[0]), .Y(netsm_71), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  OAI22_X0P4N_A10P5PP84TR_C14 U104 ( .A0(netsm_72), .A1(netsm_56), .B0(netsm_55), .B1(netsm_71), 
        .Y(netsm_45), .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U105 ( .A(netsm_58), .B(netsm_57), .C(netsm_73), .Y(value[1])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U106 ( .A(netsm_60), .B(netsm_59), .C(netsm_73), .Y(value[5])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U107 ( .A(netsm_62), .B(netsm_61), .C(netsm_73), .Y(value[6])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U108 ( .A(netsm_64), .B(netsm_63), .C(netsm_73), .Y(value[3])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U109 ( .A(netsm_66), .B(netsm_65), .C(netsm_73), .Y(value[4])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U110 ( .A(netsm_68), .B(netsm_67), .C(netsm_73), .Y(value[2])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U111 ( .A(netsm_70), .B(netsm_69), .C(netsm_73), .Y(value[7])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
  NAND3_X0P4N_A10P5PP84TR_C14 U112 ( .A(netsm_72), .B(netsm_71), .C(netsm_48), .Y(value[0])
        , .VSS(VSS), .VDD(VDD), .VNW(VNW), .VPW(VPW));
endmodule

