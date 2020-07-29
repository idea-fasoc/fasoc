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
// Abstract : System level design for the example Cortex-M0 system
//-----------------------------------------------------------------------------
`include "cmsdk_mcu_defs.v"

module cmsdk_mcu_system #(
  `ifdef ARM_CMSDK_INCLUDE_CLKGATE
  parameter CLKGATE_PRESENT      = 1                       ,
  `else
  parameter CLKGATE_PRESENT      = 0                       ,
  `endif
  parameter BASEADDR_GPIO0       = 32'h4001_0000           , // GPIO0 peripheral base address
  parameter BASEADDR_GPIO1       = 32'h4001_1000           , // GPIO1 peripheral base address
  parameter BE                   = 0                       , // 1: Big endian 0: little endian
  parameter BKPT                 = 4                       , // Number of breakpoint comparators
  parameter DBG                  = 1                       , // Debug configuration
  parameter NUMIRQ               = 32                      , // NUM of IRQ
  parameter SMUL                 = 0                       , // Multiplier configuration
  parameter SYST                 = 1                       , // SysTick
  parameter WIC                  = 1                       , // Wake-up interrupt controller support
  parameter WICLINES             = 34                      , // Supported WIC lines
  parameter WPT                  = 2                       , // Number of DWT comparators
  `ifdef CORTEX_M0PLUS
  parameter HWF                  = 0                       , // Half-Word Fetching
  `ifdef ARM_CMSDK_INCLUDE_IOP
  parameter IOP                  = 1                       , // IO Port interface selected
  `else
  parameter IOP                  = 0                       , // IO Port not selected
  `endif
  parameter IRQDIS               = 32'h00000000            , // Interrupt Disable
  parameter MPU                  = 8                       , // 8 Memory Protection Regions
  `ifdef ARM_CMSDK_INCLUDE_MTB
  parameter MTB                  = 1                       , // MTB present
  `else
  parameter MTB                  = 0                       , // MTB not present
  `endif
  parameter USER                 = 0                       , // User/Privilege
  parameter VTOR                 = 0                       , // Vector Table Offset support
  parameter AWIDTH               = 12                      , // Micro Trace Buffer SRAM address width.
  parameter BASEADDR             = 32'hF0000003            ,
  `endif

  parameter BOOT_MEM_TYPE        = `ARM_CMSDK_BOOT_MEM_TYPE, // Boot loader memory type

  `ifdef ARM_CMSDK_INCLUDE_DMA
  parameter INCLUDE_DMA          = 1                       , // Include instantiation of DMA-230
  // This option also add a number of bus components
  parameter DMA_CHANNEL_NUM      = 1                       ,
  `else
  parameter INCLUDE_DMA          = 0                       , // Do not instantiation DMA-230
  parameter DMA_CHANNEL_NUM      = 1                       ,
  `endif

  `ifdef ARM_CMSDK_INCLUDE_BITBAND
  parameter INCLUDE_BITBAND      = 1                       ,
  // Include instantiation of Bit-band wrapper
  // This option add bit band wrapper to CPU interface
  `else
  parameter INCLUDE_BITBAND      = 0                       ,
  `endif

  `ifdef ARM_CMSDK_INCLUDE_JTAG
  parameter INCLUDE_JTAG         = 1                       , // Include JTAG feature
  `else
  parameter INCLUDE_JTAG         = 0                       , // Do not Include JTAG feature
  `endif

  // Generate BOOT_LOADER_PRESENT based on BOOT_MEM_TYPE
  // This is a derived parameter - do not override using instiantiation
  parameter BOOT_LOADER_PRESENT  = (BOOT_MEM_TYPE            ==0) ? 0 : 1,

  // Location of the System ROM Table.
  parameter BASEADDR_SYSROMTABLE = 32'hF000_0000,

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
  input  wire              FCLK           , // Free running clock
  input  wire              HCLK           , // AHB clock(from PMU)
  `ifndef CORTEX_M0DESIGNSTART
  input  wire              DCLK           , // Debug system clock (from PMU)
  `endif
  input  wire              SCLK           , // System clock
  input  wire              HRESETn        , // AHB and System reset
  input  wire              PORESETn       , // Power on reset
  `ifdef CORTEX_M0
  input  wire              DBGRESETn      , // Debug reset
  input  wire              RSTBYPASS      , // Reset by pass (for testing)
  `endif
  `ifdef CORTEX_M0PLUS
  input  wire              DBGRESETn      , // Debug reset
  input  wire              DFTRSTDISABLE  , // Reset by pass (for testing)
  `endif
  input  wire              PCLK           , // Peripheral clock
  input  wire              PCLKG          , // Gated Peripheral bus clock
  input  wire              PRESETn        , // Peripheral system and APB reset
  input  wire              PCLKEN         , // Clock divide control for AHB to APB bridge

  output wire [      31:0] HADDR          , // AHB to memory blocks - address
  output wire [       1:0] HTRANS         , // AHB to memory blocks - transfer ctrl
  output wire [       2:0] HSIZE          , // AHB to memory blocks - transfer size
  output wire              HWRITE         , // AHB to memory blocks - write ctrl
  output wire [      31:0] HWDATA         , // AHB to memory blocks - write data
  output wire              HREADY         , // AHB to memory blocks - AHB ready

  output wire              flash_hsel     , // AHB to flash memory - select
  input  wire              flash_hreadyout, // AHB from flash blocks - ready
  input  wire [      31:0] flash_hrdata   , // AHB from flash blocks - read data
  input  wire              flash_hresp    , // AHB from flash blocks - response

  output wire              sram_hsel      , // AHB to SRAM - select
  input  wire              sram_hreadyout , // AHB from SRAM - ready
  input  wire [      31:0] sram_hrdata    , // AHB from SRAM - read data
  input  wire              sram_hresp     , // AHB from SRAM - response

                                            // Optional : only if BOOT_MEM_TYPE!=0
  output wire              boot_hsel      , // AHB to boot loader - select
  input  wire              boot_hreadyout , // AHB from boot loader - ready
  input  wire [      31:0] boot_hrdata    , // AHB from boot loader - read data
  input  wire              boot_hresp     , // AHB from boot loader - response

  output wire              APBACTIVE      , // APB bus active (for clock gating of PCLKG)
  output wire              SLEEPING       , // Processor status - sleeping
  output wire              SLEEPDEEP      , // Processor status - deep sleep
  output wire              SYSRESETREQ    , // Processor control - system reset request
  output wire              WDOGRESETREQ   , // Watchdog reset request
  output wire              LOCKUP         , // Processor status - Locked up
  output wire              LOCKUPRESET    , // System Controller cfg - reset if lockup
  output wire              PMUENABLE      , // System Controller cfg - Enable PMU

  `ifdef CORTEX_M0DESIGNSTART
  `else  //if using DesignStart Cortex-M0, remove these signals
  output wire              GATEHCLK       , // Processor status - safe to gate HCLK
  output wire              WAKEUP         , // Wake up request from WIC
  input  wire              WICENREQ       , // WIC enable request from PMU
  output wire              WICENACK       , // WIC enable ack to PMU
  output wire              CDBGPWRUPREQ   , // Debug Power Up request to PMU
  input  wire              CDBGPWRUPACK   , // Debug Power Up ACK from PMU
  input  wire              SLEEPHOLDREQn  , // Sleep extension request from PMU
  output wire              SLEEPHOLDACKn  , // Sleep extension request to PMU

  input  wire              nTRST          , // JTAG - Test reset (active low)
  input  wire              SWDITMS        , // JTAG/SWD - TMS / SWD data input
  input  wire              SWCLKTCK       , // JTAG/SWD - TCK / SWCLK
  input  wire              TDI            , // JTAG - Test data in
  output wire              TDO            , // JTAG - Test data out
  output wire              nTDOEN         , // JTAG - Test data out enable (active low)
  output wire              SWDO           , // SWD - SWD data output
  output wire              SWDOEN         , // SWD - SWD data output enable
  `endif

  output wire [      31:0] GPIO_O         ,

  input  wire              uart_rxd       , // Uart receive data
  output wire              uart_txd       , // Uart transmit data
  output wire              uart_txen      , // Uart transmit data enable

  input  wire              LDO_SPI_RESETn ,
  input  wire [       1:0] LDO_SPI_SS     ,
  input  wire              LDO_SPI_SCLK   ,
  input  wire              LDO_SPI_MOSI   ,
  output wire              LDO_SPI_MISO   ,
  input  wire              LDO_SPI_APB_SEL,
  input  wire              LDO_VREF       ,
  // inout  wire              LDO_0_VREG     ,
  // inout  wire              LDO_1_VREG     ,
  // inout  wire              LDO_2_VREG     ,
  input  wire              LDO_REFCLK     ,

  input  wire              MEM_DATA_REQ   ,
  input  wire              MEM_WE         ,
  input  wire              MEM_TEST_MODE  ,
  input  wire              MEM_CLK_IN     ,
  input  wire              MEM_RESET      ,
  input  wire              MEM_SPI_CLOCK  ,
  input  wire              MEM_SPI_MOSI   ,
  input  wire              MEM_SPI_RST    ,
  input  wire              MEM_SPI_SCLK   ,
  input  wire              MEM_SPI_SS     ,
  output wire              MEM_DOUT32     ,
  output wire              MEM_SPI_MISO   ,

  input  wire              PLL_CLKREF0    ,
  input  wire              PLL_CLKREF1    ,
  output wire              PLL_CLKOUT0    ,
  output wire              PLL_CLKOUT1    ,

  output wire              TEMP_0_CLKOUT  ,
  output wire              TEMP_1_CLKOUT  ,
  input  wire              TEMP_0_REFCLK  ,
  input  wire              TEMP_1_REFCLK  ,
  input  wire              VIN_TEMPSENSE  ,


  `ifdef CORTEX_M0PLUS
  `ifdef ARM_CMSDK_INCLUDE_MTB
  // MTB Control
  input  wire              TSTART         , // External Trace Start pin
  input  wire              TSTOP          , // External Trace Stop pin

  // EMBEDDED SRAM (MTB) INTERFACE
  input  wire [      31:0] SRAMBASEADDR   , // MTB SRAM base address
  output wire              RAMHCLK        , // MTB RAM clock, optionally gated
  input  wire [      31:0] RAMRD          , // MTB connected RAM read-data
  output wire [AWIDTH-3:0] RAMAD          , // MTB connected RAM address
  output wire [      31:0] RAMWD          , // MTB connected RAM write-data
  output wire              RAMCS          , // MTB connected RAM chip select
  output wire [       3:0] RAMWE          , // MTB RAM byte lane write enables
  `endif

  // SRPG IO (no RTL-level function)
  input  wire              SYSRETAINn     , // Power specific controls
  input  wire              SYSISOLATEn    , // ...
  input  wire              SYSPWRDOWN     , // ...
  output wire              SYSPWRDOWNACK  , // ...
  input  wire              DBGISOLATEn    , // ...
  input  wire              DBGPWRDOWN     , // ...
  output wire              DBGPWRDOWNACK  , // ...
  `endif

  input  wire              DFTSE,
  output  wire  [3:0]  i_paddr,
  output  wire         i_psel,
  input  wire         apb0_psel,
  output  wire         apb0_pready,
  output  wire  [31:0]  apb0_prdata,
  output  wire         apb0_pslverr,
  input  wire         apb1_psel,
  output  wire         apb1_pready,
  output  wire  [31:0]  apb1_prdata,
  output  wire         apb1_pslverr,
  input  wire         apb2_psel,
  output  wire         apb2_pready,
  output  wire  [31:0]  apb2_prdata,
  output  wire         apb2_pslverr,
  input  wire         apb3_psel,
  output  wire         apb3_pready,
  output  wire  [31:0]  apb3_prdata,
  output  wire         apb3_pslverr,
  input  wire         apb4_psel,
  output  wire         apb4_pready,
  output  wire  [31:0]  apb4_prdata,
  output  wire         apb4_pslverr,
  input  wire         apb5_psel,
  output  wire         apb5_pready,
  output  wire  [31:0]  apb5_prdata,
  output  wire         apb5_pslverr,
  input  wire         apb6_psel,
  output  wire         apb6_pready,
  output  wire  [31:0]  apb6_prdata,
  output  wire         apb6_pslverr,
  input  wire         apb7_psel,
  output  wire         apb7_pready,
  output  wire  [31:0]  apb7_prdata,
  output  wire         apb7_pslverr,
  input  wire         apb8_psel,
  output  wire         apb8_pready,
  output  wire  [31:0]  apb8_prdata,
  output  wire         apb8_pslverr,
  input  wire         apb9_psel,
  output  wire         apb9_pready,
  output  wire  [31:0]  apb9_prdata,
  output  wire         apb9_pslverr,
  input  wire         apb10_psel,
  output  wire         apb10_pready,
  output  wire  [31:0]  apb10_prdata,
  output  wire         apb10_pslverr,
  input  wire         apb11_psel,
  output  wire         apb11_pready,
  output  wire  [31:0]  apb11_prdata,
  output  wire         apb11_pslverr,
  input  wire         apb12_psel,
  output  wire         apb12_pready,
  output  wire  [31:0]  apb12_prdata,
  output  wire         apb12_pslverr,
  input  wire         apb13_psel,
  output  wire         apb13_pready,
  output  wire  [31:0]  apb13_prdata,
  output  wire         apb13_pslverr,
  input  wire         apb14_psel,
  output  wire         apb14_pready,
  output  wire  [31:0]  apb14_prdata,
  output  wire         apb14_pslverr,
  input  wire         apb15_psel,
  output  wire         apb15_pready,
  output  wire  [31:0]  apb15_prdata,
  output  wire         apb15_pslverr,
  input  wire         i_pready_mux,
  input  wire  [31:0]  i_prdata_mux
);           // dummy scan enable port for synthesis

  // -------------------------------
  // Internal signals
  // -------------------------------
  wire              HCLKSYS;        // System AHB clock

  // System bus from processor
  wire     [31:0]   cm0_haddr;
  wire     [1:0]    cm0_htrans;
  wire     [2:0]    cm0_hsize;
  wire     [2:0]    cm0_hburst;
  wire     [3:0]    cm0_hprot;
  wire              cm0_hmaster;
  wire              cm0_hmastlock;
  wire              cm0_hwrite;
  wire     [31:0]   cm0_hwdata;
  wire     [31:0]   cm0_hrdata;
  wire              cm0_hready;
  wire              cm0_hresp;

  // Bit band wrapper bus between CPU and the reset of the system
  wire     [31:0]   cm_haddr;
  wire     [1:0]    cm_htrans;
  wire     [2:0]    cm_hsize;
  wire     [2:0]    cm_hburst;
  wire     [3:0]    cm_hprot;
  wire              cm_hmastlock;
  wire              cm_hmaster;
  wire              cm_hwrite;
  wire     [31:0]   cm_hwdata;
  wire     [31:0]   cm_hrdata;
  wire              cm_hready;
  wire              cm_hreadyout;
  wire              cm_hresp;

  // System bus from DMA Controller
  // (Optional, only used when INCLUDE_DMA!=0)
  wire     [31:0]   dmac_haddr;
  wire     [1:0]    dmac_htrans;
  wire     [2:0]    dmac_hsize;
  wire     [2:0]    dmac_hburst;
  wire     [3:0]    dmac_hprot;
  wire              dmac_hmastlock;
  wire              dmac_hwrite;
  wire     [31:0]   dmac_hwdata;
  wire     [31:0]   dmac_hrdata;
  wire              dmac_hready;
  wire              dmac_hresp;

  wire              dmac_psel;
  wire              dmac_pready;
  wire              dmac_pslverr;
  wire     [31:0]   dmac_prdata;

  // System bus
  wire              sys_hselm;  // Note: the sys_hselm signal is for protocol checking only.
  wire     [31:0]   sys_haddr;
  wire     [1:0]    sys_htrans;
  wire     [2:0]    sys_hsize;
  wire     [2:0]    sys_hburst;
  wire     [3:0]    sys_hprot;
  wire              sys_hmaster;
  wire              sys_hmastlock;
  wire              sys_hwrite;
  wire     [31:0]   sys_hwdata;
  wire     [31:0]   sys_hrdata;
  wire              sys_hready;
  wire              sys_hreadyout;
  wire              sys_hresp;

  wire              defslv_hsel;   // AHB default slave signals
  wire              defslv_hreadyout;
  wire     [31:0]   defslv_hrdata;
  wire              defslv_hresp;

  wire              apbsys_hsel;  // APB subsystem AHB interface signals
  wire              apbsys_hreadyout;
  wire     [31:0]   apbsys_hrdata;
  wire              apbsys_hresp;

  wire              gpio0_hsel;   // AHB GPIO bus interface signals
  wire              gpio0_hreadyout;
  wire     [31:0]   gpio0_hrdata;
  wire              gpio0_hresp;

  wire              gpio1_hsel;   // AHB GPIO bus interface signals
  wire              gpio1_hreadyout;
  wire     [31:0]   gpio1_hrdata;
  wire              gpio1_hresp;

  wire              sysctrl_hsel;  // System control bus interface signals
  wire              sysctrl_hreadyout;
  wire     [31:0]   sysctrl_hrdata;
  wire              sysctrl_hresp;

  // MTB (Only available to the Cortex-M0+)
  wire              HSELMTB;
  wire              HREADYOUTMTB;
  wire     [31:0]   HRDATAMTB;
  wire              HRESPMTB;
  wire              HSELSFR;
  wire              HSELRAM;
`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_MTB
  wire              TSTART_SYNC;
  wire              TSTOP_SYNC;
`endif
`endif

  // System ROM Table
  wire              sysrom_hsel;      // AHB to System ROM Table - select
  wire              sysrom_hreadyout; // AHB from System ROM Table - ready
  wire     [31:0]   sysrom_hrdata;    // AHB from System ROM Table - read data
  wire              sysrom_hresp;     // AHB from System ROM Table - response

`ifdef CORTEX_M0PLUS
  // Debug
  wire              DBGEN;
  wire              NIDEN;
  wire              SLVSTALL;

  wire              CPUWAIT;

  // Processor status
  wire      [3:0]   CODEHINT;
`endif

  wire [1:0]        sys_hmaster_i;

  // APB expansion port signals
  wire     [11:0]   exp_paddr;
  wire     [31:0]   exp_pwdata;
  wire              exp_pwrite;
  wire              exp_penable;

  wire     [33:0]   WICSENSE;

  wire              remap_ctrl;

  // Interrupt request
  wire     [31:0]   intisr_cm0;
  wire              intnmi_cm0;
  wire     [15:0]   gpio0_intr;
  wire              gpio0_combintr;
  wire              gpio1_combintr;
  wire     [31:0]   apbsubsys_interrupt;
  wire              dma_done;
  wire              dma_err;
  wire              watchdog_interrupt;

     // I/O Port
  wire              IOMATCH;
  wire     [31:0]   IORDATA;
  wire              IOTRANS;
  wire              IOWRITE;
  wire     [31:0]   IOCHECK;
  wire     [31:0]   IOADDR;
  wire     [ 1:0]   IOSIZE;
  wire              IOMASTER;
  wire              IOPRIV;
  wire     [31:0]   IOWDATA;
`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_IOP
  wire     [31:0]   IORDATA0;
  wire     [31:0]   IORDATA1;
  wire              IOSEL0;
  wire              IOSEL1;
`endif
`endif

  // event signals
  wire              TXEV;
  wire              RXEV;

  // SysTick timer signals
  wire              STCLKEN;
  wire     [25:0]   STCALIB;

  // Processor debug signals
  wire              DBGRESTART;
  wire              DBGRESTARTED;
  wire              EDBGRQ;

  // Processor status
  wire              HALTED;
`ifdef CORTEX_M0
  wire      [2:0]   CODEHINTDE;
`endif
  wire              SPECHTRANS;
  wire              CODENSEQ;
  wire              SHAREABLE;


  // -------------------------------
  // Processor and power management
  // -------------------------------
  // If DMA is presented, use SCLK for system HCLK so that
  // DMA can run even if processor is in sleep mode.
  // Otherwise there is only one master (cpu), so AHB system
  // clock can be stopped when DMA take place.

  assign   HCLKSYS  = (INCLUDE_DMA!=0) ? SCLK : HCLK;


`ifdef CORTEX_M0DESIGNSTART
  // DESIGN START version, without PMU support

//instantiate the DesignStart Cortex M0
CORTEXM0DS
u_cortexm0_ds
(
  // CLOCK AND RESETS ------------------
  .HCLK          (HCLK),              // Clock
  .HRESETn       (HRESETn),           // Asynchronous reset

  // AHB-LITE MASTER PORT --------------
  .HADDR         (cm0_haddr),
  .HTRANS        (cm0_htrans),
  .HSIZE         (cm0_hsize),
  .HBURST        (cm0_hburst),
  .HPROT         (cm0_hprot),
  .HMASTLOCK     (cm0_hmastlock),
  .HWRITE        (cm0_hwrite),
  .HWDATA        (cm0_hwdata),
  .HRDATA        (cm0_hrdata),
  .HREADY        (cm0_hready),
  .HRESP         (cm0_hresp),


  // MISCELLANEOUS ---------------------

  .NMI            (intnmi_cm0),        // Non-maskable interrupt input
  .IRQ            (intisr_cm0[15:0]),  // Interrupt request inputs
  .TXEV           (TXEV),              // Event output (SEV executed)
  .RXEV           (RXEV),              // Event input
  .LOCKUP         (LOCKUP),            // Core is locked-up
  .SYSRESETREQ    (SYSRESETREQ),       // System reset request

  // POWER MANAGEMENT ------------------
  .SLEEPING      (SLEEPING)           // Core and NVIC sleeping
);

// Force connect some signals to 0 or 1
   assign        SLEEPDEEP    = 1'b0;
   assign        cm0_hmaster  = 1'b0;


  // Unused debug feature
  assign   DBGRESTART = 1'b0; // multi-core synchronous restart from halt
  assign   EDBGRQ     = 1'b0; // multi-core synchronous halt request

  assign   RXEV = dma_done;   // Generate event when a DMA operation completed.

  // No MTB in Cortex-M0
  assign   HRDATAMTB    = {32{1'b0}};
  assign   HREADYOUTMTB = 1'b0;
  assign   HRESPMTB     = 1'b0;

`else

`ifdef CORTEX_M0 // Cortex-M0 full version
  // Cortex-M0 integration level
  CORTEXM0INTEGRATION
            #(.ACG       (CLKGATE_PRESENT), // Architectural clock gating
              .BE        (BE),              // Big-endian
              .BKPT      (BKPT),            // Number of breakpoint comparators
              .DBG       (DBG),             // Debug configuration
              .JTAGnSW   (INCLUDE_JTAG),    // Debug port interface: JTAGnSW
              .NUMIRQ    (NUMIRQ),          // Number of Interrupts
              .RAR       (0),               // Reset All Registers
              .SMUL      (SMUL),            // Multiplier configuration
              .SYST      (SYST),            // SysTick
              .WIC       (WIC),             // Wake-up interrupt controller support
              .WICLINES  (WICLINES),        // Supported WIC lines
              .WPT       (WPT))             // Number of DWT comparators

  u_cortex_m0_integration (
  // System inputs
  .FCLK          (FCLK),  // FCLK
  .SCLK          (SCLK),  // SCLK generated from PMU
  .HCLK          (HCLK),  // HCLK generated from PMU
  .DCLK          (DCLK),  // DCLK generated from PMU
  .PORESETn      (PORESETn),
  .HRESETn       (HRESETn),
  .DBGRESETn     (DBGRESETn),
  .RSTBYPASS     (RSTBYPASS),
  .SE            (DFTSE),

  // Power management inputs
  .SLEEPHOLDREQn (SLEEPHOLDREQn),
  .WICENREQ      (WICENREQ),
  .CDBGPWRUPACK  (CDBGPWRUPACK),

  // Power management outputs
  .SLEEPHOLDACKn (SLEEPHOLDACKn),
  .WICENACK      (WICENACK),
  .CDBGPWRUPREQ  (CDBGPWRUPREQ),

  .WAKEUP        (WAKEUP),
  .WICSENSE      (WICSENSE),
  .GATEHCLK      (GATEHCLK),
  .SYSRESETREQ   (SYSRESETREQ),

  // System bus
  .HADDR         (cm0_haddr),
  .HTRANS        (cm0_htrans),
  .HSIZE         (cm0_hsize),
  .HBURST        (cm0_hburst),
  .HPROT         (cm0_hprot),
  .HMASTER       (cm0_hmaster),
  .HMASTLOCK     (cm0_hmastlock),
  .HWRITE        (cm0_hwrite),
  .HWDATA        (cm0_hwdata),
  .HRDATA        (cm0_hrdata),
  .HREADY        (cm0_hready),
  .HRESP         (cm0_hresp),

  .CODEHINTDE    (CODEHINTDE),
  .SPECHTRANS    (SPECHTRANS),
  .CODENSEQ      (CODENSEQ),

  // Interrupts
  .IRQ           (intisr_cm0[31:0]),
  .NMI           (intnmi_cm0),
  .IRQLATENCY    (8'h00),

  .ECOREVNUM     (28'h0),
  // Systick
  .STCLKEN       (STCLKEN),
  .STCALIB       (STCALIB),

  // Debug - JTAG or Serial wire
     // inputs
  .nTRST         (nTRST),
  .SWDITMS       (SWDITMS),
  .SWCLKTCK      (SWCLKTCK),
  .TDI           (TDI),
     // outputs
  .TDO           (TDO),
  .nTDOEN        (nTDOEN),
  .SWDO          (SWDO),
  .SWDOEN        (SWDOEN),

  .DBGRESTART    (DBGRESTART),
  .DBGRESTARTED  (DBGRESTARTED),

  // Event communication
  .TXEV          (TXEV),
  .RXEV          (RXEV),
  .EDBGRQ        (EDBGRQ),
  // Status output
  .HALTED        (HALTED),
  .LOCKUP        (LOCKUP),
  .SLEEPING      (SLEEPING),
  .SLEEPDEEP     (SLEEPDEEP)
  );

  // Unused debug feature
  assign   DBGRESTART = 1'b0; // multi-core synchronous restart from halt
  assign   EDBGRQ     = 1'b0; // multi-core synchronous halt request

  assign   RXEV = dma_done;  // Generate event when a DMA operation completed.

  // No MTB in Cortex-M0
  assign   HRDATAMTB    = {32{1'b0}};
  assign   HREADYOUTMTB = 1'b0;
  assign   HRESPMTB     = 1'b0;

`else // Cortex-M0+ full version
  // Cortex-M0+ & CoreSight MTB M0+ integration level
  CM0PMTBINTEGRATION
            #(.ACG       (CLKGATE_PRESENT), // Architectural clock gating
              .BE        (BE),              // Big-endian
              .BKPT      (BKPT),            // Number of breakpoint comparators
              .DBG       (DBG),             // Debug configuration
              .HALTEV    (1'b0),            // Debug halt event
              .HWF       (HWF),             // Half-Word Fetching
              .IOP       (IOP),             // IO Port interface
              .IRQDIS    (IRQDIS),          // Interrupt Disable
              .MPU       (MPU),             // MPU with 8 regions or none
              .NUMIRQ    (NUMIRQ),          // Number of Interrupts
              .RAR       (0),               // Reset All Registers
              .SMUL      (SMUL),            // Multiplier configuration
              .SYST      (SYST),            // SysTick
              .USER      (USER),            // User/Privilege modes
              .VTOR      (VTOR),            // Vector Table Offset support
              .WIC       (WIC),             // Wake-up interrupt controller support
              .WICLINES  (WICLINES),        // Supported WIC lines
              .WPT       (WPT),             // Number of DWT comparators
              .BASEADDR  (BASEADDR),        // ROM Table base Address
              .JTAGnSW   (INCLUDE_JTAG),    // Debug port interface: JTAGnSW
              .SWMD      (1'b0),            // For Serial Wire support protocol 2 & multi-drop
              .TARGETID  (32'h00000001),
              .AWIDTH    (AWIDTH),          // Micro Trace Buffer SRAM address width
              .MTB       (MTB))             // Select Instruction Trace

    u_cm0pmtbintegration
  (
   // System inputs
   .FCLK          (FCLK),  // FCLK
   .SCLK          (SCLK),  // SCLK generated from PMU
   .HCLK          (HCLK),  // HCLK generated from PMU
   .DCLK          (DCLK),  // DCLK generated from PMU
   .PORESETn      (PORESETn),
   .HRESETn       (HRESETn),
   .DBGRESETn     (DBGRESETn),
   .DFTSE         (DFTSE),

   // Power management inputs
   .SLEEPHOLDREQn (SLEEPHOLDREQn),
   .WICENREQ      (WICENREQ),
   .CDBGPWRUPACK  (CDBGPWRUPACK),

   // Power management outputs
   .SLEEPHOLDACKn (SLEEPHOLDACKn),
   .WICENACK      (WICENACK),
   .CDBGPWRUPREQ  (CDBGPWRUPREQ),

   .WAKEUP        (WAKEUP),
   .WICSENSE      (WICSENSE),
   .GATEHCLK      (GATEHCLK),
   .SYSRESETREQ   (SYSRESETREQ),

   // System bus
   .HADDR         (cm0_haddr),
   .HTRANS        (cm0_htrans),
   .HSIZE         (cm0_hsize),
   .HBURST        (cm0_hburst),
   .HPROT         (cm0_hprot),
   .HMASTER       (cm0_hmaster),
   .HMASTLOCK     (cm0_hmastlock),
   .HWRITE        (cm0_hwrite),
   .HWDATA        (cm0_hwdata),
   .HRDATA        (cm0_hrdata),
   .HREADY        (cm0_hready),
   .HRESP         (cm0_hresp),

   // IO Port bus
   .IOTRANS       (IOTRANS),
   .IOWRITE       (IOWRITE),
   .IOCHECK       (IOCHECK),
   .IOADDR        (IOADDR),
   .IOSIZE        (IOSIZE),
   .IOMASTER      (IOMASTER),
   .IOPRIV        (IOPRIV),
   .IOWDATA       (IOWDATA),
   .IOMATCH       (IOMATCH),
   .IORDATA       (IORDATA),

   .CODEHINT      (CODEHINT),
   .SPECHTRANS    (SPECHTRANS),
   .CODENSEQ      (CODENSEQ),

   // Interrupts
   .IRQ           (intisr_cm0[31:0]),
   .NMI           (intnmi_cm0),
   .IRQLATENCY    (8'h00),

   .ECOREVNUM     (32'h0),

   // Systick
   .STCLKEN       (STCLKEN),
   .STCALIB       (STCALIB),

   // Debug - JTAG or Serial wire
   // inputs
   .nTRST         (nTRST),
   .SWDITMS       (SWDITMS),
   .SWCLKTCK      (SWCLKTCK),
   .TDI           (TDI),
   // outputs
   .TDO           (TDO),
   .nTDOEN        (nTDOEN),
   .SWDO          (SWDO),
   .SWDOEN        (SWDOEN),

   .DBGRESTART    (DBGRESTART),
   .DBGRESTARTED  (DBGRESTARTED),

   // Event communication
   .TXEV          (TXEV),
   .RXEV          (RXEV),
   .EDBGRQ        (EDBGRQ),

   // Status output
   .HALTED        (HALTED),
   .LOCKUP        (LOCKUP),
   .SLEEPING      (SLEEPING),
   .SLEEPDEEP     (SLEEPDEEP),

    // Outputs
   .SHAREABLE     (SHAREABLE),
   .HRDATAMTB     (HRDATAMTB[31:0]),
   .HREADYOUTMTB  (HREADYOUTMTB),
   .HRESPMTB      (HRESPMTB),
`ifdef ARM_CMSDK_INCLUDE_MTB
   .RAMHCLK       (RAMHCLK),
   .RAMAD         (RAMAD[AWIDTH-3:0]),
   .RAMWD         (RAMWD[31:0]),
   .RAMCS         (RAMCS),
   .RAMWE         (RAMWE[3:0]),
`else
   .RAMHCLK       (),
   .RAMAD         (),
   .RAMWD         (),
   .RAMCS         (),
   .RAMWE         (),
`endif
   .DATAHINT      (),
   .SWDETECT      (),
   .SYSPWRDOWNACK (SYSPWRDOWNACK),
   .DBGPWRDOWNACK (DBGPWRDOWNACK),

   // Inputs
   .HADDRMTB      (sys_haddr[31:0]),
   .HPROTMTB      (sys_hprot[3:0]),
   .HSIZEMTB      (sys_hsize[2:0]),
   .HTRANSMTB     (sys_htrans[1:0]),
   .HWDATAMTB     (sys_hwdata[31:0]),
   .HSELRAM       (HSELRAM),
   .HSELSFR       (HSELSFR),
   .HWRITEMTB     (sys_hwrite),
   .HREADYMTB     (sys_hready),
`ifdef ARM_CMSDK_INCLUDE_MTB
   .TSTART        (TSTART_SYNC),
   .TSTOP         (TSTOP_SYNC),
   .SRAMBASEADDR  (SRAMBASEADDR),
   .RAMRD         (RAMRD),
`else
   .TSTART        (1'b0),
   .TSTOP         (1'b0),
   .SRAMBASEADDR  ({32{1'b0}}),
   .RAMRD         ({32{1'b0}}),
`endif
   .NIDEN         (NIDEN),
   .DBGEN         (DBGEN),
   .INSTANCEID    (4'h0),
   .CPUWAIT       (CPUWAIT),
   .SLVSTALL      (SLVSTALL),
   .DFTRSTDISABLE (DFTRSTDISABLE),
   .SYSRETAINn    (SYSRETAINn),
   .SYSISOLATEn   (SYSISOLATEn),
   .SYSPWRDOWN    (SYSPWRDOWN),
   .DBGISOLATEn   (DBGISOLATEn),
   .DBGPWRDOWN    (DBGPWRDOWN));

  // Unused debug feature
  assign   DBGRESTART  = 1'b0; // multi-core synchronous restart from halt
  assign   EDBGRQ      = 1'b0; // multi-core synchronous halt request
  assign   DBGEN       = 1'b1; // Debug enable
  assign   NIDEN       = 1'b1; // Non-invasive Debug enable
  assign   SLVSTALL    = 1'b0; // Firmware protection
  assign   CPUWAIT     = 1'b0; // Halt CPU

  assign   RXEV = dma_done;  // Generate event when a DMA operation completed.

`endif
`endif

  // -------------------------------
  // AHB system
  // -------------------------------

  generate if (INCLUDE_BITBAND != 0) begin : gen_ahb_bitband

  cmsdk_ahb_bitband #(.MW(1), .BE(BE)) u_ahb_bitband (
  // System
  .HCLK        (HCLKSYS),
  .HRESETn     (HRESETn),

  .HSELS       (1'b1),
  .HADDRS      (cm0_haddr),
  .HTRANSS     (cm0_htrans),
  .HPROTS      (cm0_hprot),
  .HBURSTS     (cm0_hburst),
  .HMASTERS    (cm0_hmaster),
  .HMASTLOCKS  (cm0_hmastlock),
  .HSIZES      (cm0_hsize),
  .HWRITES     (cm0_hwrite),
  .HREADYS     (cm0_hready),
  .HWDATAS     (cm0_hwdata),
  .HREADYOUTS  (cm0_hready),
  .HRDATAS     (cm0_hrdata),
  .HRESPS      (cm0_hresp),


  .HSELM       (),
  .HADDRM      (cm_haddr),
  .HTRANSM     (cm_htrans),
  .HPROTM      (cm_hprot),
  .HBURSTM     (cm_hburst),
  .HMASTERM    (cm_hmaster),
  .HMASTLOCKM  (cm_hmastlock),
  .HSIZEM      (cm_hsize),
  .HWRITEM     (cm_hwrite),
  .HREADYM     (cm_hready),
  .HWDATAM     (cm_hwdata),
  .HREADYOUTM  (cm_hreadyout),
  .HRDATAM     (cm_hrdata),
  .HRESPM      (cm_hresp)
  );

  end else begin  : gen_no_ahb_bitband
  // No bitband wrapper, direct signal connections
  assign   cm_haddr[31:0]  = cm0_haddr[31:0];
  assign   cm_htrans[1:0]  = cm0_htrans[1:0];
  assign   cm_hsize[2:0]   = cm0_hsize[2:0];
  assign   cm_hburst[2:0]  = cm0_hburst[2:0];
  assign   cm_hprot[3:0]   = cm0_hprot[3:0];
  assign   cm_hmaster      = cm0_hmaster;
  assign   cm_hmastlock    = cm0_hmastlock;
  assign   cm_hwrite       = cm0_hwrite;
  assign   cm_hwdata[31:0] = cm0_hwdata[31:0];
  assign   cm_hready       = cm0_hready;
  assign   cm0_hrdata[31:0]= cm_hrdata[31:0];
  assign   cm0_hready      = cm_hreadyout;
  assign   cm0_hresp       = cm_hresp;

  end endgenerate

  generate if (INCLUDE_DMA != 0) begin  : gen_ahb_master_mux


  cmsdk_ahb_master_mux #(
    .PORT0_ENABLE (1),
    .PORT1_ENABLE (0),
    .PORT2_ENABLE (1),
    .DW           (32)
    )
  u_ahb_master_mux (
    .HCLK         (HCLKSYS),
    .HRESETn      (HRESETn),

    .HSELS0       (1'b1),
    .HADDRS0      (cm_haddr[31:0]),
    .HTRANSS0     (cm_htrans[1:0]),
    .HSIZES0      (cm_hsize[2:0]),
    .HWRITES0     (cm_hwrite),
    .HREADYS0     (cm_hready),
    .HPROTS0      (cm_hprot[3:0]),
    .HBURSTS0     (cm_hburst[2:0]),
    .HMASTLOCKS0  (cm_hmastlock),
    .HWDATAS0     (cm_hwdata[31:0]),

    .HREADYOUTS0  (cm_hreadyout),
    .HRESPS0      (cm_hresp),
    .HRDATAS0     (cm_hrdata[31:0]),

    .HSELS1       (1'b0),
    .HADDRS1      ({32{1'b0}}),
    .HTRANSS1     ({2{1'b0}}),
    .HSIZES1      ({3{1'b0}}),
    .HWRITES1     (1'b0),
    .HREADYS1     (1'b1),
    .HPROTS1      ({4{1'b0}}),
    .HBURSTS1     ({3{1'b0}}),
    .HMASTLOCKS1  (1'b0),
    .HWDATAS1     ({32{1'b0}}),

    .HREADYOUTS1  (),
    .HRESPS1      (),
    .HRDATAS1     (),

    .HSELS2       (1'b1),
    .HADDRS2      (dmac_haddr[31:0]),
    .HTRANSS2     (dmac_htrans[1:0]),
    .HSIZES2      (dmac_hsize[2:0]),
    .HWRITES2     (dmac_hwrite),
    .HREADYS2     (dmac_hready),
    .HPROTS2      (dmac_hprot[3:0]),
    .HBURSTS2     (dmac_hburst[2:0]),
    .HMASTLOCKS2  (dmac_hmastlock),
    .HWDATAS2     (dmac_hwdata[31:0]),

    .HREADYOUTS2  (dmac_hready),
    .HRESPS2      (dmac_hresp),
    .HRDATAS2     (dmac_hrdata[31:0]),

  // Output master port
    .HSELM        (sys_hselm), // Note: sys_hselm is not required for this particular example system.
                               //       It is connected to the AHB Lite protocol checker only.
    .HADDRM       (sys_haddr[31:0]),
    .HTRANSM      (sys_htrans[1:0]),
    .HSIZEM       (sys_hsize[2:0]),
    .HWRITEM      (sys_hwrite),
    .HREADYM      (sys_hready),
    .HPROTM       (sys_hprot[3:0]),
    .HBURSTM      (sys_hburst[2:0]),
    .HMASTLOCKM   (sys_hmastlock),
    .HWDATAM      (sys_hwdata[31:0]),
    .HMASTERM     (sys_hmaster_i[1:0]),

    .HREADYOUTM   (sys_hreadyout),
    .HRESPM       (sys_hresp),
    .HRDATAM      (sys_hrdata[31:0])
  );

  assign sys_hmaster = (sys_hmaster_i==2'b10); // 2'b00 (core) or 2'b10 (dma)
  // This signal is currently not used, but if the customer need to extend the subsystem, this signal may
  // be needed

  end else begin  : gen_no_ahb_master_mux
  // No DMA controller - no need to have master multiplexer
  // direct connection from cpu to system bus if DMA is not presented
  assign   sys_haddr[31:0] = cm_haddr[31:0];
  assign   sys_htrans[1:0] = cm_htrans[1:0];
  assign   sys_hsize[2:0]  = cm_hsize[2:0];
  assign   sys_hburst[2:0] = cm_hburst[2:0];
  assign   sys_hprot[3:0]  = cm_hprot[3:0];
  assign   sys_hmaster     = cm_hmaster;
  assign   sys_hmastlock   = cm_hmastlock;
  assign   sys_hwrite      = cm_hwrite;
  assign   sys_hwdata[31:0]= cm_hwdata[31:0];
  assign   sys_hready      = cm_hready;
  assign   cm_hrdata[31:0] = sys_hrdata[31:0];
  assign   cm_hreadyout    = sys_hreadyout;
  assign   cm_hresp        = sys_hresp;
  assign   sys_hmaster_i   = 2'b00;

  end endgenerate

  // AHB address decode
  cmsdk_mcu_addr_decode #(
     .BASEADDR_GPIO0       (BASEADDR_GPIO0),
     .BASEADDR_GPIO1       (BASEADDR_GPIO1),
     .BOOT_LOADER_PRESENT  (BOOT_LOADER_PRESENT),
     .BASEADDR_SYSROMTABLE (BASEADDR_SYSROMTABLE)
    )
    u_addr_decode (
    // System Address
    .haddr        (sys_haddr),
    .remap_ctrl   (remap_ctrl),

    .boot_hsel    (boot_hsel),
    .flash_hsel   (flash_hsel),
    .sram_hsel    (sram_hsel),
    .apbsys_hsel  (apbsys_hsel),
    .gpio0_hsel   (gpio0_hsel),
    .gpio1_hsel   (gpio1_hsel),
    .sysctrl_hsel (sysctrl_hsel),
    .sysrom_hsel  (sysrom_hsel),
    .defslv_hsel  (defslv_hsel),
    .hselmtb      (HSELMTB),
    .hselram      (HSELRAM),
    .hselsfr      (HSELSFR)
  );

`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_MTB
  cmsdk_mtb_sync u_mtb_sync (
    // Free running clock
    .FCLK         (FCLK),
    // Global reset
    .HRESETn      (HRESETn),
    // MTB Control
    .TSTART       (TSTART),          // External Trace Start pin
    .TSTOP        (TSTOP),           // External Trace Stop pin

    // MTB Control
    .TSTART_SYNC  (TSTART_SYNC),     // Synchronised Trace Start pin
    .TSTOP_SYNC   (TSTOP_SYNC)       // Synchronised Trace Stop pin
  );
`endif
`endif

  // AHB slave multiplexer
  cmsdk_ahb_slave_mux #(
    .PORT0_ENABLE  (1),
    .PORT1_ENABLE  (1),
    .PORT2_ENABLE  (BOOT_LOADER_PRESENT),
    .PORT3_ENABLE  (1),
    .PORT4_ENABLE  (1),
    .PORT5_ENABLE  (1),
    .PORT6_ENABLE  (1),
    .PORT7_ENABLE  (1),
    .PORT8_ENABLE  (1),
`ifdef CORTEX_M0PLUS
    .PORT9_ENABLE  (MTB),
`else
    .PORT9_ENABLE  (0),
`endif
    .DW            (32)
    )
    u_ahb_slave_mux_sys_bus (
    .HCLK         (HCLKSYS),
    .HRESETn      (HRESETn),
    .HREADY       (sys_hready),
    .HSEL0        (flash_hsel),      // Input Port 0
    .HREADYOUT0   (flash_hreadyout),
    .HRESP0       (flash_hresp),
    .HRDATA0      (flash_hrdata),
    .HSEL1        (sram_hsel),       // Input Port 1
    .HREADYOUT1   (sram_hreadyout),
    .HRESP1       (sram_hresp),
    .HRDATA1      (sram_hrdata),
    .HSEL2        (boot_hsel),       // Input Port 2
    .HREADYOUT2   (boot_hreadyout),
    .HRESP2       (boot_hresp),
    .HRDATA2      (boot_hrdata),
    .HSEL3        (defslv_hsel),     // Input Port 3
    .HREADYOUT3   (defslv_hreadyout),
    .HRESP3       (defslv_hresp),
    .HRDATA3      (defslv_hrdata),
    .HSEL4        (apbsys_hsel),     // Input Port 4
    .HREADYOUT4   (apbsys_hreadyout),
    .HRESP4       (apbsys_hresp),
    .HRDATA4      (apbsys_hrdata),
    .HSEL5        (gpio0_hsel),      // Input Port 5
    .HREADYOUT5   (gpio0_hreadyout),
    .HRESP5       (gpio0_hresp),
    .HRDATA5      (gpio0_hrdata),
    .HSEL6        (gpio1_hsel),      // Input Port 6
    .HREADYOUT6   (gpio1_hreadyout),
    .HRESP6       (gpio1_hresp),
    .HRDATA6      (gpio1_hrdata),
    .HSEL7        (sysctrl_hsel),    // Input Port 7
    .HREADYOUT7   (sysctrl_hreadyout),
    .HRESP7       (sysctrl_hresp),
    .HRDATA7      (sysctrl_hrdata),
    .HSEL8        (sysrom_hsel),     // Input Port 8
    .HREADYOUT8   (sysrom_hreadyout),
    .HRESP8       (sysrom_hresp),
    .HRDATA8      (sysrom_hrdata),
    .HSEL9        (HSELMTB),         // Input Port 9
    .HREADYOUT9   (HREADYOUTMTB),
    .HRESP9       (HRESPMTB),
    .HRDATA9      (HRDATAMTB),

    .HREADYOUT    (sys_hreadyout),   // Outputs
    .HRESP        (sys_hresp),
    .HRDATA       (sys_hrdata)
  );

  // Default slave
  cmsdk_ahb_default_slave u_ahb_default_slave_1 (
    .HCLK         (HCLKSYS),
    .HRESETn      (HRESETn),
    .HSEL         (defslv_hsel),
    .HTRANS       (sys_htrans),
    .HREADY       (sys_hready),
    .HREADYOUT    (defslv_hreadyout),
    .HRESP        (defslv_hresp)
  );

  assign   defslv_hrdata = 32'h00000000; // Default slave do not have read data


  // -------------------------------
  // System ROM Table
  // -------------------------------
  cmsdk_ahb_cs_rom_table
   #(//.JEPID                             (),
     //.JEPCONTINUATION                   (),
     //.PARTNUMBER                        (),
     //.REVISION                          (),
     .BASE              (BASEADDR_SYSROMTABLE),
     // Entry 0 = Cortex-M0+ Processor
     .ENTRY0BASEADDR    (32'hE00FF000),
     .ENTRY0PRESENT     (1'b1),
     // Entry 1 = CoreSight MTB-M0+
     .ENTRY1BASEADDR    (32'hF0200000),
`ifdef CORTEX_M0PLUS
     .ENTRY1PRESENT     (MTB))
`else
     .ENTRY1PRESENT     (0))
`endif
    u_system_rom_table
    (//Outputs
     .HRDATA                            (sysrom_hrdata[31:0]),
     .HREADYOUT                         (sysrom_hreadyout),
     .HRESP                             (sysrom_hresp),
     //Inputs
     .HCLK                              (HCLKSYS),
     .HSEL                              (sysrom_hsel),
     .HADDR                             (sys_haddr[31:0]),
     .HBURST                            (sys_hburst[2:0]),
     .HMASTLOCK                         (sys_hmastlock),
     .HPROT                             (sys_hprot[3:0]),
     .HSIZE                             (sys_hsize[2:0]),
     .HTRANS                            (sys_htrans[1:0]),
     .HWDATA                            (sys_hwdata[31:0]),
     .HWRITE                            (sys_hwrite),
     .HREADY                            (sys_hready),
     .ECOREVNUM                         (4'h0));

  // -------------------------------
  // Peripherals
  // -------------------------------

  cmsdk_mcu_sysctrl #(.BE (BE))
    u_cmsdk_mcu_sysctrl
  (
   // AHB Inputs
    .HCLK         (HCLKSYS),
    .HRESETn      (HRESETn),
    .FCLK         (FCLK),
    .PORESETn     (PORESETn),
    .HSEL         (sysctrl_hsel),
    .HREADY       (sys_hready),
    .HTRANS       (sys_htrans),
    .HSIZE        (sys_hsize),
    .HWRITE       (sys_hwrite),
    .HADDR        (sys_haddr[11:0]),
    .HWDATA       (sys_hwdata),
   // AHB Outputs
    .HREADYOUT    (sysctrl_hreadyout),
    .HRESP        (sysctrl_hresp),
    .HRDATA       (sysctrl_hrdata),
   // Reset information
    .SYSRESETREQ  (SYSRESETREQ),
    .WDOGRESETREQ (WDOGRESETREQ),
    .LOCKUP       (LOCKUP),
    // Engineering-change-order revision bits
    .ECOREVNUM    (4'h0),
   // System control signals
    .REMAP        (remap_ctrl),
    .PMUENABLE    (PMUENABLE),
    .LOCKUPRESET  (LOCKUPRESET)
   );

`ifdef CORTEX_M0PLUS
`ifdef ARM_CMSDK_INCLUDE_IOP
  // GPIO is driven from the IO Port

  cmsdk_iop_interconnect #(
     .BASEADDR_GPIO0    (BASEADDR_GPIO0),
     .BASEADDR_GPIO1    (BASEADDR_GPIO1))
    u_iop_interconnect (
   // IOP Inputs
   .IOADDR        (IOADDR[31:0]),
   .IOCHECK       (IOCHECK),
   .IORDATA0      (IORDATA0),
   .IORDATA1      (IORDATA1),
   // IOP Outputs
   .IOSEL0        (IOSEL0),
   .IOSEL1        (IOSEL1),
   .IOMATCH       (IOMATCH),
   .IORDATA       (IORDATA)
   );

  cmsdk_iop_gpio #(
    .ALTERNATE_FUNC_MASK     (16'h0000), // No pin muxing for Port #0
    .ALTERNATE_FUNC_DEFAULT  (16'h0000), // All pins default to GPIO
    .BE                      (BE)
    )
    u_iop_gpio_0  (
   // IO Port Inputs
    .HCLK         (HCLKSYS),
    .HRESETn      (HRESETn),
    .FCLK         (FCLK),
    .IOADDR       (IOADDR[11:0]),
    .IOSEL        (IOSEL0),
    .IOTRANS      (IOTRANS),
    .IOSIZE       (IOSIZE),
    .IOWRITE      (IOWRITE),
    .IOWDATA      (IOWDATA),
   // IO Port Outputs
    .IORDATA      (IORDATA0),

    .ECOREVNUM    (4'h0),// Engineering-change-order revision bits

    .PORTIN       (p0_in),   // GPIO Interface inputs
    .PORTOUT      (p0_out),  // GPIO Interface outputs
    .PORTEN       (p0_outen),
    .PORTFUNC     (p0_altfunc), // Alternate function control

    .GPIOINT      (gpio0_intr[15:0]),  // Interrupt outputs
    .COMBINT      (gpio0_combintr)
  );

  assign gpio0_hreadyout = 1'b1;
  assign gpio0_hresp     = 1'b0;
  assign gpio0_hrdata    = {32{(1'b0)}};

  cmsdk_iop_gpio #(
    .ALTERNATE_FUNC_MASK     (16'h002A), // pin muxing for Port #1
    .ALTERNATE_FUNC_DEFAULT  (16'h0000), // All pins default to GPIO
    .BE                      (BE)
    )
    u_iop_gpio_1  (
   // IO Port Outputs
    .HCLK         (HCLKSYS),
    .HRESETn      (HRESETn),
    .FCLK         (FCLK),
    .IOADDR       (IOADDR[11:0]),
    .IOSEL        (IOSEL1),
    .IOTRANS      (IOTRANS),
    .IOSIZE       (IOSIZE),
    .IOWRITE      (IOWRITE),
    .IOWDATA      (IOWDATA),
   // IO Port Outputs
    .IORDATA      (IORDATA1),

    .ECOREVNUM    (4'h0),// Engineering-change-order revision bits

    .PORTIN       (p1_in),   // GPIO Interface inputs
    .PORTOUT      (p1_out),  // GPIO Interface outputs
    .PORTEN       (p1_outen),
    .PORTFUNC     (p1_altfunc), // Alternate function control

    .GPIOINT      (),  // Interrupt outputs
    .COMBINT      (gpio1_combintr)
  );

  assign gpio1_hreadyout = 1'b1;
  assign gpio1_hresp     = 1'b0;
  assign gpio1_hrdata    = {32{(1'b0)}};
`endif
`endif

`ifndef ARM_CMSDK_INCLUDE_IOP


  assign IOMATCH = 1'b0;
  assign IORDATA = {32{(1'b0)}};

  assign gpio0_intr[15:0]= {16{(1'b0)}};
  assign gpio0_combintr = 1'b0;
  assign gpio1_combintr = 1'b0;

  assign gpio0_hreadyout = 1'b1;
  assign gpio0_hresp     = 1'b0;
  assign gpio0_hrdata    = {32{(1'b0)}};

  assign gpio1_hreadyout = 1'b1;
  assign gpio1_hresp     = 1'b0;
  assign gpio1_hrdata    = {32{(1'b0)}};

`endif


assign watchdog_interrupt = 1'b0;
assign WDOGRESETREQ = 1'b0;

  // APB subsystem for timers, UARTs
  cmsdk_fasoc_apb_subsystem #(.BE(BE)) u_apb_subsystem (
    // AHB interface for AHB to APB bridge
    .HCLK               (HCLKSYS            ),
    .HRESETn            (HRESETn            ),

    .HSEL               (apbsys_hsel        ),
    .HADDR              (sys_haddr[15:0]    ),
    .HTRANS             (sys_htrans[1:0]    ),
    .HWRITE             (sys_hwrite         ),
    .HSIZE              (sys_hsize          ),
    .HPROT              (sys_hprot          ),
    .HREADY             (sys_hready         ),
    .HWDATA             (sys_hwdata[31:0]   ),

    .HREADYOUT          (apbsys_hreadyout   ),
    .HRDATA             (apbsys_hrdata      ),
    .HRESP              (apbsys_hresp       ),

    // APB clock and reset
    .PCLK               (PCLK               ),
    .PCLKG              (PCLKG              ),
    .PCLKEN             (PCLKEN             ),
    .PRESETn            (PRESETn            ),


    .APBACTIVE          (APBACTIVE          ), // Status Output for clock gating

    // Peripherals

    .GPIO_O             (GPIO_O             ),

    // UART
    .uart_rxd           (uart_rxd           ),
    .uart_txd           (uart_txd           ),
    .uart_txen          (uart_txen          ),

    .LDO_SPI_RESETn     (LDO_SPI_RESETn     ),
    .LDO_SPI_SS         (LDO_SPI_SS         ),
    .LDO_SPI_SCLK       (LDO_SPI_SCLK       ),
    .LDO_SPI_MOSI       (LDO_SPI_MOSI       ),
    .LDO_SPI_MISO       (LDO_SPI_MISO       ),
    .LDO_SPI_APB_SEL    (LDO_SPI_APB_SEL    ),
    .LDO_VREF           (LDO_VREF           ),
    // .LDO_0_VREG         (LDO_0_VREG         ),
    // .LDO_1_VREG         (LDO_1_VREG         ),
    // .LDO_2_VREG         (LDO_2_VREG         ),
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

    // Interrupt outputs
    .apbsubsys_interrupt(apbsubsys_interrupt)
  );


  // Connect system bus to external
  assign   HADDR  = sys_haddr;
  assign   HTRANS = sys_htrans;
  assign   HSIZE  = sys_hsize;
  assign   HWRITE = sys_hwrite;
  assign   HWDATA = sys_hwdata;
  assign   HREADY = sys_hready;

  // -------------------------------
  // DMA Controller
  // -------------------------------

  // DMA interface not used in this example system
  wire  [DMA_CHANNEL_NUM-1:0] dma230_tie0;  // tie off signal.

  assign dma230_tie0 = {DMA_CHANNEL_NUM{1'b0}};

  // DMA done per channel
  wire  [DMA_CHANNEL_NUM-1:0] dma230_done_ch;

  generate if (INCLUDE_DMA != 0) begin : gen_pl230_udma
  // DMA controller present
  pl230_udma u_pl230_udma (
  // Clock and Reset
    .hclk          (HCLKSYS),
    .hresetn       (HRESETn),
  // DMA Control
    .dma_req       (dma230_tie0),
    .dma_sreq      (dma230_tie0),
    .dma_waitonreq (dma230_tie0),
    .dma_stall     (1'b0),
    .dma_active    (),
    .dma_done      (dma230_done_ch),
    .dma_err       (dma_err),
  // AHB-Lite Master Interface
    .hready        (dmac_hready),
    .hresp         (dmac_hresp),
    .hrdata        (dmac_hrdata),
    .htrans        (dmac_htrans),
    .hwrite        (dmac_hwrite),
    .haddr         (dmac_haddr),
    .hsize         (dmac_hsize),
    .hburst        (dmac_hburst),
    .hmastlock     (dmac_hmastlock),
    .hprot         (dmac_hprot),
    .hwdata        (dmac_hwdata),
  // APB Slave Interface
    .pclken        (PCLKEN),
    .psel          (dmac_psel),
    .pen           (exp_penable),
    .pwrite        (exp_pwrite),
    .paddr         (exp_paddr[11:0]),
    .pwdata        (exp_pwdata[31:0]),
    .prdata        (dmac_prdata)
  );

    assign dmac_pready  = 1'b1;
    assign dmac_pslverr = 1'b0;
    assign dma_done     = |dma230_done_ch; // OR all the DMA done together

  end else begin : gen_no_pl230_udma
    // DMA controller not present
    assign dmac_htrans = 2'b00;
    assign dmac_hwrite = 1'b0;
    assign dmac_haddr  = 32'h00000000;
    assign dmac_hsize  = 3'b000;
    assign dmac_hburst = 3'b000;
    assign dmac_hmastlock = 1'b0;
    assign dmac_hprot  = 4'b0000;
    assign dmac_hwdata = 32'h00000000;

    assign dma_done = 1'b0;
    assign dma_err  = 1'b0;
    assign dmac_pready  = 1'b1;
    assign dmac_pslverr = 1'b0;
    assign dmac_prdata  = 32'h00000000;
    assign dma230_done_ch = {DMA_CHANNEL_NUM{1'b0}};

  end endgenerate

  // -------------------------------
  // Interrupt assignment
  // -------------------------------

  // assign intnmi_cm0        = watchdog_interrupt;
  // assign intisr_cm0[ 5: 0] = apbsubsys_interrupt[ 5: 0];
  // assign intisr_cm0[ 6]    = apbsubsys_interrupt[ 6]   | gpio0_combintr;
  // assign intisr_cm0[ 7]    = apbsubsys_interrupt[ 7]   | gpio1_combintr;
  // assign intisr_cm0[14: 8] = apbsubsys_interrupt[14: 8];
  // assign intisr_cm0[15]    = apbsubsys_interrupt[15]   | dma_done | dma_err;
  // assign intisr_cm0[31:16] = apbsubsys_interrupt[31:16]| gpio0_intr;

  assign intnmi_cm0        = 1'b0;
  assign intisr_cm0[ 5: 0] = apbsubsys_interrupt[ 5: 0];
  assign intisr_cm0[ 6]    = apbsubsys_interrupt[ 6];
  assign intisr_cm0[ 7]    = apbsubsys_interrupt[ 7];
  assign intisr_cm0[14: 8] = apbsubsys_interrupt[14: 8];
  assign intisr_cm0[15]    = apbsubsys_interrupt[15]   | dma_done | dma_err;
  assign intisr_cm0[31:16] = apbsubsys_interrupt[31:16];

  // -------------------------------
  // SysTick signals
  // -------------------------------
  cmsdk_mcu_stclkctrl
   #(.DIV_RATIO (18'd01000))
   u_cmsdk_mcu_stclkctrl (
    .FCLK      (FCLK),
    .SYSRESETn (HRESETn),

    .STCLKEN   (STCLKEN),
    .STCALIB   (STCALIB)
    );

 // --------------------------------------------------------------------------------
 // Verification components
 // --------------------------------------------------------------------------------
`ifdef ARM_AHB_ASSERT_ON
  // AHB protocol checker for process bus
  AhbLitePC #(
      .ADDR_WIDTH                           (32),
      .DATA_WIDTH                           (32),
      .BIG_ENDIAN                           (BE),
      .MASTER_TO_INTERCONNECT               ( 1),
      .EARLY_BURST_TERMINATION              ( 0),
      // Property type (0=prove, 1=assume, 2=ignore)
      .MASTER_REQUIREMENT_PROPTYPE          ( 0),
      .MASTER_RECOMMENDATION_PROPTYPE       ( 0),
      .MASTER_XCHECK_PROPTYPE               ( 0),
      .SLAVE_REQUIREMENT_PROPTYPE           ( 0),
      .SLAVE_RECOMMENDATION_PROPTYPE        ( 0),
      .SLAVE_XCHECK_PROPTYPE                ( 0),
      .INTERCONNECT_REQUIREMENT_PROPTYPE    ( 0),
      .INTERCONNECT_RECOMMENDATION_PROPTYPE ( 0),
      .INTERCONNECT_XCHECK_PROPTYPE         ( 0)
   ) u_AhbLitePC_processor
  (
   // clock
   .HCLK         (HCLKSYS),

   // active low reset
   .HRESETn      (HRESETn),

   // Main Master signals
   .HADDR        (cm0_haddr),
   .HTRANS       (cm0_htrans),
   .HWRITE       (cm0_hwrite),
   .HSIZE        (cm0_hsize),
   .HBURST       (cm0_hburst),
   .HPROT        (cm0_hprot),
   .HWDATA       (cm0_hwdata),

   // Main Decoder signals
   .HSELx        (1'bx), // Ignored for this instance

   // Main Slave signals
   .HRDATA       (cm0_hrdata),
   .HREADY       (cm0_hready),
   .HREADYOUT    (1'bx),  // Ignored for this instance
   .HRESP        (cm0_hresp),

   // HMASTER, // NOTE: not used

   .HMASTLOCK    (cm0_hmastlock)
   );

  generate if (INCLUDE_DMA != 0) begin : gen_ahblite_with_dma
  // AHB protocol checker for DMA bus
  AhbLitePC #(
      .ADDR_WIDTH                           (32),
      .DATA_WIDTH                           (32),
      .BIG_ENDIAN                           (BE),
      .MASTER_TO_INTERCONNECT               ( 1),
      .EARLY_BURST_TERMINATION              ( 0),
      // Property type (0=prove, 1=assume, 2=ignore)
      .MASTER_REQUIREMENT_PROPTYPE          ( 0),
      .MASTER_RECOMMENDATION_PROPTYPE       ( 0),
      .MASTER_XCHECK_PROPTYPE               ( 0),
      .SLAVE_REQUIREMENT_PROPTYPE           ( 0),
      .SLAVE_RECOMMENDATION_PROPTYPE        ( 0),
      .SLAVE_XCHECK_PROPTYPE                ( 0),
      .INTERCONNECT_REQUIREMENT_PROPTYPE    ( 0),
      .INTERCONNECT_RECOMMENDATION_PROPTYPE ( 0),
      .INTERCONNECT_XCHECK_PROPTYPE         ( 0)
   ) u_AhbLitePC_dma
  (
   // clock
   .HCLK         (HCLKSYS),

   // active low reset
   .HRESETn      (HRESETn),

   // Main Master signals
   .HADDR        (dmac_haddr),
   .HTRANS       (dmac_htrans),
   .HWRITE       (dmac_hwrite),
   .HSIZE        (dmac_hsize),
   .HBURST       (dmac_hburst),
   .HPROT        (dmac_hprot),
   .HWDATA       (dmac_hwdata),

   // Main Decoder signals
   .HSELx        (1'bx), // Ignored for this instance

   // Main Slave signals
   .HRDATA       (dmac_hrdata),
   .HREADY       (dmac_hready),
   .HREADYOUT    (1'bx), // Ignored for this instance
   .HRESP        (dmac_hresp),

   .HMASTLOCK    (dmac_hmastlock)
   );

  // AHB protocol checker for the out bus from bus multiplexer
   // AHB-Lite slave interface
   AhbLitePC #(
      .ADDR_WIDTH                           (32),
      .DATA_WIDTH                           (32),
      .BIG_ENDIAN                           (BE),
      .MASTER_TO_INTERCONNECT               ( 1),
      .EARLY_BURST_TERMINATION              ( 0),
      // Property type (0=prove, 1=assume, 2=ignore)
      .MASTER_REQUIREMENT_PROPTYPE          ( 0),
      .MASTER_RECOMMENDATION_PROPTYPE       ( 0),
      .MASTER_XCHECK_PROPTYPE               ( 0),
      .SLAVE_REQUIREMENT_PROPTYPE           ( 0),
      .SLAVE_RECOMMENDATION_PROPTYPE        ( 0),
      .SLAVE_XCHECK_PROPTYPE                ( 0),
      .INTERCONNECT_REQUIREMENT_PROPTYPE    ( 0),
      .INTERCONNECT_RECOMMENDATION_PROPTYPE ( 0),
      .INTERCONNECT_XCHECK_PROPTYPE         ( 0)
   ) u_AhbLitePC_sys
  (
   // clock
   .HCLK         (HCLKSYS),

   // active low reset
   .HRESETn      (HRESETn),

   // Main Master signals
   .HADDR        (sys_haddr),
   .HTRANS       (sys_htrans),
   .HWRITE       (sys_hwrite),
   .HSIZE        (sys_hsize),
   .HBURST       (sys_hburst),
   .HPROT        (sys_hprot),
   .HWDATA       (sys_hwdata),

   // Main Decoder signals
   .HSELx        (1'bx), // Ignored for this instance

   // Main Slave signals
   .HRDATA       (sys_hrdata),
   .HREADY       (sys_hready),
   .HREADYOUT    (1'bx), // Ignored for this instance
   .HRESP        (sys_hresp),

   .HMASTLOCK    (dmac_hmastlock)
   );

  end endgenerate

`ifdef CORTEX_M0PLUS
  generate if (MTB != 0) begin : gen_ahbpc_with_mtb
  // AHB protocol checker for MTB bus
  AhbLitePC #(
      .ADDR_WIDTH                           (32),
      .DATA_WIDTH                           (32),
      .BIG_ENDIAN                           (BE),
      .MASTER_TO_INTERCONNECT               ( 0),
      .EARLY_BURST_TERMINATION              ( 0),
      // Property type (0=prove, 1=assume, 2=ignore)
      .MASTER_REQUIREMENT_PROPTYPE          ( 0),
      .MASTER_RECOMMENDATION_PROPTYPE       ( 0),
      .MASTER_XCHECK_PROPTYPE               ( 0),
      .SLAVE_REQUIREMENT_PROPTYPE           ( 0),
      .SLAVE_RECOMMENDATION_PROPTYPE        ( 0),
      .SLAVE_XCHECK_PROPTYPE                ( 0),
      .INTERCONNECT_REQUIREMENT_PROPTYPE    ( 0),
      .INTERCONNECT_RECOMMENDATION_PROPTYPE ( 0),
      .INTERCONNECT_XCHECK_PROPTYPE         ( 0)
   ) u_AhbLitePC_mtb
  (
   // clock
   .HCLK         (FCLK),

   // active low reset
   .HRESETn      (HRESETn),

   // Main Master signals
   .HADDR        (sys_haddr),
   .HTRANS       (sys_htrans),
   .HWRITE       (sys_hwrite),
   .HSIZE        (sys_hsize),
   .HBURST       (sys_hburst),
   .HPROT        (sys_hprot),
   .HWDATA       (sys_hwdata),

   // Main Decoder signals
   .HSELx        (HSELMTB),

   // Main Slave signals
   .HRDATA       (HRDATAMTB),
   .HREADY       (sys_hready),
   .HREADYOUT    (HREADYOUTMTB), // HREADY signal from Slave
   .HRESP        (HRESPMTB),

   .HMASTLOCK    (sys_hmastlock)
   );

  end endgenerate
`endif
`endif

`ifdef ARM_CMSDK_INCLUDE_IOP
`ifdef ARM_IOP_ASSERT_ON
  // IO Port protocol checker for GPIO

  cm0p_ioppc
   #(.DRIVEMASTER        (1'b0),
     .DRIVESLAVE         (1'b0))
     u_cm0p_ioppc
  (
   // Inputs
   .IOCLK                               (HCLKSYS),
   .IORESETn                            (HRESETn),
   .IOCHECK                             (IOCHECK),
   .IOMATCH                             (IOMATCH),
   .IOTRANS                             (IOTRANS),
   .IOADDR                              (IOADDR),
   .IOSIZE                              (IOSIZE),
   .IOWRITE                             (IOWRITE),
   .IOPRIV                              (IOPRIV),
   .IOMASTER                            (IOMASTER),
   .IORDATA                             (IORDATA),
   .IOWDATA                             (IOWDATA));
`endif
`endif



endmodule
