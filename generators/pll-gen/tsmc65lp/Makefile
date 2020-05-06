#=======================================================================
# pll-gen top Makfile
#=======================================================================


#HOME_PATH= /n/ludington/v/kmkwon/PROJECTS/fasoc/generators/pll-gen/tsmc65lp/
HOME_PATH := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
#HSPICE_DIR= $(HOME_PATH)/HSPICE
HSPICE_DIR= $(HOME_PATH)/../../../private/generators/pll-gen/tsmc65lp/HSPICE
PY_DIR=$(HOME_PATH)/tools

$(info *** PY_PATH is: $(PY_PATH))
$(info *** HOME_PATH is: $(HOME_PATH))
$(info *** HSPICE_DIR is: $(HSPICE_DIR))


CHECK = $(HSPICE_DIR)/hspicesim.mk
CHECK_pex = $(HSPICE_DIR)/pex_hspicesim.mk
ifneq ("$(wildcard $(CHECK))","")
	include $(HSPICE_DIR)/hspicesim.mk
endif

ifneq ("$(wildcard $(CHECK_pex))","")
	include $(HSPICE_DIR)/pex_hspicesim.mk
endif

# --  ignore makefile: make commands for test purpose
CHECK_ignore = ignore_make.mk
ifneq ("$(wildcard $(CHECK_ignore))","")
	include ignore_make.mk
endif

include bleach.mk

modeling:
	cd $(HOME_PATH); python $(PY_DIR)/MDL_GEN_65nm.py --platform tsmc65lp

pex_modeling:
	cd $(HOME_PATH); python $(PY_DIR)/PEX_MDL_GEN_65nm.py --platform tsmc65lp

pll_gen_beta:
	$(PY_DIR)/PLL_GEN_Beta.py --specfile test_beta.json --output ./work --platform tsmc65lp --mode verilog 
