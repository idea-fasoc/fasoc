load File.dirname(__FILE__) + "/Define_SoCParameters.rb"
  
require 'IPXACT2009API'

component = findComponent(:name => "fasoc_test2")

##### generic exports
export(component, :instance => "i_fasoc_m0mcu", :port => "XTAL1",
:exported_port_name => "XTAL1")
export(component, :instance => "i_fasoc_m0mcu", :port => "XTAL2",
:exported_port_name => "XTAL2")
export(component, :instance => "i_fasoc_m0mcu", :port => "NRST",
:exported_port_name => "NRST")
export(component, :instance => "i_fasoc_m0mcu", :port => "P0",
:exported_port_name => "P0")
export(component, :instance => "i_fasoc_m0mcu", :port => "P1",
:exported_port_name => "P1")
export(component, :instance => "i_fasoc_m0mcu", :port => "SWDIOTMS",
:exported_port_name => "SWDIOTMS")
export(component, :instance => "i_fasoc_m0mcu", :port => "SWCLKTCK",
:exported_port_name => "SWCLKTCK")
export(component, :instance => "i_fasoc_m0mcu", :port => "ext_HCLK",
:exported_port_name => "SYSCLK")
export(component, :instance => "i_fasoc_m0mcu", :port => "ext_HRESETN",
:exported_port_name => "SYSRESETN")
export(component, :instance => "i_synth_pll_apb", :port => "CLKOUT",
:exported_port_name => "SYSCLKOUT")

######### clocks and resets
connect(component, :port1 => "SYSCLK",
                   :instance2 => "u_ahb_to_apb", :port2 => "HCLK")
connect(component, :port1 => "SYSRESETN",
                   :instance2 => "u_ahb_to_apb", :port2 => "HRESETN")
connect(component, :port1 => "SYSCLK",
                   :instance2 => ".*", :port2 => "PCLK")
connect(component, :port1 => "SYSRESETN",
                   :instance2 => ".*", :port2 => "PRESETN")
connect(component, :port1 => "SYSRESETN",
                   :instance2 => "i_ldo", :port2 => "reset")
                   
########### connect interfaces
connect(component, :instance1 => "i_fasoc_m0mcu", :interface1 => "M0MCU_AHBM",
                   :instance2 => "u_ahb_to_apb", :interface2 => "AHB_S", :exclude_logical_ports1 => "HSELx,HREADYOUT", 
                   :check_direct_connection => false)
connect(component, :instance1 => "u_ahb_to_apb", :interface1 => "APB_M",
                   :instance2 => "u_apb_slave_mux", :interface2 => "APBS")
connect(component, :instance1 => "u_apb_slave_mux", :interface1 => "APBM0",
                   :instance2 => "i_synth_adc_apb", :interface2 => "ADC_APBS")
connect(component, :instance1 => "u_apb_slave_mux", :interface1 => "APBM1",
                   :instance2 => "i_synth_cdc_apb", :interface2 => "CDC_APBS")
connect(component, :instance1 => "u_apb_slave_mux", :interface1 => "APBM4",
                   :instance2 => "i_mem_apb", :interface2 => "MEM_APBS")
connect(component, :instance1 => "u_apb_slave_mux", :interface1 => "APBM5",
                   :instance2 => "i_synth_pll_apb", :interface2 => "PLL_APBS")
connect(component, :instance1 => "u_apb_slave_mux", :interface1 => "APBM6",
                   :instance2 => "i_synth_temp_apb", :interface2 => "TEMP_APBS")
		   
########### connect ports
connect(component, :instance1 => "u_ahb_to_apb", :port1 => "PADDR[11:0]",
                   :instance2 => "i_mem_apb", :port2 => "PADDR[11:0]")
connect(component, :instance1 => "u_ahb_to_apb", :port1 => "PADDR[11:2]",
                   :instance2 => ".*", :port2 => "PADDR[11:2]")
connect(component, :instance1 => "u_ahb_to_apb", :port1 => "PENABLE",
                   :instance2 => ".*", :port2 => "PENABLE")
connect(component, :instance1 => "u_ahb_to_apb", :port1 => "PWRITE",
                   :instance2 => ".*", :port2 => "PWRITE")
connect(component, :instance1 => "u_ahb_to_apb", :port1 => "PWDATA",
                   :instance2 => ".*", :port2 => "PWDATA")
connect(component, :instance1 => "u_ahb_to_apb", :port1 => "PADDR[15:12]",
                   :instance2 => "u_apb_slave_mux", :port2 => "DECODE4BIT[15:12]")
connect(component, :instance1 => "i_fasoc_m0mcu", :port1 => "APBACTIVE",
                   :instance2 => "u_ahb_to_apb", :port2 => "APBACTIVE")
connect(component, :instance1 => "i_fasoc_m0mcu", :port1 => "PCLKEN",
                   :instance2 => "u_ahb_to_apb", :port2 => "PCLKEN")
                   
########## tieoffs
tieOff(component, :instance => "i_ldo", :port => "Vref",
                  :value => "0")
tieOff(component, :instance => "i_ldo", :port => "Vreg",
                  :value => :open)
tieOff(component, :instance => "u_ahb_to_apb", :port => "HSEL|HREADY",
                  :value => "1")
tieOff(component, :instance => "u_ahb_to_apb", :port => "HREADYOUT",
                  :value => :open)
tieOff(component, :instance => "u_apb_slave_mux", :port => "PREADY.*",
                  :value => "1")
tieOff(component, :instance => "u_ahb_to_apb", :port => "PSTRB|PPROT",
                  :value => :open)
tieOff(component, :instance => "u_apb_slave_mux", :port => "PSLVERR.*|PRDATA.*",
                  :value => :low)
tieOff(component, :instance => "u_apb_slave_mux", :port => "PSEL.*",
                  :value => "open")


# Save the changes
saveDesignElement(component, :force_overwrite => true)
