#=======================================================================
# pll-gen top Makfile
#=======================================================================


#HOME_PATH= /n/ludington/v/kmkwon/PROJECTS/fasoc/generators/pll-gen/tsmc65lp/
HOME_PATH := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
#HSPICE_DIR= $(HOME_PATH)/HSPICE
HSPICE_DIR_65= $(HOME_PATH)/../../private/generators/pll-gen/tsmc65lp/HSPICE
HSPICE_DIR_12= $(HOME_PATH)/../../private/generators/pll-gen/gf12lp/HSPICE
FSIM_DIR_12= /tmp/kmkwon_sim/HSPICE_mod3_halfFC 
PY_DIR=$(HOME_PATH)/tools

$(info *** PY_PATH is: $(PY_PATH))
$(info *** HOME_PATH is: $(HOME_PATH))
$(info *** HSPICE_DIR_65 is: $(HSPICE_DIR_65))
$(info *** HSPICE_DIR_12 is: $(HSPICE_DIR_12))
$(info *** FSIM_DIR_12 is: $(FSIM_DIR_12))


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

CHECK2 = $(FSIM_DIR_12)/finesim.mk
#CHECK_pex2 = $(FSIM_DIR_12)/pex_finesim.mk
CHECK_pex2 = /tmp/kmkwon_sim/HSPICE_mod3_halfFC/pex_finesim.mk
#ifneq ("$(wildcard $(CHECK))","")
#	include $(FSIM_DIR_12)/finesim.mk
#endif
ifneq ("$(wildcard $(CHECK_pex2))","")
	include /tmp/kmkwon_sim/HSPICE_mod3_halfFC/pex_finesim.mk
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
	cd $(HOME_PATH); python $(PY_DIR)/MDL_GEN_Beta.py --output ./work --platform gf12lp --mode full

modeling12_kbr:
	cd $(HOME_PATH); python $(PY_DIR)/MDL_GEN_Beta.py --output ./work --platform gf12lp --mode full --synth_tool genus --track 9

dcoto12:
	cd $(HOME_PATH); python $(PY_DIR)/DCO_TO_PREP.py --platform gf12lp --mode full

pll_gen_beta65:
	$(PY_DIR)/PLL_GEN_Beta.py --specfile test_beta65.json --output ./work --platform tsmc65lp --mode macro 

pll_gen_beta12:
	$(PY_DIR)/PLL_GEN_Beta.py --specfile test_alpha12.json --output ./work --platform gf12lp --mode macro

pll_gen_beta12_kbr:
	$(PY_DIR)/PLL_GEN_Beta.py --specfile test_alpha12.json --output ./work --platform gf12lp --mode macro --synth_tool genus --track 9

ble_pll_gen:
	$(PY_DIR)/BLE_PLL_GEN.py --specfile test_alpha12.json --output ./ble_outputs --platform gf12lp --mode macro

dltdc12:
	cd $(HOME_PATH); python $(PY_DIR)/ignore_dltdc_gen.py --platform gf12lp --mode full
