load File.dirname(__FILE__) + "/Define_SoCParameters.rb"

require 'IPXACT2009API'

component = findComponent(:name => "design_test_2")

loadBusDefinitions(:name => "APB4")

loadBusDefinitions(:name => "AHBLite")

connect(component, :instance1 => "i_fasoc_m0mcu2", :interface1 => "M0MCU_AHBM",
                   :instance2 => "u_ahb_to_apb2", :interface2 => "AHB_S",
                   :exclude_logical_ports1 => "HSELx,HREADYOUT,HCLK,HRESETn",
                   :check_direct_connection => false)
connect(component, :instance1 => "u_ahb_to_apb2", :interface1 => "APB_M",
                   :instance2 => "u_apb_slave_mux2", :interface2 => "APBS",
                   :exclude_logical_ports1 => "PCLK|PRESETn")
export(component, :instance => "i_fasoc_m0mcu2", :port => "XTAL1",
:exported_port_name => "XTAL1")
export(component, :instance => "i_fasoc_m0mcu2", :port => "XTAL2",
:exported_port_name => "XTAL2")
export(component, :instance => "i_fasoc_m0mcu2", :port => "nTRST",
:exported_port_name => "nTRST")
export(component, :instance => "i_fasoc_m0mcu2", :port => "P0",
:exported_port_name => "P0")
export(component, :instance => "i_fasoc_m0mcu2", :port => "P1",
:exported_port_name => "P1")
export(component, :instance => "i_fasoc_m0mcu2", :port => "SWDIOTMS",
:exported_port_name => "SWDIOTMS")
export(component, :instance => "i_fasoc_m0mcu2", :port => "SWCLKTCK",
:exported_port_name => "SWCLKTCK")
export(component, :instance => "i_fasoc_m0mcu2", :port => "ext_HCLK",
:exported_port_name => "SYSCLK")
export(component, :instance => "u_ahb_to_apb2", :port => "HCLK",
:exported_port_name => "SYSCLK")
export(component, :instance => "i_fasoc_m0mcu2", :port => "ext_HRESETN",
:exported_port_name => "SYSRESETN")
export(component, :instance => "i_ldo2", :port => "PCLK",
:exported_port_name => "SYSCLK")
export(component, :instance => "i_fasoc_m0mcu2", :port => "PCLK",
:exported_port_name => "SYSCLK")
export(component, :instance => "i_ldo2", :port => "reset",
:exported_port_name => "SYSRESETN")
export(component, :instance => "u_ahb_to_apb2", :port => "HRESETn",
:exported_port_name => "SYSRESETN")
export(component, :instance => "i_fasoc_m0mcu2", :port => "ext_HRESETn",
:exported_port_name => "SYSRESETN")
export(component, :instance => "i_fasoc_m0mcu2", :port => "PRESETn",
:exported_port_name => "SYSRESETN")
connect(component, :instance1 => "i_fasoc_m0mcu2", :port1 => "APBACTIVE",
                   :instance2 => "u_ahb_to_apb2", :port2 => "APBACTIVE")
connect(component, :instance1 => "u_ahb_to_apb2", :port1 => "PCLKEN",
                   :instance2 => "i_fasoc_m0mcu2", :port2 => "PCLKEN")
connect(component, :instance1 => "u_ahb_to_apb2", :port1 => "PADDR[15:12]",
                   :instance2 => "u_apb_slave_mux2", :port2 => "DECODE4BIT[15:12]")
tieOff(component, :instance => "u_ahb_to_apb2", :port => "HSEL",
                  :value => "1")
tieOff(component, :instance => "u_ahb_to_apb2", :port => "HREADY",
                  :value => "1")
tieOff(component, :instance => "u_ahb_to_apb2", :port => "HREADYOUT",
                  :value => "open")
tieOff(component, :instance => "u_ahb_to_apb2", :port => "PSTRB",
                  :value => "open")
tieOff(component, :instance => "u_ahb_to_apb2", :port => "PPROT",
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

saveDesignElement(component, :force_overwrite => true)
