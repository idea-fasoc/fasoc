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
//      Checked In          : $Date: 2013-04-19 12:06:38 +0100 (Fri, 19 Apr 2013) $
//
//      Revision            : $Revision: 244587 $
//
//      Release Information : Cortex-M System Design Kit-r1p0-00rel0
//
//-----------------------------------------------------------------------------
//-----------------------------------------------------------------------------
// Abstract : Top level for example Cortex-M0/Cortex-M0+ microcontroller
//-----------------------------------------------------------------------------
//

`include "cmsdk_mcu_defs.v"

module cmsdk_mcu #(
   `ifdef ARM_CMSDK_INCLUDE_CLKGATE
  parameter CLKGATE_PRESENT = 1                       ,
  `else
  parameter CLKGATE_PRESENT = 0                       ,
  `endif
  parameter BE              = 0                       , // Big or little endian
  parameter BKPT            = 4                       , // Number of breakpoint comparators
  parameter DBG             = 1                       , // Debug configuration
  parameter NUMIRQ          = 32                      , // NUM of IRQ
  parameter SMUL            = 0                       , // Multiplier configuration
  parameter SYST            = 1                       , // SysTick
  parameter WIC             = 1                       , // Wake-up interrupt controller support
  parameter WICLINES        = 34                      , // Supported WIC lines
  parameter WPT             = 2                       , // Number of DWT comparators
  `ifdef CORTEX_M0PLUS
  parameter AWIDTH          = 12                      , // Micro Trace Buffer SRAM address width:
  // 5 to 32
  parameter BASEADDR        = 32'hF0000003            , // ROM Table Base Address.
  parameter HWF             = 0                       , // Half-Word Fetching
  `ifdef ARM_CMSDK_INCLUDE_IOP
  parameter IOP             = 1                       , // IO Port interface selected
  `else
  parameter IOP             = 0                       , // IO Port not selected
  `endif
  parameter IRQDIS          = 32'h00000000            , // Interrupt Disable
  parameter MPU             = 8                       , // 8 Memory Protection Regions
  `ifdef ARM_CMSDK_INCLUDE_MTB
  parameter MTB             = 1                       , // MTB present
  `else
  parameter MTB             = 0                       , // MTB not present
  `endif
  parameter USER            = 0                       , // User/Privilege
  parameter VTOR            = 0                       , // Vector Table Offset support
  `endif

  //-----------------------------------------
  // Memory options - see cmsdk_mcu_defs.v

  //  This is defined in systems/cortex_m0_mcu/cmsdk_mcu_defs.v
  //  Based on the definition constants in logical/models/memories/cmsdk_ahb_memory_model_defs.v
  //  0) AHB_ROM_NONE             - memory not present
  //  1) AHB_ROM_BEH_MODEL        - behavioral ROM memory
  //  2) AHB_ROM_FPGA_SRAM_MODEL  - behavioral FPGA SRAM model with SRAM wrapper
  //  3) AHB_ROM_FLASH32_MODEL    - behavioral 32-bit flash memory
  parameter BOOT_MEM_TYPE   = `ARM_CMSDK_BOOT_MEM_TYPE, // Boot loader memory type

  //  This is defined in systems/cortex_m0_mcu/cmsdk_mcu_defs.v
  //  Based on the definition constants in logical/models/memories/cmsdk_ahb_memory_model_defs.v
  //  0) AHB_ROM_NONE             - memory not present (Not valid for a Cortex-M0 system)
  //  1) AHB_ROM_BEH_MODEL        - behavioral ROM memory
  //  2) AHB_ROM_FPGA_SRAM_MODEL  - behavioral FPGA SRAM model with SRAM wrapper
  //  3) AHB_ROM_FLASH32_MODEL    - behavioral 32-bit flash memory
  parameter ROM_MEM_TYPE    = `ARM_CMSDK_ROM_MEM_TYPE , // ROM memory type

  //  This is defined in systems/cortex_m0_mcu/cmsdk_mcu_defs.v
  //  Based on the definition constants in logical/models/memories/cmsdk_ahb_memory_model_defs.v
  //  0) AHB_RAM_NONE             - memory not present (Not valid for a Cortex-M0 system
  //  1) AHB_RAM_BEH_MODEL        - behavioral RAM memory
  //  2) AHB_RAM_FPGA_SRAM_MODEL  - behavioral SRAM model with SRAM wrapper
  //  3) AHB_RAM_EXT_SRAM16_MODEL - for benchmarking using 16-bit external asynchronous SRAM
  //  4) AHB_RAM_EXT_SRAM8_MODEL  - for benchmarking using 8-bit external asynchronous SRAM
  parameter RAM_MEM_TYPE    = `ARM_CMSDK_RAM_MEM_TYPE , // RAM memory type

  //-----------------------------------------
  // System options

  `ifdef ARM_CMSDK_INCLUDE_DMA
  parameter INCLUDE_DMA     = 1                       , // Include instantiation of DMA-230
  // This option also add a number of bus components
  `else
  parameter INCLUDE_DMA     = 0                       ,
  `endif

  `ifdef ARM_CMSDK_INCLUDE_BITBAND
  parameter INCLUDE_BITBAND = 1                       ,
  // Include instantiation of Bit-band wrapper
  // This option add bit band wrapper to CPU interface
  `else
  parameter INCLUDE_BITBAND = 0                       ,
  `endif

  `ifdef ARM_CMSDK_INCLUDE_JTAG
  parameter INCLUDE_JTAG    = 1,                         // Include JTAG feature
  `else
  parameter INCLUDE_JTAG    = 0,                         // Do not Include JTAG feature
  `endif



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
  parameter INCLUDE_APB_15 = 0 // CDC2
) (
  
  input  wire        XTAL1_PAD          , // input
  output wire        XTAL2_PAD          , // output
  input  wire        NRST_PAD           , // active low reset

  output wire        GPIO_INIT_PAD      ,
  output wire        GPIO_USER0_PAD     ,
  output wire        GPIO_USER1_PAD     ,

  input  wire        UART_RXD_PAD       ,
  output wire        UART_TXD_PAD       ,

  input  wire        LDO_SPI_RESETn_PAD ,
  input  wire [1:0]  LDO_SPI_SS_PAD     ,
  input  wire        LDO_SPI_SCLK_PAD   ,
  input  wire        LDO_SPI_MOSI_PAD   ,
  output wire        LDO_SPI_MISO_PAD   ,
  input  wire        LDO_SPI_APB_SEL_PAD,
  input  wire        LDO_VREF_PAD       ,
  // inout  wire       LDO_0_VREG_PAD     ,
  // inout  wire       LDO_1_VREG_PAD     ,
  // inout  wire       LDO_2_VREG_PAD     ,
  input  wire        LDO_REFCLK_PAD     ,

  input  wire        MEM_DATA_REQ_PAD   ,
  input  wire        MEM_WE_PAD         ,
  input  wire        MEM_TEST_MODE_PAD  ,
  input  wire        MEM_CLK_IN_PAD     ,
  input  wire        MEM_RESET_PAD      ,
  input  wire        MEM_SPI_CLOCK_PAD  ,
  input  wire        MEM_SPI_MOSI_PAD   ,
  input  wire        MEM_SPI_RST_PAD    ,
  input  wire        MEM_SPI_SCLK_PAD   ,
  input  wire        MEM_SPI_SS_PAD     ,
  output wire        MEM_DOUT32_PAD     ,
  output wire        MEM_SPI_MISO_PAD   ,

  input  wire        PLL_CLKREF0_PAD    ,
  input  wire        PLL_CLKREF1_PAD    ,
  output wire        PLL_CLKOUT0_PAD    ,
  output wire        PLL_CLKOUT1_PAD    ,


  output wire        TEMP_0_CLKOUT_PAD  ,
  output wire        TEMP_1_CLKOUT_PAD  ,
  input  wire        TEMP_0_REFCLK_PAD  ,
  input  wire        TEMP_1_REFCLK_PAD  ,
  input  wire        VIN_TEMPSENSE_PAD  ,


  `ifdef ARM_CMSDK_INCLUDE_JTAG
  input  wire        nTRST              ,
  input  wire        TDI                ,
  output wire        TDO                ,
  `endif
  inout  wire        SWDIOTMS           ,
  input  wire        SWCLKTCK



//   input  wire [15:0] i_paddr  ,
//   input  wire        i_psel   ,

// // wire from APB slave mux to APB bridge
//   output wire        i_pready_mux ,
//   output wire [31:0] i_prdata_mux ,
//   output wire        i_pslverr_mux,

// // Peripheral signals
//   output wire        apb0_psel   ,
//   input  wire [31:0] apb0_prdata ,
//   input  wire        apb0_pready ,
//   input  wire        apb0_pslverr,

//   output wire        apb1_psel   ,
//   input  wire [31:0] apb1_prdata ,
//   input  wire        apb1_pready ,
//   input  wire        apb1_pslverr,

//   output wire        apb2_psel   ,
//   input  wire [31:0] apb2_prdata ,
//   input  wire        apb2_pready ,
//   input  wire        apb2_pslverr,

//   output wire        apb3_psel   ,
//   input  wire [31:0] apb3_prdata ,
//   input  wire        apb3_pready ,
//   input  wire        apb3_pslverr,

//   output wire        apb4_psel   ,
//   input  wire [31:0] apb4_prdata ,
//   input  wire        apb4_pready ,
//   input  wire        apb4_pslverr,

//   output wire        apb5_psel   ,
//   input  wire [31:0] apb5_prdata ,
//   input  wire        apb5_pready ,
//   input  wire        apb5_pslverr,

//   output wire        apb6_psel   ,
//   input  wire [31:0] apb6_prdata ,
//   input  wire        apb6_pready ,
//   input  wire        apb6_pslverr,

//   output wire        apb7_psel   ,
//   input  wire [31:0] apb7_prdata ,
//   input  wire        apb7_pready ,
//   input  wire        apb7_pslverr,

//   output wire        apb8_psel   ,
//   input  wire [31:0] apb8_prdata ,
//   input  wire        apb8_pready ,
//   input  wire        apb8_pslverr,

//   output wire        apb9_psel   ,
//   input  wire [31:0] apb9_prdata ,
//   input  wire        apb9_pready ,
//   input  wire        apb9_pslverr,

//   output wire        apb10_psel   ,
//   input  wire [31:0] apb10_prdata ,
//   input  wire        apb10_pready ,
//   input  wire        apb10_pslverr,

//   output wire        apb11_psel   ,
//   input  wire [31:0] apb11_prdata ,
//   input  wire        apb11_pready ,
//   input  wire        apb11_pslverr,

//   output wire        apb12_psel   ,
//   input  wire [31:0] apb12_prdata ,
//   input  wire        apb12_pready ,
//   input  wire        apb12_pslverr,

//   output wire        apb13_psel   ,
//   input  wire [31:0] apb13_prdata ,
//   input  wire        apb13_pready ,
//   input  wire        apb13_pslverr,

//   output wire        apb14_psel   ,
//   input  wire [31:0] apb14_prdata ,
//   input  wire        apb14_pready ,
//   input  wire        apb14_pslverr,

//   output wire        apb15_psel   ,
//   input  wire [31:0] apb15_prdata ,
//   input  wire        apb15_pready ,
//   input  wire        apb15_pslverr

  );

  wire [15:0] i_paddr  ;
  wire        i_psel   ;

//wire from APB slave mux to APB bridge
  wire        i_pready_mux ;
  wire [31:0] i_prdata_mux ;
  wire        i_pslverr_mux;

  // Peripheral signals
  wire        apb0_psel   ;
  wire [31:0] apb0_prdata ;
  wire        apb0_pready ;
  wire        apb0_pslverr;

  wire        apb1_psel   ;
  wire [31:0] apb1_prdata ;
  wire        apb1_pready ;
  wire        apb1_pslverr;

  wire        apb2_psel   ;
  wire [31:0] apb2_prdata ;
  wire        apb2_pready ;
  wire        apb2_pslverr;

  wire        apb3_psel   ;
  wire [31:0] apb3_prdata ;
  wire        apb3_pready ;
  wire        apb3_pslverr;

  wire        apb4_psel   ;
  wire [31:0] apb4_prdata ;
  wire        apb4_pready ;
  wire        apb4_pslverr;

  wire        apb5_psel   ;
  wire [31:0] apb5_prdata ;
  wire        apb5_pready ;
  wire        apb5_pslverr;

  wire        apb6_psel   ;
  wire [31:0] apb6_prdata ;
  wire        apb6_pready ;
  wire        apb6_pslverr;

  wire        apb7_psel   ;
  wire [31:0] apb7_prdata ;
  wire        apb7_pready ;
  wire        apb7_pslverr;

  wire        apb8_psel   ;
  wire [31:0] apb8_prdata ;
  wire        apb8_pready ;
  wire        apb8_pslverr;

  wire        apb9_psel   ;
  wire [31:0] apb9_prdata ;
  wire        apb9_pready ;
  wire        apb9_pslverr;

  wire        apb10_psel   ;
  wire [31:0] apb10_prdata ;
  wire        apb10_pready ;
  wire        apb10_pslverr;

  wire        apb11_psel   ;
  wire [31:0] apb11_prdata ;
  wire        apb11_pready ;
  wire        apb11_pslverr;

  wire        apb12_psel   ;
  wire [31:0] apb12_prdata ;
  wire        apb12_pready ;
  wire        apb12_pslverr;

  wire        apb13_psel   ;
  wire [31:0] apb13_prdata ;
  wire        apb13_pready ;
  wire        apb13_pslverr;

  wire        apb14_psel   ;
  wire [31:0] apb14_prdata ;
  wire        apb14_pready ;
  wire        apb14_pslverr;

  wire        apb15_psel   ;
  wire [31:0] apb15_prdata ;
  wire        apb15_pready ;
  wire        apb15_pslverr;

  cmsdk_apb_slave_mux #(
    // Parameter to determine which ports are used
    .PORT0_ENABLE  (INCLUDE_APB_0 ), // Simple slave/gpio
    .PORT1_ENABLE  (INCLUDE_APB_1 ), // UART
    .PORT2_ENABLE  (INCLUDE_APB_2 ), // LDO0
    .PORT3_ENABLE  (INCLUDE_APB_3 ), // LDO1
    .PORT4_ENABLE  (INCLUDE_APB_4 ), // LDO2
    .PORT5_ENABLE  (INCLUDE_APB_5 ), // PLL1
    .PORT6_ENABLE  (INCLUDE_APB_6 ), // PLL2
    .PORT7_ENABLE  (INCLUDE_APB_7 ), // UNUSED
    .PORT8_ENABLE  (INCLUDE_APB_8 ), // MEM0
    .PORT9_ENABLE  (INCLUDE_APB_8 ), // Used by MEM0
    .PORT10_ENABLE (INCLUDE_APB_8 ),  // Used by MEM0
    .PORT11_ENABLE (INCLUDE_APB_8 ),  // Used by MEM0
    .PORT12_ENABLE (INCLUDE_APB_12), // TEMP0
    .PORT13_ENABLE (INCLUDE_APB_13), // TEMP1
    .PORT14_ENABLE (INCLUDE_APB_14), // CDC1
    .PORT15_ENABLE (INCLUDE_APB_15)  // CDC2
  ) u_apb_slave_mux (
    // Inputs
    .DECODE4BIT(i_paddr[15:12]),
    .PSEL      (i_psel        ),

    // PSEL (output) and return status & data (inputs) for each port
    .PSEL0     (apb0_psel     ),
    .PREADY0   (apb0_pready   ),
    .PRDATA0   (apb0_prdata   ),
    .PSLVERR0  (apb0_pslverr  ),

    .PSEL1     (apb1_psel     ),
    .PREADY1   (apb1_pready   ),
    .PRDATA1   (apb1_prdata   ),
    .PSLVERR1  (apb1_pslverr  ),

    .PSEL2     (apb2_psel     ),
    .PREADY2   (apb2_pready   ),
    .PRDATA2   (apb2_prdata   ),
    .PSLVERR2  (apb2_pslverr  ),

    .PSEL3     (apb3_psel     ),
    .PREADY3   (apb3_pready   ),
    .PRDATA3   (apb3_prdata   ),
    .PSLVERR3  (apb3_pslverr  ),

    .PSEL4     (apb4_psel     ),
    .PREADY4   (apb4_pready   ),
    .PRDATA4   (apb4_prdata   ),
    .PSLVERR4  (apb4_pslverr  ),

    .PSEL5     (apb5_psel     ),
    .PREADY5   (apb5_pready   ),
    .PRDATA5   (apb5_prdata   ),
    .PSLVERR5  (apb5_pslverr  ),

    .PSEL6     (apb6_psel     ),
    .PREADY6   (apb6_pready   ),
    .PRDATA6   (apb6_prdata   ),
    .PSLVERR6  (apb6_pslverr  ),

    .PSEL7     (apb7_psel     ),
    .PREADY7   (apb7_pready   ),
    .PRDATA7   (apb7_prdata   ),
    .PSLVERR7  (apb7_pslverr  ),

    .PSEL8     (apb8_psel     ),
    .PREADY8   (apb8_pready   ),
    .PRDATA8   (apb8_prdata   ),
    .PSLVERR8  (apb8_pslverr  ),

    .PSEL9     (apb9_psel     ),
    .PREADY9   (apb9_pready   ),
    .PRDATA9   (apb9_prdata   ),
    .PSLVERR9  (apb9_pslverr  ),

    .PSEL10    (apb10_psel    ),
    .PREADY10  (apb10_pready  ),
    .PRDATA10  (apb10_prdata  ),
    .PSLVERR10 (apb10_pslverr ),

    .PSEL11    (apb11_psel    ),
    .PREADY11  (apb11_pready  ),
    .PRDATA11  (apb11_prdata  ),
    .PSLVERR11 (apb11_pslverr ),

    .PSEL12    (apb12_psel    ),
    .PREADY12  (apb12_pready  ),
    .PRDATA12  (apb12_prdata  ),
    .PSLVERR12 (apb12_pslverr ),

    .PSEL13    (apb13_psel    ),
    .PREADY13  (apb13_pready  ),
    .PRDATA13  (apb13_prdata  ),
    .PSLVERR13 (apb13_pslverr ),

    .PSEL14    (apb14_psel    ),
    .PREADY14  (apb14_pready  ),
    .PRDATA14  (apb14_prdata  ),
    .PSLVERR14 (apb14_pslverr ),

    .PSEL15    (apb15_psel    ),
    .PREADY15  (apb15_pready  ),
    .PRDATA15  (apb15_prdata  ),
    .PSLVERR15 (apb15_pslverr ),

    // Output
    .PREADY    (i_pready_mux  ),
    .PRDATA    (i_prdata_mux  ),
    .PSLVERR   (i_pslverr_mux )
  );

  m0_wrapper #(

    .CLKGATE_PRESENT (CLKGATE_PRESENT),
    .BE              (BE),
    .BKPT            (BKPT),
    .DBG             (DBG),
    .NUMIRQ          (NUMIRQ),
    .SMUL            (SMUL),
    .SYST            (SYST),
    .WIC             (WIC),
    .WICLINES        (WICLINES),
    .WPT             (WPT),
  `ifdef CORTEX_M0PLUS
    .AWIDTH          (AWIDTH),
    .BASEADDR        (BASEADDR),
    .HWF             (HWF),
    .IOP             (IOP),
    .IRQDIS          (IRQDIS),
    .MPU             (MPU),
    .MTB             (MTB),
    .USER            (USER),
    .VTOR            (VTOR),
  `endif

    .BOOT_MEM_TYPE   (BOOT_MEM_TYPE),
    .ROM_MEM_TYPE    (ROM_MEM_TYPE),
    .RAM_MEM_TYPE    (RAM_MEM_TYPE),
    .INCLUDE_DMA     (INCLUDE_DMA),
    .INCLUDE_BITBAND (INCLUDE_BITBAND),
    .INCLUDE_JTAG    (INCLUDE_JTAG),
    .INCLUDE_APB_0   (INCLUDE_APB_0 ),
    .INCLUDE_APB_1   (INCLUDE_APB_1 ), // UART
    .INCLUDE_APB_2   (INCLUDE_APB_2 ), // LDO0
    .INCLUDE_APB_3   (INCLUDE_APB_3 ), // LDO1
    .INCLUDE_APB_4   (INCLUDE_APB_4 ), // LDO2
    .INCLUDE_APB_5   (INCLUDE_APB_5 ), // PLL1
    .INCLUDE_APB_6   (INCLUDE_APB_6 ), // PLL2
    .INCLUDE_APB_7   (INCLUDE_APB_7 ), // UNUSED
    .INCLUDE_APB_8   (INCLUDE_APB_8 ), // MEM0
    .INCLUDE_APB_12  (INCLUDE_APB_12), // TEMP0
    .INCLUDE_APB_13  (INCLUDE_APB_13), // TEMP1
    .INCLUDE_APB_14  (INCLUDE_APB_14), // CDC1
    .INCLUDE_APB_15  (INCLUDE_APB_15)  // CDC2
) 
  u_m0_wrapper(
    .XTAL1_PAD           (XTAL1_PAD          ),
    .XTAL2_PAD           (XTAL2_PAD          ),
    .NRST_PAD            (NRST_PAD           ),
    .GPIO_INIT_PAD       (GPIO_INIT_PAD      ),
    .GPIO_USER0_PAD      (GPIO_USER0_PAD     ),
    .GPIO_USER1_PAD      (GPIO_USER1_PAD     ),
    .UART_RXD_PAD        (UART_RXD_PAD       ),
    .UART_TXD_PAD        (UART_TXD_PAD       ),

    .LDO_SPI_RESETn_PAD(LDO_SPI_RESETn_PAD),
    .LDO_SPI_SS_PAD      (LDO_SPI_SS_PAD     ),
    .LDO_SPI_SCLK_PAD    (LDO_SPI_SCLK_PAD   ),
    .LDO_SPI_MOSI_PAD    (LDO_SPI_MOSI_PAD   ),
    .LDO_SPI_MISO_PAD    (LDO_SPI_MISO_PAD   ),
    .LDO_SPI_APB_SEL_PAD (LDO_SPI_APB_SEL_PAD),
    .LDO_VREF_PAD        (LDO_VREF_PAD       ),
    .LDO_REFCLK_PAD      (LDO_REFCLK_PAD     ),

    .MEM_DATA_REQ_PAD    (MEM_DATA_REQ_PAD   ),
    .MEM_WE_PAD          (MEM_WE_PAD         ),
    .MEM_TEST_MODE_PAD   (MEM_TEST_MODE_PAD  ),
    .MEM_CLK_IN_PAD      (MEM_CLK_IN_PAD     ),
    .MEM_RESET_PAD       (MEM_RESET_PAD      ),
    .MEM_SPI_CLOCK_PAD   (MEM_SPI_CLOCK_PAD  ),
    .MEM_SPI_MOSI_PAD    (MEM_SPI_MOSI_PAD   ),
    .MEM_SPI_RST_PAD     (MEM_SPI_RST_PAD    ),
    .MEM_SPI_SCLK_PAD    (MEM_SPI_SCLK_PAD   ),
    .MEM_SPI_SS_PAD      (MEM_SPI_SS_PAD     ),
    .MEM_DOUT32_PAD      (MEM_DOUT32_PAD     ),
    .MEM_SPI_MISO_PAD    (MEM_SPI_MISO_PAD   ),

    .PLL_CLKREF0_PAD     (PLL_CLKREF0_PAD    ),
    .PLL_CLKREF1_PAD     (PLL_CLKREF1_PAD    ),
    .PLL_CLKOUT0_PAD     (PLL_CLKOUT0_PAD    ),
    .PLL_CLKOUT1_PAD     (PLL_CLKOUT1_PAD    ),

    .TEMP_0_CLKOUT_PAD   (TEMP_0_CLKOUT_PAD  ),
    .TEMP_1_CLKOUT_PAD   (TEMP_1_CLKOUT_PAD  ),
    .TEMP_0_REFCLK_PAD   (TEMP_0_REFCLK_PAD  ),
    .TEMP_1_REFCLK_PAD   (TEMP_1_REFCLK_PAD  ),
    .VIN_TEMPSENSE_PAD   (VIN_TEMPSENSE_PAD  ),

  `ifdef ARM_CMSDK_INCLUDE_JTAG
    .nTRST               (nTRST              ),
    .TDI                 (TDI                ),
    .TDO                 (TDO                ),
  `endif
    .SWDIOTMS            (SWDIOTMS           ),
    .SWCLKTCK            (SWCLKTCK           ),


    .i_paddr             (i_paddr            ),
    .i_psel              (i_psel             ),

    // PSEL (output) and return status & data (inputs) for each port
    .apb0_psel           (apb0_psel          ),
    .apb0_pready         (apb0_pready        ),
    .apb0_prdata         (apb0_prdata        ),
    .apb0_pslverr        (apb0_pslverr       ),

    .apb1_psel           (apb1_psel          ),
    .apb1_pready         (apb1_pready        ),
    .apb1_prdata         (apb1_prdata        ),
    .apb1_pslverr        (apb1_pslverr       ),

    .apb2_psel           (apb2_psel          ),
    .apb2_pready         (apb2_pready        ),
    .apb2_prdata         (apb2_prdata        ),
    .apb2_pslverr        (apb2_pslverr       ),

    .apb3_psel           (apb3_psel          ),
    .apb3_pready         (apb3_pready        ),
    .apb3_prdata         (apb3_prdata        ),
    .apb3_pslverr        (apb3_pslverr       ),

    .apb4_psel           (apb4_psel          ),
    .apb4_pready         (apb4_pready        ),
    .apb4_prdata         (apb4_prdata        ),
    .apb4_pslverr        (apb4_pslverr       ),

    .apb5_psel           (apb5_psel          ),
    .apb5_pready         (apb5_pready        ),
    .apb5_prdata         (apb5_prdata        ),
    .apb5_pslverr        (apb5_pslverr       ),

    .apb6_psel           (apb6_psel          ),
    .apb6_pready         (apb6_pready        ),
    .apb6_prdata         (apb6_prdata        ),
    .apb6_pslverr        (apb6_pslverr       ),

    .apb7_psel           (apb7_psel          ),
    .apb7_pready         (apb7_pready        ),
    .apb7_prdata         (apb7_prdata        ),
    .apb7_pslverr        (apb7_pslverr       ),

    .apb8_psel           (apb8_psel          ),
    .apb8_pready         (apb8_pready        ),
    .apb8_prdata         (apb8_prdata        ),
    .apb8_pslverr        (apb8_pslverr       ),

    .apb9_psel           (apb9_psel          ),
    .apb9_pready         (apb9_pready        ),
    .apb9_prdata         (apb9_prdata        ),
    .apb9_pslverr        (apb9_pslverr       ),

    .apb10_psel          (apb10_psel         ),
    .apb10_pready        (apb10_pready       ),
    .apb10_prdata        (apb10_prdata       ),
    .apb10_pslverr       (apb10_pslverr      ),

    .apb11_psel          (apb11_psel         ),
    .apb11_pready        (apb11_pready       ),
    .apb11_prdata        (apb11_prdata       ),
    .apb11_pslverr       (apb11_pslverr      ),

    .apb12_psel          (apb12_psel         ),
    .apb12_pready        (apb12_pready       ),
    .apb12_prdata        (apb12_prdata       ),
    .apb12_pslverr       (apb12_pslverr      ),

    .apb13_psel          (apb13_psel         ),
    .apb13_pready        (apb13_pready       ),
    .apb13_prdata        (apb13_prdata       ),
    .apb13_pslverr       (apb13_pslverr      ),

    .apb14_psel          (apb14_psel         ),
    .apb14_pready        (apb14_pready       ),
    .apb14_prdata        (apb14_prdata       ),
    .apb14_pslverr       (apb14_pslverr      ),

    .apb15_psel          (apb15_psel         ),
    .apb15_pready        (apb15_pready       ),
    .apb15_prdata        (apb15_prdata       ),
    .apb15_pslverr       (apb15_pslverr      ),

    // Output
    .i_pready_mux        (i_pready_mux       ),
    .i_prdata_mux        (i_prdata_mux       ),
    .i_pslverr_mux       (i_pslverr_mux      )


);

endmodule