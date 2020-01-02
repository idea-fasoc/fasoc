require 'IPXACT2009API'

design = getConfigItem("arg1", :default => ("arg1"))
if component = findComponent(:name => "#{design}")
  deleteComponent(component)
end
