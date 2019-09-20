/////////////////////////////////////////////////////////////
// Created by: Synopsys DC Expert(TM) in wire load mode
// Version   : L-2016.03-SP2
// Date      : Sun Dec  9 23:32:14 2018
/////////////////////////////////////////////////////////////

module SC_AUTO ( rst, rstb, clk0, clk0b, clk1, clk1b, VSS, VOUT, VDD);
  input rst, rstb, clk0, clk0b, clk1, clk1b;
  inout	VSS, VDD, VOUT;
@@   @c1_1st sc_temp_a@ni ( .rst(rst), .rstb(rstb), .clk0(clk0), .clk0b(clk0b), .clk1(clk1), .clk1b(clk1b), .VSS(VSS), .VOUT(VOUT), .VDD(VDD));
@@ @s2 @c2_2nd_@u2 sc_temp_b@nj ( .rst(rst), .rstb(rstb), .clk0(clk0), .clk0b(clk0b), .clk1(clk1), .clk1b(clk1b), .VSS(@g2), .VOUT(VOUT2), .VDD(@d2));
@@ @s3 @c3_3rd_@u3 sc_temp_c@nk ( .rst(rst), .rstb(rstb), .clk0(clk0), .clk0b(clk0b), .clk1(clk1), .clk1b(clk1b), .VSS(@g3), .VOUT(VOUT3), .VDD(@d3));
endmodule

