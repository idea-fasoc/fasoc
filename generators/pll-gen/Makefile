#=======================================================================
# pll-gen top Makfile
#=======================================================================


#HOME_PATH= /n/ludington/v/kmkwon/PROJECTS/fasoc/generators/pll-gen/tsmc65lp/
HOME_PATH := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
#HSPICE_DIR= $(HOME_PATH)/HSPICE
HSPICE_DIR_65= $(HOME_PATH)/../../private/generators/pll-gen/tsmc65lp/HSPICE
HSPICE_DIR_12= $(HOME_PATH)/../../private/generators/pll-gen/gf12lp/HSPICE
PY_DIR=$(HOME_PATH)/tools

$(info *** PY_PATH is: $(PY_PATH))
$(info *** HOME_PATH is: $(HOME_PATH))
$(info *** HSPICE_DIR_65 is: $(HSPICE_DIR_65))
$(info *** HSPICE_DIR_12 is: $(HSPICE_DIR_12))


CHECK = $(HSPICE_DIR_65)/hspicesim.mk
CHECK_pex = $(HSPICE_DIR_65)/pex_hspicesim.mk
ifneq ("$(wildcard $(CHECK))","")
	include $(HSPICE_DIR_65)/hspicesim.mk
endif

ifneq ("$(wildcard $(CHECK_pex))","")
	include $(HSPICE_DIR_65)/pex_hspicesim.mk
endif

CHECK = $(HSPICE_DIR_12)/hspicesim.mk
CHECK_pex = $(HSPICE_DIR_12)/pex_hspicesim.mk
ifneq ("$(wildcard $(CHECK))","")
	include $(HSPICE_DIR_12)/hspicesim.mk
endif

ifneq ("$(wildcard $(CHECK_pex))","")
	include $(HSPICE_DIR_12)/pex_hspicesim.mk
endif


# --  ignore makefile: make commands for test purpose
CHECK_ignore = ignore_make.mk
ifneq ("$(wildcard $(CHECK_ignore))","")
	include ignore_make.mk
endif

include bleach.mk

modeling:
	cd $(HOME_PATH); python $(PY_DIR)/MDL_GEN_65nm.py --platform tsmc65lp --mode full

pex_modeling:
	cd $(HOME_PATH); python $(PY_DIR)/PEX_MDL_GEN_65nm.py --platform tsmc65lp

modeling65:
	cd $(HOME_PATH); python $(PY_DIR)/MDL_GEN_Beta.py --platform tsmc65lp --mode full

modeling12:
	cd $(HOME_PATH); python $(PY_DIR)/MDL_GEN_Beta.py --platform gf12lp --mode full

pll_gen_beta65:
	$(PY_DIR)/PLL_GEN_Beta.py --specfile test_beta65.json --output ./work --platform tsmc65lp --mode macro 

pll_gen_beta12:
	$(PY_DIR)/PLL_GEN_Beta.py --specfile test_alpha12.json --output ./work --platform gf12lp --mode macro 

