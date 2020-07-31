load File.dirname(__FILE__) + "/Define_SoCParameters.rb"

require 'IPXACT2009API'

component = findComponent(:name => "1ldo_1pll_1mem_1m0")

loadBusDefinitions(:name => "APB4")

loadBusDefinitions(:name => "AHBLite")

export(component, :instance => "i_m0mcu2", :port => "XTAL1_PAD",
:exported_port_name => "XTAL1_PAD")
export(component, :instance => "i_m0mcu2", :port => "XTAL2_PAD",
:exported_port_name => "XTAL2_PAD")
export(component, :instance => "i_m0mcu2", :port => "NRST_PAD",
:exported_port_name => "NRST_PAD")
export(component, :instance => "i_m0mcu2", :port => "GPIO_INIT_PAD",
:exported_port_name => "GPIO_INIT_PAD")
export(component, :instance => "i_m0mcu2", :port => "GPIO_USER0_PAD",
:exported_port_name => "GPIO_USER0_PAD")
export(component, :instance => "i_m0mcu2", :port => "GPIO_USER1_PAD",
:exported_port_name => "GPIO_USER1_PAD")
export(component, :instance => "i_m0mcu2", :port => "UART_RXD_PAD",
:exported_port_name => "UART_RXD_PAD")
export(component, :instance => "i_m0mcu2", :port => "UART_TXD_PAD",
:exported_port_name => "UART_TXD_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_SPI_RESETn_PAD",
:exported_port_name => "LDO_SPI_RESETn_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_SPI_SS_PAD[1:0]",
:exported_port_name => "LDO_SPI_SS_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_SPI_SCLK_PAD",
:exported_port_name => "LDO_SPI_SCLK_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_SPI_MOSI_PAD",
:exported_port_name => "LDO_SPI_MOSI_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_SPI_MISO_PAD",
:exported_port_name => "LDO_SPI_MISO_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_SPI_APB_SEL_PAD",
:exported_port_name => "LDO_SPI_APB_SEL_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_VREF_PAD",
:exported_port_name => "LDO_VREF_PAD")
export(component, :instance => "i_m0mcu2", :port => "LDO_REFCLK_PAD",
:exported_port_name => "LDO_REFCLK_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_DATA_REQ_PAD",
:exported_port_name => "MEM_DATA_REQ_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_WE_PAD",
:exported_port_name => "MEM_WE_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_TEST_MODE_PAD",
:exported_port_name => "MEM_TEST_MODE_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_CLK_IN_PAD",
:exported_port_name => "MEM_CLK_IN_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_RESET_PAD",
:exported_port_name => "MEM_RESET_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_SPI_CLOCK_PAD",
:exported_port_name => "MEM_SPI_CLOCK_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_SPI_MOSI_PAD",
:exported_port_name => "MEM_SPI_MOSI_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_SPI_RST_PAD",
:exported_port_name => "MEM_SPI_RST_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_SPI_SCLK_PAD",
:exported_port_name => "MEM_SPI_SCLK_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_SPI_SS_PAD",
:exported_port_name => "MEM_SPI_SS_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_DOUT32_PAD",
:exported_port_name => "MEM_DOUT32_PAD")
export(component, :instance => "i_m0mcu2", :port => "MEM_SPI_MISO_PAD",
:exported_port_name => "MEM_SPI_MISO_PAD")
export(component, :instance => "i_m0mcu2", :port => "PLL_CLKREF0_PAD",
:exported_port_name => "PLL_CLKREF0_PAD")
export(component, :instance => "i_m0mcu2", :port => "PLL_CLKREF1_PAD",
:exported_port_name => "PLL_CLKREF1_PAD")
export(component, :instance => "i_m0mcu2", :port => "PLL_CLKOUT0_PAD",
:exported_port_name => "PLL_CLKOUT0_PAD")
export(component, :instance => "i_m0mcu2", :port => "PLL_CLKOUT1_PAD",
:exported_port_name => "PLL_CLKOUT1_PAD")
export(component, :instance => "i_m0mcu2", :port => "TEMP_0_CLKOUT_PAD",
:exported_port_name => "TEMP_0_CLKOUT_PAD")
export(component, :instance => "i_m0mcu2", :port => "TEMP_1_CLKOUT_PAD",
:exported_port_name => "TEMP_1_CLKOUT_PAD")
export(component, :instance => "i_m0mcu2", :port => "TEMP_0_REFCLK_PAD",
:exported_port_name => "TEMP_0_REFCLK_PAD")
export(component, :instance => "i_m0mcu2", :port => "TEMP_1_REFCLK_PAD",
:exported_port_name => "TEMP_1_REFCLK_PAD")
export(component, :instance => "i_m0mcu2", :port => "VIN_TEMPSENSE_PAD",
:exported_port_name => "VIN_TEMPSENSE_PAD")
export(component, :instance => "i_m0mcu2", :port => "nTRST",
:exported_port_name => "nTRST")
export(component, :instance => "i_m0mcu2", :port => "TDI",
:exported_port_name => "TDI")
export(component, :instance => "i_m0mcu2", :port => "TDO",
:exported_port_name => "TDO")
export(component, :instance => "i_m0mcu2", :port => "SWDIOTMS",
:exported_port_name => "SWDIOTMS")
export(component, :instance => "i_m0mcu2", :port => "SWCLKTCK",
:exported_port_name => "SWCLKTCK")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL0",
                   :instance2 => "i_gpio2", :port2 => "PSEL")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PRDATA0[31:0]",
                   :instance2 => "i_gpio2", :port2 => "PRDATA[31:0]")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PREADY0",
                   :instance2 => "i_gpio2", :port2 => "PREADY")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSLVERR0",
                   :instance2 => "i_gpio2", :port2 => "PSLVERR")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL0",
                   :instance2 => "i_m0mcu2", :port2 => "apb0_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL2",
                   :instance2 => "i_m0mcu2", :port2 => "apb2_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL3",
                   :instance2 => "i_m0mcu2", :port2 => "apb3_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL4",
                   :instance2 => "i_m0mcu2", :port2 => "apb4_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL5",
                   :instance2 => "i_m0mcu2", :port2 => "apb5_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL6",
                   :instance2 => "i_m0mcu2", :port2 => "apb6_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL7",
                   :instance2 => "i_m0mcu2", :port2 => "apb7_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL8",
                   :instance2 => "i_m0mcu2", :port2 => "apb8_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL9",
                   :instance2 => "i_m0mcu2", :port2 => "apb9_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL10",
                   :instance2 => "i_m0mcu2", :port2 => "apb10_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL11",
                   :instance2 => "i_m0mcu2", :port2 => "apb11_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL12",
                   :instance2 => "i_m0mcu2", :port2 => "apb12_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL13",
                   :instance2 => "i_m0mcu2", :port2 => "apb13_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL14",
                   :instance2 => "i_m0mcu2", :port2 => "apb14_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL15",
                   :instance2 => "i_m0mcu2", :port2 => "apb15_psel")
connect(component, :instance1 => "u_apb_slave_mux2", :interface1 => "APBM1",
                   :instance2 => "i_m0mcu2", :interface2 => "M0_APB1",
                   :exclude_logical_ports1 => "PCLK|PRESETn")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_paddr[15:12]",
                   :instance2 => "u_apb_slave_mux2", :port2 => "DECODE4BIT[3:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_psel",
                   :instance2 => "u_apb_slave_mux2", :port2 => "PSEL")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pready_mux",
                   :instance2 => "u_apb_slave_mux2", :port2 => "PREADY")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_prdata_mux[31:0]",
                   :instance2 => "u_apb_slave_mux2", :port2 => "PRDATA[31:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pslverr_mux",
                   :instance2 => "u_apb_slave_mux2", :port2 => "PSLVERR")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_SPI_SS[1:0]",
                   :instance2 => "i_ldo_mux2", :port2 => "LDO_SPI_SS[1:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_SPI_MISO",
                   :instance2 => "i_ldo_mux2", :port2 => "LDO_SPI_MISO")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_paddr[11:0]",
                   :instance2 => "i_gpio2", :port2 => "PADDR[11:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwrite",
                   :instance2 => "i_gpio2", :port2 => "PWRITE")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_penable",
                   :instance2 => "i_gpio2", :port2 => "PENABLE")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwdata[31:0]",
                   :instance2 => "i_gpio2", :port2 => "PWDATA[31:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "GPIO_O[31:0]",
                   :instance2 => "i_gpio2", :port2 => "GPIO_O[31:0]")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL2",
                   :instance2 => "i_ldo1", :port2 => "PSEL")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PRDATA2[31:0]",
                   :instance2 => "i_ldo1", :port2 => "PRDATA[31:0]")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PREADY2",
                   :instance2 => "i_ldo1", :port2 => "PREADY")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSLVERR2",
                   :instance2 => "i_ldo1", :port2 => "PSLVERR")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_paddr[11:0]",
                   :instance2 => "i_ldo1", :port2 => "PADDR[11:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwrite",
                   :instance2 => "i_ldo1", :port2 => "PWRITE")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_penable",
                   :instance2 => "i_ldo1", :port2 => "PENABLE")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwdata[31:0]",
                   :instance2 => "i_ldo1", :port2 => "PWDATA[31:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_SPI_RESETn",
                   :instance2 => "i_ldo1", :port2 => "SRESETn")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_SPI_SCLK",
                   :instance2 => "i_ldo1", :port2 => "SCLK")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_SPI_MOSI",
                   :instance2 => "i_ldo1", :port2 => "MOSI")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_SPI_APB_SEL",
                   :instance2 => "i_ldo1", :port2 => "SPI_APB_SEL")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_VREF",
                   :instance2 => "i_ldo1", :port2 => "VREF")
connect(component, :instance1 => "i_m0mcu2", :port1 => "LDO_REFCLK",
                   :instance2 => "i_ldo1", :port2 => "CLK")
connect(component, :instance1 => "i_ldo_mux2", :port1 => "LDO_SPI_0_MISO",
                   :instance2 => "i_ldo1", :port2 => "MISO")
connect(component, :instance1 => "i_ldo_mux2", :port1 => "LDO_SPI_0_SS",
                   :instance2 => "i_ldo1", :port2 => "SS")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL3",
                   :instance2 => "i_mem2", :port2 => "psel")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PRDATA3[31:0]",
                   :instance2 => "i_mem2", :port2 => "prdata[31:0]")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PREADY3",
                   :instance2 => "i_mem2", :port2 => "pready")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSLVERR3",
                   :instance2 => "i_mem2", :port2 => "pslverr")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_paddr[11:0]",
                   :instance2 => "i_mem2", :port2 => "paddr[11:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwrite",
                   :instance2 => "i_mem2", :port2 => "pwrite")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_penable",
                   :instance2 => "i_mem2", :port2 => "penable")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwdata[31:0]",
                   :instance2 => "i_mem2", :port2 => "pwdata[31:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_DATA_REQ",
                   :instance2 => "i_mem2", :port2 => "DATA_REQ_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_WE",
                   :instance2 => "i_mem2", :port2 => "WE_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_TEST_MODE",
                   :instance2 => "i_mem2", :port2 => "TEST_MODE_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_CLK_IN",
                   :instance2 => "i_mem2", :port2 => "CLK_IN_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_RESET",
                   :instance2 => "i_mem2", :port2 => "RESET_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_SPI_CLOCK",
                   :instance2 => "i_mem2", :port2 => "SPI_CLOCK_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_SPI_MOSI",
                   :instance2 => "i_mem2", :port2 => "SPI_MOSI_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_SPI_RST",
                   :instance2 => "i_mem2", :port2 => "SPI_RST_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_SPI_SCLK",
                   :instance2 => "i_mem2", :port2 => "SPI_SCLK_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_SPI_SS",
                   :instance2 => "i_mem2", :port2 => "SPI_SS_pad")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_DOUT32",
                   :instance2 => "i_mem2", :port2 => "DOUT32_PO")
connect(component, :instance1 => "i_m0mcu2", :port1 => "MEM_SPI_MISO",
                   :instance2 => "i_mem2", :port2 => "SPI_MISO_PO")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSEL4",
                   :instance2 => "i_pll1", :port2 => "PSEL")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PRDATA4[31:0]",
                   :instance2 => "i_pll1", :port2 => "PRDATA[31:0]")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PREADY4",
                   :instance2 => "i_pll1", :port2 => "PREADY")
connect(component, :instance1 => "u_apb_slave_mux2", :port1 => "PSLVERR4",
                   :instance2 => "i_pll1", :port2 => "PSLVERR")
export(component, :instance => "i_pll1", :port => "CLKOUT",
:exported_port_name => "SYSCLKOUT2")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_paddr[11:0]",
                   :instance2 => "i_pll1", :port2 => "PADDR[11:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwrite",
                   :instance2 => "i_pll1", :port2 => "PWRITE")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_penable",
                   :instance2 => "i_pll1", :port2 => "PENABLE")
connect(component, :instance1 => "i_m0mcu2", :port1 => "i_pwdata[31:0]",
                   :instance2 => "i_pll1", :port2 => "PWDATA[31:0]")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PCLK",
                   :instance2 => "i_gpio2", :port2 => "PCLK")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PCLK",
                   :instance2 => "i_ldo1", :port2 => "PCLK")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PCLK",
                   :instance2 => "i_mem2", :port2 => "pclk")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PCLK",
                   :instance2 => "i_pll1", :port2 => "PCLK")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PRESETn",
                   :instance2 => "i_gpio2", :port2 => "PRESETn")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PRESETn",
                   :instance2 => "i_ldo1", :port2 => "PRESETn")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PRESETn",
                   :instance2 => "i_mem2", :port2 => "presetn")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PRESETn",
                   :instance2 => "i_pll1", :port2 => "PRESETn")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PLL_CLKREF0",
                   :instance2 => "i_pll1", :port2 => "CLKREF")
connect(component, :instance1 => "i_m0mcu2", :port1 => "PLL_CLKOUT0",
                   :instance2 => "i_pll1", :port2 => "CLK_OUT")
tieOff(component, :instance => "i_m0mcu2", :port => "ext_HREADY",
                  :value => "1")
tieOff(component, :instance => "i_m0mcu2", :port => "NRST",
                  :value => "1")
tieOff(component, :instance => "i_m0mcu2", :port => "TDI",
                  :value => "1")
tieOff(component, :instance => "i_m0mcu2", :port => "TDO",
                  :value => "open")
tieOff(component, :instance => "i_m0mcu2", :port => "PCLKG",
                  :value => "open")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PSLVERR.*|PRDATA.*",
                  :value => "0")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PSEL.*",
                  :value => "open")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY0",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY1",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY2",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY3",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY4",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY5",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY6",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY7",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY8",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY9",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY10",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY11",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY12",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY13",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY14",
                  :value => "1")
tieOff(component, :instance => "u_apb_slave_mux2", :port => "PREADY15",
                  :value => "1")
tieOff(component, :instance => ".*", :port => ".*", :direction => :in,
                  :value => "0")
tieOff(component, :instance => ".*", :port => ".*", :direction => :out,
                  :value => "open")

saveDesignElement(component, :force_overwrite => true)
