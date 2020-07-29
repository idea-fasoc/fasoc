//-----------------------------------------------------------------------------
// The confidential and proprietary information contained in this file may
// only be used by a person authorised under and to the extent permitted
// by a subsisting licensing agreement from ARM Limited.
//
//            (C) COPYRIGHT 2010-2013 ARM Limited.
//                ALL RIGHTS RESERVED
//
// This entire notice must be reproduced on all copies of this file
// and copies of this file may only be made by a person if such person is
// permitted to do so under the terms of a subsisting license agreement
// from ARM Limited.
//
//      SVN Information
//
//      Checked In          : $Date: 2013-04-12 18:34:22 +0100 (Fri, 12 Apr 2013) $
//
//      Revision            : $Revision: 243882 $
//
//      Release Information : Cortex-M System Design Kit-r1p0-00rel0
//
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
// Abstract : APB sub system
//-----------------------------------------------------------------------------
module cmsdk_fasoc_apb_subsystem #(
  parameter INCLUDE_APB_0  = 1, // Simple slave/gpio
  parameter INCLUDE_APB_1  = 1, // UART
  parameter INCLUDE_APB_2  = 1, // LDO0
  parameter INCLUDE_APB_3  = 1, // LDO1
  parameter INCLUDE_APB_4  = 1, // LDO2
  parameter INCLUDE_APB_5  = 1, // PLL1
  parameter INCLUDE_APB_6  = 1, // PLL2
  parameter INCLUDE_APB_7  = 0, // UNUSED
  parameter INCLUDE_APB_8  = 1, // MEM0
  // parameter INCLUDE_APB_9  = 1, // Used by MEM0
  // parameter INCLUDE_APB_10 = 1, // Used by MEM0
  // parameter INCLUDE_APB_11 = 1, // Used by MEM0
  parameter INCLUDE_APB_12 = 1, // TEMP0
  parameter INCLUDE_APB_13 = 1, // TEMP1
  parameter INCLUDE_APB_14 = 0, // CDC1
  parameter INCLUDE_APB_15 = 0, // CDC2




  // Big endian - Add additional endian conversion logic to support big endian.
  //              (for ARM internal testing and evaluation of the processor in
  //              big endian configuration).
  //              0 = little endian, 1 = big endian
  //
  //              The example systems including this APB subsystem are designed as
  //              little endian. Most of the peripherals and memory system are
  //              little endian. This parameter is introduced to allows ARM to
  //              perform system level tests to verified behaviour of bus
  //              components in big endian configuration, and to allow designers
  //              to evaluate the processor in big endian configuration.
  //
  //              Use of this parameter is not recommended for actual product
  //              development as this adds extra hardware. For big endian systems
  //              ideally the peripherals should be modified to use a big endian
  //              programmer's model.
  parameter BE             = 0
) (
  // --------------------------------------------------------------------------
  // Port Definitions
  // --------------------------------------------------------------------------
  // AHB interface for AHB to APB bridge

  input  wire        HCLK               ,
  input  wire        HRESETn            ,

  input  wire        HSEL               ,
  input  wire [15:0] HADDR              ,
  input  wire [ 1:0] HTRANS             ,
  input  wire        HWRITE             ,
  input  wire [ 2:0] HSIZE              ,
  input  wire [ 3:0] HPROT              ,
  input  wire        HREADY             ,
  input  wire [31:0] HWDATA             ,
  output wire        HREADYOUT          ,
  output wire [31:0] HRDATA             ,
  output wire        HRESP              ,

  input  wire        PCLK               , // Peripheral clock
  input  wire        PCLKG              , // Gate PCLK for bus interface only
  input  wire        PCLKEN             , // Clock divider for AHB to APB bridge
  input  wire        PRESETn            , // APB reset

  output wire        APBACTIVE          ,

  // Peripherals

  output wire [31:0] GPIO_O             ,


  // UART
  input  wire        uart_rxd           ,
  output wire        uart_txd           ,
  output wire        uart_txen          ,

  // Pad pins
  input  wire        LDO_SPI_RESETn     ,
  input  wire [ 1:0] LDO_SPI_SS         ,
  input  wire        LDO_SPI_SCLK       ,
  input  wire        LDO_SPI_MOSI       ,
  output wire        LDO_SPI_MISO       ,
  input  wire        LDO_SPI_APB_SEL    ,
  input  wire        LDO_VREF           ,
  // inout  wire        LDO_0_VREG         ,
  // inout  wire        LDO_1_VREG         ,
  // inout  wire        LDO_2_VREG         ,
  input  wire        LDO_REFCLK         ,


  input  wire        MEM_DATA_REQ       ,
  input  wire        MEM_WE             ,
  input  wire        MEM_TEST_MODE      ,
  input  wire        MEM_CLK_IN         ,
  input  wire        MEM_RESET          ,
  input  wire        MEM_SPI_CLOCK      ,
  input  wire        MEM_SPI_MOSI       ,
  input  wire        MEM_SPI_RST        ,
  input  wire        MEM_SPI_SCLK       ,
  input  wire        MEM_SPI_SS         ,
  output wire        MEM_DOUT32         ,
  output wire        MEM_SPI_MISO       ,

  input  wire        PLL_CLKREF0        ,
  input  wire        PLL_CLKREF1        ,
  output wire        PLL_CLKOUT0        ,
  output wire        PLL_CLKOUT1        ,

  output wire        TEMP_0_CLKOUT      ,
  output wire        TEMP_1_CLKOUT      ,
  input  wire        TEMP_0_REFCLK      ,
  input  wire        TEMP_1_REFCLK      ,
  input  wire        VIN_TEMPSENSE      ,

  // Interrupt outputs
  output wire [31:0] apbsubsys_interrupt,



  output wire [15:0] i_paddr           ,
  output wire        i_psel            ,

// wire from APB slave mux to APB bridge
  input  wire        i_pready_mux      ,
  input  wire [31:0] i_prdata_mux      ,
  input  wire        i_pslverr_mux     ,

// Peripheral signals
  input  wire        apb0_psel         ,
  output wire [31:0] apb0_prdata       ,
  output wire        apb0_pready       ,
  output wire        apb0_pslverr      ,

  input  wire        apb1_psel         ,
  output wire [31:0] apb1_prdata       ,
  output wire        apb1_pready       ,
  output wire        apb1_pslverr      ,

  input  wire        apb2_psel         ,
  output wire [31:0] apb2_prdata       ,
  output wire        apb2_pready       ,
  output wire        apb2_pslverr      ,

  input  wire        apb3_psel         ,
  output wire [31:0] apb3_prdata       ,
  output wire        apb3_pready       ,
  output wire        apb3_pslverr      ,

  input  wire        apb4_psel         ,
  output wire [31:0] apb4_prdata       ,
  output wire        apb4_pready       ,
  output wire        apb4_pslverr      ,

  input  wire        apb5_psel         ,
  output wire [31:0] apb5_prdata       ,
  output wire        apb5_pready       ,
  output wire        apb5_pslverr      ,

  input  wire        apb6_psel         ,
  output wire [31:0] apb6_prdata       ,
  output wire        apb6_pready       ,
  output wire        apb6_pslverr      ,

  input  wire        apb7_psel         ,
  output wire [31:0] apb7_prdata       ,
  output wire        apb7_pready       ,
  output wire        apb7_pslverr      ,

  input  wire        apb8_psel         ,
  output wire [31:0] apb8_prdata       ,
  output wire        apb8_pready       ,
  output wire        apb8_pslverr      ,

  input  wire        apb9_psel         ,
  output wire [31:0] apb9_prdata       ,
  output wire        apb9_pready       ,
  output wire        apb9_pslverr      ,

  input  wire        apb10_psel        ,
  output wire [31:0] apb10_prdata      ,
  output wire        apb10_pready      ,
  output wire        apb10_pslverr     ,

  input  wire        apb11_psel        ,
  output wire [31:0] apb11_prdata      ,
  output wire        apb11_pready      ,
  output wire        apb11_pslverr     ,

  input  wire        apb12_psel        ,
  output wire [31:0] apb12_prdata      ,
  output wire        apb12_pready      ,
  output wire        apb12_pslverr     ,

  input  wire        apb13_psel        ,
  output wire [31:0] apb13_prdata      ,
  output wire        apb13_pready      ,
  output wire        apb13_pslverr     ,

  input  wire        apb14_psel        ,
  output wire [31:0] apb14_prdata      ,
  output wire        apb14_pready      ,
  output wire        apb14_pslverr     ,

  input  wire        apb15_psel        ,
  output wire [31:0] apb15_prdata      ,
  output wire        apb15_pready      ,
  output wire        apb15_pslverr
);

  // --------------------------------------------------------------------------
  // Internal wires
  // --------------------------------------------------------------------------
  // wire [15:0] i_paddr  ;
  // wire        i_psel   ;
  wire        i_penable;
  wire        i_pwrite ;
  wire [ 2:0] i_pprot  ;
  wire [ 3:0] i_pstrb  ;
  wire [31:0] i_pwdata ;

  // wire from APB slave mux to APB bridge
  // wire        i_pready_mux ;
  // wire [31:0] i_prdata_mux ;
  // wire        i_pslverr_mux;

  // // Peripheral signals
  // wire        apb0_psel   ;
  // wire [31:0] apb0_prdata ;
  // wire        apb0_pready ;
  // wire        apb0_pslverr;

  // wire        apb1_psel   ;
  // wire [31:0] apb1_prdata ;
  // wire        apb1_pready ;
  // wire        apb1_pslverr;

  // wire        apb2_psel   ;
  // wire [31:0] apb2_prdata ;
  // wire        apb2_pready ;
  // wire        apb2_pslverr;

  // wire        apb3_psel   ;
  // wire [31:0] apb3_prdata ;
  // wire        apb3_pready ;
  // wire        apb3_pslverr;

  // wire        apb4_psel   ;
  // wire [31:0] apb4_prdata ;
  // wire        apb4_pready ;
  // wire        apb4_pslverr;

  // wire        apb5_psel   ;
  // wire [31:0] apb5_prdata ;
  // wire        apb5_pready ;
  // wire        apb5_pslverr;

  // wire        apb6_psel   ;
  // wire [31:0] apb6_prdata ;
  // wire        apb6_pready ;
  // wire        apb6_pslverr;

  // wire        apb7_psel   ;
  // wire [31:0] apb7_prdata ;
  // wire        apb7_pready ;
  // wire        apb7_pslverr;

  // wire        apb8_psel   ;
  // wire [31:0] apb8_prdata ;
  // wire        apb8_pready ;
  // wire        apb8_pslverr;

  // wire        apb9_psel   ;
  // wire [31:0] apb9_prdata ;
  // wire        apb9_pready ;
  // wire        apb9_pslverr;

  // wire        apb10_psel   ;
  // wire [31:0] apb10_prdata ;
  // wire        apb10_pready ;
  // wire        apb10_pslverr;

  // wire        apb11_psel   ;
  // wire [31:0] apb11_prdata ;
  // wire        apb11_pready ;
  // wire        apb11_pslverr;

  // wire        apb12_psel   ;
  // wire [31:0] apb12_prdata ;
  // wire        apb12_pready ;
  // wire        apb12_pslverr;

  // wire        apb13_psel   ;
  // wire [31:0] apb13_prdata ;
  // wire        apb13_pready ;
  // wire        apb13_pslverr;

  // wire        apb14_psel   ;
  // wire [31:0] apb14_prdata ;
  // wire        apb14_pready ;
  // wire        apb14_pslverr;

  // wire        apb15_psel   ;
  // wire [31:0] apb15_prdata ;
  // wire        apb15_pready ;
  // wire        apb15_pslverr;

  // Interrupt signals from peripherals
  wire uart_txint       ;
  wire uart_rxint       ;
  wire uart_txovrint    ;
  wire uart_rxovrint    ;
  wire uart_combined_int;
  wire uart_overflow_int;


  // Synchronized interrupt signals
  wire i_uart_txint       ;
  wire i_uart_rxint       ;
  wire i_uart_overflow_int;

  wire LDO_SPI_0_SS;
  wire LDO_SPI_1_SS;
  wire LDO_SPI_2_SS;

  wire LDO_SPI_0_MISO;
  wire LDO_SPI_1_MISO;
  wire LDO_SPI_2_MISO;


  // endian handling
  wire bigendian;
  assign bigendian = (BE!=0) ? 1'b1 : 1'b0;

  wire [31:0] hwdata_le                                                  ; // Little endian write data
  wire [31:0] hrdata_le                                                  ; // Little endian read data
  wire        reg_be_swap_ctrl_en = HSEL & HTRANS[1] & HREADY & bigendian;
  reg  [ 1:0] reg_be_swap_ctrl                                           ; // registered byte swap control
  wire [ 1:0] nxt_be_swap_ctrl                                           ; // next state of byte swap control

  assign nxt_be_swap_ctrl[1] = bigendian & (HSIZE[1:0]==2'b10); // Swap upper and lower half word
  assign nxt_be_swap_ctrl[0] = bigendian & (HSIZE[1:0]!=2'b00); // Swap byte within hafword

  // Register byte swap control for data phase
  always @(posedge HCLK or negedge HRESETn)
    begin
      if (~HRESETn)
        reg_be_swap_ctrl <= 2'b00;
      else if (reg_be_swap_ctrl_en)
        reg_be_swap_ctrl <= nxt_be_swap_ctrl;
    end

  // swap byte within half word
  wire [31:0] hwdata_mux_1 = (reg_be_swap_ctrl[0] & bigendian) ?
    {HWDATA[23:16],HWDATA[31:24],HWDATA[7:0],HWDATA[15:8]}:
      {HWDATA[31:24],HWDATA[23:16],HWDATA[15:8],HWDATA[7:0]};

  // swap lower and upper half word
  assign hwdata_le = (reg_be_swap_ctrl[1] & bigendian) ?
    {hwdata_mux_1[15: 0],hwdata_mux_1[31:16]}:
    {hwdata_mux_1[31:16],hwdata_mux_1[15:0]};

  // swap byte within half word
  wire [31:0] hrdata_mux_1 = (reg_be_swap_ctrl[0] & bigendian) ?
    {hrdata_le[23:16],hrdata_le[31:24],hrdata_le[ 7:0],hrdata_le[15:8]}:
      {hrdata_le[31:24],hrdata_le[23:16],hrdata_le[15:8],hrdata_le[7:0]};

  // swap lower and upper half word
  assign HRDATA = (reg_be_swap_ctrl[1] & bigendian) ?
    {hrdata_mux_1[15: 0],hrdata_mux_1[31:16]}:
    {hrdata_mux_1[31:16],hrdata_mux_1[15:0]};

  // AHB to APB bus bridge
  cmsdk_ahb_to_apb #(
    .ADDRWIDTH     (16),
    .REGISTER_RDATA(1 ),
    .REGISTER_WDATA(0 )
  ) u_ahb_to_apb (
    // AHB side
    .HCLK     (HCLK         ),
    .HRESETn  (HRESETn      ),
    .HSEL     (HSEL         ),
    .HADDR    (HADDR[15:0]  ),
    .HTRANS   (HTRANS       ),
    .HSIZE    (HSIZE        ),
    .HPROT    (HPROT        ),
    .HWRITE   (HWRITE       ),
    .HREADY   (HREADY       ),
    .HWDATA   (hwdata_le    ),

    .HREADYOUT(HREADYOUT    ), // AHB Outputs
    .HRDATA   (hrdata_le    ),
    .HRESP    (HRESP        ),

    .PADDR    (i_paddr[15:0]),
    .PSEL     (i_psel       ),
    .PENABLE  (i_penable    ),
    .PSTRB    (i_pstrb      ),
    .PPROT    (i_pprot      ),
    .PWRITE   (i_pwrite     ),
    .PWDATA   (i_pwdata     ),

    .APBACTIVE(APBACTIVE    ),
    .PCLKEN   (PCLKEN       ), // APB clock enable signal

    .PRDATA   (i_prdata_mux ),
    .PREADY   (i_pready_mux ),
    .PSLVERR  (i_pslverr_mux)
  );

  // APB slave multiplexer
  // cmsdk_apb_slave_mux #(
  //   // Parameter to determine which ports are used
  //   .PORT0_ENABLE (INCLUDE_APB_0 ), // Simple slave/gpio
  //   .PORT1_ENABLE (INCLUDE_APB_1 ), // UART
  //   .PORT2_ENABLE (INCLUDE_APB_2 ), // LDO0
  //   .PORT3_ENABLE (INCLUDE_APB_3 ), // LDO1
  //   .PORT4_ENABLE (INCLUDE_APB_4 ), // LDO2
  //   .PORT5_ENABLE (INCLUDE_APB_5 ), // PLL1
  //   .PORT6_ENABLE (INCLUDE_APB_6 ), // PLL2
  //   .PORT7_ENABLE (INCLUDE_APB_7 ), // UNUSED
  //   .PORT8_ENABLE (INCLUDE_APB_8 ), // MEM0
  //   .PORT9_ENABLE (INCLUDE_APB_8 ), // Used by MEM0
  //   .PORT10_ENABLE(INCLUDE_APB_8),  // Used by MEM0
  //   .PORT11_ENABLE(INCLUDE_APB_8),  // Used by MEM0
  //   .PORT12_ENABLE(INCLUDE_APB_12), // TEMP0
  //   .PORT13_ENABLE(INCLUDE_APB_13), // TEMP1
  //   .PORT14_ENABLE(INCLUDE_APB_14), // CDC1
  //   .PORT15_ENABLE(INCLUDE_APB_15)  // CDC2
  // ) u_apb_slave_mux (
  //   // Inputs
  //   .DECODE4BIT(i_paddr[15:12]),
  //   .PSEL      (i_psel        ),

  //   // PSEL (output) and return status & data (inputs) for each port
  //   .PSEL0     (apb0_psel     ),
  //   .PREADY0   (apb0_pready   ),
  //   .PRDATA0   (apb0_prdata   ),
  //   .PSLVERR0  (apb0_pslverr  ),

  //   .PSEL1     (apb1_psel     ),
  //   .PREADY1   (apb1_pready   ),
  //   .PRDATA1   (apb1_prdata   ),
  //   .PSLVERR1  (apb1_pslverr  ),

  //   .PSEL2     (apb2_psel     ),
  //   .PREADY2   (apb2_pready   ),
  //   .PRDATA2   (apb2_prdata   ),
  //   .PSLVERR2  (apb2_pslverr  ),

  //   .PSEL3     (apb3_psel     ),
  //   .PREADY3   (apb3_pready   ),
  //   .PRDATA3   (apb3_prdata   ),
  //   .PSLVERR3  (apb3_pslverr  ),

  //   .PSEL4     (apb4_psel     ),
  //   .PREADY4   (apb4_pready   ),
  //   .PRDATA4   (apb4_prdata   ),
  //   .PSLVERR4  (apb4_pslverr  ),

  //   .PSEL5     (apb5_psel     ),
  //   .PREADY5   (apb5_pready   ),
  //   .PRDATA5   (apb5_prdata   ),
  //   .PSLVERR5  (apb5_pslverr  ),

  //   .PSEL6     (apb6_psel     ),
  //   .PREADY6   (apb6_pready   ),
  //   .PRDATA6   (apb6_prdata   ),
  //   .PSLVERR6  (apb6_pslverr  ),

  //   .PSEL7     (apb7_psel     ),
  //   .PREADY7   (apb7_pready   ),
  //   .PRDATA7   (apb7_prdata   ),
  //   .PSLVERR7  (apb7_pslverr  ),

  //   .PSEL8     (apb8_psel     ),
  //   .PREADY8   (apb8_pready   ),
  //   .PRDATA8   (apb8_prdata   ),
  //   .PSLVERR8  (apb8_pslverr  ),

  //   .PSEL9     (apb9_psel     ),
  //   .PREADY9   (apb9_pready   ),
  //   .PRDATA9   (apb9_prdata   ),
  //   .PSLVERR9  (apb9_pslverr  ),

  //   .PSEL10    (apb10_psel    ),
  //   .PREADY10  (apb10_pready  ),
  //   .PRDATA10  (apb10_prdata  ),
  //   .PSLVERR10 (apb10_pslverr ),

  //   .PSEL11    (apb11_psel    ),
  //   .PREADY11  (apb11_pready  ),
  //   .PRDATA11  (apb11_prdata  ),
  //   .PSLVERR11 (apb11_pslverr ),

  //   .PSEL12    (apb12_psel    ),
  //   .PREADY12  (apb12_pready  ),
  //   .PRDATA12  (apb12_prdata  ),
  //   .PSLVERR12 (apb12_pslverr ),

  //   .PSEL13    (apb13_psel    ),
  //   .PREADY13  (apb13_pready  ),
  //   .PRDATA13  (apb13_prdata  ),
  //   .PSLVERR13 (apb13_pslverr ),

  //   .PSEL14    (apb14_psel    ),
  //   .PREADY14  (apb14_pready  ),
  //   .PRDATA14  (apb14_prdata  ),
  //   .PSLVERR14 (apb14_pslverr ),

  //   .PSEL15    (apb15_psel    ),
  //   .PREADY15  (apb15_pready  ),
  //   .PRDATA15  (apb15_prdata  ),
  //   .PSLVERR15 (apb15_pslverr ),

  //   // Output
  //   .PREADY    (i_pready_mux  ),
  //   .PRDATA    (i_prdata_mux  ),
  //   .PSLVERR   (i_pslverr_mux )
  // );

  // -----------------------------------------------------------------
  // APB0

  generate if (INCLUDE_APB_0) begin : gen_apb0
      gpio_apb #(.ID(32'hFA50C0)) u_gpio_apb (
        .PCLK   (PCLK         ), // PCLK for timer operation
        .PRESETn(PRESETn      ), // Reset
        // APB interface inputs
        .PSEL   (apb0_psel    ),
        .PADDR  (i_paddr[11:0]),
        .PENABLE(i_penable    ),
        .PWRITE (i_pwrite     ),
        .PWDATA (i_pwdata     ),

        // APB interface outputs
        .PRDATA (apb0_prdata  ),
        .PREADY (apb0_pready  ),
        .PSLVERR(apb0_pslverr ),

        .GPIO_O (GPIO_O       )
      );
    end else
    begin : gen_no_apb0
      assign apb0_prdata  = {32{1'b0}};
      assign apb0_pready  = 1'b1;
      assign apb0_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB1

  generate if (INCLUDE_APB_1) begin : gen_apb1
      cmsdk_apb_uart u_apb_uart (
        .PCLK     (PCLK             ), // Peripheral clock
        .PCLKG    (PCLKG            ), // Gated PCLK for bus
        .PRESETn  (PRESETn          ), // Reset

        // APB interface inputs
        .PSEL     (apb1_psel        ), // APB interface inputs
        .PADDR    (i_paddr[11:2]    ),
        .PENABLE  (i_penable        ),
        .PWRITE   (i_pwrite         ),
        .PWDATA   (i_pwdata         ),

        // APB interface outputs
        .PRDATA   (apb1_prdata      ), // APB interface outputs
        .PREADY   (apb1_pready      ),
        .PSLVERR  (apb1_pslverr     ),

        // UART signals
        .ECOREVNUM(4'h0             ), // Engineering-change-order revision bits

        .RXD      (uart_rxd         ), // Receive data

        .TXD      (uart_txd         ), // Transmit data
        .TXEN     (uart_txen        ), // Transmit Enabled

        .BAUDTICK (                 ), // Baud rate x16 tick output (for testing)

        .TXINT    (uart_txint       ), // Transmit Interrupt
        .RXINT    (uart_rxint       ), // Receive  Interrupt
        .TXOVRINT (uart_txovrint    ), // Transmit Overrun Interrupt
        .RXOVRINT (uart_rxovrint    ), // Receive  Overrun Interrupt
        .UARTINT  (uart_combined_int)  // Combined Interrupt
      );
    end else
    begin : gen_no_apb1
      assign apb1_prdata  = {32{1'b0}};
      assign apb1_pready  = 1'b1;
      assign apb1_pslverr = 1'b0;

      assign uart_txd          = 1'b1;
      assign uart_txen         = 1'b0;
      assign uart_txint        = 1'b0;
      assign uart_rxint        = 1'b0;
      assign uart_txovrint     = 1'b0;
      assign uart_rxovrint     = 1'b0;
      assign uart_combined_int = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB2

  ldo_mux u_ldo_mux (
    .LDO_SPI_SS(LDO_SPI_SS),
    .LDO_SPI_0_MISO(LDO_SPI_0_MISO),
    .LDO_SPI_1_MISO(LDO_SPI_1_MISO),
    .LDO_SPI_2_MISO(LDO_SPI_2_MISO),

    .LDO_SPI_0_SS(LDO_SPI_0_SS),
    .LDO_SPI_1_SS(LDO_SPI_1_SS),
    .LDO_SPI_2_SS(LDO_SPI_2_SS),
    .LDO_SPI_MISO(LDO_SPI_MISO)
    );

  generate if (INCLUDE_APB_2) begin : gen_apb2
      ldo0_apb #(.ID(32'hFA50C2)) u_ldo_0 (
        // APB Interface
        .PCLK           (PCLK           ), // PCLK for timer operation
        .PRESETn        (PRESETn        ), // Active Low Reset

        // APB interface inputs
        .PSEL           (apb2_psel      ), // Device select
        .PADDR          (i_paddr[11:0]  ), // Address
        .PENABLE        (i_penable      ), // Transfer control
        .PWRITE         (i_pwrite       ), // Write control
        .PWDATA         (i_pwdata       ), // Write data

        // APB interface outputs
        .PRDATA         (apb2_prdata    ), // Read data
        .PREADY         (apb2_pready    ), // Device ready
        .PSLVERR        (apb2_pslverr   ), // Device error response

        .SRESETn        (LDO_SPI_RESETn ), // Active Low Reset
        .SS             (LDO_SPI_0_SS   ), // Slave Select
        .SCLK           (LDO_SPI_SCLK   ), // Serial Clock
        .MOSI           (LDO_SPI_MOSI   ), // Master Out Slave In
        .MISO           (LDO_SPI_0_MISO ), // Master In Slave Out
        .SPI_APB_SEL    (LDO_SPI_APB_SEL), // 0 (SPI), 1 (APB)

        .VREF           (LDO_VREF       ), // Reference voltage in
        // .VREG           (LDO_0_VREG     )  // Regulated voltage
        .CLK           (LDO_REFCLK     )
      );

    end else
    begin : gen_no_apb2
      assign apb2_prdata  = {32{1'b0}};
      assign apb2_pready  = 1'b1;
      assign apb2_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB3

  generate if (INCLUDE_APB_3) begin : gen_apb3
      ldo1_apb #(.ID(32'hFA50C3)) u_ldo_1 (
        // APB Interface
        .PCLK           (PCLK           ), // PCLK for timer operation
        .PRESETn        (PRESETn        ), // Active Low Reset

        // APB interface inputs
        .PSEL           (apb3_psel      ), // Device select
        .PADDR          (i_paddr[11:0]  ), // Address
        .PENABLE        (i_penable      ), // Transfer control
        .PWRITE         (i_pwrite       ), // Write control
        .PWDATA         (i_pwdata       ), // Write data

        // APB interface outputs
        .PRDATA         (apb3_prdata    ), // Read data
        .PREADY         (apb3_pready    ), // Device ready
        .PSLVERR        (apb3_pslverr   ), // Device error response

        .SRESETn        (LDO_SPI_RESETn ), // Active Low Reset
        .SS             (LDO_SPI_1_SS   ), // Slave Select
        .SCLK           (LDO_SPI_SCLK   ), // Serial Clock
        .MOSI           (LDO_SPI_MOSI   ), // Master Out Slave In
        .MISO           (LDO_SPI_1_MISO ), // Master In Slave Out
        .SPI_APB_SEL    (LDO_SPI_APB_SEL), // 0 (SPI), 1 (APB)

        .VREF           (LDO_VREF       ), // Reference voltage in
        // .VREG           (LDO_1_VREG     )  // Regulated voltage
        .CLK           (LDO_REFCLK     )
      );

    end else
    begin : gen_no_apb3
      assign apb3_prdata  = {32{1'b0}};
      assign apb3_pready  = 1'b1;
      assign apb3_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB4

  generate if (INCLUDE_APB_4) begin : gen_apb4
      ldo2_apb #(.ID(32'hFA50C4)) u_ldo_2 (
        // APB Interface
        .PCLK           (PCLK           ), // PCLK for timer operation
        .PRESETn        (PRESETn        ), // Active Low Reset

        // APB interface inputs
        .PSEL           (apb4_psel      ), // Device select
        .PADDR          (i_paddr[11:0]  ), // Address
        .PENABLE        (i_penable      ), // Transfer control
        .PWRITE         (i_pwrite       ), // Write control
        .PWDATA         (i_pwdata       ), // Write data

        // APB interface outputs
        .PRDATA         (apb4_prdata    ), // Read data
        .PREADY         (apb4_pready    ), // Device ready
        .PSLVERR        (apb4_pslverr   ), // Device error response

        .SRESETn        (LDO_SPI_RESETn ), // Active Low Reset
        .SS             (LDO_SPI_2_SS   ), // Slave Select
        .SCLK           (LDO_SPI_SCLK   ), // Serial Clock
        .MOSI           (LDO_SPI_MOSI   ), // Master Out Slave In
        .MISO           (LDO_SPI_2_MISO ), // Master In Slave Out
        .SPI_APB_SEL    (LDO_SPI_APB_SEL), // 0 (SPI), 1 (APB)

        .VREF           (LDO_VREF       ), // Reference voltage in
        // .VREG           (LDO_2_VREG     )  // Regulated voltage
        .CLK           (LDO_REFCLK     )
      );
    end else
    begin : gen_no_apb4
      assign apb4_prdata  = {32{1'b0}};
      assign apb4_pready  = 1'b1;
      assign apb4_pslverr = 1'b0;
    end endgenerate



  // -----------------------------------------------------------------
  // APB5

  generate if (INCLUDE_APB_5) begin : gen_apb5
      pll0_apb #(
        .ID(32'hFA50C5)
      ) u_pll_0 (
        .PCLK   (PCLK         ),
        .PRESETn(PRESETn      ),

        .PSEL   (apb5_psel    ),
        .PADDR  (i_paddr[11:0]),
        .PENABLE(i_penable    ),
        .PWRITE (i_pwrite     ),
        .PWDATA (i_pwdata     ),

        .PRDATA (apb5_prdata  ),
        .PREADY (apb5_pready  ),
        .PSLVERR(apb5_pslverr ),

        .CLKREF (PLL_CLKREF0),
        .CLK_OUT (PLL_CLKOUT0)
      );

    end else
    begin : gen_no_apb5
      assign apb5_prdata  = {32{1'b0}};
      assign apb5_pready  = 1'b1;
      assign apb5_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB6

  generate if (INCLUDE_APB_6) begin : gen_apb6
      pll1_apb #(
        .ID(32'hFA50C6)
      ) u_pll_1 (
        .PCLK   (PCLK         ),
        .PRESETn(PRESETn      ),

        .PSEL   (apb6_psel    ),
        .PADDR  (i_paddr[11:0]),
        .PENABLE(i_penable    ),
        .PWRITE (i_pwrite     ),
        .PWDATA (i_pwdata     ),

        .PRDATA (apb6_prdata  ),
        .PREADY (apb6_pready  ),
        .PSLVERR(apb6_pslverr ),

        .CLKREF (PLL_CLKREF1),
        .CLK_OUT (PLL_CLKOUT1)
      );

    end else
    begin : gen_no_apb6
      assign apb6_prdata  = {32{1'b0}};
      assign apb6_pready  = 1'b1;
      assign apb6_pslverr = 1'b0;
    end endgenerate

  // -----------------------------------------------------------------
  // APB7 - Unused

  generate if (INCLUDE_APB_7) begin : gen_apb7


    end else
    begin : gen_no_apb7
      assign apb7_prdata  = {32{1'b0}};
      assign apb7_pready  = 1'b1;
      assign apb7_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB5
  wire mem_sel;
  assign mem_sel = apb8_psel | apb9_psel | apb10_psel | apb11_psel;

  generate if (INCLUDE_APB_8) begin : gen_apb8
      SRAM_Digital_top #(
        .ADDRWIDTH(14),
        .DATAWIDTH(32)
      ) u_mem_0 (
        .pclk         (PCLK         ),
        .presetn      (PRESETn      ),

        // APB interface inputs
        .psel         (mem_sel      ),
        .paddr        (i_paddr[13:0]),
        .penable      (i_penable    ),
        .pwrite       (i_pwrite     ),
        .pwdata       (i_pwdata     ),

        // APB interface outputs
        .prdata       (apb8_prdata  ),
        .pready       (apb8_pready  ),
        .pslverr      (apb8_pslverr ),

        .DATA_REQ_pad (MEM_DATA_REQ ),
        .WE_pad       (MEM_WE       ),
        .TEST_MODE_pad(MEM_TEST_MODE),
        .CLK_IN_pad   (MEM_CLK_IN   ),
        .RESET_pad    (MEM_RESET    ),
        .SPI_CLOCK_pad(MEM_SPI_CLOCK),
        .SPI_MOSI_pad (MEM_SPI_MOSI ),
        .SPI_RST_pad  (MEM_SPI_RST  ),
        .SPI_SCLK_pad (MEM_SPI_SCLK ),
        .SPI_SS_pad   (MEM_SPI_SS   ),
        .DOUT32_PO    (MEM_DOUT32   ),
        .SPI_MISO_PO  (MEM_SPI_MISO )
      );

    end else
    begin : gen_no_apb8
      assign apb8_prdata  = {32{1'b0}};
      assign apb8_pready  = 1'b1;
      assign apb8_pslverr = 1'b0;

      assign MEM_DOUT32 = 1'b0;
      assign MEM_SPI_MISO = 1'b0;

    end endgenerate

  // -----------------------------------------------------------------
  // APB9 - Used by mem (APB8)
  assign apb9_prdata  = apb8_prdata;
  assign apb9_pready  = apb8_pready;
  assign apb9_pslverr = apb8_pslverr;

  // -----------------------------------------------------------------
  // APB10 - Used by mem (APB8)

  assign apb10_prdata  = apb8_prdata;
  assign apb10_pready  = apb8_pready;
  assign apb10_pslverr = apb8_pslverr;

  // -----------------------------------------------------------------
  // APB11 - Used by mem (APB8)

  assign apb11_prdata  = apb8_prdata;
  assign apb11_pready  = apb8_pready;
  assign apb11_pslverr = apb8_pslverr;



  // -----------------------------------------------------------------
  // APB12

  generate if (INCLUDE_APB_12) begin : gen_apb12
      temp0_apb #(.ID(32'hFA50C12)) u_temp_0 (
        .PCLK         (PCLK         ),
        .PRESETn      (PRESETn      ),

        .PSEL         (apb12_psel   ),
        .PADDR        (i_paddr[11:0]),
        .PENABLE      (i_penable    ),
        .PWRITE       (i_pwrite     ),
        .PWDATA       (i_pwdata     ),

        .PRDATA       (apb12_prdata ),
        .PREADY       (apb12_pready ),
        .PSLVERR      (apb12_pslverr),

        .CLK_REF      (TEMP_0_REFCLK),
        .CLKOUT       (TEMP_0_CLKOUT),
        .VIN_TEMPSENSE(VIN_TEMPSENSE)
      );
    end else
    begin : gen_no_apb12
      assign apb12_prdata  = {32{1'b0}};
      assign apb12_pready  = 1'b1;
      assign apb12_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB13

  generate if (INCLUDE_APB_13) begin : gen_apb13
      temp1_apb #(.ID(32'hFA50C13)) u_temp_1 (
        .PCLK         (PCLK         ),
        .PRESETn      (PRESETn      ),

        .PSEL         (apb13_psel   ),
        .PADDR        (i_paddr[11:0]),
        .PENABLE      (i_penable    ),
        .PWRITE       (i_pwrite     ),
        .PWDATA       (i_pwdata     ),

        .PRDATA       (apb13_prdata ),
        .PREADY       (apb13_pready ),
        .PSLVERR      (apb13_pslverr),

        .CLK_REF      (TEMP_1_REFCLK),
        .CLKOUT       (TEMP_1_CLKOUT),
        .VIN_TEMPSENSE(VIN_TEMPSENSE)
      );
    end else
    begin : gen_no_apb13
      assign apb13_prdata  = {32{1'b0}};
      assign apb13_pready  = 1'b1;
      assign apb13_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB14

  generate if (INCLUDE_APB_14) begin : gen_apb14
      cdc0_apb #(
        .ID(32'hFA50C14)
      ) u_cdc_0 (
        .PCLK   (PCLK         ),
        .PRESETn(PRESETn      ),

        .PSEL   (apb14_psel   ),
        .PADDR  (i_paddr[11:0]),
        .PENABLE(i_penable    ),
        .PWRITE (i_pwrite     ),
        .PWDATA (i_pwdata     ),

        .PRDATA (apb14_prdata ),
        .PREADY (apb14_pready ),
        .PSLVERR(apb14_pslverr)
      );
    end else
    begin : gen_no_apb14
      assign apb14_prdata  = {32{1'b0}};
      assign apb14_pready  = 1'b1;
      assign apb14_pslverr = 1'b0;
    end endgenerate


  // -----------------------------------------------------------------
  // APB15

  generate if (INCLUDE_APB_15) begin : gen_apb15
      cdc1_apb #(
        .ID(32'hFA50C15)
      ) u_cdc_1 (
        .PCLK   (PCLK         ),
        .PRESETn(PRESETn      ),

        .PSEL   (apb15_psel   ),
        .PADDR  (i_paddr[11:0]),
        .PENABLE(i_penable    ),
        .PWRITE (i_pwrite     ),
        .PWDATA (i_pwdata     ),

        .PRDATA (apb15_prdata ),
        .PREADY (apb15_pready ),
        .PSLVERR(apb15_pslverr)
      );
    end else
    begin : gen_no_apb15
      assign apb15_prdata  = {32{1'b0}};
      assign apb15_pready  = 1'b1;
      assign apb15_pslverr = 1'b0;
    end endgenerate



  // -----------------------------------------------------------------
  assign uart_overflow_int = uart_txovrint|uart_rxovrint;

  // If PCLK is syncrhonous to HCLK, no need to have synchronizers
  assign i_uart_txint        = uart_txint;
  assign i_uart_rxint        = uart_rxint;
  assign i_uart_overflow_int = uart_overflow_int;



  assign apbsubsys_interrupt[31:0] = {
    {16{1'b0}},          // 16-31 (AHB GPIO #0 individual interrupt)
    1'b0,                // 15
    i_uart_overflow_int, // 14
    1'b0,                // 13
    1'b0,                // 12
    1'b0,                // 11
    1'b0,                // 10
    1'b0,                // 9
    1'b0,                // 8
    1'b0,                // 7
    1'b0,                // 6
    i_uart_txint,        // 5
    i_uart_rxint,        // 4
    1'b0,                // 3
    1'b0,                // 2
    1'b0,                // 1
    1'b0};               // 0



  `ifdef ARM_APB_ASSERT_ON
    // ------------------------------------------------------------
    // Assertions
    // ------------------------------------------------------------
    `include "std_ovl_defines.h"

    // PSEL should be one-hot
    // If this OVL fires - there is an error in the design of the address decoder
    assert_zero_one_hot
      #(`OVL_FATAL,16,`OVL_ASSERT,
        "Only one PSEL input can be activated.")
      u_ovl_psel_one_hot
        (.clk(PCLK), .reset_n(PRESETn),
          .test_expr({apb0_psel,apb1_psel,apb2_psel,apb3_psel,apb4_psel,apb5_psel,
              apb6_psel,apb7_psel,apb8_psel,apb9_psel,apb10_psel,apb11_psel,
              apb12_psel,apb13_psel,apb14_psel,apb15_psel}));


    // All Writes to the APB peripherals must be word size since PSTRB only
    // supported on the APB test slave. Therefore, the AHB bridge can generate
    // non-word sized writes which can break the APB peripherals (not
    // including the the test slave) since they don't support this (i.e. PSTRB
    // is not present). Hence, restrict the appropriate accesses to word sized
    // writes.
    assert_implication #(
      `OVL_ERROR,`OVL_ASSERT,
      "All Writes to the APB peripherals must be word size not including the test slave"
    ) u_ovl_apb_write_word_size_32bits (
      .clk            (PCLK                           ),
      .reset_n        (PRESETn                        ),
      .antecedent_expr(i_penable && i_psel && i_pwrite),
      .consequent_expr(i_pstrb == 4'b1111             )
    );

    // This protocol checker is placed here and attached to the PCLK and PCLKEN.
    // A note should be made that this means that the value of PCLKEN may not
    // necessarily be the same as the enable term that is gating PCLK to generate
    // PCLKG.
    ApbPC #(
      .ADDR_WIDTH                 (16),
      .DATA_WIDTH                 (32),
      .SEL_WIDTH                  (1 ),
      // OVL instances property_type (0=assert, 1=assume, 2=ignore)
      .MASTER_REQUIREMENT_PROPTYPE(0 ),
      .SLAVE_REQUIREMENT_PROPTYPE (0 ),

      .PREADY_FUNCTIONAL          (1 ),
      .PSLVERR_FUNCTIONAL         (1 ),
      .PPROT_FUNCTIONAL           (1 ),
      .PSTRB_FUNCTIONAL           (1 )
    ) u_ApbPC (
      // Inputs
      .PCLK   (PCLK         ),
      .PRESETn(PRESETn      ),
      .PSELx  (i_psel       ),
      .PPROT  (i_pprot      ),
      .PSTRB  (i_pstrb      ),
      .PENABLE(i_penable    ),
      .PREADY (i_pready_mux ),
      .PSLVERR(i_pslverr_mux),
      .PADDR  (i_paddr      ),
      .PWRITE (i_pwrite     ),
      .PWDATA (i_pwdata     ),
      .PRDATA (i_prdata_mux )
    );


  `endif

endmodule
