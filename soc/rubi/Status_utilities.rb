# isConnected returns true if the given bus interface or port is connected otherwise false
def my_isConnected(design_element, options={}) # :nodoc:
  # Checks
  de_received = defined?(design_element) ? design_element : :none
  arguments_received = defined?(options) ? options : nil
  supported_element_types = ["Design"]
  valid_options = [:instance_name, :interface_name, :port_name, :mode]
  design_element, element_type, error_messages = commonChecks(de_received, arguments_received, supported_element_types, valid_options)

  instance_name = options[:instance_name]
  interface_name = options[:interface_name]
  port_name = options[:port_name]
  mode = options[:mode]
  
  if (interface_name.nil? == port_name.nil?)
    error_messages << "Either an interface name or a port name must be specified but not both of them"
  end
  if !(error_messages.empty?)
    raiseError(__method__, design_element, arguments_received, error_messages)
  end
  # Body
  design = design_element
  is_connected = "false"

  #if selectionType(options) == :interface
  if mode == :interface
    # looking for interface on top level
    if instance_name.nil?
      # finds all unconnected ports on top boundary
      unconnected_ports = findUnconnectedPorts(design)
      # finds top component
      comp = findComponent(:design => design)
      # looks into all hierConnections
      foreachHierConnection(design) do |hier_connection|
        # gets InterfaceRef name
        ifref_name = hier_connection.get("InterfaceRef")
        # gets InterfaceRef
        ifref = findBusInterface(comp, :name => "#{ifref_name}")
  # if InterfaceRef is equal to interface_name argument sets is_connected to true
        if ifref_name == interface_name
          is_connected = "true"
    break
  end
      end
      if is_connected == "true"
        ifref = findBusInterface(comp, :name => "#{interface_name}")
  # checks connectivity on all ports belonging to InterfaceRef
  # iterates over all InterfaceRef ports
        foreachPortMap(ifref) do |logical_port, physical_port|
    # iterates over all top boundary unconnected ports
          unconnected_ports[nil].each do |unconnected_port|
            unconnected_port_name = extractName(unconnected_port)
      # if InterfaceRef port is unconnected sets is_connected to partial
            if unconnected_port_name == getName(physical_port)
        is_connected = "partial" #false
              break
      end
    end
    if is_connected == "partial" #false
      break
    end 
        end
      else # is_connected == "false"
        ifref = findBusInterface(comp, :name => interface_name)
  unconnected_count = 0
  physical_ports_count = 0
  # checks connectivity on all ports belonging to InterfaceRef
  # iterates over all InterfaceRef ports
        foreachPortMap(ifref) do |logical_port, physical_port|
    physical_ports_count+=1
    # iterates over all top boundary unconnected ports
          unconnected_ports[nil].each do |unconnected_port|
            unconnected_port_name = extractName(unconnected_port)
      # if InterfaceRef port is unconnected sets is_connected to false
            if unconnected_port_name == getName(physical_port)
        unconnected_count+=1
      end
    end
        end
  if unconnected_count == 0
    is_connected = "true"
  elsif (unconnected_count > 0) and (unconnected_count < physical_ports_count)
    is_connected = "partial"
  else
    is_connected = "false"
  end
      end
    else # looking for interface on instance
      found = 0
      # looks for instance interfaces in interconnections
      foreachInterconnection(design) do |interconnection|
        interconnection.elements("ActiveInterface").each do |active_interface|
          if (active_interface.get("ComponentRef") == instance_name) && (active_interface.get("BusRef") == interface_name)
            is_connected = "true"
      found = 1
      # finds unconnected ports in instance_name
            unconnected_ports = findUnconnectedPorts(design, :instance_name => instance_name, :port_name=>".*")[instance_name]
            instance = findComponentInstance(design, :name => instance_name)
            component = findComponent(:instance => instance)
      ifref = findBusInterface(component, :name => interface_name)#active_interface.get("BusRef"))
      # iterates over all InterfaceRef ports
      foreachPortMap(ifref) do |logical_port, physical_port|
        # iterates over all instance unconnected ports
        unconnected_ports.each do |unconnected_port|
    unconnected_port_name = extractName(unconnected_port)
    # if InterfaceRef port is unconnected sets is_connected to partial
    if unconnected_port_name == getName(physical_port)
      is_connected = "partial" #false
      break
    end
        end
        if is_connected == "partial"
          break
        end
      end
          else # is_connected == "false"
      # finds unconnected ports in instance_name
            unconnected_ports = findUnconnectedPorts(design, :instance_name => instance_name, :port_name=>".*")[instance_name]
            instance = findComponentInstance(design, :name => instance_name)
            component = findComponent(:instance => instance)
            ifref = findBusInterface(component, :name => interface_name)#active_interface.get("BusRef"))
      unconnected_count = 0
      physical_ports_count = 0
      # iterates over all InterfaceRef ports
            foreachPortMap(ifref) do |logical_port, physical_port|
        physical_ports_count+=1
        # iterates over all instance unconnected ports
        unconnected_ports.each do |unconnected_port|
                unconnected_port_name = extractName(unconnected_port)
          # if InterfaceRef port is unconnected sets is_connected to false
                if unconnected_port_name == getName(physical_port)
            unconnected_count+=1
      break
          end
        end
            end
      if unconnected_count == 0
        is_connected = "true"
        found = 1
      elsif (unconnected_count > 0) and (unconnected_count < physical_ports_count)
        is_connected = "partial"
        found = 1
      else
        is_connected = "false"
      end
    end
    if found == 1
      break
    end
        end
  if found == 1
    break
  end
      end
      # looks for instance interfaces in hierConnections
      if found == 0
        foreachHierConnection(design) do |hier_connection|
          if (hier_connection.element("Interface").get("ComponentRef") == instance_name) && (hier_connection.element("Interface").get("BusRef") == interface_name)
            is_connected = "true"
          end
          if is_connected == "true"
      # finds unconnected ports in instance_name
            unconnected_ports = findUnconnectedPorts(design, :instance_name => instance_name, :port_name=>".*")[instance_name]
            instance = findComponentInstance(design, :name => instance_name)
            component = findComponent(:instance => instance)
            ifref = findBusInterface(component, :name => hier_connection.element("Interface").get("BusRef"))
      # iterates over all InterfaceRef ports
            foreachPortMap(ifref) do |logical_port, physical_port|
        # iterates over all instance unconnected ports
        unconnected_ports.each do |unconnected_port|
                unconnected_port_name = extractName(unconnected_port)
          # if InterfaceRef port is unconnected sets is_connected to false
                if unconnected_port_name == getName(physical_port)
            is_connected = "partial" #false
                  break
          end
        end
              if is_connected == "partial" or is_connected == "true" #false
          break
        end
            end
          end
          if is_connected == "partial"or is_connected == "true" #false
      break
    end
        end
      end
    end
  #elsif selectionType(options) == :mix
  elsif mode == :mix
    # looking for interface on top level
    if instance_name.nil?
      # finds all unconnected ports on top boundary
      unconnected_ports = findUnconnectedPorts(design)
      # finds top component
      comp = findComponent(:design => design)
      # looks into all hierConnections
      foreachHierConnection(design) do |hier_connection|
        # gets InterfaceRef name
        ifref_name = hier_connection.get("InterfaceRef")
        # gets InterfaceRef
        ifref = findBusInterface(comp, :name => "#{ifref_name}")
  # if InterfaceRef is equal to interface_name argument sets is_connected to true
        if ifref_name == interface_name
          is_connected = "true"
    break
  end
      end
      if is_connected == "true"
        ifref = findBusInterface(comp, :name => "#{interface_name}")
  # checks connectivity on all ports belonging to InterfaceRef
  # iterates over all InterfaceRef ports
        foreachPortMap(ifref) do |logical_port, physical_port|
    # iterates over all top boundary unconnected ports
          unconnected_ports[nil].each do |unconnected_port|
            unconnected_port_name = extractName(unconnected_port)
      # if InterfaceRef port is unconnected sets is_connected to partial
            if unconnected_port_name == getName(physical_port)
        is_connected = "partial" #false
              break
      end
    end
    if is_connected == "partial" #false
      break
    end 
        end
      else # is_connected == "false"
        ifref = findBusInterface(comp, :name => interface_name)
  unconnected_count = 0
  physical_ports_count = 0
  # checks connectivity on all ports belonging to InterfaceRef
  # iterates over all InterfaceRef ports
        foreachPortMap(ifref) do |logical_port, physical_port|
    physical_ports_count+=1
    # iterates over all top boundary unconnected ports
          unconnected_ports[nil].each do |unconnected_port|
            unconnected_port_name = extractName(unconnected_port)
      # if InterfaceRef port is unconnected sets is_connected to false
            if unconnected_port_name == getName(physical_port)
        unconnected_count+=1
      end
    end
        end
  if unconnected_count == 0
    is_connected = "true"
  elsif (unconnected_count > 0) and (unconnected_count < physical_ports_count)
    is_connected = "partial"
  else
    is_connected = "false"
  end
      end
    else # looking for interface on instance
      found = 0
      # looks for instance interfaces in interconnections
      foreachInterconnection(design) do |interconnection|
        interconnection.elements("ActiveInterface").each do |active_interface|
          if (active_interface.get("ComponentRef") == instance_name) && (active_interface.get("BusRef") == interface_name)
            is_connected = "true"
      found = 1
      # finds unconnected ports in instance_name
            unconnected_ports = findUnconnectedPorts(design, :instance_name => instance_name, :port_name=>".*")[instance_name]
            instance = findComponentInstance(design, :name => instance_name)
            component = findComponent(:instance => instance)
      ifref = findBusInterface(component, :name => interface_name)#active_interface.get("BusRef"))
      # iterates over all InterfaceRef ports
      foreachPortMap(ifref) do |logical_port, physical_port|
        # iterates over all instance unconnected ports
        unconnected_ports.each do |unconnected_port|
    unconnected_port_name = extractName(unconnected_port)
    # if InterfaceRef port is unconnected sets is_connected to partial
    if unconnected_port_name == getName(physical_port)
      is_connected = "partial" #false
      break
    end
        end
        if is_connected == "partial"
          break
        end
      end
          else # is_connected == "false"
      # finds unconnected ports in instance_name
            unconnected_ports = findUnconnectedPorts(design, :instance_name => instance_name, :port_name=>".*")[instance_name]
            instance = findComponentInstance(design, :name => instance_name)
            component = findComponent(:instance => instance)
            ifref = findBusInterface(component, :name => interface_name)#active_interface.get("BusRef"))
      unconnected_count = 0
      physical_ports_count = 0
      # iterates over all InterfaceRef ports
            foreachPortMap(ifref) do |logical_port, physical_port|
        physical_ports_count+=1
        # iterates over all instance unconnected ports
        unconnected_ports.each do |unconnected_port|
                unconnected_port_name = extractName(unconnected_port)
          # if InterfaceRef port is unconnected sets is_connected to false
                if unconnected_port_name == getName(physical_port)
            unconnected_count+=1
      break
          end
        end
            end
      if unconnected_count == 0
        is_connected = "true"
        found = 1
      elsif (unconnected_count > 0) and (unconnected_count < physical_ports_count)
        is_connected = "partial"
        found = 1
      else
        is_connected = "false"
      end
    end
    if found == 1
      break
    end
        end
  if found == 1
    break
  end
      end
      # looks for instance interfaces in hierConnections
      if found == 0
        foreachHierConnection(design) do |hier_connection|
          if (hier_connection.element("Interface").get("ComponentRef") == instance_name) && (hier_connection.element("Interface").get("BusRef") == interface_name)
            is_connected = "true"
          end
          if is_connected == "true"
      # finds unconnected ports in instance_name
            unconnected_ports = findUnconnectedPorts(design, :instance_name => instance_name, :port_name=>".*")[instance_name]
            instance = findComponentInstance(design, :name => instance_name)
            component = findComponent(:instance => instance)
            ifref = findBusInterface(component, :name => hier_connection.element("Interface").get("BusRef"))
      # iterates over all InterfaceRef ports
            foreachPortMap(ifref) do |logical_port, physical_port|
        # iterates over all instance unconnected ports
        unconnected_ports.each do |unconnected_port|
                unconnected_port_name = extractName(unconnected_port)
          # if InterfaceRef port is unconnected sets is_connected to false
                if unconnected_port_name == getName(physical_port)
            is_connected = "partial" #false
                  break
          end
        end
              if is_connected == "partial" or is_connected == "true" #false
          break
        end
            end
          end
          if is_connected == "partial"or is_connected == "true" #false
      break
    end
        end
      end
    end
  else # looking for port connection
    if findUnconnectedPorts(design, options)[instance_name].empty?
      if !instance_name.to_s.empty?
        instance = findComponentInstance(design, :name => instance_name)
        if (instance)
          component = findComponent(:instance => instance)
        else
          component = nil
        end
      else
        component = findComponent(:design => design_element)
      end
      if (component)
        port = findPort(component, :name => port_name)
      else
        port = nil
      end
      if (component.nil? || port.nil?)
        error_messages << "Port: #{port_name} does not exist!"
        raiseError(__method__, design_element, arguments_received, error_messages)
      else
        is_connected = "true"
      end
    end
  end
  return is_connected
end

def connStatus(design_element, options ={})
  # Checks
  de_received = defined?(design_element) ? design_element : :none
  arguments_received = defined?(options) ? options : nil
  supported_element_types = ["Design", "Component"]
  valid_options = [:filter, :sort_by, :format, :mode]
  design_element, element_type, error_messages = commonChecks(de_received, arguments_received, supported_element_types, valid_options)

  defaults                            = {:filter => ".*", :sort_by => :bus_type, :format => :API, :mode => :interface}
  options                             = defaults.merge(options)

  filter                              = options[:filter] 
  sort_by                             = options[:sort_by]
  format                              = options[:format]
  mode                                = options[:mode]

  conn_value = "Connectivity report\n\n"
  if !(error_messages.empty?)
    raiseError(__method__, design_element, arguments_received, error_messages)
  end
  # Body 
  if element_type == "Component"
    de_top_component   = design_element
    hierarchy_ref      = de_top_component.find("HierarchyRef", nil, nil, false)[0]
    if (hierarchy_ref.nil?)
      conn_value = conn_value + "Skipping reporting unconnected interfaces on component " + de_top_component.get("Name") + " as no Hierarchy Ref found\n\n"
      puts "Skipping reporting unconnected interfaces on component " + de_top_component.get("Name") + " as no Hierarchy Ref found"
      return
    else
      vlnv = getVLNV(hierarchy_ref)
      de_design = findDesign(:vendor => vlnv[:vendor], :library =>  vlnv[:library], :name => vlnv[:name], :version => vlnv[:version] )
    end 
    if (findDesign :component => de_top_component) == nil
    else       
      de_design              = findDesign :component => de_top_component
    end
  elsif element_type == "Design"
    de_design              = design_element  
    de_top_component       = findComponent :design => de_design
  end
  if mode == :interface or mode == :mix
    de_interface_ref_arr                 = []
    list_top_bus_interfaces              = []
    unconnected_interface_count          = 0
    tot_unconnected_interface_count      = 0
    connected_interface_count            = 0
    partialconnected_interface_count     = 0
    tot_partialconnected_interface_count = 0
    tot_connected_interface_count        = 0
    top_interface_count                  = 0
    top_unconnected_interface_count      = 0
    top_partialconnected_interface_count = 0
    interface_count                      = 0
    tot_interface_count                  = 0
    #find boundary interfaces that are unconnected
    if de_top_component.element("BusInterfaces") != nil
      if de_top_component.element("BusInterfaces").elements("BusInterface") != nil
        list_de_bus_interfaces = de_top_component.element("BusInterfaces").elements("BusInterface")
        list_de_bus_interfaces.each do |de_bus_interface|
          top_interface_count+=1
          active_interface_connection_found = my_isConnected(de_design, :interface_name => getName(de_bus_interface), :mode => mode)
	  if active_interface_connection_found == "false"
	    top_unconnected_interface_count+=1
	  elsif active_interface_connection_found == "partial"
	    top_partialconnected_interface_count+=1
	  end
        end
      end 
    end 
#    de_hier_connections        =  de_design.element("HierConnections")
#    unless de_hier_connections == nil
#      list_de_hier_connections = de_hier_connections.elements("HierConnection")
#      list_de_hier_connections.each do |de_hier_connection|
#        de_interface_ref_arr << de_hier_connection.get("InterfaceRef").strip
#      end
#    end
#    de_interface_ref_arr.each do |de_interface_ref|
#      list_top_bus_interfaces.delete_if{|e| e.interface == de_interface_ref}
#    end
#    for e in list_top_bus_interfaces
#      top_unconnected_interface_count+=1
#    end
    if filter == ".*"
      conn_value = conn_value + "#{de_top_component.get("Name")} boundary has #{top_unconnected_interface_count} unconnected interfaces, #{top_partialconnected_interface_count} of which are partially connected, out of #{top_interface_count}\n"
      puts "#{de_top_component.get("Name")} boundary has #{top_unconnected_interface_count} unconnected interfaces, #{top_partialconnected_interface_count} of which are partially connected, out of #{top_interface_count}\n"
    end
      ### Find unconnected interfaces inside the Design
    de_comp_instances                   = de_design.element("ComponentInstances")
    unless de_comp_instances == nil
      list_comp_instances =   de_comp_instances.elements("ComponentInstance")
      list_comp_instances.each do |de_comp_instance|
        de_comp_ref                = de_comp_instance.element("ComponentRef")
        de_instantiated_component  = de_comp_ref.element("InstantiatedComponent")
        de_comp_bus_interfaces     = de_instantiated_component.element("BusInterfaces")
        unless de_comp_bus_interfaces == nil
          list_compbus_interfaces = de_comp_bus_interfaces.elements("BusInterface")
          list_compbus_interfaces.each do |de_bus_interface|
            if ((de_comp_instance.get("InstanceName") =~ /^#{filter}$/) and (sort_by == :instance)) or ((de_bus_interface.element("BusType").get("Name") =~ /^#{filter}$/) and (sort_by == :bus_type))
              role = getRole(de_bus_interface)
              next if role.nil?
              active_interface_connection_found = my_isConnected(de_design, :instance_name => getName(de_comp_instance), :interface_name => getName(de_bus_interface), :mode => mode)
              if active_interface_connection_found == "false"
                next if de_bus_interface.element("BusType").nil?
                unconnected_interface_count+=1
              elsif active_interface_connection_found == "partial"
                next if de_bus_interface.element("BusType").nil?
                unconnected_interface_count+=1
                partialconnected_interface_count+=1
              else
                next if de_bus_interface.element("BusType").nil?
                connected_interface_count+=1
              end
            end
          end
          interface_count = connected_interface_count + unconnected_interface_count
          if ((de_comp_instance.get("InstanceName") =~ /^#{filter}$/))
            conn_value = conn_value + "#{de_comp_instance.get("InstanceName")} has #{unconnected_interface_count} unconnected interfaces, #{partialconnected_interface_count} of which are partially connected, out of #{interface_count}\n"
            puts "#{de_comp_instance.get("InstanceName")} has #{unconnected_interface_count} unconnected interfaces, #{partialconnected_interface_count} of which are partially connected, out of #{interface_count}"
            tot_unconnected_interface_count+=unconnected_interface_count
            tot_connected_interface_count+=connected_interface_count
	          tot_partialconnected_interface_count+=partialconnected_interface_count
            unconnected_interface_count=0            
            connected_interface_count=0            
            partialconnected_interface_count=0            
          end
        end
      end
    end
    tot_interface_count = tot_connected_interface_count + tot_unconnected_interface_count
    if filter == ".*"
      conn_value = conn_value + "#{de_top_component.get("Name")} design has #{tot_unconnected_interface_count} unconnected interfaces, #{tot_partialconnected_interface_count} of which are partially connected, out of #{tot_interface_count}\n\n"
      puts "#{de_top_component.get("Name")} design has #{tot_unconnected_interface_count} unconnected interfaces, #{tot_partialconnected_interface_count} of which are partially connected, out of #{tot_interface_count}\n\n"
    end
  else #mode is port level connectivity
    unconnected_port_count = 0
    top_ports              = 0.0
    top_unconnected_ports  = 0
    tot_ports              = 0.0
    tot_unconnected_port_count = 0
    #evaluates top number of ports
    top_ports = 0
    component = findComponent(:design => de_design)
    foreachPort(component, :matches => ".*") do |port|
      top_ports+=1
    end
    unconnected_ports = findUnconnectedPorts(de_design) # top boundary
    unconnected_ports.each_key do |instance_name|
      unconnected_ports[instance_name].each do |unconnected_port| 
        if instance_name.nil?
          component = findComponent(:design => de_design)
        else
          instance = findComponentInstance(de_design, :name => instance_name)
          component = findComponent(:instance => instance)
        end
        port_name = extractName(unconnected_port)
        port = findPort(component, :name => port_name)
        top_unconnected_ports+=1
      end
    end
    if filter == ".*"
      conn_value = conn_value + "#{de_top_component.get("Name")} boundary has #{top_unconnected_ports} unconnected ports out of #{top_ports} ports\n"
      puts "#{de_top_component.get("Name")} boundary has #{top_unconnected_ports} unconnected ports out of #{top_ports} ports"
    end
    unconnected_ports = findUnconnectedPorts(de_design, :instance_name => "#{filter}")
    unconnected_ports.each_key do |instance_name|
      unconnected_ports[instance_name].each do |unconnected_port| 
        if instance_name.nil?
          component = findComponent(:design => de_design)
        else
          instance = findComponentInstance(de_design, :name => instance_name)
          component = findComponent(:instance => instance)
        end
        port_name = extractName(unconnected_port)
        port = findPort(component, :name => port_name)
        unconnected_port_count+=1
      end
      n_ports = 0
      instance = findComponentInstance(de_design, :name => instance_name)
      component = findComponent(:instance => instance)
      foreachPort(component, :matches => ".*") do |port|
        n_ports+=1
      end
      conn_value = conn_value + "#{instance_name} has #{unconnected_port_count} unconnected ports out of #{n_ports}\n"
      puts "#{instance_name} has #{unconnected_port_count} unconnected ports out of #{n_ports}"
      tot_unconnected_port_count+=unconnected_port_count
      tot_ports+=n_ports
      unconnected_port_count=0
    end
    tot_ports+=top_ports
    tot_unconnected_port_count+=top_unconnected_ports
    if filter == ".*"
      conn_value = conn_value + "#{de_top_component.get("Name")} Design has #{tot_unconnected_port_count} unconnected ports out of #{tot_ports}\n"
      puts "#{de_top_component.get("Name")} Design has #{tot_unconnected_port_count} unconnected ports out of #{tot_ports}"
      conn_rate = (tot_ports - tot_unconnected_port_count)/(tot_ports) * 100
      conn_value = conn_value + "Connectivity rate is #{conn_rate}%\n\n"
      puts "Connectivity rate is #{conn_rate}%"
    end
  end
  return conn_value
end
