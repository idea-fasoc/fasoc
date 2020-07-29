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
    
    def xml_writer(element, attributes, parrent_name, element_name):
        for attribute in attributes:
            element.setAttribute(attribute[0],attribute[1])
        if element_name[0]:
            element.appendChild(root.createTextNode(element_name[1]))
        parrent_name.appendChild(element)

    general_title = ['power','area','platform','vin','Aspect_Ratio','AspectRatio','aspect ratio']
    non_typical_spec = ['platform']
    aspect_ratio_sepc = ['Aspect_Ratio','AspectRatio','aspect ratio']
    physical_port_set = []

    designModule = designJson["module_name"]
    designGen = designJson["generator"]

    root = minidom.Document()
    component = root.createElement('spirit:component')
    xml_writer(component,[['xmlns:spirit',"http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"],['xmlns:xsi',"http://www.w3.org/2001/XMLSchema-instance"],['xmlns:arm',"http://www.arm.com/SPIRIT/1685-2009"],['xmlns:IDEA',"https://www.umich.edu"],['xmlns:soc',"http://www.duolog.com/2011/05/socrates"],['xsi:schemaLocation',"http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009 http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009/index.xsd"]],root,[False,'Dumb'])
    
    component_vendor = root.createElement('spirit:vendor')
    xml_writer(component_vendor,[],component,[True,'IDEA_UofM_UV'])
    component_library = root.createElement('spirit:library')
    xml_writer(component_library,[],component,[True,'IDEA'])
    component_name = root.createElement('spirit:name')
    xml_writer(component_name,[],component,[True,designModule])
    component_version = root.createElement('spirit:version')
    xml_writer(component_version,[],component,[True,'1.00'])

    if "interfaces" in configJson:
        businterfaces = root.createElement('spirit:busInterfaces')
        xml_writer(businterfaces,[],component,[False,'Dumb'])
        jsn_interfaces = configJson["interfaces"]
        for jsn_interface in jsn_interfaces:
            jsn_interface_name = jsn_interface["name"]
            jsn_abstraction_type = jsn_interface["type"].split("-")
            jsn_abstraction_name = jsn_abstraction_type[0]
            jsn_abstraction_mode = jsn_abstraction_type[1]
            jsn_interface_map = jsn_interface["map"]
            jsn_interface_position = jsn_interface["position"]

            businterface = root.createElement('spirit:busInterface')
            xml_writer(businterface,[],businterfaces,[False,'Dumb'])
            businterface_name = root.createElement('spirit:name')
            xml_writer(businterface_name,[],businterface,[True,jsn_interface_name])
            bustype = root.createElement('spirit:busType')
            abstractiontype = root.createElement('spirit:abstractionType')

            if jsn_abstraction_name == 'apb':
                xml_writer(bustype,[['spirit:vendor','amba.com'],['spirit:library','AMBA4'],['spirit:name','APB4'],['spirit:version','r0p0_0']],businterface,[False,'Dumb'])
                abstractiontype_attribure = [['spirit:vendor','amba.com'],['spirit:library','AMBA4'],['spirit:name','APB4_rtl'],['spirit:version','r0p0_0']]

            if jsn_abstraction_name == 'ahb':
                xml_writer(bustype,[['spirit:vendor','amba.com'],['spirit:library','AMBA3'],['spirit:name','AHBLite'],['spirit:version','r2p0_0']],businterface,[False,'Dumb'])
                abstractiontype_attribure = [['spirit:vendor','amba.com'],['spirit:library','AMBA3'],['spirit:name','AHBLite_rtl'],['spirit:version','r2p0_0']]

            xml_writer(abstractiontype,abstractiontype_attribure,businterface,[False,'Dumb'])
            interface_mode = root.createElement('spirit:'+ jsn_abstraction_mode)
            xml_writer(interface_mode,[],businterface,[False,'Dumb'])

            portmaps = root.createElement('spirit:portMaps')
            xml_writer(portmaps,[],businterface,[False,'Dumb'])
            for jsn_port_instreface_map in jsn_interface_map:
                if "name" in jsn_interface_map[jsn_port_instreface_map]:
                    jsns_interface_logical_port = jsn_interface_map[jsn_port_instreface_map]["name"]
                else:
                    jsns_interface_logical_port = jsn_interface_map[jsn_port_instreface_map]
                if jsn_abstraction_mode == 'master' and jsn_abstraction_name == 'ahb' and (jsns_interface_logical_port == "HREADYOUT" or jsns_interface_logical_port == "HSELx"):
                    pass
                else:
                    portmap = root.createElement('spirit:portMap')
                    xml_writer(portmap,[],portmaps,[False,'Dumb'])
                    logical_port = root.createElement('spirit:logicalPort')
                    xml_writer(logical_port,[],portmap,[False,'Dumb'])
                    logical_port_name = root.createElement('spirit:name')
                    xml_writer(logical_port_name,[],logical_port,[True,jsns_interface_logical_port])

                    physical_port = root.createElement('spirit:physicalPort')
                    xml_writer(physical_port,[],portmap,[False,'Dumb'])
                    physical_port_name = root.createElement('spirit:name')
                    xml_writer(physical_port_name,[],physical_port,[True,jsn_port_instreface_map])

            interface_vendor_extension = root.createElement('spirit:vendorExtensions')
            xml_writer(interface_vendor_extension,[],businterface,[False,'Dumb'])
            interface_position = root.createElement('IDEA:position')
            xml_writer(interface_position,[],interface_vendor_extension,[True,jsn_interface_position])

    component_model = root.createElement('spirit:model')
    xml_writer(component_model,[],component,[False,'Dumb'])
    model_views = root.createElement('spirit:views')
    xml_writer(model_views,[],component_model,[False,'Dumb'])
    model_view = root.createElement('spirit:view')
    xml_writer(model_view,[],model_views,[False,'Dumb'])
    view_name = root.createElement('spirit:name')
    xml_writer(view_name,[],model_view,[True,'verilogSource'])
    view_envIdentifier=root.createElement('spirit:envIdentifier')
    xml_writer(view_envIdentifier,[],model_view,[True,':modelsim.mentor.com:'])
    view_envIdentifier = root.createElement('spirit:envIdentifier')
    xml_writer(view_envIdentifier,[],model_view,[True,':ncsim.cadence.com:'])
    view_envIdentifier = root.createElement('spirit:envIdentifier')
    xml_writer(view_envIdentifier,[],model_view,[True,':vcs.synopsys.com:'])
    view_envIdentifier = root.createElement('spirit:envIdentifier')
    xml_writer(view_envIdentifier,[],model_view,[True,':designcompiler.synopsys.com:'])
    view_language = root.createElement('spirit:language')
    xml_writer(view_language,[],model_view,[True,'Verilog'])
    view_modelname = root.createElement('spirit:modelName')
    xml_writer(view_modelname,[],model_view,[True,designGen])
    view_filesetref = root.createElement('spirit:fileSetRef')
    xml_writer(view_filesetref,[],model_view,[False,'Dumb'])
    filesetref_localname = root.createElement('spirit:localName')
    xml_writer(filesetref_localname,[],view_filesetref,[True,designModule])

    model_ports = root.createElement('spirit:ports')
    xml_writer(model_ports,[],component_model,[False,'Dumb'])

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
                        jsns_interface_logical_port=jsn_interface_map[jsn_port_instreface_map]

                    if jsn_abstraction_mode =='master' and jsn_abstraction_name == 'ahb' and (jsns_interface_logical_port == "HREADYOUT" or jsns_interface_logical_port == "HSELx"):
                        pass
                    else:
                        model_port = root.createElement('spirit:port')
                        xml_writer(model_port,[],model_ports,[False,'Dumb'])
                        model_port_name = root.createElement('spirit:name')
                        xml_writer(model_port_name,[],model_port,[True,jsn_port_instreface_map])
                        model_port_wire = root.createElement('spirit:wire')
                        xml_writer(model_port_wire,[],model_port,[False,'Dumb'])

                        model_port_wire_dir = root.createElement('spirit:direction')
                        if jsn_abstraction_mode == 'slave':
                            if jsn_abstraction_name == 'apb':
                                if jsns_interface_logical_port == "PRDATA" or jsns_interface_logical_port == "PREADY" or jsns_interface_logical_port == "PSLVERR":
                                    model_port_wire_dir_text_node = 'out'
                                else:
                                    model_port_wire_dir_text_node = 'in'
                            elif jsn_abstraction_name == 'ahb':
                                if jsns_interface_logical_port == "HRDATA" or jsns_interface_logical_port == "HREADYOUT" or jsns_interface_logical_port == "HRESP" or jsns_interface_logical_port == "HRUSER":
                                    model_port_wire_dir_text_node = 'out'
                                else:
                                    model_port_wire_dir_text_node = 'in'
                        elif jsn_abstraction_mode =='master':
                            if jsn_abstraction_name == 'apb':
                                if jsns_interface_logical_port == "PCLK" or jsns_interface_logical_port == "PRESETn" or jsns_interface_logical_port == "PCLKEN" or jsns_interface_logical_port == "PRDATA" or jsns_interface_logical_port == "PREADY" or jsns_interface_logical_port == "PSLVERR":
                                    model_port_wire_dir_text_node = 'in'
                                else:
                                    model_port_wire_dir_text_node = 'out'
                            elif jsn_abstraction_name == 'ahb':

                                if jsns_interface_logical_port == "HCLK" or jsns_interface_logical_port == "HRESETn" or jsns_interface_logical_port == "HRDATA" or jsns_interface_logical_port == "HREADY" or jsns_interface_logical_port == "HRESP" or jsns_interface_logical_port == "HRUSER":
                                    model_port_wire_dir_text_node = 'in'
                                else:
                                    model_port_wire_dir_text_node = 'out'
                        xml_writer(model_port_wire_dir,[],model_port_wire,[True,model_port_wire_dir_text_node])

                        if "width" in jsn_interface_map[jsn_port_instreface_map]:
                            model_port_wire_vec = root.createElement('spirit:vector')
                            xml_writer(model_port_wire_vec,[],model_port_wire,[False,'Dumb'])
                            model_port_wire_left = root.createElement('spirit:left')
                            xml_writer(model_port_wire_left,[],model_port_wire_vec,[True,str(jsn_interface_map[jsn_port_instreface_map]["width"]-1)])
                            model_port_wire_right = root.createElement('spirit:right')
                            xml_writer(model_port_wire_right,[],model_port_wire_vec,[True,'0'])
        
    if "ports" in configJson:
        jsn_ports = configJson["ports"]
        for jsn_port in jsn_ports:
            if jsn_port['type'] != "power":
                if jsn_port['name'] not in physical_port_set:
                    physical_port_set.append(jsn_port['name'])
                    model_port = root.createElement('spirit:port')
                    xml_writer(model_port,[],model_ports,[False,'Dumb'])
                    model_port_name = root.createElement('spirit:name')
                    xml_writer(model_port_name,[],model_port,[True,jsn_port['name']])
                    model_port_wire = root.createElement('spirit:wire')
                    xml_writer(model_port_wire,[],model_port,[False,'Dumb'])
                    model_port_wire_dir = root.createElement('spirit:direction')
                    xml_writer(model_port_wire_dir,[],model_port_wire,[True,jsn_port['direction']])
                    if "width" in jsn_port:
                        model_port_wire_vec = root.createElement('spirit:vector')
                        xml_writer(model_port_wire_vec,[],model_port_wire,[False,'Dumb'])
                        model_port_wire_left = root.createElement('spirit:left')
                        xml_writer(model_port_wire_left,[],model_port_wire_vec,[True,str(jsn_port['width']-1)])
                        model_port_wire_right = root.createElement('spirit:right')
                        xml_writer(model_port_wire_right,[],model_port_wire_vec,[True,'0'])
                    port_vendor_extension = root.createElement('spirit:vendorExtensions')
                    xml_writer(port_vendor_extension,[],model_port,[False,'Dumb'])
                    port_position = root.createElement('IDEA:position')
                    xml_writer(port_position,[],port_vendor_extension,[True,jsn_port['position']])

    component_filesets = root.createElement('spirit:fileSets')
    xml_writer(component_filesets,[],component,[False,'Dumb'])
    filesets_fileset = root.createElement('spirit:fileSet')
    xml_writer(filesets_fileset,[],component_filesets,[False,'Dumb'])
    fileset_name = root.createElement('spirit:name')
    xml_writer(fileset_name,[],filesets_fileset,[True,designModule])
    fileset_file = root.createElement('spirit:file')
    xml_writer(fileset_file,[],filesets_fileset,[False,'Dumb'])
    fileset_file_name = root.createElement('spirit:name')
    xml_writer(fileset_file_name,[],fileset_file,[True,os.path.join(outputDir,designModule + '.v')])
    fileset_filetype = root.createElement('spirit:fileType')
    xml_writer(fileset_filetype,[],fileset_file,[True,'verilogSource'])
    fileset_logicalname = root.createElement('spirit:logicalName')
    xml_writer(fileset_logicalname,[],fileset_file,[True,'verilog_output'])

    if 'parameters' in designJson:
        component_parameters = root.createElement('spirit:parameters')
        xml_writer(component_parameters,[],component,[False,'Dumb'])
        for parameter in designJson['parameters']:
            jsn_parameter = designJson['parameters'][parameter]
            component_parameter = root.createElement('spirit:parameter')
            xml_writer(component_parameter,[],component_parameters,[False,'Dumb'])
            parameter_name = root.createElement('spirit:name')
            xml_writer(parameter_name,[],component_parameter,[True,parameter])
            parameter_value = root.createElement('spirit:value')
            xml_writer(parameter_value,[],component_parameter,[True,str(jsn_parameter)])

    gen_result_path = os.path.join(outputDir,designModule+'.json')
    if os.path.isfile(gen_result_path):
        with open(gen_result_path, 'r') as generator_result:
            jsn_result_elmnts = json.load(generator_result)
        jsn_generator_results = jsn_result_elmnts["results"]
        general_tag=False

        component_vendor_extension = root.createElement('spirit:vendorExtensions')
        xml_writer(component_vendor_extension,[],component,[False,'Dumb'])
        circuitFunctionDescriptions = root.createElement('IDEA:circuitFunctionDescriptions')
        xml_writer(circuitFunctionDescriptions,[],component_vendor_extension,[False,'Dumb'])
        for jsn_result in jsn_generator_results:
            if jsn_result in general_title:
                general_tag = True
                break

        circuitFunction = root.createElement('IDEA:'+jsn_circuit_functionality[0])
        xml_writer(circuitFunction,[],circuitFunctionDescriptions,[False,'Dumb'])

        if(general_tag):
            general = root.createElement('IDEA:general')
            xml_writer(general,[],circuitFunction,[False,'Dumb'])
            for jsn_result in jsn_generator_results:
                if jsn_result in general_title:
                    if jsn_result in non_typical_spec:
                        IDEA_value = root.createElement('IDEA:'+jsn_result)
                        xml_writer(IDEA_value,[],general,[True  ,str(jsn_generator_results[jsn_result])])
                    else:
                        if jsn_result in aspect_ratio_sepc:
                            spec_name = root.createElement('IDEA:'+'aspect_ratio')
                        else:
                            spec_name = root.createElement('IDEA:'+jsn_result)
                        xml_writer(spec_name,[],general,[False,'Dumb'])
                        if isinstance(jsn_generator_results[jsn_result], dict):
                            IDEA_max_value = root.createElement('IDEA:maximum')
                            if jsn_result in units:
                                IDEA_max_value_attribute = [["IDEA:unit",units[jsn_result]]]
                            else:
                                IDEA_max_value_attribute = []
                            xml_writer(IDEA_max_value,IDEA_max_value_attribute,spec_name,[True,str(jsn_generator_results[jsn_result]["max"])])
                            IDEA_min_value = root.createElement('IDEA:minimum')
                            if jsn_result in units:
                                IDEA_min_value_attribute = [["IDEA:unit",units[jsn_result]]]
                            else:
                                IDEA_min_value_attribute = []
                            xml_writer(IDEA_min_value,IDEA_min_value_attribute,spec_name,[True,str(jsn_generator_results[jsn_result]["min"])])
                        
                        else:
                            IDEA_typ_value = root.createElement('IDEA:typical')
                            if jsn_result in units:
                                IDEA_typ_value_attribute = [["IDEA:unit",units[jsn_result]]]
                            else:
                                IDEA_typ_value_attribute = []
                            xml_writer(IDEA_typ_value,IDEA_typ_value_attribute,spec_name,[True  ,str(jsn_generator_results[jsn_result])])

        specific = root.createElement('IDEA:specific')
        xml_writer(specific,[],circuitFunction,[False,'Dumb'])
        for jsn_result in jsn_generator_results:
            if jsn_result not in general_title:
                spec_name = root.createElement('IDEA:'+jsn_result)
                xml_writer(spec_name,[],specific,[False,'Dumb'])

                if isinstance(jsn_generator_results[jsn_result], dict):
                    IDEA_max_value = root.createElement('IDEA:maximum')
                    if jsn_result in units:
                        IDEA_max_value_attribute = [["IDEA:unit",units[jsn_result]]]
                    else:
                        IDEA_max_value_attribute = []
                    xml_writer(IDEA_max_value,IDEA_max_value_attribute,spec_name,[True,str(jsn_generator_results[jsn_result]["max"])])
                    IDEA_min_value = root.createElement('IDEA:minimum')
                    if key in units:
                        IDEA_min_value_attribute = [["IDEA:unit",units[jsn_result]]]
                    else:
                        IDEA_min_value_attribute = []
                    xml_writer(IDEA_min_value,IDEA_min_value_attribute,spec_name,[True,str(jsn_generator_results[jsn_result]["min"])])
                    
                else:
                    IDEA_typ_value = root.createElement('IDEA:typical')
                    if jsn_result in units:
                        IDEA_typ_value_attribute = [["IDEA:unit",units[jsn_result]]]
                    else:
                        IDEA_typ_value_attribute = []
                    xml_writer(IDEA_typ_value,IDEA_typ_value_attribute,spec_name,[True,str(jsn_generator_results[jsn_result])])

    xml_str = root.toprettyxml(indent="\t")                
    save_path_file = os.path.join(ipXactDir,designModule+'.xml')
    with open(save_path_file,"w") as f1:
        f1.write(xml_str)
    shutil.copy(save_path_file,os.path.join(outputDir,designModule + '.xml'))