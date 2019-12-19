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

def connectionGen(generator,instance,module_number,designJson,designDir):

	with open(designDir, "r") as f:
		designJson = json.load(f)

	total_gen_numbers = -1

	for module in designJson["modules"]:
		if module["generator"] == "cmsdk_apb_slave_mux_rtl":
			module_slave = module["module_name"]
			instance_slave = module["instance_name"]

		elif module["generator"] == "cmsdk_ahb_to_apb_rtl":
			module_ahp = module["module_name"]
			instance_ahp = module["instance_name"]

		elif module["generator"] == "fasoc_m0mcu_rtl":
			module_m0 = module["module_name"]
			instance_m0 = module["instance_name"]

		else:
			total_gen_numbers += 1


	if module_number == 0:
		if "connections" in designJson:
			del designJson["connections"]
		connections = []

		connection_m0_ahp_M0MCU_AHBM = {}
		connection_m0_ahp_M0MCU_AHBM["type"] = "ahb"

		connection_from_m0_ahp_M0MCU_AHBM = {}
		connection_from_m0_ahp_M0MCU_AHBM["instance"] = instance_m0
		connection_from_m0_ahp_M0MCU_AHBM["port"] = "M0MCU_AHBM"
		connection_m0_ahp_M0MCU_AHBM["from"] = connection_from_m0_ahp_M0MCU_AHBM

		connection_to_m0_ahp_AHB_S_list = []
		connection_to_m0_ahp_AHB_S_dict = {}
		connection_to_m0_ahp_AHB_S_dict["instance"] = instance_ahp
		connection_to_m0_ahp_AHB_S_dict["port"] = "AHB_S"
		connection_to_m0_ahp_AHB_S_list.append(connection_to_m0_ahp_AHB_S_dict)
		connection_m0_ahp_M0MCU_AHBM["to"] = connection_to_m0_ahp_AHB_S_list
		connections.append(connection_m0_ahp_M0MCU_AHBM)



		connection_ahp_slave_APB_M = {}
		connection_ahp_slave_APB_M["type"] = "apb"

		connection_from_ahp_slave_APB_M = {}
		connection_from_ahp_slave_APB_M["instance"] = instance_ahp
		connection_from_ahp_slave_APB_M["port"] = "APB_M"
		connection_ahp_slave_APB_M["from"] = connection_from_ahp_slave_APB_M

		connection_to_ahp_slave_APBS_list = []
		connection_to_ahp_slave_APBS_dict = {}
		connection_to_ahp_slave_APBS_dict["instance"] = instance_slave
		connection_to_ahp_slave_APBS_dict["port"] = "APBS"
		connection_to_ahp_slave_APBS_list.append(connection_to_ahp_slave_APBS_dict)
		connection_ahp_slave_APB_M["to"] = connection_to_ahp_slave_APBS_list
		connections.append(connection_ahp_slave_APB_M)



		connection_top_m0_XTAL1 = {}
		connection_top_m0_XTAL1["type"] = "clock"

		connection_from_top_m0_XTAL1 = {}
		connection_from_top_m0_XTAL1["instance"] = "toplevel"
		connection_from_top_m0_XTAL1["port"] = "XTAL1"
		connection_top_m0_XTAL1["from"] = connection_from_top_m0_XTAL1

		connection_to_top_m0_XTAL1_list = []
		connection_to_top_m0_XTAL1_dict = {}
		connection_to_top_m0_XTAL1_dict["instance"] = instance_m0
		connection_to_top_m0_XTAL1_dict["port"] = "XTAL1"
		connection_to_top_m0_XTAL1_list.append(connection_to_top_m0_XTAL1_dict)
		connection_top_m0_XTAL1["to"] = connection_to_top_m0_XTAL1_list
		connections.append(connection_top_m0_XTAL1)



		connection_m0_top_XTAL2 = {}
		connection_m0_top_XTAL2["type"] = "clock"

		connection_from_m0_top_XTAL2 = {}
		connection_from_m0_top_XTAL2["instance"] = instance_m0
		connection_from_m0_top_XTAL2["port"] = "XTAL2"
		connection_m0_top_XTAL2["from"] = connection_from_m0_top_XTAL2

		connection_to_m0_top_XTAL2_list = []
		connection_to_m0_top_XTAL2_dict = {}
		connection_to_m0_top_XTAL2_dict["instance"] = "toplevel"
		connection_to_m0_top_XTAL2_dict["port"] = "XTAL2"
		connection_to_m0_top_XTAL2_list.append(connection_to_m0_top_XTAL2_dict)
		connection_m0_top_XTAL2["to"] = connection_to_m0_top_XTAL2_list
		connections.append(connection_m0_top_XTAL2)



		connection_top_m0_nTRST = {}
		connection_top_m0_nTRST["type"] = "reset"

		connection_from_top_m0_nTRST = {}
		connection_from_top_m0_nTRST["instance"] = "toplevel"
		connection_from_top_m0_nTRST["port"] = "nTRST"
		connection_top_m0_nTRST["from"] = connection_from_top_m0_nTRST

		connection_to_top_m0_nTRST_list = []
		connection_to_top_m0_nTRST_dict = {}
		connection_to_top_m0_nTRST_dict["instance"] = instance_m0
		connection_to_top_m0_nTRST_dict["port"] = "nTRST"
		connection_to_top_m0_nTRST_list.append(connection_to_top_m0_nTRST_dict)
		connection_top_m0_nTRST["to"] = connection_to_top_m0_nTRST_list
		connections.append(connection_top_m0_nTRST)



		connection_m0_top_P0 = {}
		connection_m0_top_P0["type"] = "adhoc"

		connection_from_m0_top_P0 = {}
		connection_from_m0_top_P0["instance"] = instance_m0
		connection_from_m0_top_P0["port"] = "P0"
		connection_from_m0_top_P0["range"] = {}
		connection_from_m0_top_P0["range"]["max"] = 15
		connection_from_m0_top_P0["range"]["min"] = 0
		connection_m0_top_P0["from"] = connection_from_m0_top_P0

		connection_to_m0_top_P0_list = []
		connection_to_m0_top_P0_dict = {}
		connection_to_m0_top_P0_dict["instance"] = "toplevel"
		connection_to_m0_top_P0_dict["port"] = "P0"
		connection_to_m0_top_P0_dict["range"] = {}
		connection_to_m0_top_P0_dict["range"]["max"] = 15
		connection_to_m0_top_P0_dict["range"]["min"] = 0
		connection_to_m0_top_P0_list.append(connection_to_m0_top_P0_dict)
		connection_m0_top_P0["to"] = connection_to_m0_top_P0_list
		connections.append(connection_m0_top_P0)



		connection_m0_top_P1 = {}
		connection_m0_top_P1["type"] = "adhoc"

		connection_from_m0_top_P1 = {}
		connection_from_m0_top_P1["instance"] = instance_m0
		connection_from_m0_top_P1["port"] = "P1"
		connection_from_m0_top_P1["range"] = {}
		connection_from_m0_top_P1["range"]["max"] = 15
		connection_from_m0_top_P1["range"]["min"] = 0
		connection_m0_top_P1["from"] = connection_from_m0_top_P1

		connection_to_m0_top_P1_list = []
		connection_to_m0_top_P1_dict = {}
		connection_to_m0_top_P1_dict["instance"] = "toplevel"
		connection_to_m0_top_P1_dict["port"] = "P1"
		connection_to_m0_top_P1_dict["range"] = {}
		connection_to_m0_top_P1_dict["range"]["max"] = 15
		connection_to_m0_top_P1_dict["range"]["min"] = 0
		connection_to_m0_top_P1_list.append(connection_to_m0_top_P1_dict)
		connection_m0_top_P1["to"] = connection_to_m0_top_P1_list
		connections.append(connection_m0_top_P1)

		connection_m0_top_SWDIOTMS = {}
		connection_m0_top_SWDIOTMS["type"] = "adhoc"

		connection_from_m0_top_SWDIOTMS = {}
		connection_from_m0_top_SWDIOTMS["instance"] = instance_m0
		connection_from_m0_top_SWDIOTMS["port"] = "SWDIOTMS"
		connection_m0_top_SWDIOTMS["from"] = connection_from_m0_top_SWDIOTMS

		connection_to_m0_top_SWDIOTMS_list = []
		connection_to_m0_top_SWDIOTMS_dict = {}
		connection_to_m0_top_SWDIOTMS_dict["instance"] = "toplevel"
		connection_to_m0_top_SWDIOTMS_dict["port"] = "SWDIOTMS"
		connection_to_m0_top_SWDIOTMS_list.append(connection_to_m0_top_SWDIOTMS_dict)
		connection_m0_top_SWDIOTMS["to"] = connection_to_m0_top_SWDIOTMS_list
		connections.append(connection_m0_top_SWDIOTMS)



		connection_top_m0_SWCLKTCK = {}
		connection_top_m0_SWCLKTCK["type"] = "adhoc"

		connection_from_top_m0_SWCLKTCK = {}
		connection_from_top_m0_SWCLKTCK["instance"] = "toplevel"
		connection_from_top_m0_SWCLKTCK["port"] = "SWCLKTCK"
		connection_top_m0_SWCLKTCK["from"] = connection_from_top_m0_SWCLKTCK

		connection_to_top_m0_SWCLKTCK_list = []
		connection_to_top_m0_SWCLKTCK_dict = {}
		connection_to_top_m0_SWCLKTCK_dict["instance"] = instance_m0
		connection_to_top_m0_SWCLKTCK_dict["port"] = "SWCLKTCK"
		connection_to_top_m0_SWCLKTCK_list.append(connection_to_top_m0_SWCLKTCK_dict)
		connection_top_m0_SWCLKTCK["to"] = connection_to_top_m0_SWCLKTCK_list
		connections.append(connection_top_m0_SWCLKTCK)



		connection_top_m0_SYSCLK = {}
		connection_top_m0_SYSCLK["type"] = "clock"

		connection_from_top_m0_SYSCLK = {}
		connection_from_top_m0_SYSCLK["instance"] = "toplevel"
		connection_from_top_m0_SYSCLK["port"] = "SYSCLK"
		connection_top_m0_SYSCLK["from"] = connection_from_top_m0_SYSCLK

		connection_to_top_m0_SYSCLK_list = []
		connection_to_top_m0_ext_HCLK_dict = {}
		connection_to_top_m0_ext_HCLK_dict["instance"] = instance_m0
		connection_to_top_m0_ext_HCLK_dict["port"] = "ext_HCLK"
		connection_to_top_m0_SYSCLK_list.append(connection_to_top_m0_ext_HCLK_dict)

		connection_to_top_m0_HCLK_dict = {}
		connection_to_top_m0_HCLK_dict["instance"] = instance_ahp
		connection_to_top_m0_HCLK_dict["port"] = "HCLK"
		connection_to_top_m0_SYSCLK_list.append(connection_to_top_m0_HCLK_dict)

		connection_to_top_m0_PCLK_dict = {}
		connection_to_top_m0_PCLK_dict["instance"] = instance_m0
		connection_to_top_m0_PCLK_dict["port"] = "PCLK"
		connection_to_top_m0_SYSCLK_list.append(connection_to_top_m0_PCLK_dict)
		connection_top_m0_SYSCLK["to"] = connection_to_top_m0_SYSCLK_list
		connections.append(connection_top_m0_SYSCLK)



		connection_top_m0_SYSRESETN = {}
		connection_top_m0_SYSRESETN["type"] = "reset"

		connection_from_top_m0_SYSRESETN = {}
		connection_from_top_m0_SYSRESETN["instance"] = "toplevel"
		connection_from_top_m0_SYSRESETN["port"] = "SYSRESETN"
		connection_top_m0_SYSRESETN["from"] = connection_from_top_m0_SYSRESETN

		connection_to_top_m0_SYSRESETN_list = []
		connection_to_top_m0_HRESETn_dict = {}
		connection_to_top_m0_HRESETn_dict["instance"] = instance_ahp
		connection_to_top_m0_HRESETn_dict["port"] = "HRESETn"
		connection_to_top_m0_SYSRESETN_list.append(connection_to_top_m0_HRESETn_dict)

		connection_to_top_m0_ext_HRESETn_dict = {}
		connection_to_top_m0_ext_HRESETn_dict["instance"] = instance_m0
		connection_to_top_m0_ext_HRESETn_dict["port"] = "ext_HRESETn"
		connection_to_top_m0_SYSRESETN_list.append(connection_to_top_m0_ext_HRESETn_dict)

		connection_to_top_m0_PRESETn_dict = {}
		connection_to_top_m0_PRESETn_dict["instance"] = instance_m0
		connection_to_top_m0_PRESETn_dict["port"] = "PRESETn"
		connection_to_top_m0_SYSRESETN_list.append(connection_to_top_m0_PRESETn_dict)
		connection_top_m0_SYSRESETN["to"] = connection_to_top_m0_SYSRESETN_list
		connections.append(connection_top_m0_SYSRESETN)



		connection_m0_ahp_APBACTIVE = {}
		connection_m0_ahp_APBACTIVE["type"] = "adhoc"

		connection_from_m0_ahp_APBACTIVE = {}
		connection_from_m0_ahp_APBACTIVE["instance"] = instance_m0
		connection_from_m0_ahp_APBACTIVE["port"] = "APBACTIVE"
		connection_m0_ahp_APBACTIVE["from"] = connection_from_m0_ahp_APBACTIVE

		connection_to_m0_ahp_APBACTIVE_list = []
		connection_to_m0_ahp_APBACTIVE_dict = {}
		connection_to_m0_ahp_APBACTIVE_dict["instance"] = instance_ahp
		connection_to_m0_ahp_APBACTIVE_dict["port"] = "APBACTIVE"
		connection_to_m0_ahp_APBACTIVE_list.append(connection_to_m0_ahp_APBACTIVE_dict)
		connection_m0_ahp_APBACTIVE["to"] = connection_to_m0_ahp_APBACTIVE_list
		connections.append(connection_m0_ahp_APBACTIVE)



		connection_ahp_m0_PCLKEN = {}
		connection_ahp_m0_PCLKEN["type"] = "adhoc"

		connection_from_ahp_m0_PCLKEN = {}
		connection_from_ahp_m0_PCLKEN["instance"] = instance_ahp
		connection_from_ahp_m0_PCLKEN["port"] = "PCLKEN"
		connection_ahp_m0_PCLKEN["from"] = connection_from_ahp_m0_PCLKEN

		connection_to_ahp_m0_PCLKEN_list = []
		connection_to_ahp_m0_PCLKEN_dict = {}
		connection_to_ahp_m0_PCLKEN_dict["instance"] = instance_m0
		connection_to_ahp_m0_PCLKEN_dict["port"] = "PCLKEN"
		connection_to_ahp_m0_PCLKEN_list.append(connection_to_ahp_m0_PCLKEN_dict)
		connection_ahp_m0_PCLKEN["to"] = connection_to_ahp_m0_PCLKEN_list
		connections.append(connection_ahp_m0_PCLKEN)



		connection_ahp_slave_PADDR = {}
		connection_ahp_slave_PADDR["type"] = "adhoc"

		connection_from_ahp_slave_PADDR = {}
		connection_from_ahp_slave_PADDR["instance"] = instance_ahp
		connection_from_ahp_slave_PADDR["port"] = "PADDR"
		connection_from_ahp_slave_PADDR["range"] = {}
		connection_from_ahp_slave_PADDR["range"]["max"] = 15
		connection_from_ahp_slave_PADDR["range"]["min"] = 12
		connection_ahp_slave_PADDR["from"] = connection_from_ahp_slave_PADDR

		connection_to_ahp_slave_DECODE4BIT_list = []
		connection_to_ahp_slave_DECODE4BIT_dict = {}
		connection_to_ahp_slave_DECODE4BIT_dict["instance"] = instance_slave
		connection_to_ahp_slave_DECODE4BIT_dict["port"] = "DECODE4BIT"
		connection_to_ahp_slave_DECODE4BIT_dict["range"] = {}
		connection_to_ahp_slave_DECODE4BIT_dict["range"]["max"] = 3
		connection_to_ahp_slave_DECODE4BIT_dict["range"]["min"] = 0
		connection_to_ahp_slave_DECODE4BIT_list.append(connection_to_ahp_slave_DECODE4BIT_dict)
		connection_ahp_slave_PADDR["to"] = connection_to_ahp_slave_DECODE4BIT_list
		connections.append(connection_ahp_slave_PADDR)



		designJson["connections"] = connections
	if "connections" in designJson:
		connections = designJson["connections"]
		#tag_top_pll_SYSCLKOUT = False
		tag_top_SYSCLK = False
		tag_top_SYSRESETN = False
		tag_ahp_PADDR_11_8 = False
		tag_ahp_PENABLE = False
		tag_ahp_PWRITE = False
		tag_ahp_PWDATA = False

		for connection in connections:
			if "from" in connection:
				if "port" in connection["from"]:

					if connection["from"]["port"] == "SYSRESETN":
						tag_top_SYSRESETN = True
						connection_top_SYSRESETN = connection

					elif connection["from"]["port"] == "SYSCLK":
						tag_top_SYSCLK = True
						connection_top_SYSCLK = connection

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
			if tag_top_SYSCLK:
				connection_to_top_ldo_PCLK_list = connection_top_SYSCLK["to"]
				connection_to_top_ldo_PCLK_dict = {}
				connection_to_top_ldo_PCLK_dict["instance"] = instance
				connection_to_top_ldo_PCLK_dict["port"] = "PCLK"
				connection_to_top_ldo_PCLK_list.append(connection_to_top_ldo_PCLK_dict)
				connection_top_SYSCLK["to"] = connection_to_top_ldo_PCLK_list
				connections.append(connection_top_SYSCLK)



			if tag_top_SYSRESETN:
				connection_to_top_ldo_SYSRESETN_list = connection_top_SYSRESETN["to"]
				connection_to_top_ldo_SYSRESETN_dict = {}
				connection_to_top_ldo_SYSRESETN_dict["instance"] = instance
				connection_to_top_ldo_SYSRESETN_dict["port"] = "reset"
				connection_to_top_ldo_SYSRESETN_list.append(connection_to_top_ldo_SYSRESETN_dict)
				connection_top_SYSRESETN["to"] = connection_to_top_ldo_SYSRESETN_list
				connections.append(connection_top_SYSRESETN)

		elif (generator == 'memory-gen'):
			connection_slave_mem_APBM = {}
			connection_slave_mem_APBM["type"] = "apb"

			connection_from_slave_mem_APBM = {}
			connection_from_slave_mem_APBM["instance"] = instance_slave
			connection_from_slave_mem_APBM["port"] = "APBM" + str(1 + module_number)
			connection_slave_mem_APBM["from"] = connection_from_slave_mem_APBM

			connection_to_slave_mem_MEM_APBS_list = []
			connection_to_slave_mem_MEM_APBS_dict = {}
			connection_to_slave_mem_MEM_APBS_dict["instance"] = instance
			connection_to_slave_mem_MEM_APBS_dict["port"] = "MEM_APBS"
			connection_to_slave_mem_MEM_APBS_list.append(connection_to_slave_mem_MEM_APBS_dict)
			connection_slave_mem_APBM["to"] = connection_to_slave_mem_MEM_APBS_list
			connections.append(connection_slave_mem_APBM)



			if tag_top_SYSCLK:
				connection_to_top_mem_pclk_list = connection_top_SYSCLK["to"]
				connection_to_top_mem_pclk_dict = {}
				connection_to_top_mem_pclk_dict["instance"] = instance
				connection_to_top_mem_pclk_dict["port"] = "pclk"
				connection_to_top_mem_pclk_list.append(connection_to_top_mem_pclk_dict)
				connection_top_SYSCLK["to"] = connection_to_top_mem_pclk_list
				connections.append(connection_top_SYSCLK)



			if tag_top_SYSRESETN:
				connection_to_top_mem_SYSRESETN_list = connection_top_SYSRESETN["to"]
				connection_to_top_mem_SYSRESETN_dict = {}
				connection_to_top_mem_SYSRESETN_dict["instance"] = instance
				connection_to_top_mem_SYSRESETN_dict["port"] = "presetn"
				connection_to_top_mem_SYSRESETN_list.append(connection_to_top_mem_SYSRESETN_dict)
				connection_top_SYSRESETN["to"] = connection_to_top_mem_SYSRESETN_list
				connections.append(connection_top_SYSRESETN)



			if not tag_ahp_PADDR_11_8:
				connection_ahp_PADDR_11_8 = {}
				connection_ahp_PADDR_11_8["type"] = "adhoc"

				connection_from_ahp_PADDR_11_8 = {}
				connection_from_ahp_PADDR_11_8["instance"] = instance_ahp
				connection_from_ahp_PADDR_11_8["port"] = "PADDR"
				connection_from_ahp_PADDR_11_8["range"] = {}
				connection_from_ahp_PADDR_11_8["range"]["max"] = 11
				connection_from_ahp_PADDR_11_8["range"]["min"] = 8
				connection_ahp_PADDR_11_8["from"] = connection_from_ahp_PADDR_11_8

				connection_to_ahp_PADDR_11_8_list = []
				connection_to_ahp_PADDR_11_8_dict = {}
				connection_to_ahp_PADDR_11_8_dict["instance"] = instance
				connection_to_ahp_PADDR_11_8_dict["port"] = "paddr"
				connection_to_ahp_PADDR_11_8_dict["range"] = {}
				connection_to_ahp_PADDR_11_8_dict["range"]["max"] = 3
				connection_to_ahp_PADDR_11_8_dict["range"]["min"] = 0
				connection_to_ahp_PADDR_11_8_list.append(connection_to_ahp_PADDR_11_8_dict)
				connection_ahp_PADDR_11_8["to"] = connection_to_ahp_PADDR_11_8_list
				connections.append(connection_ahp_PADDR_11_8)

			else:
				connection_to_ahp_PADDR_11_8_list = connection_ahp_PADDR_11_8["to"]
				connection_to_ahp_PADDR_11_8_dict = {}
				connection_to_ahp_PADDR_11_8_dict["instance"] = instance
				connection_to_ahp_PADDR_11_8_dict["port"] = "paddr"
				connection_to_ahp_PADDR_11_8_dict["range"] = {}
				connection_to_ahp_PADDR_11_8_dict["range"]["max"] = 3
				connection_to_ahp_PADDR_11_8_dict["range"]["min"] = 0
				connection_to_ahp_PADDR_11_8_list.append(connection_to_ahp_PADDR_11_8_dict)
				connection_ahp_PADDR_11_8["to"] = connection_to_ahp_PADDR_11_8_list
				connections.append(connection_ahp_PADDR_11_8)



			if not tag_ahp_PENABLE:
				connection_ahp_PENABLE = {}
				connection_ahp_PENABLE["type"] = "adhoc"

				connection_from_ahp_PENABLE = {}
				connection_from_ahp_PENABLE["instance"] = instance_ahp
				connection_from_ahp_PENABLE["port"] = "PENABLE"
				connection_ahp_PENABLE["from"] = connection_from_ahp_PENABLE

				connection_to_ahp_PENABLE_list = []
				connection_to_ahp_PENABLE_dict = {}
				connection_to_ahp_PENABLE_dict["instance"] = instance
				connection_to_ahp_PENABLE_dict["port"] = "penable"
				connection_to_ahp_PENABLE_list.append(connection_to_ahp_PENABLE_dict)
				connection_ahp_PENABLE["to"] = connection_to_ahp_PENABLE_list
				connections.append(connection_ahp_PENABLE)

			else:
				connection_to_ahp_PENABLE_list = connection_ahp_PENABLE["to"]
				connection_to_ahp_PENABLE_dict = {}
				connection_to_ahp_PENABLE_dict["instance"] = instance
				connection_to_ahp_PENABLE_dict["port"] = "penable"
				connection_to_ahp_PENABLE_list.append(connection_to_ahp_PENABLE_dict)
				connection_ahp_PENABLE["to"] = connection_to_ahp_PENABLE_list
				connections.append(connection_ahp_PENABLE)



			if not tag_ahp_PWRITE:
				connection_ahp_PWRITE = {}
				connection_ahp_PWRITE["type"] = "adhoc"

				connection_from_ahp_PWRITE = {}
				connection_from_ahp_PWRITE["instance"] = instance_ahp
				connection_from_ahp_PWRITE["port"] = "PWRITE"
				connection_ahp_PWRITE["from"] = connection_from_ahp_PWRITE

				connection_to_ahp_PWRITE_list = []
				connection_to_ahp_PWRITE_dict = {}
				connection_to_ahp_PWRITE_dict["instance"] = instance
				connection_to_ahp_PWRITE_dict["port"] = "pwrite"
				connection_to_ahp_PWRITE_list.append(connection_to_ahp_PWRITE_dict)
				connection_ahp_PWRITE["to"] = connection_to_ahp_PWRITE_list
				connections.append(connection_ahp_PWRITE)

			else:
				connection_to_ahp_PWRITE_list = connection_ahp_PWRITE["to"]
				connection_to_ahp_PWRITE_dict = {}
				connection_to_ahp_PWRITE_dict["instance"] = instance
				connection_to_ahp_PWRITE_dict["port"] = "pwrite"
				connection_to_ahp_PWRITE_list.append(connection_to_ahp_PWRITE_dict)
				connection_ahp_PWRITE["to"] = connection_to_ahp_PWRITE_list
				connections.append(connection_ahp_PWRITE)



			if not tag_ahp_PWDATA:
				connection_ahp_PWDATA = {}
				connection_ahp_PWDATA["type"] = "adhoc"

				connection_from_ahp_PWDATA = {}
				connection_from_ahp_PWDATA["instance"] = instance_ahp
				connection_from_ahp_PWDATA["port"] = "PWDATA"
				connection_ahp_PWDATA["from"] = connection_from_ahp_PWDATA

				connection_to_ahp_PWDATA_list = []
				connection_to_ahp_PWDATA_dict = {}
				connection_to_ahp_PWDATA_dict["instance"] = instance
				connection_to_ahp_PWDATA_dict["port"] = "pwdata"
				connection_to_ahp_PWDATA_list.append(connection_to_ahp_PWDATA_dict)
				connection_ahp_PWDATA["to"] = connection_to_ahp_PWDATA_list
				connections.append(connection_ahp_PWDATA)

			else:
				connection_to_ahp_PWDATA_list = connection_ahp_PWDATA["to"]
				connection_to_ahp_PWDATA_dict = {}
				connection_to_ahp_PWDATA_dict["instance"] = instance
				connection_to_ahp_PWDATA_dict["port"] = "pwdata"
				connection_to_ahp_PWDATA_list.append(connection_to_ahp_PWDATA_dict)
				connection_ahp_PWDATA["to"] = connection_to_ahp_PWDATA_list
				connections.append(connection_ahp_PWDATA)



		elif (generator == 'pll-gen'):
			connection_slave_pll_APBM = {}
			connection_slave_pll_APBM["type"] = "apb"

			connection_from_slave_pll_APBM = {}
			connection_from_slave_pll_APBM["instance"] = instance_slave
			connection_from_slave_pll_APBM["port"] = "APBM" + str(1 + module_number)
			connection_slave_pll_APBM["from"] = connection_from_slave_pll_APBM

			connection_to_slave_pll_PLL_APBS_list = []
			connection_to_slave_pll_PLL_APBS_dict = {}
			connection_to_slave_pll_PLL_APBS_dict["instance"] = instance
			connection_to_slave_pll_PLL_APBS_dict["port"] = "PLL_APBS"
			connection_to_slave_pll_PLL_APBS_list.append(connection_to_slave_pll_PLL_APBS_dict)
			connection_slave_pll_APBM["to"] = connection_to_slave_pll_PLL_APBS_list
			connections.append(connection_slave_pll_APBM)



			connection_top_pll_SYSCLKOUT = {}
			connection_top_pll_SYSCLKOUT["type"] = "clock"

			connection_from_top_pll_SYSCLKOUT = {}
			connection_from_top_pll_SYSCLKOUT["instance"] = "toplevel"
			connection_from_top_pll_SYSCLKOUT["port"] = "SYSCLKOUT" + str(module_number)
			connection_top_pll_SYSCLKOUT["from"] = connection_from_top_pll_SYSCLKOUT

			connection_to_top_pll_CLKOUT_list = []
			connection_to_top_pll_CLKOUT_dict = {}
			connection_to_top_pll_CLKOUT_dict["instance"] = instance
			connection_to_top_pll_CLKOUT_dict["port"] = "CLKOUT"
			connection_to_top_pll_CLKOUT_list.append(connection_to_top_pll_CLKOUT_dict)
			connection_top_pll_SYSCLKOUT["to"] = connection_to_top_pll_CLKOUT_list
			connections.append(connection_top_pll_SYSCLKOUT)



			if tag_top_SYSCLK:
				connection_to_top_pll_PCLK_list = connection_top_SYSCLK["to"]
				connection_to_top_pll_PCLK_dict = {}
				connection_to_top_pll_PCLK_dict["instance"] = instance
				connection_to_top_pll_PCLK_dict["port"] = "PCLK"
				connection_to_top_pll_PCLK_list.append(connection_to_top_pll_PCLK_dict)
				connection_top_SYSCLK["to"] = connection_to_top_pll_PCLK_list
				connections.append(connection_top_SYSCLK)



			if tag_top_SYSRESETN:
				connection_to_top_pll_SYSRESETN_list = connection_top_SYSRESETN["to"]
				connection_to_top_pll_SYSRESETN_dict = {}
				connection_to_top_pll_SYSRESETN_dict["instance"] = instance
				connection_to_top_pll_SYSRESETN_dict["port"] = "PRESETn"
				connection_to_top_pll_SYSRESETN_list.append(connection_to_top_pll_SYSRESETN_dict)
				connection_top_SYSRESETN["to"] = connection_to_top_pll_SYSRESETN_list
				connections.append(connection_top_SYSRESETN)



			if not tag_ahp_PADDR_11_8:
				connection_ahp_PADDR_11_8 = {}
				connection_ahp_PADDR_11_8["type"] = "adhoc"

				connection_from_ahp_PADDR_11_8 = {}
				connection_from_ahp_PADDR_11_8["instance"] = instance_ahp
				connection_from_ahp_PADDR_11_8["port"] = "PADDR"
				connection_from_ahp_PADDR_11_8["range"] = {}
				connection_from_ahp_PADDR_11_8["range"]["max"] = 11
				connection_from_ahp_PADDR_11_8["range"]["min"] = 8
				connection_ahp_PADDR_11_8["from"] = connection_from_ahp_PADDR_11_8

				connection_to_ahp_PADDR_11_8_list = []
				connection_to_ahp_PADDR_11_8_dict = {}
				connection_to_ahp_PADDR_11_8_dict["instance"] = instance
				connection_to_ahp_PADDR_11_8_dict["port"] = "PADDR"
				connection_to_ahp_PADDR_11_8_dict["range"] = {}
				connection_to_ahp_PADDR_11_8_dict["range"]["max"] = 3
				connection_to_ahp_PADDR_11_8_dict["range"]["min"] = 0
				connection_to_ahp_PADDR_11_8_list.append(connection_to_ahp_PADDR_11_8_dict)
				connection_ahp_PADDR_11_8["to"] = connection_to_ahp_PADDR_11_8_list
				connections.append(connection_ahp_PADDR_11_8)

			else:
				connection_to_ahp_PADDR_11_8_list = connection_ahp_PADDR_11_8["to"]
				connection_to_ahp_PADDR_11_8_dict = {}
				connection_to_ahp_PADDR_11_8_dict["instance"] = instance
				connection_to_ahp_PADDR_11_8_dict["port"] = "PADDR"
				connection_to_ahp_PADDR_11_8_dict["range"] = {}
				connection_to_ahp_PADDR_11_8_dict["range"]["max"] = 3
				connection_to_ahp_PADDR_11_8_dict["range"]["min"] = 0
				connection_to_ahp_PADDR_11_8_list.append(connection_to_ahp_PADDR_11_8_dict)
				connection_ahp_PADDR_11_8["to"] = connection_to_ahp_PADDR_11_8_list
				connections.append(connection_ahp_PADDR_11_8)



			if not tag_ahp_PENABLE:
				connection_ahp_PENABLE = {}
				connection_ahp_PENABLE["type"] = "adhoc"

				connection_from_ahp_PENABLE = {}
				connection_from_ahp_PENABLE["instance"] = instance_ahp
				connection_from_ahp_PENABLE["port"] = "PENABLE"
				connection_ahp_PENABLE["from"] = connection_from_ahp_PENABLE

				connection_to_ahp_PENABLE_list = []
				connection_to_ahp_PENABLE_dict = {}
				connection_to_ahp_PENABLE_dict["instance"] = instance
				connection_to_ahp_PENABLE_dict["port"] = "PENABLE"
				connection_to_ahp_PENABLE_list.append(connection_to_ahp_PENABLE_dict)
				connection_ahp_PENABLE["to"] = connection_to_ahp_PENABLE_list
				connections.append(connection_ahp_PENABLE)

			else:
				connection_to_ahp_PENABLE_list = connection_ahp_PENABLE["to"]
				connection_to_ahp_PENABLE_dict = {}
				connection_to_ahp_PENABLE_dict["instance"] = instance
				connection_to_ahp_PENABLE_dict["port"] = "PENABLE"
				connection_to_ahp_PENABLE_list.append(connection_to_ahp_PENABLE_dict)
				connection_ahp_PENABLE["to"] = connection_to_ahp_PENABLE_list
				connections.append(connection_ahp_PENABLE)



			if not tag_ahp_PWRITE:
				connection_ahp_PWRITE = {}
				connection_ahp_PWRITE["type"] = "adhoc"

				connection_from_ahp_PWRITE = {}
				connection_from_ahp_PWRITE["instance"] = instance_ahp
				connection_from_ahp_PWRITE["port"] = "PWRITE"
				connection_ahp_PWRITE["from"] = connection_from_ahp_PWRITE

				connection_to_ahp_PWRITE_list = []
				connection_to_ahp_PWRITE_dict = {}
				connection_to_ahp_PWRITE_dict["instance"] = instance
				connection_to_ahp_PWRITE_dict["port"] = "PWRITE"
				connection_to_ahp_PWRITE_list.append(connection_to_ahp_PWRITE_dict)
				connection_ahp_PWRITE["to"] = connection_to_ahp_PWRITE_list
				connections.append(connection_ahp_PWRITE)

			else:
				connection_to_ahp_PWRITE_list = connection_ahp_PWRITE["to"]
				connection_to_ahp_PWRITE_dict = {}
				connection_to_ahp_PWRITE_dict["instance"] = instance
				connection_to_ahp_PWRITE_dict["port"] = "PWRITE"
				connection_to_ahp_PWRITE_list.append(connection_to_ahp_PWRITE_dict)
				connection_ahp_PWRITE["to"] = connection_to_ahp_PWRITE_list
				connections.append(connection_ahp_PWRITE)



			if not tag_ahp_PWDATA:
				connection_ahp_PWDATA = {}
				connection_ahp_PWDATA["type"] = "adhoc"

				connection_from_ahp_PWDATA = {}
				connection_from_ahp_PWDATA["instance"] = instance_ahp
				connection_from_ahp_PWDATA["port"] = "PWDATA"
				connection_ahp_PWDATA["from"] = connection_from_ahp_PWDATA

				connection_to_ahp_PWDATA_list = []
				connection_to_ahp_PWDATA_dict = {}
				connection_to_ahp_PWDATA_dict["instance"] = instance
				connection_to_ahp_PWDATA_dict["port"] = "PWDATA"
				connection_to_ahp_PWDATA_list.append(connection_to_ahp_PWDATA_dict)
				connection_ahp_PWDATA["to"] = connection_to_ahp_PWDATA_list
				connections.append(connection_ahp_PWDATA)

			else:
				connection_to_ahp_PWDATA_list = connection_ahp_PWDATA["to"]
				connection_to_ahp_PWDATA_dict = {}
				connection_to_ahp_PWDATA_dict["instance"] = instance
				connection_to_ahp_PWDATA_dict["port"] = "PWDATA"
				connection_to_ahp_PWDATA_list.append(connection_to_ahp_PWDATA_dict)
				connection_ahp_PWDATA["to"] = connection_to_ahp_PWDATA_list
				connections.append(connection_ahp_PWDATA)

	else:
		return

	last_SYSRESETN = -1
	last_SYSCLK = -1
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
				if connection["from"]["port"] == "SYSRESETN":
					index.append(counter)
					last_SYSRESETN = counter
				elif connection["from"]["port"] == "SYSCLK":
					index.append(counter)
					last_SYSCLK = counter
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
	last = [last_SYSRESETN,last_SYSCLK,last_PADDR,last_PENABLE,last_PWRITE,last_PWDATA]

	for i in index:
		if i not in last:
			del(connections[i - counter])
			counter += 1



	if module_number == total_gen_numbers:
		connection_tie_ahp_HSEL = {}
		connection_tie_ahp_HSEL["type"] = "tieoff"

		connection_from_tie_ahp_HSEL = {}
		connection_from_tie_ahp_HSEL["value"] = 1
		connection_tie_ahp_HSEL["from"] = connection_from_tie_ahp_HSEL

		connection_to_tie_ahp_HSEL_list = []
		connection_to_tie_ahp_HSEL_dict = {}
		connection_to_tie_ahp_HSEL_dict["instance"] = instance_ahp
		connection_to_tie_ahp_HSEL_dict["port"] = "HSEL"
		connection_to_tie_ahp_HSEL_list.append(connection_to_tie_ahp_HSEL_dict)
		connection_tie_ahp_HSEL["to"] = connection_to_tie_ahp_HSEL_list
		connections.append(connection_tie_ahp_HSEL)



		connection_tie_ahp_HREADY = {}
		connection_tie_ahp_HREADY["type"] = "tieoff"

		connection_from_tie_ahp_HREADY = {}
		connection_from_tie_ahp_HREADY["value"] = 1
		connection_tie_ahp_HREADY["from"] = connection_from_tie_ahp_HREADY

		connection_to_tie_ahp_HREADY_list = []
		connection_to_tie_ahp_HREADY_dict = {}
		connection_to_tie_ahp_HREADY_dict["instance"] = instance_ahp
		connection_to_tie_ahp_HREADY_dict["port"] = "HREADY"
		connection_to_tie_ahp_HREADY_list.append(connection_to_tie_ahp_HREADY_dict)
		connection_tie_ahp_HREADY["to"] = connection_to_tie_ahp_HREADY_list
		connections.append(connection_tie_ahp_HREADY)



		connection_tie_m0_ext_HREADY = {}
		connection_tie_m0_ext_HREADY["type"] = "tieoff"

		connection_from_tie_m0_ext_HREADY = {}
		connection_from_tie_m0_ext_HREADY["value"] = 1
		connection_tie_m0_ext_HREADY["from"] = connection_from_tie_m0_ext_HREADY

		connection_to_tie_m0_ext_HREADY_list = []
		connection_to_tie_m0_ext_HREADY_dict = {}
		connection_to_tie_m0_ext_HREADY_dict["instance"] = instance_m0
		connection_to_tie_m0_ext_HREADY_dict["port"] = "ext_HREADY"
		connection_to_tie_m0_ext_HREADY_list.append(connection_to_tie_m0_ext_HREADY_dict)
		connection_tie_m0_ext_HREADY["to"] = connection_to_tie_m0_ext_HREADY_list
		connections.append(connection_tie_m0_ext_HREADY)



		connection_tie_m0_NRST = {}
		connection_tie_m0_NRST["type"] = "tieoff"

		connection_from_tie_m0_NRST = {}
		connection_from_tie_m0_NRST["value"] = 1
		connection_tie_m0_NRST["from"] = connection_from_tie_m0_NRST

		connection_to_tie_m0_NRST_list = []
		connection_to_tie_m0_NRST_dict = {}
		connection_to_tie_m0_NRST_dict["instance"] = instance_m0
		connection_to_tie_m0_NRST_dict["port"] = "NRST"
		connection_to_tie_m0_NRST_list.append(connection_to_tie_m0_NRST_dict)
		connection_tie_m0_NRST["to"] = connection_to_tie_m0_NRST_list
		connections.append(connection_tie_m0_NRST)



		connection_tie_m0_TDI = {}
		connection_tie_m0_TDI["type"] = "tieoff"

		connection_from_tie_m0_TDI = {}
		connection_from_tie_m0_TDI["value"] = 1
		connection_tie_m0_TDI["from"] = connection_from_tie_m0_TDI

		connection_to_tie_m0_TDI_list = []
		connection_to_tie_m0_TDI_dict = {}
		connection_to_tie_m0_TDI_dict["instance"] = instance_m0
		connection_to_tie_m0_TDI_dict["port"] = "TDI"
		connection_to_tie_m0_TDI_list.append(connection_to_tie_m0_TDI_dict)
		connection_tie_m0_TDI["to"] = connection_to_tie_m0_TDI_list
		connections.append(connection_tie_m0_TDI)



		connection_tie_m0_TDO = {}
		connection_tie_m0_TDO["type"] = "tieoff"

		connection_from_tie_m0_TDO = {}
		connection_from_tie_m0_TDO["value"] = "open"
		connection_tie_m0_TDO["from"] = connection_from_tie_m0_TDO

		connection_to_tie_m0_TDO_list = []
		connection_to_tie_m0_TDO_dict = {}
		connection_to_tie_m0_TDO_dict["instance"] = instance_m0
		connection_to_tie_m0_TDO_dict["port"] = "TDO"
		connection_to_tie_m0_TDO_list.append(connection_to_tie_m0_TDO_dict)
		connection_tie_m0_TDO["to"] = connection_to_tie_m0_TDO_list
		connections.append(connection_tie_m0_TDO)



		connection_tie_m0_PCLKG = {}
		connection_tie_m0_PCLKG["type"] = "tieoff"

		connection_from_tie_m0_PCLKG = {}
		connection_from_tie_m0_PCLKG["value"] = "open"
		connection_tie_m0_PCLKG["from"] = connection_from_tie_m0_PCLKG

		connection_to_tie_m0_PCLKG_list = []
		connection_to_tie_m0_PCLKG_dict = {}
		connection_to_tie_m0_PCLKG_dict["instance"] = instance_m0
		connection_to_tie_m0_PCLKG_dict["port"] = "PCLKG"
		connection_to_tie_m0_PCLKG_list.append(connection_to_tie_m0_PCLKG_dict)
		connection_tie_m0_PCLKG["to"] = connection_to_tie_m0_PCLKG_list
		connections.append(connection_tie_m0_PCLKG)



		connection_tie_ahp_HREADYOUT = {}
		connection_tie_ahp_HREADYOUT["type"] = "tieoff"

		connection_from_tie_ahp_HREADYOUT = {}
		connection_from_tie_ahp_HREADYOUT["value"] = "open"
		connection_tie_ahp_HREADYOUT["from"] = connection_from_tie_ahp_HREADYOUT

		connection_to_tie_ahp_HREADYOUT_list = []
		connection_to_tie_ahp_HREADYOUT_dict = {}
		connection_to_tie_ahp_HREADYOUT_dict["instance"] = instance_ahp
		connection_to_tie_ahp_HREADYOUT_dict["port"] = "HREADYOUT"
		connection_to_tie_ahp_HREADYOUT_list.append(connection_to_tie_ahp_HREADYOUT_dict)
		connection_tie_ahp_HREADYOUT["to"] = connection_to_tie_ahp_HREADYOUT_list
		connections.append(connection_tie_ahp_HREADYOUT)



		connection_tie_ahp_PSTRB = {}
		connection_tie_ahp_PSTRB["type"] = "tieoff"

		connection_from_tie_ahp_PSTRB = {}
		connection_from_tie_ahp_PSTRB["value"] = "open"
		connection_tie_ahp_PSTRB["from"] = connection_from_tie_ahp_PSTRB

		connection_to_tie_ahp_PSTRB_list = []
		connection_to_tie_ahp_PSTRB_dict = {}
		connection_to_tie_ahp_PSTRB_dict["instance"] = instance_ahp
		connection_to_tie_ahp_PSTRB_dict["port"] = "PSTRB"
		connection_to_tie_ahp_PSTRB_list.append(connection_to_tie_ahp_PSTRB_dict)
		connection_tie_ahp_PSTRB["to"] = connection_to_tie_ahp_PSTRB_list
		connections.append(connection_tie_ahp_PSTRB)



		connection_tie_ahp_PPROT = {}
		connection_tie_ahp_PPROT["type"] = "tieoff"

		connection_from_tie_ahp_PPROT = {}
		connection_from_tie_ahp_PPROT["value"] = "open"
		connection_tie_ahp_PPROT["from"] = connection_from_tie_ahp_PPROT

		connection_to_tie_ahp_PPROT_list = []
		connection_to_tie_ahp_PPROT_dict = {}
		connection_to_tie_ahp_PPROT_dict["instance"] = instance_ahp
		connection_to_tie_ahp_PPROT_dict["port"] = "PPROT"
		connection_to_tie_ahp_PPROT_list.append(connection_to_tie_ahp_PPROT_dict)
		connection_tie_ahp_PPROT["to"] = connection_to_tie_ahp_PPROT_list
		connections.append(connection_tie_ahp_PPROT)



		connection_tie_slave_PSLVERR = {}
		connection_tie_slave_PSLVERR["type"] = "tieoff"

		connection_from_tie_slave_PSLVERR = {}
		connection_from_tie_slave_PSLVERR["value"] = 0
		connection_tie_slave_PSLVERR["from"] = connection_from_tie_slave_PSLVERR

		connection_to_tie_slave_PSLVERR_list = []
		connection_to_tie_slave_PSLVERR_dict = {}
		connection_to_tie_slave_PSLVERR_dict["instance"] = instance_slave
		connection_to_tie_slave_PSLVERR_dict["port"] = "PSLVERR.*|PRDATA.*"
		connection_to_tie_slave_PSLVERR_list.append(connection_to_tie_slave_PSLVERR_dict)
		connection_tie_slave_PSLVERR["to"] = connection_to_tie_slave_PSLVERR_list
		connections.append(connection_tie_slave_PSLVERR)



		connection_tie_slave_PSEL = {}
		connection_tie_slave_PSEL["type"] = "tieoff"

		connection_from_tie_slave_PSEL = {}
		connection_from_tie_slave_PSEL["value"] = "open"
		connection_tie_slave_PSEL["from"] = connection_from_tie_slave_PSEL

		connection_to_tie_slave_PSEL_list = []
		connection_to_tie_slave_PSEL_dict = {}
		connection_to_tie_slave_PSEL_dict["instance"] = instance_slave
		connection_to_tie_slave_PSEL_dict["port"] = "PSEL.*"
		connection_to_tie_slave_PSEL_list.append(connection_to_tie_slave_PSEL_dict)
		connection_tie_slave_PSEL["to"] = connection_to_tie_slave_PSEL_list
		connections.append(connection_tie_slave_PSEL)



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