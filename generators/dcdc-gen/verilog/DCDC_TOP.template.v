// Designed by Jeongsup Lee

module DCDC_TOP (
    //inout VDD,
    //inout VSS,
    //inout AVDD,
    //inout GND,
    //inout VOUT,

    input clk,

	input dummy_in,
	output reg dummy_out
);

    parameter DCDC_NUM_STAGE = 3;
    parameter DCDC_CONFIG = 8; //i.e. 4'b1000
    parameter DCDC_CAP_SIZE = 48;
    parameter DCDC_SW_SIZE = 12;

    wire w_clk0, w_clk0b, w_clk1, w_clk1b;

    //wire[DCDC_NUM_STAGE-1:0] y0_top, y0_bot, y1_top, y1_bot;
    //wire[DCDC_NUM_STAGE-1:0] w_vint;

    //assign VOUT = w_vint[DCDC_NUM_STAGE-1];

    always @ (posedge clk) begin
		dummy_out <= ~dummy_in;
    end

    genvar i, j;
    generate
        for(i=0; i<DCDC_NUM_STAGE; i=i+1) begin: gen_stage
            for(j=0; (j==0)||(j<(DCDC_SW_SIZE>>(DCDC_NUM_STAGE-1-i))); j=j+1) begin: gen_conv
                if(i==0)
                    DCDC_CONV2to1 u_DCDC_CONV2to1 (
                      //.VDD(VDD),
                      //.VSS(VSS),
                      //.vhigh(AVDD),
                      //.vlow(GND),
                      //.vmid(w_vint[i]),
                      //.y1_top(y1_top[i]),
                      //.y0_top(y0_top[i]),
                      //.y1_bot(y1_bot[i]),
                      //.y0_bot(y0_bot[i]),

                        .clk0(w_clk0),
                        .clk0b(w_clk0b),
                        .clk1(w_clk1),
                        .clk1b(w_clk1b)
                    );
                else if((DCDC_CONFIG>>i)&1'b1)
                    DCDC_CONV2to1 u_DCDC_CONV2to1 (
                      //.VDD(VDD),
                      //.VSS(VSS),
                      //.vhigh(AVDD),
                      //.vlow(w_vint[i-1]),
                      //.vmid(w_vint[i]),
                      //.y1_top(y1_top[i]),
                      //.y0_top(y0_top[i]),
                      //.y1_bot(y1_bot[i]),
                      //.y0_bot(y0_bot[i]),

                        .clk0(w_clk0),
                        .clk0b(w_clk0b),
                        .clk1(w_clk1),
                        .clk1b(w_clk1b)
                    );
                else
                    DCDC_CONV2to1 u_DCDC_CONV2to1 (
                      //.VDD(VDD),
                      //.VSS(VSS),
                      //.vhigh(w_vint[i-1]),
                      //.vlow(GND),
                      //.vmid(w_vint[i]),
                      //.y1_top(y1_top[i]),
                      //.y0_top(y0_top[i]),
                      //.y1_bot(y1_bot[i]),
                      //.y0_bot(y0_bot[i]),

                        .clk0(w_clk0),
                        .clk0b(w_clk0b),
                        .clk1(w_clk1),
                        .clk1b(w_clk1b)
                    );
            end

            for(j=0; (j==0)||(j<(DCDC_CAP_SIZE>>(DCDC_NUM_STAGE-1-i))); j=j+1) begin: gen_cap
                DCDC_CAP_UNIT u0_DCDC_CAP_UNIT (
                  //.top(y0_top[i]),
                  //.bot(y0_bot[i])
                );

                DCDC_CAP_UNIT u1_DCDC_CAP_UNIT (
                  //.top(y1_top[i]),
                  //.bot(y1_bot[i])
                );
            end
        end
    endgenerate

    DCDC_NOV_CLKGEN u_DCDC_NOV_CLKGEN (
      //.VDD(VDD),
      //.VSS(VSS),
        
        .clk(clk),
        .clk0(w_clk0),
        .clk0b(w_clk0b),
        .clk1(w_clk1),
        .clk1b(w_clk1b)
    );

endmodule
