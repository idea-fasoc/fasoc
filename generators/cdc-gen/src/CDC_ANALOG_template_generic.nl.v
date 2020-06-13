module CDC_ANALOG (PRECHARGE, PRECHARGEB, in_vin, IN, INB, OSEN, LCOUT);
inout in_vin;
input  PRECHARGE, PRECHARGEB, IN, INB;
output OSEN, LCOUT;


wire pre;

INVCHAIN_ISOVDD a_iniso_0 (.IN(LCOUT), .OUT(OSEN)); 
//INVCHAIN a_iniso_1 (.IN(LCOUT), .OUT(OREF));

@@ @na a_precharge_@ni (.IN(pre), .VIN(in_vin));

@@ @nb a_lc_2 (.A(PRECHARGE), .AB(PRECHARGEB), .Y(pre));
@@ @nb a_lc_1 (.A(IN), .AB(INB), .Y(LCOUT));


//BUFX4HVT_ISOVDD a_buf_0 (.A(lc_out), .Y(LCOUT));
//BUFX4HVT a_buf_1 (.A(IN), .Y(in_buf));
//INVX1HVT a_inv_0 (.A(IN), .Y(inb));
//BUFX4HVT_ISOVDD a_buf_2 (.A(inb), .Y(inb_buf));:13

endmodule

