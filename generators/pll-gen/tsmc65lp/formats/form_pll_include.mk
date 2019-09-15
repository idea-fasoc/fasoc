################################################################################
# PREAMBLE
################################################################################
# This include.mk sets all of the options for the directory structure, design
# options, and CAD tool options.
#
# A majority of the options are set to defaults located in
# $(CAD_FLOW)/common/include_default.mk
#
# You should only need to include variables that are non-default or need to
# override the defaults. It is recommended to look at include_default.mk at
# least once to understand what variables are defaults

################################################################################
# DESIGN-SPECIFIC VARIABLES
################################################################################
@@ export DESIGN_NAME := @dn
export PLATFORM    := tsmc65lp
export MODULE_TYPE := block
export DC_OPTIONS  := -64bit

# Search backwards to find the root directory, which has ".PROJECT_TOP".
export ROOT_DIR        := $(shell while [ "$$(pwd)" != "/" ]; do if [ -f .PROJECT_TOP ]; then break; fi; cd ..; done; pwd;)
export DESIGN_ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

ifeq ($(ROOT_DIR),/)
        $(error ERROR: ROOT_DIR not found. Check your file hierarchy.
        	Create and empty ".PROJECT_TOP" file in the same directory as the "cad" repository)
endif

################################################################################
# LIBRARY PATHS
################################################################################

# Function to check if a source directory is in the block design or the chip
# design
# Usage: $(eval $(call check_src_dir,[name of src dir],[name of var]))
define check_src_dir
  ifneq ($$(wildcard $(DESIGN_ROOT_DIR)/$(1)),)
    $$(info Info: Using $(1) from local directory)
    export $(2) = $(DESIGN_ROOT_DIR)/$(1)
  else
    $$(info Info: Using $(1) from root directory)
    export $(2) = $(ROOT_DIR)/$(1)
  endif
endef

$(eval $(call check_src_dir,cad,CAD_FLOW_DIR))

################################################################################
# DEFAULT OPTIONS
################################################################################
include $(CAD_FLOW_DIR)/common/include_default.mk

################################################################################
# DEFAULT OVERRIDES
################################################################################
# Specify any options to override the defaults here

