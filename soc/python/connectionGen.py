#!/usr/bin/env python3

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

import json

def connectionGen(generator,instance,module_number,designJson,designDir,ldo_number,pll_number,temp_sense_number):

#------------------------------------------------------------------------------------

	def addConnection_from_to(connection_type,range_tag,instance1,port1,range1,instance2,port2,range2,value):
# Creating connections
		connection = {}
		connection["type"] = connection_type

		connection_from = {}
		if not value[0]:
			connection_from["instance"] = instance1
			connection_from["port"] = port1
			if range_tag:
				connection_from["range"] = {}
				connection_from["range"]["max"] = range1[0]
				connection_from["range"]["min"] = range1[1]
		else:
			connection_from["value"] = value[1]
		connection["from"] = connection_from

		connection_to_list = []
		for i in range(0,len(instance2)):
			connection_to_dict = {}
			connection_to_dict["instance"] = instance2[i]
			connection_to_dict["port"] = port2[i]
			if range_tag:
				connection_to_dict["range"] = {}
				connection_to_dict["range"]["max"] = range2[i][0]
				connection_to_dict["range"]["min"] = range2[i][1]
			connection_to_list.append(connection_to_dict)
		connection["to"] = connection_to_list
		connections.append(connection)

		designJson["connections"] = connections
		with open(designDir, "w") as f:
			json.dump(designJson, f, indent=True)

#------------------------------------------------------------------------------------

	def addConnection_to(existed_connection,range_tag,instance2,port2,range2):
# Creating connections

		connection = existed_connection
		connection_to_list = existed_connection["to"]
		for i in range(0,len(instance2)):
			connection_to_dict = {}
			connection_to_dict["instance"] = instance2[i]
			connection_to_dict["port"] = port2[i]
			connection_to_list.append(connection_to_dict)
			if range_tag:
				connection_to_dict["range"] = {}
				connection_to_dict["range"]["max"] = range2[i][0]
				connection_to_dict["range"]["min"] = range2[i][1]
			connection["to"] = connection_to_list
			connections.append(connection)

			designJson["connections"] = connections
			with open(designDir, "w") as f:
				json.dump(designJson, f, indent=True)
#------------------------------------------------------------------------------------

	with open(designDir, "r") as f:
		designJson = json.load(f)

	total_gen_numbers = -1

	for module in designJson["modules"]:
		if module["generator"] == "cmsdk_apb_slave_mux_rtl":
			module_slave = module["module_name"]
			instance_slave = module["instance_name"]

		elif module["generator"] == "m0mcu_rtl":
			module_m0 = module["module_name"]
			instance_m0 = module["instance_name"]

		elif module["generator"] == "ldo_mux_rtl":
			module_ldo_mux = module["module_name"]
			instance_ldo_mux = module["instance_name"]

		elif module["generator"] == "gpio_rtl":
			module_gpio = module["module_name"]
			instance_gpio = module["instance_name"]

		else:
			total_gen_numbers += 1


	if module_number == 0:
		if "connections" in designJson:
			del designJson["connections"]
		connections = []

# Toplevel Connections

		addConnection_from_to("clock",False,"toplevel","XTAL1_PAD",[0,0],[instance_m0],["XTAL1_PAD"],[[0,0]],[False,0])
		addConnection_from_to("clock",False,instance_m0,"XTAL2_PAD",[0,0],["toplevel"],["XTAL2_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","NRST_PAD",[0,0],[instance_m0],["NRST_PAD"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,instance_m0,"GPIO_INIT_PAD",[0,0],["toplevel"],["GPIO_INIT_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"GPIO_USER0_PAD",[0,0],["toplevel"],["GPIO_USER0_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"GPIO_USER1_PAD",[0,0],["toplevel"],["GPIO_USER1_PAD"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,"toplevel","UART_RXD_PAD",[0,0],[instance_m0],["UART_RXD_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"UART_TXD_PAD",[0,0],["toplevel"],["UART_TXD_PAD"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,"toplevel","LDO_SPI_RESETn_PAD",[0,0],[instance_m0],["LDO_SPI_RESETn_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",True,"toplevel","LDO_SPI_SS_PAD",[1,0],[instance_m0],["LDO_SPI_SS_PAD"],[[1,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","LDO_SPI_SCLK_PAD",[0,0],[instance_m0],["LDO_SPI_SCLK_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","LDO_SPI_MOSI_PAD",[0,0],[instance_m0],["LDO_SPI_MOSI_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"LDO_SPI_MISO_PAD",[0,0],["toplevel"],["LDO_SPI_MISO_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","LDO_SPI_APB_SEL_PAD",[0,0],[instance_m0],["LDO_SPI_APB_SEL_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","LDO_VREF_PAD",[0,0],[instance_m0],["LDO_VREF_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","LDO_REFCLK_PAD",[0,0],[instance_m0],["LDO_REFCLK_PAD"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,"toplevel","MEM_DATA_REQ_PAD",[0,0],[instance_m0],["MEM_DATA_REQ_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_WE_PAD",[0,0],[instance_m0],["MEM_WE_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_TEST_MODE_PAD",[0,0],[instance_m0],["MEM_TEST_MODE_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_CLK_IN_PAD",[0,0],[instance_m0],["MEM_CLK_IN_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_RESET_PAD",[0,0],[instance_m0],["MEM_RESET_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_SPI_CLOCK_PAD",[0,0],[instance_m0],["MEM_SPI_CLOCK_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_SPI_MOSI_PAD",[0,0],[instance_m0],["MEM_SPI_MOSI_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_SPI_RST_PAD",[0,0],[instance_m0],["MEM_SPI_RST_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_SPI_SCLK_PAD",[0,0],[instance_m0],["MEM_SPI_SCLK_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","MEM_SPI_SS_PAD",[0,0],[instance_m0],["MEM_SPI_SS_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"MEM_DOUT32_PAD",[0,0],["toplevel"],["MEM_DOUT32_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_MISO_PAD",[0,0],["toplevel"],["MEM_SPI_MISO_PAD"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,"toplevel","PLL_CLKREF0_PAD",[0,0],[instance_m0],["PLL_CLKREF0_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","PLL_CLKREF1_PAD",[0,0],[instance_m0],["PLL_CLKREF1_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"PLL_CLKOUT0_PAD",[0,0],["toplevel"],["PLL_CLKOUT0_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"PLL_CLKOUT1_PAD",[0,0],["toplevel"],["PLL_CLKOUT1_PAD"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,instance_m0,"TEMP_0_CLKOUT_PAD",[0,0],["toplevel"],["TEMP_0_CLKOUT_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"TEMP_1_CLKOUT_PAD",[0,0],["toplevel"],["TEMP_1_CLKOUT_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","TEMP_0_REFCLK_PAD",[0,0],[instance_m0],["TEMP_0_REFCLK_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","TEMP_1_REFCLK_PAD",[0,0],[instance_m0],["TEMP_1_REFCLK_PAD"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","VIN_TEMPSENSE_PAD",[0,0],[instance_m0],["VIN_TEMPSENSE_PAD"],[[0,0]],[False,0])

		addConnection_from_to("reset",False,"toplevel","nTRST",[0,0],[instance_m0],["nTRST"],[[0,0]],[False,0])
		addConnection_from_to("reset",False,"toplevel","TDI",[0,0],[instance_m0],["TDI"],[[0,0]],[False,0])
		addConnection_from_to("reset",False,instance_m0,"TDO",[0,0],["toplevel"],["TDO"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,"toplevel","SWDIOTMS",[0,0],[instance_m0],["SWDIOTMS"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,"toplevel","SWCLKTCK",[0,0],[instance_m0],["SWCLKTCK"],[[0,0]],[False,0])
		

#RTL Connections
		addConnection_from_to("adhoc",False,instance_slave,"PSEL0",[0,0],[instance_gpio],["PSEL"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",True,instance_slave,"PRDATA0",[31,0],[instance_gpio],["PRDATA"],[[31,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_slave,"PREADY0",[0,0],[instance_gpio],["PREADY"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_slave,"PSLVERR0",[0,0],[instance_gpio],["PSLVERR"],[[0,0]],[False,0])
		
		for i in range(0,16):
			#addConnection_from_to("apb",False,instance_slave,"APBM" + str(i),[0,0],[instance_m0],["M0_APB" + str(i)],[[0,0]],[False,0])
			if i != 1:
				addConnection_from_to("adhoc",False,instance_slave,"PSEL" + str(i),[0,0],[instance_m0],["apb" + str(i) + "_psel"],[[0,0]],[False,0])
		addConnection_from_to("apb",False,instance_slave,"APBM1",[0,0],[instance_m0],["M0_APB1"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",True,instance_m0,"i_paddr",[15,12],[instance_slave],["DECODE4BIT"],[[3,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"i_psel",[0,0],[instance_slave],["PSEL"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",False,instance_m0,"i_pready_mux",[0,0],[instance_slave],["PREADY"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",True,instance_m0,"i_prdata_mux",[31,0],[instance_slave],["PRDATA"],[[31,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"i_pslverr_mux",[0,0],[instance_slave],["PSLVERR"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",True,instance_m0,"LDO_SPI_SS",[1,0],[instance_ldo_mux],["LDO_SPI_SS"],[[1,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"LDO_SPI_MISO",[0,0],[instance_ldo_mux],["LDO_SPI_MISO"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",True,instance_m0,"i_paddr",[11,0],[instance_gpio],["PADDR"],[[11,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"i_pwrite",[0,0],[instance_gpio],["PWRITE"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",False,instance_m0,"i_penable",[0,0],[instance_gpio],["PENABLE"],[[0,0]],[False,0])
		addConnection_from_to("adhoc",True,instance_m0,"i_pwdata",[31,0],[instance_gpio],["PWDATA"],[[31,0]],[False,0])

		addConnection_from_to("clock",False,instance_m0,"PCLK",[0,0],[instance_gpio],["PCLK"],[[0,0]],[False,0])
		addConnection_from_to("reset",False,instance_m0,"PRESETn",[0,0],[instance_gpio],["PRESETn"],[[0,0]],[False,0])

		addConnection_from_to("adhoc",True,instance_m0,"GPIO_O",[31,0],[instance_gpio],["GPIO_O"],[[31,0]],[False,0])

	if "connections" in designJson:
		connections = designJson["connections"]
		tag_top_PCLK = False
		tag_top_PRESETn = False
		tag_ahp_PADDR_11_8 = False
		tag_ahp_PENABLE = False
		tag_ahp_PWRITE = False
		tag_ahp_PWDATA = False

		for connection in connections:
			if "from" in connection:
				if "port" in connection["from"]:

					if connection["from"]["port"] == "PRESETn":
						tag_top_PRESETn = True
						connection_top_PRESETn = connection

					elif connection["from"]["port"] == "PCLK":
						tag_top_PCLK = True
						connection_top_PCLK = connection

					elif connection["from"]["port"] == "PENABLE":
						tag_ahp_PENABLE = True
						connection_ahp_PENABLE = connection

					elif connection["from"]["port"] == "PWRITE":
						tag_ahp_PWRITE = True
						connection_ahp_PWRITE = connection

					elif connection["from"]["port"] == "PWDATA":
						tag_ahp_PWDATA = True
						connection_ahp_PWDATA = connection

					elif "range" in connection["from"]:
						if "max" in connection["from"]["range"] and "min" in connection["from"]["range"]:
							if  connection["from"]["port"] == "PADDR" and connection["from"]["range"]["max"] == 11 and connection["from"]["range"]["min"] == 8:
								tag_ahp_PADDR_11_8 = True
								connection_ahp_PADDR_11_8 = connection


		
		if (generator == 'ldo-gen'):
			#addConnection_from_to("apb",False,instance_slave,"APBM" + str(module_number),[0,0],[instance],["LDO_APBS"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSEL" + str(module_number+2),[0,0],[instance],["PSEL"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_slave,"PRDATA" + str(module_number+2),[31,0],[instance],["PRDATA"],[[31,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PREADY" + str(module_number+2),[0,0],[instance],["PREADY"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSLVERR" + str(module_number+2),[0,0],[instance],["PSLVERR"],[[0,0]],[False,0])

			addConnection_from_to("adhoc",True,instance_m0,"i_paddr",[11,0],[instance],["PADDR"],[[11,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_pwrite",[0,0],[instance],["PWRITE"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_penable",[0,0],[instance],["PENABLE"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_m0,"i_pwdata",[31,0],[instance],["PWDATA"],[[31,0]],[False,0])

			addConnection_from_to("adhoc",False,instance_m0,"LDO_SPI_RESETn",[0,0],[instance],["SRESETn"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"LDO_SPI_SCLK",[0,0],[instance],["SCLK"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"LDO_SPI_MOSI",[0,0],[instance],["MOSI"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"LDO_SPI_APB_SEL",[0,0],[instance],["SPI_APB_SEL"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"LDO_VREF",[0,0],[instance],["VREF"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"LDO_REFCLK",[0,0],[instance],["CLK"],[[0,0]],[False,0])

			if not tag_top_PCLK:
				addConnection_from_to("clock",False,instance_m0,"PCLK",[0,0],[instance],["PCLK"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PCLK,False,[instance],["PCLK"],[[0,0]])

			if not tag_top_PRESETn:
				addConnection_from_to("reset",False,instance_m0,"PRESETn",[0,0],[instance],["PRESETn"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PRESETn,False,[instance],["PRESETn"],[[0,0]])

			addConnection_from_to("adhoc",False,instance_ldo_mux,"LDO_SPI_"+str(ldo_number)+"_MISO",[0,0],[instance],["MISO"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_ldo_mux,"LDO_SPI_"+str(ldo_number)+"_SS",[0,0],[instance],["SS"],[[0,0]],[False,0])

		elif (generator == 'memory-gen'):
			#addConnection_from_to("apb",False,instance_slave,"APBM" + str(module_number),[0,0],[instance],["MEM_APBS"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSEL" + str(module_number+2),[0,0],[instance],["psel"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_slave,"PRDATA" + str(module_number+2),[31,0],[instance],["prdata"],[[31,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PREADY" + str(module_number+2),[0,0],[instance],["pready"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSLVERR" + str(module_number+2),[0,0],[instance],["pslverr"],[[0,0]],[False,0])

			addConnection_from_to("adhoc",True,instance_m0,"i_paddr",[13,0],[instance],["paddr"],[[11,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_pwrite",[0,0],[instance],["pwrite"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_penable",[0,0],[instance],["penable"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_m0,"i_pwdata",[31,0],[instance],["pwdata"],[[31,0]],[False,0])

			addConnection_from_to("adhoc",False,instance_m0,"MEM_DATA_REQ",[0,0],[instance],["DATA_REQ_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_WE",[0,0],[instance],["WE_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_TEST_MODE",[0,0],[instance],["TEST_MODE_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_CLK_IN",[0,0],[instance],["CLK_IN_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_RESET",[0,0],[instance],["RESET_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_CLOCK",[0,0],[instance],["SPI_CLOCK_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_MOSI",[0,0],[instance],["SPI_MOSI_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_RST",[0,0],[instance],["SPI_RST_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_SCLK",[0,0],[instance],["SPI_SCLK_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_SS",[0,0],[instance],["SPI_SS_pad"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_DOUT32",[0,0],[instance],["DOUT32_PO"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"MEM_SPI_MISO",[0,0],[instance],["SPI_MISO_PO"],[[0,0]],[False,0])

			if not tag_top_PCLK:
				addConnection_from_to("clock",False,instance_m0,"PCLK",[0,0],[instance],["pclk"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PCLK,False,[instance],["pclk"],[[0,0]])

			if not tag_top_PRESETn:
				addConnection_from_to("reset",False,instance_m0,"PRESETn",[0,0],[instance],["presetn"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PRESETn,False,[instance],["presetn"],[[0,0]])

		elif (generator == 'pll-gen'):
			#addConnection_from_to("apb",False,instance_slave,"APBM" + str(module_number),[0,0],[instance],["PLL_APBS"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSEL" + str(module_number+2),[0,0],[instance],["PSEL"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_slave,"PRDATA" + str(module_number+2),[31,0],[instance],["PRDATA"],[[31,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PREADY" + str(module_number+2),[0,0],[instance],["PREADY"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSLVERR" + str(module_number+2),[0,0],[instance],["PSLVERR"],[[0,0]],[False,0])

			addConnection_from_to("clock",False,"toplevel","SYSCLKOUT" + str(module_number),[0,0],[instance],["CLKOUT"],[[0,0]],[False,0])

			addConnection_from_to("adhoc",True,instance_m0,"i_paddr",[11,0],[instance],["PADDR"],[[11,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_pwrite",[0,0],[instance],["PWRITE"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_penable",[0,0],[instance],["PENABLE"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_m0,"i_pwdata",[31,0],[instance],["PWDATA"],[[31,0]],[False,0])

			if not tag_top_PCLK:
				addConnection_from_to("clock",False,instance_m0,"PCLK",[0,0],[instance],["PCLK"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PCLK,False,[instance],["PCLK"],[[0,0]])

			if not tag_top_PRESETn:
				addConnection_from_to("reset",False,instance_m0,"PRESETn",[0,0],[instance],["PRESETn"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PRESETn,False,[instance],["PRESETn"],[[0,0]])

			addConnection_from_to("adhoc",False,instance_m0,"PLL_CLKREF"+str(pll_number),[0,0],[instance],["CLKREF"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"PLL_CLKOUT"+str(pll_number),[0,0],[instance],["CLK_OUT"],[[0,0]],[False,0])

		elif (generator == 'temp-sense-gen'):
			#addConnection_from_to("apb",False,instance_slave,"APBM" + str(module_number),[0,0],[instance],["TEMP_APBS"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSEL" + str(module_number+2),[0,0],[instance],["PSEL"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_slave,"PRDATA" + str(module_number+2),[31,0],[instance],["PRDATA"],[[31,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PREADY" + str(module_number+2),[0,0],[instance],["PREADY"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_slave,"PSLVERR" + str(module_number+2),[0,0],[instance],["PSLVERR"],[[0,0]],[False,0])

			addConnection_from_to("clock",False,instance_m0,"TEMP_" + str(temp_sense_number) + "_CLKOUT",[0,0],[instance],["CLKOUT"],[[0,0]],[False,0])

			addConnection_from_to("adhoc",True,instance_m0,"i_paddr",[11,0],[instance],["PADDR"],[[11,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_pwrite",[0,0],[instance],["PWRITE"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",False,instance_m0,"i_penable",[0,0],[instance],["PENABLE"],[[0,0]],[False,0])
			addConnection_from_to("adhoc",True,instance_m0,"i_pwdata",[31,0],[instance],["PWDATA"],[[31,0]],[False,0])

			if not tag_top_PCLK:
				addConnection_from_to("clock",False,instance_m0,"PCLK",[0,0],[instance],["PCLK"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PCLK,False,[instance],["PCLK"],[[0,0]])

			if not tag_top_PRESETn:
				addConnection_from_to("reset",False,instance_m0,"PRESETn",[0,0],[instance],["PRESETn"],[[0,0]],[False,0])
			else:
				addConnection_to(connection_top_PRESETn,False,[instance],["PRESETn"],[[0,0]])

	else:
		return

	last_PRESETn = -1
	last_PCLK = -1
	last_PADDR = -1
	last_PENABLE = -1
	last_PWRITE = -1
	last_PWDATA = -1
	last_SYSCLKOUT = -1
	index = []
	counter = 0

	for connection in connections:
		if "from" in connection:
			if "port" in connection["from"]:
				if connection["from"]["port"] == "PRESETn":
					index.append(counter)
					last_PRESETn = counter
				elif connection["from"]["port"] == "PCLK":
					index.append(counter)
					last_PCLK = counter
				elif connection["from"]["port"] == "PADDR" and connection["from"]["range"]["max"] == 11 and connection["from"]["range"]["min"] == 8:
					index.append(counter)
					last_PADDR = counter
				elif connection["from"]["port"] == "PENABLE":
					index.append(counter)
					last_PENABLE = counter
				elif connection["from"]["port"] == "PWRITE":
					index.append(counter)
					last_PWRITE = counter
				elif connection["from"]["port"] == "PWDATA":
					index.append(counter)
					last_PWDATA = counter
		counter += 1

	counter = 0
	last = [last_PRESETn,last_PCLK,last_PADDR,last_PENABLE,last_PWRITE,last_PWDATA]

	for i in index:
		if i not in last:
			del(connections[i - counter])
			counter += 1



	if module_number == total_gen_numbers:
		# addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_ahp],["HSEL"],[[0,0]],[True,1])

		# addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_ahp],["HREADY"],[[0,0]],[True,1])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_m0],["ext_HREADY"],[[0,0]],[True,1])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_m0],["NRST"],[[0,0]],[True,1])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_m0],["TDI"],[[0,0]],[True,1])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_m0],["TDO"],[[0,0]],[True,"open"])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_m0],["PCLKG"],[[0,0]],[True,"open"])

		# addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_ahp],["HREADYOUT"],[[0,0]],[True,"open"])

		# addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_ahp],["PSTRB"],[[0,0]],[True,"open"])

		# addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_ahp],["PPROT"],[[0,0]],[True,"open"])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_slave],["PSLVERR.*|PRDATA.*"],[[0,0]],[True,0])

		addConnection_from_to("tieoff",False,"None","None",[0,0],[instance_slave],["PSEL.*"],[[0,0]],[True,"open"])

		connection_tie_slave_PREADY = {}
		connection_tie_slave_PREADY["type"] = "tieoff"

		connection_from_tie_slave_PREADY = {}
		connection_from_tie_slave_PREADY["value"] = 1
		connection_tie_slave_PREADY["from"] = connection_from_tie_slave_PREADY

		connection_to_tie_slave_PREADY_list = []
		for i in range(0,16):
			connection_to_tie_slave_PREADY_dict = {}
			connection_to_tie_slave_PREADY_dict["instance"] = instance_slave
			connection_to_tie_slave_PREADY_dict["port"] = "PREADY" + str(i)
			connection_to_tie_slave_PREADY_list.append(connection_to_tie_slave_PREADY_dict)

		connection_tie_slave_PREADY["to"] = connection_to_tie_slave_PREADY_list
		connections.append(connection_tie_slave_PREADY)

	designJson["connections"] = connections
	with open(designDir, "w") as f:
		json.dump(designJson, f, indent=True)