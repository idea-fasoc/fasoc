#!/usr/bin/env python3
#MIT License

#Copyright (c) 2018 The University of Michigan

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

from xml.dom import minidom
import os
import json
import shutil

def jsonXmlGenerator(configJson,designJson,units,outputDir,ipXactDir):
	general_title = ['power','area','platform','vin','aspect_ratio']
	physical_port_set = []

	designModule = designJson["module_name"]
	designGen = designJson["generator"]

	root = minidom.Document()
	component = root.createElement('spirit:component')
	component.setAttribute('xmlns:spirit',"http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009")
	component.setAttribute('xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance")
	component.setAttribute('xmlns:arm',"http://www.arm.com/SPIRIT/1685-2009")
	component.setAttribute('xmlns:IDEA',"https://www.umich.edu")
	component.setAttribute('xmlns:soc',"http://www.duolog.com/2011/05/socrates")
	component.setAttribute('xsi:schemaLocation',"http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009/index.xsd")
	root.appendChild(component)
	component_vendor = root.createElement('spirit:vendor')
	component_vendor.appendChild(root.createTextNode('IDEA_UofM_UV'))
	component.appendChild(component_vendor)
	component_library = root.createElement('spirit:library')
	component_library.appendChild(root.createTextNode('IDEA'))
	component.appendChild(component_library)
	component_name = root.createElement('spirit:name')
	component_name.appendChild(root.createTextNode(designModule))
	component.appendChild(component_name)
	component_version = root.createElement('spirit:version')
	component_version.appendChild(root.createTextNode('1.00'))
	component.appendChild(component_version)

	if "interfaces" in configJson:
		businterfaces = root.createElement('spirit:busInterfaces')
		component.appendChild(businterfaces)
		jsn_interfaces = configJson["interfaces"]
		for jsn_interface in jsn_interfaces:
			jsn_interface_name = jsn_interface["name"]
			jsn_abstraction_type = jsn_interface["type"].split("-")
			jsn_abstraction_name = jsn_abstraction_type[0]
			jsn_abstraction_mode = jsn_abstraction_type[1]
			jsn_interface_map = jsn_interface["map"]

			businterface = root.createElement('spirit:busInterface')
			businterfaces.appendChild(businterface)
			businterface_name = root.createElement('spirit:name')
			businterface_name.appendChild(root.createTextNode(jsn_interface_name))
			businterface.appendChild(businterface_name)
			bustype = root.createElement('spirit:busType')
			if jsn_abstraction_name == 'apb':
				bustype.setAttribute('spirit:vendor','amba.com')
				bustype.setAttribute('spirit:library','AMBA4')
				bustype.setAttribute('spirit:name','APB4')
				bustype.setAttribute('spirit:version','r0p0_0')
				businterface.appendChild(bustype)

				abstractiontype = root.createElement('spirit:abstractionType')
				abstractiontype.setAttribute('spirit:vendor','amba.com')
				abstractiontype.setAttribute('spirit:library','AMBA4')
				abstractiontype.setAttribute('spirit:name','APB4_rtl')
				abstractiontype.setAttribute('spirit:version','r0p0_0')

			if jsn_abstraction_name == 'ahb':
				bustype.setAttribute('spirit:vendor','amba.com')
				bustype.setAttribute('spirit:library','AMBA3')
				bustype.setAttribute('spirit:name','AHBLite')
				bustype.setAttribute('spirit:version','r2p0_0')
				businterface.appendChild(bustype)

				abstractiontype = root.createElement('spirit:abstractionType')
				abstractiontype.setAttribute('spirit:vendor','amba.com')
				abstractiontype.setAttribute('spirit:library','AMBA3')
				abstractiontype.setAttribute('spirit:name','AHBLite_rtl')
				abstractiontype.setAttribute('spirit:version','r2p0_0')

			businterface.appendChild(abstractiontype)
			interface_mode = root.createElement('spirit:'+ jsn_abstraction_mode)
			businterface.appendChild(interface_mode)

			portmaps = root.createElement('spirit:portMaps')
			businterface.appendChild(portmaps)
			for jsn_port_instreface_map in jsn_interface_map:
				if "name" in jsn_interface_map[jsn_port_instreface_map]:
					jsns_interface_logical_port = jsn_interface_map[jsn_port_instreface_map]["name"]
				else:
					jsns_interface_logical_port = jsn_interface_map[jsn_port_instreface_map]
				if jsn_abstraction_mode =='master' and jsn_abstraction_name == 'ahb' and (jsns_interface_logical_port == "HREADYOUT" or jsns_interface_logical_port == "HSELx"):
					pass
				else:
					portmap = root.createElement('spirit:portMap')
					portmaps.appendChild(portmap)
					logical_port = root.createElement('spirit:logicalPort')
					portmap.appendChild(logical_port)
					logical_port_name = root.createElement('spirit:name')
					logical_port_name.appendChild(root.createTextNode(jsns_interface_logical_port))
					logical_port.appendChild(logical_port_name)

					physical_port = root.createElement('spirit:physicalPort')
					portmap.appendChild(physical_port)
					physical_port_name = root.createElement('spirit:name')
					physical_port_name.appendChild(root.createTextNode(jsn_port_instreface_map))
					physical_port.appendChild(physical_port_name)

	component_model = root.createElement('spirit:model')
	component.appendChild(component_model)
	model_views = root.createElement('spirit:views')
	component_model.appendChild(model_views)
	model_view = root.createElement('spirit:view')
	model_views.appendChild(model_view)
	view_name = root.createElement('spirit:name')
	view_name.appendChild(root.createTextNode('verilogSource'))
	model_view.appendChild(view_name)
	view_envIdentifier = root.createElement('spirit:envIdentifier')
	view_envIdentifier.appendChild(root.createTextNode(':modelsim.mentor.com:'))
	model_view.appendChild(view_envIdentifier)
	view_envIdentifier = root.createElement('spirit:envIdentifier')
	view_envIdentifier.appendChild(root.createTextNode(':ncsim.cadence.com:'))
	model_view.appendChild(view_envIdentifier)
	view_envIdentifier = root.createElement('spirit:envIdentifier')
	view_envIdentifier.appendChild(root.createTextNode(':vcs.synopsys.com:'))
	model_view.appendChild(view_envIdentifier)
	view_envIdentifier = root.createElement('spirit:envIdentifier')
	view_envIdentifier.appendChild(root.createTextNode(':designcompiler.synopsys.com:'))
	model_view.appendChild(view_envIdentifier)
	view_language = root.createElement('spirit:language')
	view_language.appendChild(root.createTextNode('Verilog'))
	model_view.appendChild(view_language)
	view_modelname = root.createElement('spirit:modelName')
	view_modelname.appendChild(root.createTextNode(designGen))
	model_view.appendChild(view_modelname)
	view_filesetref = root.createElement('spirit:fileSetRef')
	model_view.appendChild(view_filesetref)
	filesetref_localname = root.createElement('spirit:localName')
	filesetref_localname.appendChild(root.createTextNode(designModule))#Verilog file name
	view_filesetref.appendChild(filesetref_localname)
		

	model_ports = root.createElement('spirit:ports')
	component_model.appendChild(model_ports)
	 
	jsn_circuit_functionality = designGen.split("-gen")

	if "interfaces" in configJson:
		for jsn_interface in jsn_interfaces:
			jsn_interface_name = jsn_interface["name"]
			jsn_abstraction_type = jsn_interface["type"].split("-")
			jsn_abstraction_name = jsn_abstraction_type[0]
			jsn_abstraction_mode = jsn_abstraction_type[1]
			jsn_interface_map = jsn_interface["map"] 
			for jsn_port_instreface_map in jsn_interface_map:
				if jsn_port_instreface_map not in physical_port_set:
					physical_port_set.append(jsn_port_instreface_map)
					if "name" in jsn_interface_map[jsn_port_instreface_map]:
						jsns_interface_logical_port = jsn_interface_map[jsn_port_instreface_map]["name"]
					else:
						jsns_interface_logical_port = jsn_interface_map[jsn_port_instreface_map]

					if jsn_abstraction_mode =='master' and jsn_abstraction_name == 'ahb' and (jsns_interface_logical_port == "HREADYOUT" or jsns_interface_logical_port == "HSELx"):
						pass
					else:
						model_port = root.createElement('spirit:port')
						model_ports.appendChild(model_port)
						model_port_name = root.createElement('spirit:name')
						model_port_name.appendChild(root.createTextNode(jsn_port_instreface_map))
						model_port.appendChild(model_port_name)
						model_port_wire = root.createElement('spirit:wire')
						model_port.appendChild(model_port_wire)

						model_port_wire_dir=root.createElement('spirit:direction')
						if jsn_abstraction_mode == 'slave':
							if jsn_abstraction_name == 'apb':
								if jsns_interface_logical_port == "PRDATA" or jsns_interface_logical_port == "PREADY" or jsns_interface_logical_port == "PSLVERR":
									model_port_wire_dir.appendChild(root.createTextNode('out'))
								else:
									model_port_wire_dir.appendChild(root.createTextNode('in'))
							if jsn_abstraction_name == 'ahb':
								if jsns_interface_logical_port == "HRDATA" or jsns_interface_logical_port == "HREADYOUT" or jsns_interface_logical_port == "HRESP" or jsns_interface_logical_port == "HRUSER":
									model_port_wire_dir.appendChild(root.createTextNode('out'))
								else:
									model_port_wire_dir.appendChild(root.createTextNode('in'))
						if jsn_abstraction_mode =='master':
							if jsn_abstraction_name == 'apb':
								if jsns_interface_logical_port == "PCLK" or jsns_interface_logical_port == "PRESETn" or jsns_interface_logical_port == "PCLKEN" or jsns_interface_logical_port == "PRDATA" or jsns_interface_logical_port == "PREADY" or jsns_interface_logical_port == "PSLVERR":
									model_port_wire_dir.appendChild(root.createTextNode('in'))
								else:
									model_port_wire_dir.appendChild(root.createTextNode('out'))
							if jsn_abstraction_name == 'ahb':

								if jsns_interface_logical_port == "HCLK" or jsns_interface_logical_port == "HRESETn" or jsns_interface_logical_port == "HRDATA" or jsns_interface_logical_port == "HREADY" or jsns_interface_logical_port == "HRESP" or jsns_interface_logical_port == "HRUSER":
									model_port_wire_dir.appendChild(root.createTextNode('in'))
								else:
									model_port_wire_dir.appendChild(root.createTextNode('out'))
						model_port_wire.appendChild(model_port_wire_dir)

						if "width" in jsn_interface_map[jsn_port_instreface_map]:
							model_port_wire_vec = root.createElement('spirit:vector')
							model_port_wire.appendChild(model_port_wire_vec)
							model_port_wire_left = root.createElement('spirit:left')
							model_port_wire_left.appendChild(root.createTextNode(str(jsn_interface_map[jsn_port_instreface_map]["width"]-1)))
							model_port_wire_vec.appendChild(model_port_wire_left)
							model_port_wire_right = root.createElement('spirit:right')
							model_port_wire_right.appendChild(root.createTextNode('0'))
							model_port_wire_vec.appendChild(model_port_wire_right)
		
	if "ports" in configJson:
		jsn_ports = configJson["ports"]
		for jsn_port in jsn_ports:
			if jsn_port['type'] != "power":
				if jsn_port['name'] not in physical_port_set:
					physical_port_set.append(jsn_port['name'])
					model_port = root.createElement('spirit:port')
					model_ports.appendChild(model_port)
					model_port_name = root.createElement('spirit:name')
					model_port_name.appendChild(root.createTextNode(jsn_port['name']))
					model_port.appendChild(model_port_name)
					model_port_wire = root.createElement('spirit:wire')
					model_port.appendChild(model_port_wire)
					model_port_wire_dir = root.createElement('spirit:direction')
					model_port_wire_dir.appendChild(root.createTextNode(jsn_port['direction']))
					model_port_wire.appendChild(model_port_wire_dir)
					if "width" in jsn_port:
						model_port_wire_vec = root.createElement('spirit:vector')
						model_port_wire.appendChild(model_port_wire_vec)
						model_port_wire_left = root.createElement('spirit:left')
						model_port_wire_left.appendChild(root.createTextNode(str(jsn_port['width']-1)))
						model_port_wire_vec.appendChild(model_port_wire_left)
						model_port_wire_right = root.createElement('spirit:right')
						model_port_wire_right.appendChild(root.createTextNode('0'))
						model_port_wire_vec.appendChild(model_port_wire_right)

	component_filesets = root.createElement('spirit:fileSets')
	component.appendChild(component_filesets)
	filesets_fileset = root.createElement('spirit:fileSet')
	component_filesets.appendChild(filesets_fileset)
	fileset_name = root.createElement('spirit:name')
	fileset_name.appendChild(root.createTextNode(designModule))#what is this
	filesets_fileset.appendChild(fileset_name)
	fileset_file = root.createElement('spirit:file')
	filesets_fileset.appendChild(fileset_file)
	fileset_file_name = root.createElement('spirit:name')
	fileset_file_name.appendChild(root.createTextNode(os.path.join(outputDir,designModule + '.v')))
	fileset_file.appendChild(fileset_file_name)
	fileset_filetype = root.createElement('spirit:fileType')
	fileset_filetype.appendChild(root.createTextNode('verilogSource'))
	fileset_file.appendChild(fileset_filetype)
	fileset_logicalname = root.createElement('spirit:logicalName')
	fileset_logicalname.appendChild(root.createTextNode('verilog_output'))
	fileset_file.appendChild(fileset_logicalname)

	if 'parameters' in designJson:
		component_parameters = root.createElement('spirit:parameters')
		component.appendChild(component_parameters)
		for parameter in designJson['parameters']:
			jsn_parameter = designJson['parameters'][parameter]
			component_parameter = root.createElement('spirit:parameter')
			component_parameters.appendChild(component_parameter)
			parameter_name = root.createElement('spirit:name')
			parameter_name.appendChild(root.createTextNode(parameter))
			component_parameter.appendChild(parameter_name)
			parameter_value = root.createElement('spirit:value')
			parameter_value.appendChild(root.createTextNode(str(jsn_parameter)))
			component_parameter.appendChild(parameter_value)

	gen_result_path=os.path.join(outputDir,designModule+'.json')
	if os.path.isfile(gen_result_path):
		with open(gen_result_path, 'r') as generator_result:
			jsn_result_elmnts = json.load(generator_result)
		jsn_generator_results = jsn_result_elmnts["results"]
		general_tag=False

		component_vendor_extension = root.createElement('spirit:vendorExtensions')
		component.appendChild(component_vendor_extension)
		circuitFunctionDescriptions = root.createElement('IDEA:circuitFunctionDescriptions')
		component_vendor_extension.appendChild(circuitFunctionDescriptions)
		for jsn_result in jsn_generator_results:
			if jsn_result in general_title:
				general_tag = True
				break
		circuit_name = root.createElement('IDEA:'+designModule)
		circuitFunctionDescriptions.appendChild(circuit_name)
	
		if(general_tag):
			general = root.createElement('IDEA:general')
			circuit_name.appendChild(general)
			aspect_ratio_tag = False
			for jsn_result in jsn_generator_results:
				if jsn_result in general_title:
					if jsn_result == "aspect_ratio":
						aspect_ratio_tag = True
					
					spec_name = root.createElement('IDEA:'+jsn_result)
					general.appendChild(spec_name)
					
					IDEA_typical_value=root.createElement('IDEA:typical')
					if jsn_result in units:
						IDEA_typical_value.setAttribute("IDEA:unit",units[jsn_result])
					IDEA_typical_value.appendChild(root.createTextNode(str(jsn_generator_results[jsn_result])))
					spec_name.appendChild(IDEA_typical_value)

			if not aspect_ratio_tag:
				spec_name = root.createElement('IDEA:aspect_ratio')
				general.appendChild(spec_name)

				IDEA_typical_value = root.createElement('IDEA:typical')
				IDEA_typical_value.appendChild(root.createTextNode('1:1'))
				spec_name.appendChild(IDEA_typical_value)

		specific = root.createElement('IDEA:specific')
		circuit_name.appendChild(specific)

		for jsn_result in jsn_generator_results:
			if jsn_result not in general_title:
				spec_name = root.createElement('IDEA:'+jsn_result)
				specific.appendChild(spec_name)

				if isinstance(jsn_generator_results[jsn_result], dict):
					IDEA_maximum_value = root.createElement('IDEA:maximum')
					if jsn_result in units:
						IDEA_maximum_value.setAttribute("IDEA:unit",units[jsn_result])
					IDEA_maximum_value.appendChild(root.createTextNode(str(jsn_generator_results[jsn_result]["max"])))
					spec_name.appendChild(IDEA_maximum_value)
					
					IDEA_minimum_value = root.createElement('IDEA:minimum')
					if jsn_result in units:
						IDEA_minimum_value.setAttribute("IDEA:unit",units[jsn_result])
					IDEA_minimum_value.appendChild(root.createTextNode(str(jsn_generator_results[jsn_result]["min"])))
					spec_name.appendChild(IDEA_minimum_value)

					if "typ" in jsn_generator_results[jsn_result]:
						IDEA_typical_value = root.createElement('IDEA:typical')
						if jsn_result in units:
							IDEA_typical_value.setAttribute("IDEA:unit",units[jsn_result])
						IDEA_typical_value.appendChild(root.createTextNode(str(jsn_generator_results[jsn_result]["typ"])))
						spec_name.appendChild(IDEA_typical_value)
					
				else:
					IDEA_typical_value = root.createElement('IDEA:typical')
					if jsn_result in units:
						IDEA_typical_value.setAttribute("IDEA:unit",units[jsn_result])
					IDEA_typical_value.appendChild(root.createTextNode(str(jsn_generator_results[jsn_result])))
					spec_name.appendChild(IDEA_typical_value)

	xml_str = root.toprettyxml(indent="\t")				
	save_path_file = os.path.join(ipXactDir,designModule+'.xml')
	with open(save_path_file,"w") as f1:
		f1.write(xml_str)
	shutil.copy(save_path_file,os.path.join(outputDir,designModule+'.xml'))