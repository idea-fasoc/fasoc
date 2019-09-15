load File.dirname(__FILE__) + "/utilities/Status_utilities.rb"
load File.dirname(__FILE__) + "/utilities/VE_utilities.rb"
require 'IPXACT2009API'

design_name =  "fasoc_test2"
component = findComponent(:name => design_name)
design = findDesign(:component => component, :stop_when_nil => true)

#reportUnconnected(component, :mode => :port, :filter => "u_ahb_to_apb", :sort_by => :instance)
#reportUnconnected(component, :mode => :port, :filter => "i_fasoc_m0mcu", :sort_by => :instance)
#reportUnconnected(component, :mode => :port, :filter => ".*", :sort_by => :instance)

#connStatus(component, :mode => :port, :filter => ".*", :sort_by => :instance)

insts = design.element("ComponentInstances").elements("ComponentInstance")
outfile = File.dirname(__FILE__) + "/../Design_Report.txt"
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
