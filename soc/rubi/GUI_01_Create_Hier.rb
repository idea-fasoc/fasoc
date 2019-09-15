load File.dirname(__FILE__) + "/Define_SoCParameters.rb"
  
require 'IPXACT2009API'

# Create the hierarchical component
component = createComponent(:name => "fasoc_test2")

if INCLUDE_ADCGEN == 1
  createComponentInstance(component, :instance_name => "i_synth_adc_apb", :name => "synth_adc_apb")  
end

if INCLUDE_CDCGEN == 1
  createComponentInstance(component, :instance_name => "i_synth_cdc_apb", :name => "synth_cdc_apb")  
end

#if INCLUDE_DCDCGEN == 1
#  createComponentInstance(component, :instance_name => "u_dcdc-gen_IDEA", :name => "dcdc-gen_IDEA")  
#end

if INCLUDE_LDOGEN == 1
  createComponentInstance(component, :instance_name => "i_ldo", :name => "synth_ldo")  
end

if INCLUDE_MEMGEN == 1
  createComponentInstance(component, :instance_name => "i_mem_apb", :name => "mem_apb")  
end

if INCLUDE_PLLGEN == 1
  createComponentInstance(component, :instance_name => "i_synth_pll_apb", :name => "synth_pll_apb")  
end

if INCLUDE_TEMPGEN == 1
  createComponentInstance(component, :instance_name => "i_synth_temp_apb", :name => "synth_temp_apb")  
end

createComponentInstance(component, :instance_name => "u_apb_slave_mux", :name => "cmsdk_apb_slave_mux", :parameter_binding => {"PORT0_ENABLE" => "1", "PORT1_ENABLE" => "1", "PORT2_ENABLE" => "0", "PORT3_ENABLE" => "0", "PORT4_ENABLE" => "1", "PORT5_ENABLE" => "1", "PORT6_ENABLE" => "1", "PORT7_ENABLE" => "0", "PORT8_ENABLE" => "0", "PORT9_ENABLE" => "0", "PORT10_ENABLE" => "0", "PORT11_ENABLE" => "0", "PORT12_ENABLE" => "0", "PORT13_ENABLE" => "0", "PORT14_ENABLE" => "0", "PORT15_ENABLE" => "0"})
createComponentInstance(component, :instance_name => "i_fasoc_m0mcu", :name => "fasoc_m0mcu")  
createComponentInstance(component, :instance_name => "u_ahb_to_apb", :name => "cmsdk_ahb_to_apb", :parameter_binding => {"ADDRWIDTH" => "16", "REGISTER_RDATA" => "1", "REGISTER_WDATA" => "0"})

# Save the changes
saveDesignElement(component, :force_overwrite => true)