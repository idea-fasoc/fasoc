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

#model_parameter_list = component.element("Model").element("ModelParameters").elements("ModelParameter")
component = findComponent(:name => "cmsdk_ahb_to_apb2")
loadBusDefinitions(:name => "APB4")
loadBusDefinitions(:name => "AHBLite")
if component.element("Model").element("ModelParameters") == nil
  createModelParameter(component, :name => "ADDRWIDTH", :value => 32)
  createModelParameter(component, :name => "REGISTER_RDATA", :value => 0)
  createModelParameter(component, :name => "REGISTER_WDATA", :value => 0)
end
createPort(component, :name => "HADDR", :direction => "in", :msb => "ADDRWIDTH-1", :lsb => 0)
createPort(component, :name => "PADDR", :direction => "out", :msb => "ADDRWIDTH-1", :lsb => 0)
saveDesignElement(component, :force_overwrite => true)

component = findComponent(:name => "cmsdk_apb_slave_mux11")
if component.element("Model").element("ModelParameters") == nil
  createModelParameter(component, :name => "PORT0_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT1_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT2_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT3_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT4_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT5_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT6_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT7_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT8_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT9_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT10_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT11_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT12_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT13_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT14_ENABLE", :value => 0)
  createModelParameter(component, :name => "PORT15_ENABLE", :value => 0)
end
saveDesignElement(component, :force_overwrite => true)
