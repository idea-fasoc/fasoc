require 'IPXACT2009API'

design_name = getConfigItem("arg1", :default => ("arg1"))
component = findComponent(:name => design_name)
LOGICAL_DIR = getConfigItem("arg2", :default => ("arg2"))
system 'mkdir #{LOGICAL_DIR}'
system 'mkdir #{LOGICAL_DIR}/verilog'
OUTPUT_DIR = "#{LOGICAL_DIR}/verilog"

generateVerilog(component, :od => OUTPUT_DIR)
