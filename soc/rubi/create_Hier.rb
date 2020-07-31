load File.dirname(__FILE__) + "/Define_SoCParameters.rb"

require 'IPXACT2009API'

component = createComponent(:name => "1ldo_1pll_1mem_1m0")

if INCLUDE_LDOGEN == 1
  createComponentInstance(component, :instance_name => "i_ldo1", :name => "ldo1")
end

if INCLUDE_MEMGEN == 1
  createComponentInstance(component, :instance_name => "i_mem2", :name => "memory2")
end

if INCLUDE_PLLGEN == 1
  createComponentInstance(component, :instance_name => "i_pll1", :name => "pll1")
end

createComponentInstance(component, :instance_name => "u_apb_slave_mux2", :name => "cmsdk_apb_slave_mux2", :parameter_binding => {"PORT0_ENABLE" => "0", "PORT1_ENABLE" => "1", "PORT2_ENABLE" => "0", "PORT3_ENABLE" => "0", "PORT4_ENABLE" => "0", "PORT5_ENABLE" => "1", "PORT6_ENABLE" => "1", "PORT7_ENABLE" => "0", "PORT8_ENABLE" => "0", "PORT9_ENABLE" => "0", "PORT10_ENABLE" => "0", "PORT11_ENABLE" => "0", "PORT12_ENABLE" => "0", "PORT13_ENABLE" => "0", "PORT14_ENABLE" => "0", "PORT15_ENABLE" => "0"})

createComponentInstance(component, :instance_name => "i_m0mcu2", :name => "m0mcu2")

createComponentInstance(component, :instance_name => "i_ldo_mux2", :name => "ldo_mux2")

createComponentInstance(component, :instance_name => "i_gpio2", :name => "gpio2")


saveDesignElement(component, :force_overwrite => true)
