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
  //-----------------------------------------
  // CPU options

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
  parameter INCLUDE_JTAG    = 1                         // Include JTAG feature
  `else
  parameter INCLUDE_JTAG    = 0                         // Do not Include JTAG feature
  `endif
) (
  input  wire       XTAL1_PAD          , // input
  output wire       XTAL2_PAD          , // output
  input  wire       NRST_PAD           , // active low reset

  output wire       GPIO_INIT_PAD      ,
  output wire       GPIO_USER0_PAD     ,
  output wire       GPIO_USER1_PAD     ,

  input  wire       UART_RXD_PAD       ,
  output wire       UART_TXD_PAD       ,

  input  wire       LDO_SPI_RESETn_PAD ,
  input  wire [1:0] LDO_SPI_SS_PAD     ,
  input  wire       LDO_SPI_SCLK_PAD   ,
  input  wire       LDO_SPI_MOSI_PAD   ,
  output wire       LDO_SPI_MISO_PAD   ,
  input  wire       LDO_SPI_APB_SEL_PAD,
  input  wire       LDO_VREF_PAD       ,
  // inout  wire       LDO_0_VREG_PAD     ,
  // inout  wire       LDO_1_VREG_PAD     ,
  // inout  wire       LDO_2_VREG_PAD     ,
  input  wire       LDO_REFCLK_PAD     ,

  input  wire       MEM_DATA_REQ_PAD   ,
  input  wire       MEM_WE_PAD         ,
  input  wire       MEM_TEST_MODE_PAD  ,
  input  wire       MEM_CLK_IN_PAD     ,
  input  wire       MEM_RESET_PAD      ,
  input  wire       MEM_SPI_CLOCK_PAD  ,
  input  wire       MEM_SPI_MOSI_PAD   ,
  input  wire       MEM_SPI_RST_PAD    ,
  input  wire       MEM_SPI_SCLK_PAD   ,
  input  wire       MEM_SPI_SS_PAD     ,
  output wire       MEM_DOUT32_PAD     ,
  output wire       MEM_SPI_MISO_PAD   ,

  input  wire       PLL_CLKREF0_PAD    ,
  input  wire       PLL_CLKREF1_PAD    ,
  output wire       PLL_CLKOUT0_PAD    ,
  output wire       PLL_CLKOUT1_PAD    ,


  output wire       TEMP_0_CLKOUT_PAD  ,
  output wire       TEMP_1_CLKOUT_PAD  ,
  input  wire       TEMP_0_REFCLK_PAD  ,
  input  wire       TEMP_1_REFCLK_PAD  ,
  input  wire       VIN_TEMPSENSE_PAD  ,


  `ifdef ARM_CMSDK_INCLUDE_JTAG
  input  wire       nTRST              ,
  input  wire       TDI                ,
  output wire       TDO                ,
  `endif
  inout  wire       SWDIOTMS           ,
  input  wire       SWCLKTCK
);

  wire          XTAL1;
  wire          XTAL2;
  wire          NRST;

//------------------------------------
// internal wires
  wire               SLEEPING;
  wire               APBACTIVE;
  wire               SYSRESETREQ;    // processor system reset request
  wire               WDOGRESETREQ;   // watchdog system reset request
  wire               HRESETREQ;      // Combined system reset request
  wire               cmsdk_SYSRESETREQ; // Combined system reset request
  wire               clk_ctrl_sys_reset_req;
  wire               PMUHRESETREQ;
  wire               PMUDBGRESETREQ;
  wire               LOCKUP;
  wire               LOCKUPRESET;
  wire               PMUENABLE;
  wire               SLEEPDEEP;


`ifdef CORTEX_M0DESIGNSTART
  // if using DesignStart CortexM0, remove these signals
`else
  wire               WAKEUP;
  wire               GATEHCLK;
  wire               WICENREQ;
  wire               WICENACK;
  wire               CDBGPWRUPREQ;
  wire               CDBGPWRUPACK;
  wire               SLEEPHOLDREQn;
  wire               SLEEPHOLDACKn;

  wire               SYSPWRDOWNACK;
  wire               DBGPWRDOWNACK;
  wire               SYSPWRDOWN;
  wire               DBGPWRDOWN;
  wire               SYSISOLATEn;
  wire               SYSRETAINn;
  wire               DBGISOLATEn;
`endif

  wire               PORESETn;// Power on reset
  wire               HRESETn; // AHB reset
  wire               PRESETn; // APB and peripheral reset
`ifndef CORTEX_M0DESIGNSTART
  wire               DBGRESETn; // Debug system reset
`endif
  wire               FCLK;    // Free running system clock
  wire               HCLK;    // System clock from PMU
`ifndef CORTEX_M0DESIGNSTART
  wire               DCLK;
`endif
  wire               SCLK;
  wire               PCLK;    // Peripheral clock
  wire               PCLKG;   // Gated PCLK for APB
  wire               HCLKSYS; // System clock for memory
  wire               PCLKEN;  // Clock divider for AHB to APB bridge
  // Common AHB signals
  wire  [31:0]       HADDR;
  wire  [1:0]        HTRANS;
  wire  [2:0]        HSIZE;
  wire               HWRITE;
  wire  [31:0]       HWDATA;
  wire               HREADY;

  // Flash memory AHB signals
  wire               flash_hsel;
  wire               flash_hreadyout;
  wire  [31:0]       flash_hrdata;
  wire               flash_hresp;

  // SRAM AHB signals
  wire               sram_hsel;
  wire               sram_hreadyout;
  wire  [31:0]       sram_hrdata;
  wire               sram_hresp;

  // Boot loader/firmware AHB signals
  // Only use if BOOT_MEM_TYPE is not zero
  wire               boot_hsel;
  wire               boot_hreadyout;
  wire  [31:0]       boot_hrdata;
  wire               boot_hresp;

  // internal peripheral signals
  wire               uart_rxd;
  wire               uart_txd;
  wire               uart_txen;

  wire [      31:0] GPIO_O;

  wire        LDO_SPI_RESETn;
  wire [ 1:0] LDO_SPI_SS;
  wire        LDO_SPI_SCLK;
  wire        LDO_SPI_MOSI;
  wire        LDO_SPI_MISO;
  wire        LDO_SPI_APB_SEL;
  wire        LDO_VREF;
  wire        LDO_0_VREG;
  wire        LDO_1_VREG;
  wire        LDO_2_VREG;
  wire LDO_REFCLK;

  wire        MEM_DATA_REQ;
  wire        MEM_WE;
  wire        MEM_TEST_MODE;
  wire        MEM_CLK_IN;
  wire        MEM_RESET;
  wire        MEM_SPI_CLOCK;
  wire        MEM_SPI_MOSI;
  wire        MEM_SPI_RST;
  wire        MEM_SPI_SCLK;
  wire        MEM_SPI_SS;
  wire        MEM_DOUT32;
  wire        MEM_SPI_MISO;


  wire        PLL_CLKREF0;
  wire        PLL_CLKREF1;
  wire        PLL_CLKOUT0;
  wire        PLL_CLKOUT1;

  wire TEMP_0_CLKOUT;
  wire TEMP_1_CLKOUT;
  wire TEMP_0_REFCLK;
  wire TEMP_1_REFCLK;
  wire VIN_TEMPSENSE;

  localparam BASEADDR_GPIO0       = 32'h4001_0000;
  localparam BASEADDR_GPIO1       = 32'h4001_1000;
  localparam BASEADDR_SYSROMTABLE = 32'hF000_0000;

`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_MTB
  // MTB Control
  wire               TSTART;
  wire               TSTOP;

  // EMBEDDED SRAM (MTB) INTERFACE
  wire               RAMHCLK;
  wire  [31:0]       RAMRD;
  wire  [AWIDTH-3:0] RAMAD;
  wire  [31:0]       RAMWD;
  wire               RAMCS;
  wire  [ 3:0]       RAMWE;

  localparam BASEADDR_MTBSRAM     = 32'hF021_0000;

  wire [31:0]        SRAMBASEADDR = BASEADDR_MTBSRAM;
`endif
`endif

  // Internal Debug signals
  wire               i_trst_n;
  wire               i_swditms;
  wire               i_swclktck;
  wire               i_tdi;
  wire               i_tdo;
  wire               i_tdoen_n;
  wire               i_swdo;
  wire               i_swdoen;

  wire               TESTMODE;

`ifdef ARM_CMSDK_INCLUDE_JTAG
`else
  // Serial wire debug is used.  nTRST, TDI and TDO are not needed
  wire               nTRST = 1'b0;
  wire               TDI   = 1'b1;
  wire               TDO;
`endif

  assign TESTMODE = 1'b0;

//----------------------------------------
// Clock and reset controller
//----------------------------------------
`ifdef CORTEX_M0DESIGNSTART
  // Clock controller generates reset if PMU request (PMUHRESETREQ),
  // CPU request or watchdog request (SYSRESETREQ)
  assign clk_ctrl_sys_reset_req = PMUHRESETREQ | cmsdk_SYSRESETREQ;
`else
  // Clock controller generates reset if PMU request (PMUHRESETREQ),
  // CPU request or watchdog request (HRESETREQ)
  assign clk_ctrl_sys_reset_req = PMUHRESETREQ | HRESETREQ;
`endif

  // Clock controller to generate reset and clock signals
  cmsdk_mcu_clkctrl
   #(.CLKGATE_PRESENT(CLKGATE_PRESENT))
   u_cmsdk_mcu_clkctrl(
     // inputs
    .XTAL1            (XTAL1),
    .NRST             (NRST),

    .APBACTIVE        (APBACTIVE),
    .SLEEPING         (SLEEPING),
    .SLEEPDEEP        (SLEEPDEEP),
    .LOCKUP           (LOCKUP),
    .LOCKUPRESET      (LOCKUPRESET),
    .SYSRESETREQ      (clk_ctrl_sys_reset_req),
    .DBGRESETREQ      (PMUDBGRESETREQ),
    .CGBYPASS         (TESTMODE),
    .RSTBYPASS        (TESTMODE),

     // outputs
    .XTAL2            (XTAL2),

    .FCLK             (FCLK),

    .PCLK             (PCLK),
    .PCLKG            (PCLKG),
    .PCLKEN           (PCLKEN),
`ifdef CORTEX_M0DESIGNSTART
    .PORESETn         (PORESETn),  // for cm0 designstart
    .HRESETn          (HRESETn),   // for cm0 designstart
`endif
    .PRESETn          (PRESETn)
    );

//----------------------------------------
//
   // System Reset request can be from processor or watchdog
   // or when lockup happens and the control flag is set.
   assign  cmsdk_SYSRESETREQ = SYSRESETREQ | WDOGRESETREQ |
                               (LOCKUP & LOCKUPRESET);

`ifdef CORTEX_M0DESIGNSTART
   // Power Management Unit will not be available
   assign  HCLK = FCLK;        // connect HCLK to FCLK
   assign  SCLK = FCLK;        // connect SCLK to FCLK

   // Since there is no PMU, these signals are not used
   assign  PMUDBGRESETREQ = 1'b0;
   assign  PMUHRESETREQ   = 1'b0;

`else

  wire   gated_hclk;
  wire   gated_dclk;
  wire   gated_sclk;

`ifdef CORTEX_M0
  // Cortex-M0 Power management unit
  cortexm0_pmu u_cortexm0_pmu
  ( // Inputs
    .FCLK             (FCLK),
    .PORESETn         (PORESETn),
    .HRESETREQ        (cmsdk_SYSRESETREQ), // from processor / watchdog
    .PMUENABLE        (PMUENABLE),       // from System Controller
    .WICENACK         (WICENACK),        // from WIC in integration

    .WAKEUP           (WAKEUP),          // from WIC in integration
    .CDBGPWRUPREQ     (CDBGPWRUPREQ),

    .SLEEPDEEP        (SLEEPDEEP),
    .SLEEPHOLDACKn    (SLEEPHOLDACKn),
    .GATEHCLK         (GATEHCLK),
    .SYSPWRDOWNACK    (SYSPWRDOWNACK),
    .DBGPWRDOWNACK    (DBGPWRDOWNACK),
    .CGBYPASS         (TESTMODE),

   // Outputs
    .HCLK             (gated_hclk),
    .DCLK             (gated_dclk),
    .SCLK             (gated_sclk),
    .WICENREQ         (WICENREQ),
    .CDBGPWRUPACK     (CDBGPWRUPACK),
    .SYSISOLATEn      (SYSISOLATEn),
    .SYSRETAINn       (SYSRETAINn),
    .SYSPWRDOWN       (SYSPWRDOWN),
    .DBGISOLATEn      (DBGISOLATEn),
    .DBGPWRDOWN       (DBGPWRDOWN),
    .SLEEPHOLDREQn    (SLEEPHOLDREQn),
    .PMUDBGRESETREQ   (PMUDBGRESETREQ),
    .PMUHRESETREQ     (PMUHRESETREQ)
   );

  cortexm0_rst_ctl u_rst_ctl
  (// Inputs
   .GLOBALRESETn      (NRST),
   .FCLK              (FCLK),
   .HCLK              (gated_hclk),
   .DCLK              (gated_dclk),
   .SYSRESETREQ       (cmsdk_SYSRESETREQ),
   .PMUHRESETREQ      (PMUHRESETREQ),
   .PMUDBGRESETREQ    (PMUDBGRESETREQ),
   .RSTBYPASS         (1'b0),
   .SE                (1'b0),

   // Outputs
   .PORESETn          (PORESETn),
   .HRESETn           (HRESETn),
   .DBGRESETn         (DBGRESETn),
   .HRESETREQ         (HRESETREQ));


`else
  // Cortex-M0+ Power management unit
  cm0p_ik_pmu u_cortexm0plus_pmu
  ( // Inputs
    .FCLK             (FCLK),
    .PORESETn         (PORESETn),
    .HRESETREQ        (HRESETREQ),
    .PMUENABLE        (PMUENABLE),
    .WICENACK         (WICENACK),

    .WAKEUP           (WAKEUP),
    .CDBGPWRUPREQ     (CDBGPWRUPREQ),

    .SLEEPDEEP        (SLEEPDEEP),
    .SLEEPHOLDACKn    (SLEEPHOLDACKn),
    .GATEHCLK         (GATEHCLK),
    .SYSPWRDOWNACK    (SYSPWRDOWNACK),
    .DBGPWRDOWNACK    (DBGPWRDOWNACK),
    .DFTSE            (1'b0),

    // Outputs
    .HCLK             (gated_hclk),
    .DCLK             (gated_dclk),
    .SCLK             (gated_sclk),
    .WICENREQ         (WICENREQ),
    .CDBGPWRUPACK     (CDBGPWRUPACK),
    .SYSISOLATEn      (SYSISOLATEn),
    .SYSRETAINn       (SYSRETAINn),
    .SYSPWRDOWN       (SYSPWRDOWN),
    .DBGISOLATEn      (DBGISOLATEn),
    .DBGPWRDOWN       (DBGPWRDOWN),
    .SLEEPHOLDREQn    (SLEEPHOLDREQn),
    .PMUHRESETREQ     (PMUHRESETREQ),
    .PMUDBGRESETREQ   (PMUDBGRESETREQ)
   );

  cm0p_ik_rst_ctl u_rst_ctl
  (// Inputs
   .GLOBALRESETn      (NRST),
   .FCLK              (FCLK),
   .HCLK              (gated_hclk),
   .DCLK              (gated_dclk),
   .SYSRESETREQ       (cmsdk_SYSRESETREQ),
   .PMUHRESETREQ      (PMUHRESETREQ),
   .PMUDBGRESETREQ    (PMUDBGRESETREQ),
   .HREADY            (HREADY),
   .DFTRSTDISABLE     (1'b0),
   .DFTSE             (1'b0),

   // Outputs
   .PORESETn          (PORESETn),
   .HRESETn           (HRESETn),
   .DBGRESETn         (DBGRESETn),
   .HRESETREQ         (HRESETREQ));

`endif

  // Bypass clock gating cell in PMU if CLKGATE_PRESENT is 0
  assign  HCLK = (CLKGATE_PRESENT==0) ? FCLK : gated_hclk;
  assign  DCLK = (CLKGATE_PRESENT==0) ? FCLK : gated_dclk;
  assign  SCLK = (CLKGATE_PRESENT==0) ? FCLK : gated_sclk;

  // In this example system, power control takes place immediately.
  // In a real circuit you might need to add delays in the next two
  // signal assignments for correct operation.
  assign   SYSPWRDOWNACK = SYSPWRDOWN;
  assign   DBGPWRDOWNACK = DBGPWRDOWN;

`endif

//---------------------------------------------------
// System design for example Cortex-M0/Cortex-M0+ MCU
//---------------------------------------------------
  cmsdk_mcu_system
   #(.CLKGATE_PRESENT  (CLKGATE_PRESENT),
     .BE               (BE),
     .BASEADDR_GPIO0   (BASEADDR_GPIO0), // GPIO0 Base Address
     .BASEADDR_GPIO1   (BASEADDR_GPIO1), // GPIO1 Base Address
     .BKPT             (BKPT),       // Number of breakpoint comparators
     .DBG              (DBG),        // Debug configuration
     .NUMIRQ           (NUMIRQ),     // NUMIRQ
     .SMUL             (SMUL),       // Multiplier configuration
     .SYST             (SYST),       // SysTick
     .WIC              (WIC),        // Wake-up interrupt controller support
     .WICLINES         (WICLINES),   // Supported WIC lines
     .WPT              (WPT),        // Number of DWT comparators
`ifdef CORTEX_M0PLUS
     .HWF              (HWF),        // Half Word Fetching
     .IOP              (IOP),        // IO Port interface selected
     .IRQDIS           (IRQDIS),     // Interrupt Disable
     .MPU              (MPU),        // Memory Protection support
     .MTB              (MTB),        // MTB select
     .USER             (USER),       // User/Privilege
     .VTOR             (VTOR),       // Vector Table Offset support
     .AWIDTH           (AWIDTH),     // Micro Trace Buffer SRAM address width
     .BASEADDR         (BASEADDR),   // ROM Table Base Address
`endif
     .BOOT_MEM_TYPE    (BOOT_MEM_TYPE), // Boot loader memory type
     .INCLUDE_DMA      (INCLUDE_DMA), // Include DMA feature
     .INCLUDE_BITBAND  (INCLUDE_BITBAND), // Include bit band wrapper
     .INCLUDE_JTAG     (INCLUDE_JTAG), // Include JTAG feature
     .BASEADDR_SYSROMTABLE (BASEADDR_SYSROMTABLE) // System ROM Table base address
   )
    u_cmsdk_mcu_system (
    .FCLK             (FCLK),
    .HCLK             (HCLK),
`ifndef CORTEX_M0DESIGNSTART
    .DCLK             (DCLK),
`endif
    .SCLK             (SCLK),
    .HRESETn          (HRESETn),
    .PORESETn         (PORESETn),
`ifdef CORTEX_M0
    .DBGRESETn        (DBGRESETn),
    .RSTBYPASS        (TESTMODE),
`endif
`ifdef CORTEX_M0PLUS
    .DBGRESETn        (DBGRESETn),
    .DFTRSTDISABLE    (TESTMODE),
`endif

    .PCLK             (PCLK),
    .PCLKG            (PCLKG),
    .PRESETn          (PRESETn),
    .PCLKEN           (PCLKEN),

    // Common AHB signals
    .HADDR            (HADDR),
    .HTRANS           (HTRANS),
    .HSIZE            (HSIZE),
    .HWRITE           (HWRITE),
    .HWDATA           (HWDATA),
    .HREADY           (HREADY),

    // Flash
    .flash_hsel       (flash_hsel),
    .flash_hreadyout  (flash_hreadyout),
    .flash_hrdata     (flash_hrdata),
    .flash_hresp      (flash_hresp),

    // SRAM
    .sram_hsel        (sram_hsel),
    .sram_hreadyout   (sram_hreadyout),
    .sram_hrdata      (sram_hrdata),
    .sram_hresp       (sram_hresp),

    // Optional boot loader
    // Only use if BOOT_MEM_TYPE is not zero
    .boot_hsel        (boot_hsel),
    .boot_hreadyout   (boot_hreadyout),
    .boot_hrdata      (boot_hrdata),
    .boot_hresp       (boot_hresp),

    // Status
    .APBACTIVE        (APBACTIVE),
    .SLEEPING         (SLEEPING),
    .SYSRESETREQ      (SYSRESETREQ),
    .WDOGRESETREQ     (WDOGRESETREQ),
    .LOCKUP           (LOCKUP),
    .LOCKUPRESET      (LOCKUPRESET),
    .PMUENABLE        (PMUENABLE),
    .SLEEPDEEP        (SLEEPDEEP),

`ifdef CORTEX_M0DESIGNSTART
`else  //if using DesignStart CortexM0, remove these signals

    .GATEHCLK         (GATEHCLK),
    .WAKEUP           (WAKEUP),
    .WICENREQ         (WICENREQ),
    .WICENACK         (WICENACK),
    .CDBGPWRUPREQ     (CDBGPWRUPREQ),
    .CDBGPWRUPACK     (CDBGPWRUPACK),
    .SLEEPHOLDREQn    (SLEEPHOLDREQn),
    .SLEEPHOLDACKn    (SLEEPHOLDACKn),

    // Debug
    .nTRST            (i_trst_n),
    .SWDITMS          (i_swditms),
    .SWCLKTCK         (i_swclktck),
    .TDI              (i_tdi),
    .TDO              (i_tdo),
    .nTDOEN           (i_tdoen_n),
    .SWDO             (i_swdo),
    .SWDOEN           (i_swdoen),
`endif


    .GPIO_O             (GPIO_O           ),

    // UART
    .uart_rxd           (uart_rxd),
    .uart_txd           (uart_txd),
    .uart_txen          (uart_txen),

    .LDO_SPI_RESETn     (LDO_SPI_RESETn     ),
    .LDO_SPI_SS         (LDO_SPI_SS         ),
    .LDO_SPI_SCLK       (LDO_SPI_SCLK       ),
    .LDO_SPI_MOSI       (LDO_SPI_MOSI       ),
    .LDO_SPI_MISO       (LDO_SPI_MISO       ),
    .LDO_SPI_APB_SEL    (LDO_SPI_APB_SEL    ),
    .LDO_VREF           (LDO_VREF    ),
    // .LDO_0_VREG           (LDO_0_VREG    ),
    // .LDO_1_VREG           (LDO_1_VREG    ),
    // .LDO_2_VREG           (LDO_2_VREG    ),
    .LDO_REFCLK         (LDO_REFCLK         ),


    .MEM_DATA_REQ       (MEM_DATA_REQ       ),
    .MEM_WE             (MEM_WE             ),
    .MEM_TEST_MODE      (MEM_TEST_MODE      ),
    .MEM_CLK_IN         (MEM_CLK_IN         ),
    .MEM_RESET          (MEM_RESET          ),
    .MEM_SPI_CLOCK      (MEM_SPI_CLOCK      ),
    .MEM_SPI_MOSI       (MEM_SPI_MOSI       ),
    .MEM_SPI_RST        (MEM_SPI_RST        ),
    .MEM_SPI_SCLK       (MEM_SPI_SCLK       ),
    .MEM_SPI_SS         (MEM_SPI_SS         ),
    .MEM_DOUT32         (MEM_DOUT32         ),
    .MEM_SPI_MISO       (MEM_SPI_MISO       ),

    .PLL_CLKREF0        (PLL_CLKREF0        ),
    .PLL_CLKREF1        (PLL_CLKREF1        ),
    .PLL_CLKOUT0        (PLL_CLKOUT0        ),
    .PLL_CLKOUT1        (PLL_CLKOUT1        ),


    .TEMP_0_CLKOUT      (TEMP_0_CLKOUT      ),
    .TEMP_1_CLKOUT      (TEMP_1_CLKOUT      ),
    .TEMP_0_REFCLK      (TEMP_0_REFCLK      ),
    .TEMP_1_REFCLK      (TEMP_1_REFCLK      ),
    .VIN_TEMPSENSE      (VIN_TEMPSENSE      ),


`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_MTB
    // MTB CONTROL
    .TSTART           (TSTART),
    .TSTOP            (TSTOP),

    // EMBEDDED SRAM (MTB) INTERFACE
    .SRAMBASEADDR     (SRAMBASEADDR),
    .RAMHCLK          (RAMHCLK),
    .RAMRD            (RAMRD),
    .RAMAD            (RAMAD),
    .RAMWD            (RAMWD),
    .RAMCS            (RAMCS),
    .RAMWE            (RAMWE),

`endif
    // SRPG IO (no RTL-level function)
    .SYSRETAINn       (SYSRETAINn),
    .SYSISOLATEn      (SYSISOLATEn),
    .SYSPWRDOWN       (SYSPWRDOWN),
    .SYSPWRDOWNACK    (),
    .DBGISOLATEn      (DBGISOLATEn),
    .DBGPWRDOWN       (DBGPWRDOWN),
    .DBGPWRDOWNACK    (),
`endif
    .DFTSE            (1'b0)
  );

//----------------------------------------
// If DMA is present, use SCLK for system HCLK so that
// DMA can run even if processor is in sleep mode.
// Otherwise there is only one master (cpu), so AHB system
// clock can be stopped when DMA take place.

  assign   HCLKSYS  = (INCLUDE_DMA!=0) ? SCLK : HCLK;

//----------------------------------------
// Flash memory
//----------------------------------------

// cmsdk_ahb_ram
//   #(.MEM_TYPE(ROM_MEM_TYPE),
//     .AW(16),  // 64K bytes flash ROM
//     // .filename("image.hex"),
//     .WS_N(`ARM_CMSDK_ROM_MEM_WS_N),
//     .WS_S(`ARM_CMSDK_ROM_MEM_WS_S)
//     // .BE  (BE)
//     )
//    u_ahb_rom (
//     .HCLK             (HCLKSYS),
//     .HRESETn          (HRESETn),
//     .HSEL             (flash_hsel),  // AHB inputs
//     .HADDR            (HADDR[15:0]),
//     .HTRANS           (HTRANS),
//     .HSIZE            (HSIZE),
//     .HWRITE           (HWRITE),
//     .HWDATA           (HWDATA),
//     .HREADY           (HREADY),

//     .HREADYOUT        (flash_hreadyout), // Outputs
//     .HRDATA           (flash_hrdata),
//     .HRESP            (flash_hresp)
//   );

  // wires for SRAM interface
  wire    [13:0] SRAMADDR_program;
  wire    [31:0] SRAMWDATA_program;
  wire    [31:0] SRAMRDATA_program;
  wire     [3:0] SRAMWEN_program;
  wire    [31:0] SRAMWEN_MASK_program;
  wire           SRAMCS_program;

  // AHB to SRAM bridge
  cmsdk_ahb_to_sram
    #(.AW(16)
   ) u_ahb_to_sram_program
  (
    // AHB Inputs
    .HCLK       (HCLKSYS),
    .HRESETn    (HRESETn),
    .HSEL       (flash_hsel),  // AHB inputs
    .HADDR      (HADDR[15:0]),
    .HTRANS     (HTRANS),
    .HSIZE      (HSIZE),
    .HWRITE     (HWRITE),
    .HWDATA     (HWDATA),
    .HREADY     (HREADY),

    // AHB Outputs
    .HREADYOUT  (flash_hreadyout), // Outputs
    .HRDATA     (flash_hrdata),
    .HRESP      (flash_hresp),

   // SRAM input
    .SRAMRDATA  (SRAMRDATA_program),
   // SRAM Outputs
    .SRAMADDR   (SRAMADDR_program),
    .SRAMWDATA  (SRAMWDATA_program),
    .SRAMWEN    (SRAMWEN_program),
    .SRAMCS     (SRAMCS_program)
   );

assign SRAMWEN_MASK_program = ~{ {8{SRAMWEN_program[3]}}
                            ,{8{SRAMWEN_program[2]}}
                            ,{8{SRAMWEN_program[1]}}
                            ,{8{SRAMWEN_program[0]}}};


tsmc65lp_1rw_lg14_w32_bit u_ahb_rom (
  .A(SRAMADDR_program),
  .D(SRAMWDATA_program),
  .CEN(~SRAMCS_program),
  .CLK(HCLKSYS),
  .Q(SRAMRDATA_program),
  .WEN(SRAMWEN_MASK_program),
  .GWEN(&SRAMWEN_MASK_program),

  .TEN(1'b1),
  .EMA(3'b010),
  .EMAW(2'b00),

  .CENY(),
  .WENY(),
  .AY(),
  .SO(),

  .SI(),
  .TCEN(1'b1),
  .TWEN(32'b1),
  .TA(),
  .TD(),
  .RET1N(1'b1),
  .SE(1'b0),
  .DFTRAMBYP(1'b0)
);

//----------------------------------------
// Boot loader / Firmware
//----------------------------------------
// Only use if BOOT_MEM_TYPE is not zero
// cmsdk_ahb_rom
//   #(.MEM_TYPE(BOOT_MEM_TYPE),
//     .AW(12),  // 4K bytes ROM
//     .filename("bootloader.hex"),
//     .WS_N(`ARM_CMSDK_BOOT_MEM_WS_N),
//     .WS_S(`ARM_CMSDK_BOOT_MEM_WS_S),
//     .BE  (BE))
//    u_ahb_bootloader (
//     .HCLK             (HCLKSYS),
//     .HRESETn          (HRESETn),
//     .HSEL             (boot_hsel),  // AHB inputs
//     .HADDR            (HADDR[11:0]),
//     .HTRANS           (HTRANS),
//     .HSIZE            (HSIZE),
//     .HWRITE           (HWRITE),
//     .HWDATA           (HWDATA),
//     .HREADY           (HREADY),

//     .HREADYOUT        (boot_hreadyout), // Outputs
//     .HRDATA           (boot_hrdata),
//     .HRESP            (boot_hresp)
//   );


  // wires for SRAM interface
  wire    [9:0]  SRAMADDR_bootloader;
  wire    [31:0] SRAMRDATA_bootloader;
  wire           SRAMCS_bootloader;

  // AHB to SRAM bridge
  cmsdk_ahb_to_sram
    #(.AW(12)
   ) u_ahb_to_sram_bootloader
  (
    // AHB Inputs
    .HCLK       (HCLKSYS),
    .HRESETn    (HRESETn),
    .HSEL       (boot_hsel),  // AHB inputs
    .HADDR      (HADDR[11:0]),
    .HTRANS     (HTRANS),
    .HSIZE      (HSIZE),
    .HWRITE     (HWRITE),
    .HWDATA     (HWDATA),
    .HREADY     (HREADY),

    // AHB Outputs
    .HREADYOUT  (boot_hreadyout), // Outputs
    .HRDATA     (boot_hrdata),
    .HRESP      (boot_hresp),

   // SRAM input
    .SRAMRDATA  (SRAMRDATA_bootloader),
   // SRAM Outputs
    .SRAMADDR   (SRAMADDR_bootloader),
    .SRAMWDATA  (),
    .SRAMWEN    (),
    .SRAMCS     (SRAMCS_bootloader)
   );

  tsmc65lp_rom_lg10_w32 u_ahb_bootloader (
  .A(SRAMADDR_bootloader),
  .CEN(~SRAMCS_bootloader),
  .CLK(HCLKSYS),
  .Q(SRAMRDATA_bootloader),

  .AY(),
  .CENY(),

  .EMA(3'b010),
  .TEN(1'b1),
  .BEN(1'b1),
  .TCEN(1'b1),
  .TA(10'b0000000000),
  .TQ(32'hFFFFFFFF),
  .PGEN(1'b0),
  .KEN(1'b0)

  );



//----------------------------------------
// SRAM
//----------------------------------------
// cmsdk_ahb_ram
//   #(.MEM_TYPE(RAM_MEM_TYPE),
//     .AW(16),  // 64K bytes SRAM
//     .WS_N(`ARM_CMSDK_RAM_MEM_WS_N),
//     .WS_S(`ARM_CMSDK_RAM_MEM_WS_S))
//    u_ahb_ram (
//     .HCLK             (HCLKSYS),
//     .HRESETn          (HRESETn),
//     .HSEL             (sram_hsel),  // AHB inputs
//     .HADDR            (HADDR[15:0]),
//     .HTRANS           (HTRANS),
//     .HSIZE            (HSIZE),
//     .HWRITE           (HWRITE),
//     .HWDATA           (HWDATA),
//     .HREADY           (HREADY),

//     .HREADYOUT        (sram_hreadyout), // Outputs
//     .HRDATA           (sram_hrdata),
//     .HRESP            (sram_hresp)
//   );

  // wires for SRAM interface
  wire    [13:0] SRAMADDR_data;
  wire    [31:0] SRAMWDATA_data;
  wire    [31:0] SRAMRDATA_data;
  wire     [3:0] SRAMWEN_data;
  wire    [31:0] SRAMWEN_MASK_data;
  wire           SRAMCS_data;

  // AHB to SRAM bridge
  cmsdk_ahb_to_sram
    #(.AW(16)
   ) u_ahb_to_sram_data
  (
    // AHB Inputs
    .HCLK       (HCLKSYS),
    .HRESETn    (HRESETn),
    .HSEL       (sram_hsel),  // AHB inputs
    .HADDR      (HADDR[15:0]),
    .HTRANS     (HTRANS),
    .HSIZE      (HSIZE),
    .HWRITE     (HWRITE),
    .HWDATA     (HWDATA),
    .HREADY     (HREADY),

    // AHB Outputs
    .HREADYOUT  (sram_hreadyout), // Outputs
    .HRDATA     (sram_hrdata),
    .HRESP      (sram_hresp),

   // SRAM input
    .SRAMRDATA  (SRAMRDATA_data),
   // SRAM Outputs
    .SRAMADDR   (SRAMADDR_data),
    .SRAMWDATA  (SRAMWDATA_data),
    .SRAMWEN    (SRAMWEN_data),
    .SRAMCS     (SRAMCS_data)
   );

assign SRAMWEN_MASK_data = ~{ {8{SRAMWEN_data[3]}}
                            ,{8{SRAMWEN_data[2]}}
                            ,{8{SRAMWEN_data[1]}}
                            ,{8{SRAMWEN_data[0]}}};


tsmc65lp_1rw_lg14_w32_bit u_ahb_ram (
  .A(SRAMADDR_data),
  .D(SRAMWDATA_data),
  .CEN(~SRAMCS_data),
  .CLK(HCLKSYS),
  .Q(SRAMRDATA_data),
  .WEN(SRAMWEN_MASK_data),
  .GWEN(&SRAMWEN_MASK_data),

  .TEN(1'b1),
  .EMA(3'b010),
  .EMAW(2'b00),

  .CENY(),
  .WENY(),
  .AY(),
  .SO(),

  .SI(),
  .TCEN(1'b1),
  .TWEN(32'b1),
  .TA(),
  .TD(),
  .RET1N(1'b1),
  .SE(1'b0),
  .DFTRAMBYP(1'b0)
);

//----------------------------------------
// MTB SRAM Memory
//----------------------------------------
`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_MTB

  cm0p_ik_sram
   #(.MEMNAME         ("MTB SRAM"),
     .DATAWIDTH       (32),
     .ADDRWIDTH       (AWIDTH-2),
     .MEMBASE         (BASEADDR_MTBSRAM))
    u_mtbram
    (//Output
     .RDATA           (RAMRD),
     //Inputs
     .CLK             (RAMHCLK),
     .ADDRESS         (RAMAD[AWIDTH-3:0]),
     .CS              (RAMCS),
     .WE              (RAMWE),
     .WDATA           (RAMWD));

`endif
`endif

//----------------------------------------
// I/O port pin muxing and tristate
//----------------------------------------
  cmsdk_mcu_pin_mux
    u_pin_mux (
    .XTAL1 (XTAL1),
    .NRST  (NRST),
    .XTAL2 (XTAL2),

    .GPIO_O          (GPIO_O),

    // UART
    .uart_rxd        (uart_rxd),
    .uart_txd        (uart_txd),
    .uart_txen       (uart_txen),

    .LDO_SPI_RESETn     (LDO_SPI_RESETn     ),
    .LDO_SPI_SS         (LDO_SPI_SS         ),
    .LDO_SPI_SCLK       (LDO_SPI_SCLK       ),
    .LDO_SPI_MOSI       (LDO_SPI_MOSI       ),
    .LDO_SPI_MISO       (LDO_SPI_MISO       ),
    .LDO_SPI_APB_SEL    (LDO_SPI_APB_SEL    ),
    .LDO_VREF           (LDO_VREF          ),
    // .LDO_0_VREG         (LDO_0_VREG        ),
    // .LDO_1_VREG         (LDO_1_VREG        ),
    // .LDO_2_VREG         (LDO_2_VREG        ),
    .LDO_REFCLK         (LDO_REFCLK),

    .MEM_DATA_REQ       (MEM_DATA_REQ       ),
    .MEM_WE             (MEM_WE             ),
    .MEM_TEST_MODE      (MEM_TEST_MODE      ),
    .MEM_CLK_IN         (MEM_CLK_IN         ),
    .MEM_RESET          (MEM_RESET          ),
    .MEM_SPI_CLOCK      (MEM_SPI_CLOCK      ),
    .MEM_SPI_MOSI       (MEM_SPI_MOSI       ),
    .MEM_SPI_RST        (MEM_SPI_RST        ),
    .MEM_SPI_SCLK       (MEM_SPI_SCLK       ),
    .MEM_SPI_SS         (MEM_SPI_SS         ),
    .MEM_DOUT32         (MEM_DOUT32         ),
    .MEM_SPI_MISO       (MEM_SPI_MISO       ),

    .PLL_CLKREF0        (PLL_CLKREF0),
    .PLL_CLKREF1        (PLL_CLKREF1),
    .PLL_CLKOUT0        (PLL_CLKOUT0),
    .PLL_CLKOUT1        (PLL_CLKOUT1),

    .TEMP_0_CLKOUT (TEMP_0_CLKOUT),
    .TEMP_1_CLKOUT (TEMP_1_CLKOUT),
    .TEMP_0_REFCLK (TEMP_0_REFCLK),
    .TEMP_1_REFCLK (TEMP_1_REFCLK),
    .VIN_TEMPSENSE (VIN_TEMPSENSE),

`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_MTB
    // MTB CONTROL
    .TSTART           (TSTART),
    .TSTOP            (TSTOP),
`endif
`endif


    // Debug
    .i_trst_n         (i_trst_n),
    .i_swditms        (i_swditms),
    .i_swclktck       (i_swclktck),
    .i_tdi            (i_tdi),
    .i_tdo            (i_tdo),
    .i_tdoen_n        (i_tdoen_n),
    .i_swdo           (i_swdo),
    .i_swdoen         (i_swdoen),

    // IO pads

.XTAL1_PAD(XTAL1_PAD),
.NRST_PAD(NRST_PAD),
.XTAL2_PAD(XTAL2_PAD),

    .GPIO_INIT_PAD          (GPIO_INIT_PAD),
    .GPIO_USER0_PAD         (GPIO_USER0_PAD),
    .GPIO_USER1_PAD         (GPIO_USER1_PAD),

    .UART_RXD_PAD           (UART_RXD_PAD ),
    .UART_TXD_PAD           (UART_TXD_PAD ),

    .LDO_SPI_RESETn_PAD     (LDO_SPI_RESETn_PAD     ),
    .LDO_SPI_SS_PAD         (LDO_SPI_SS_PAD         ),
    .LDO_SPI_SCLK_PAD       (LDO_SPI_SCLK_PAD       ),
    .LDO_SPI_MOSI_PAD       (LDO_SPI_MOSI_PAD       ),
    .LDO_SPI_MISO_PAD       (LDO_SPI_MISO_PAD       ),
    .LDO_SPI_APB_SEL_PAD    (LDO_SPI_APB_SEL_PAD    ),
    .LDO_VREF_PAD           (LDO_VREF_PAD          ),
    // .LDO_0_VREG_PAD         (LDO_0_VREG_PAD        ),
    // .LDO_1_VREG_PAD         (LDO_1_VREG_PAD        ),
    // .LDO_2_VREG_PAD         (LDO_2_VREG_PAD        ),
    .LDO_REFCLK_PAD         (LDO_REFCLK_PAD),

    .MEM_DATA_REQ_PAD       (MEM_DATA_REQ_PAD       ),
    .MEM_WE_PAD             (MEM_WE_PAD             ),
    .MEM_TEST_MODE_PAD      (MEM_TEST_MODE_PAD      ),
    .MEM_CLK_IN_PAD         (MEM_CLK_IN_PAD         ),
    .MEM_RESET_PAD          (MEM_RESET_PAD          ),
    .MEM_SPI_CLOCK_PAD      (MEM_SPI_CLOCK_PAD      ),
    .MEM_SPI_MOSI_PAD       (MEM_SPI_MOSI_PAD       ),
    .MEM_SPI_RST_PAD        (MEM_SPI_RST_PAD        ),
    .MEM_SPI_SCLK_PAD       (MEM_SPI_SCLK_PAD       ),
    .MEM_SPI_SS_PAD         (MEM_SPI_SS_PAD         ),
    .MEM_DOUT32_PAD         (MEM_DOUT32_PAD         ),
    .MEM_SPI_MISO_PAD       (MEM_SPI_MISO_PAD       ),

    .PLL_CLKREF0_PAD           (PLL_CLKREF0_PAD ),
    .PLL_CLKREF1_PAD           (PLL_CLKREF1_PAD ),
    .PLL_CLKOUT0_PAD           (PLL_CLKOUT0_PAD ),
    .PLL_CLKOUT1_PAD           (PLL_CLKOUT1_PAD ),

    .TEMP_0_CLKOUT_PAD (TEMP_0_CLKOUT_PAD),
    .TEMP_1_CLKOUT_PAD (TEMP_1_CLKOUT_PAD),
    .TEMP_0_REFCLK_PAD (TEMP_0_REFCLK_PAD),
    .TEMP_1_REFCLK_PAD (TEMP_1_REFCLK_PAD),
    .VIN_TEMPSENSE_PAD (VIN_TEMPSENSE_PAD),

    .nTRST            (nTRST),  // Not needed if serial-wire debug is used
    .TDI              (TDI),    // Not needed if serial-wire debug is used
    .SWDIOTMS         (SWDIOTMS),
    .SWCLKTCK         (SWCLKTCK),
    .TDO              (TDO)     // Not needed if serial-wire debug is used

  );

 // --------------------------------------------------------------------------------
 // TARMAC for the Cortex-M0 or Cortex-M0+
 // --------------------------------------------------------------------------------

`ifdef CORTEX_M0PLUS
`ifdef USE_TARMAC

`define ARM_CM0PIK_PATH cmsdk_mcu.u_cmsdk_mcu_system.u_cm0pmtbintegration.u_cm0pintegration.u_imp.u_cortexm0plus

  cm0p_tarmac
   u_tarmac
     (.en_i           (1'b1),
      .echo_i         (1'b0),
      .id_i           (32'h0),
      .use_time_i     (1'b1),
      .tube_i         (32'h40400000),
      .halted_i       (`ARM_CM0PIK_PATH.HALTED),
      .lockup_i       (`ARM_CM0PIK_PATH.LOCKUP),
      .hclk           (`ARM_CM0PIK_PATH.HCLK),
      .hready_i       (`ARM_CM0PIK_PATH.HREADY),
      .haddr_i        (`ARM_CM0PIK_PATH.HADDR[31:0]),
      .hprot_i        (`ARM_CM0PIK_PATH.HPROT[3:0]),
      .hsize_i        (`ARM_CM0PIK_PATH.HSIZE[2:0]),
      .hwrite_i       (`ARM_CM0PIK_PATH.HWRITE),
      .htrans_i       (`ARM_CM0PIK_PATH.HTRANS[1:0]),
      .hresetn_i      (`ARM_CM0PIK_PATH.HRESETn),
      .hresp_i        (`ARM_CM0PIK_PATH.HRESP),
      .hrdata_i       (`ARM_CM0PIK_PATH.HRDATA[31:0]),
      .hwdata_i       (`ARM_CM0PIK_PATH.HWDATA[31:0]),
      .ppb_trans_i    (`ARM_CM0PIK_PATH.u_top.u_sys.u_matrix.ppb_trans),
      .scs_rdata_i    (`ARM_CM0PIK_PATH.u_top.u_sys.u_matrix.scs_rdata),
      .ahb_trans_i    (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.ahb_trans),
      .ipsr_i         (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.ipsr_q[5:0]),
      .tbit_i         (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.tbit_q),
      .fault_i        (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.fault_q),
      .cc_pass_i      (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.cc_pass),
      .spsel_i        (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.spsel_q),
      .npriv_i        (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.npriv_q),
      .primask_i      (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.primask_q),
      .apsr_i         (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.apsr_q[3:0]),
      .state_i        (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.state_q[3:0]),
      .op_i           (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.op_q[15:0]),
      .op_s_i         (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.op_s_q),
      .iq_i           (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.iq_q[15:0]),
      .iq_s_i         (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.iq_s_q),
      .psp_en_i       (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.psp_en),
      .msp_en_i       (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.msp_en),
      .wr_data_i      (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.wr_data[31:0]),
      .wr_data_sp_i   (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.wr_data_sp[29:0]),
      .wr_addr_en_i   (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.wr_addr_en[3:0]),
      .iaex_i         (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.iaex_q[30:0]),
      .preempt_i      (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.preempt),
      .int_ready_i    (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.int_ready_q),
      .irq_ack_i      (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.irq_ack),
      .rfe_ack_i      (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.rfe_ack),
      .int_pend_num_i (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.nvm_int_pend_num_i[5:0]),
      .atomic_i       (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.atomic_q),
      .hardfault_i    (`ARM_CM0PIK_PATH.u_top.u_sys.u_core.hdf_req),
      .iotrans_i      (`ARM_CM0PIK_PATH.IOTRANS),
      .iowrite_i      (`ARM_CM0PIK_PATH.IOWRITE),
      .iosize_i       (`ARM_CM0PIK_PATH.IOSIZE[1:0]),
      .ioaddr_i       (`ARM_CM0PIK_PATH.IOADDR[31:0]),
      .iordata_i      (`ARM_CM0PIK_PATH.IORDATA[31:0]),
      .iowdata_i      (`ARM_CM0PIK_PATH.IOWDATA[31:0]),
      .slvtrans_i     (`ARM_CM0PIK_PATH.SLVTRANS[1:0]),
      .slvwrite_i     (`ARM_CM0PIK_PATH.SLVWRITE),
      .slvsize_i      (`ARM_CM0PIK_PATH.SLVSIZE[1:0]),
      .slvaddr_i      (`ARM_CM0PIK_PATH.SLVADDR[31:0]),
      .slvrdata_i     (`ARM_CM0PIK_PATH.SLVRDATA[31:0]),
      .slvwdata_i     (`ARM_CM0PIK_PATH.SLVWDATA[31:0]),
      .slvready_i     (`ARM_CM0PIK_PATH.SLVREADY),
      .slvresp_i      (`ARM_CM0PIK_PATH.SLVRESP)
  );

`endif // USE_TARMAC
`else

`ifdef CORTEX_M0
`ifdef USE_TARMAC

`define ARM_CM0IK_PATH cmsdk_mcu.u_cmsdk_mcu_system.u_cortex_m0_integration.u_cortexm0

  cm0_tarmac #(.LOGFILENAME("tarmac0.log"))
    u_tarmac
      (.enable_i      (1'b1),

       .hclk_i        (`ARM_CM0IK_PATH.HCLK),
       .hready_i      (`ARM_CM0IK_PATH.HREADY),
       .haddr_i       (`ARM_CM0IK_PATH.HADDR[31:0]),
       .hprot_i       (`ARM_CM0IK_PATH.HPROT[3:0]),
       .hsize_i       (`ARM_CM0IK_PATH.HSIZE[2:0]),
       .hwrite_i      (`ARM_CM0IK_PATH.HWRITE),
       .htrans_i      (`ARM_CM0IK_PATH.HTRANS[1:0]),
       .hresetn_i     (`ARM_CM0IK_PATH.HRESETn),
       .hresp_i       (`ARM_CM0IK_PATH.HRESP),
       .hrdata_i      (`ARM_CM0IK_PATH.HRDATA[31:0]),
       .hwdata_i      (`ARM_CM0IK_PATH.HWDATA[31:0]),
       .lockup_i      (`ARM_CM0IK_PATH.LOCKUP),
       .halted_i      (`ARM_CM0IK_PATH.HALTED),
       .codehintde_i  (`ARM_CM0IK_PATH.CODEHINTDE[2:0]),
       .codenseq_i    (`ARM_CM0IK_PATH.CODENSEQ),

       .hdf_req_i     (`ARM_CM0IK_PATH.u_top.u_sys.ctl_hdf_request),
       .int_taken_i   (`ARM_CM0IK_PATH.u_top.u_sys.dec_int_taken_o),
       .int_return_i  (`ARM_CM0IK_PATH.u_top.u_sys.dec_int_return_o),
       .int_pend_i    (`ARM_CM0IK_PATH.u_top.u_sys.nvm_int_pend),
       .pend_num_i    (`ARM_CM0IK_PATH.u_top.u_sys.nvm_int_pend_num[5:0]),
       .ipsr_i        (`ARM_CM0IK_PATH.u_top.u_sys.psr_ipsr[5:0]),

       .ex_last_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.ctl_ex_last),
       .iaex_en_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.ctl_iaex_en),
       .reg_waddr_i   (`ARM_CM0IK_PATH.u_top.u_sys.u_core.ctl_wr_addr[3:0]),
       .reg_write_i   (`ARM_CM0IK_PATH.u_top.u_sys.u_core.ctl_wr_en),
       .xpsr_en_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.ctl_xpsr_en),
       .fe_addr_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.pfu_fe_addr[30:0]),
       .int_delay_i   (`ARM_CM0IK_PATH.u_top.u_sys.u_core.pfu_int_delay),
       .special_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.pfu_op_special),
       .opcode_i      (`ARM_CM0IK_PATH.u_top.u_sys.u_core.pfu_opcode[15:0]),
       .reg_wdata_i   (`ARM_CM0IK_PATH.u_top.u_sys.u_core.psr_gpr_wdata[31:0]),

       .atomic_i      (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_ctl.atomic),
       .atomic_nxt_i  (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_ctl.atomic_nxt),
       .dabort_i      (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_ctl.data_abort),
       .ex_last_nxt_i (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_ctl.ex_last_nxt),
       .int_preempt_i (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_ctl.int_preempt),

       .psp_sel_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_gpr.psp_sel),
       .xpsr_i        (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_gpr.xpsr[31:0]),

       .iaex_i        (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_pfu.iaex[30:0]),
       .iaex_nxt_i    (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_pfu.iaex_nxt[30:0]),
       .opcode_nxt_i  (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_pfu.ibuf_de_nxt[15:0]),
       .delay_count_i (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_pfu.ibuf_lo[13:6]),
       .tbit_en_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_pfu.tbit_en),

       .cflag_en_i    (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_psr.cflag_ena),
       .ipsr_en_i     (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_psr.ipsr_ena),
       .nzflag_en_i   (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_psr.nzflag_ena),
       .vflag_en_i    (`ARM_CM0IK_PATH.u_top.u_sys.u_core.u_psr.vflag_ena)
  );

`endif // USE_TARMAC
`endif // CORTEX_M0
`endif // CORTEX_M0PLUS

 // --------------------------------------------------------------------------------
 // Assertion properties for configuration check
 // --------------------------------------------------------------------------------

`ifdef ARM_AHB_ASSERT_ON
`include "std_ovl_defines.h"

   assert_never
     #(`OVL_FATAL,`OVL_ASSERT,
     "No program ROM. Verilog parameter ROM_MEM_TYPE is set to AHB_ROM_NONE, which is not valid for a CMSDK system.")
   u_ovl_rom_config_check
     (.clk(HCLK), .reset_n(HRESETn), .test_expr (ROM_MEM_TYPE==`AHB_ROM_NONE));

   assert_never
     #(`OVL_FATAL,`OVL_ASSERT,
     "No SRAM. Verilog parameter RAM_MEM_TYPE is set to AHB_RAM_NONE, which is not valid for a CMSDK system.")
   u_ovl_ram_config_check
     (.clk(HCLK), .reset_n(HRESETn), .test_expr (RAM_MEM_TYPE==`AHB_RAM_NONE));

`endif

endmodule
