require 'IPXACT2009API'

design_name = "fasoc_test2"
component = findComponent(:name => design_name)
#WORKSPACE_DIR = "/home/matcol02/armSocrates/workspace"
WORKSPACE_DIR = "/n/trenton/v/fayazi/arm"
PROJECT_NAME = "jul19"
DESIGN_NAME = "fasoc_test2"
LOGICAL_DIR = "#{WORKSPACE_DIR}/#{PROJECT_NAME}/logical"
VERILOG_OUTPUT_DIR = "#{LOGICAL_DIR}/#{DESIGN_NAME}/verilog"
system 'mkdir #{LOGICAL_DIR}/#{DESIGN_NAME}'
system 'mkdir #{OUTPUT_DIR}'

runDRC(component, :checks => "IDEA_Checks")
system "cp #{WORKSPACE_DIR}/CheckResults.log #{WORKSPACE_DIR}/#{PROJECT_NAME}/cc.log"
generateVerilog(component, :od => VERILOG_OUTPUT_DIR)


