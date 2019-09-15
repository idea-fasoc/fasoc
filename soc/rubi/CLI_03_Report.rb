load File.dirname(__FILE__) + "/Status_utilities.rb"
load File.dirname(__FILE__) + "/VE_utilities.rb"
require 'IPXACT2009API'

design_name =  getConfigItem("arg1", :default => ("arg1"))
component = findComponent(:name => design_name)
design = findDesign(:component => component, :stop_when_nil => true)

#connStatus(component, :mode => :port, :filter => ".*", :sort_by => :instance)
outfile = getConfigItem("arg2", :default => ("arg2"))

insts = design.element("ComponentInstances").elements("ComponentInstance")
f = File.open(outfile, "w")
# Generate connectivity status report
f.printf("#{connStatus(component, :mode => :port, :filter => ".*", :sort_by => :instance)}")
# Generate Vendor Extensions report
f.printf("Vendor Extensions Report\n\n")
insts.each do |inst|
  comp = findComponent(:name => "#{inst.element("ComponentRef").get("Name")}")
  if !(comp.element("VendorExtensions").nil?)
    f.printf("#{getIDEA_VE(comp, :VE => "all")}")
  end
end
f.close
