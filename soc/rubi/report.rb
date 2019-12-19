# MIT License

# Copyright (c) 2018 The University of Michigan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

require 'IPXACT2009API'
rubiDir = getConfigItem("arg1", :default => ("arg1"))
load("#{rubiDir}/Status_utilities.rb")
load("#{rubiDir}/VE_utilities.rb")

design_name =  getConfigItem("arg2", :default => ("arg2"))
component = findComponent(:name => design_name)
design = findDesign(:component => component, :stop_when_nil => true)

#connStatus(component, :mode => :port, :filter => ".*", :sort_by => :instance)
outfile = getConfigItem("arg3", :default => ("arg3"))

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
