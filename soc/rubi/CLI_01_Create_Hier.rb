load File.dirname(__FILE__) + "/Define_SoCParameters.rb"

require 'IPXACT2009API'

component = createComponent(:name => "design_test_2")

if INCLUDE_LDOGEN == 1
  createComponentInstance(component, :instance_name => "i_ldo2", :name => "ldo2")
end

createComponentInstance(component, :instance_name => "u_apb_slave_mux2", :name => "cmsdk_apb_slave_mux2", :parameter_binding => {"PORT0_ENABLE" => "0", "PORT1_ENABLE" => "1", "PORT2_ENABLE" => "0", "PORT3_ENABLE" => "0", "PORT4_ENABLE" => "0", "PORT5_ENABLE" => "1", "PORT6_ENABLE" => "1", "PORT7_ENABLE" => "0", "PORT8_ENABLE" => "0", "PORT9_ENABLE" => "0", "PORT10_ENABLE" => "0", "PORT11_ENABLE" => "0", "PORT12_ENABLE" => "0", "PORT13_ENABLE" => "0", "PORT14_ENABLE" => "0", "PORT15_ENABLE" => "0"})

createComponentInstance(component, :instance_name => "u_ahb_to_apb2", :name => "cmsdk_ahb_to_apb2", :parameter_binding => {"ADDRWIDTH" => "16", "REGISTER_RDATA" => "1", "REGISTER_WDATA" => "0"})

createComponentInstance(component, :instance_name => "i_fasoc_m0mcu2", :name => "fasoc_m0mcu2")


saveDesignElement(component, :force_overwrite => true)
