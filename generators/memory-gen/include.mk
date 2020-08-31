#----------------------------------------
# Env Vairables related to CAD Flow Dir
#----------------------------------------
export MemGen_ROOT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
export FASOC_private := $(MemGen_ROOT_DIR)/../../private
export CAD_FLOWS_DIR := $(FASOC_private)/cad
export MemGen_APR_DIR := $(FASOC_private)/generators/memory-gen/apr

# The bleach.mk file to clean the CADRE related files. Sourced from CADRE dir.
include $(CAD_FLOWS_DIR)/common/bleach.mk
