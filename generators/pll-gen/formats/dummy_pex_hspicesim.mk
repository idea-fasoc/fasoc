#=======================================================================
#  format for making form_Makefile
#  This is the point of modification if any needed for Makefile
#  make presim: generates model
#=======================================================================

pex_hspicesim:
	cd $(HSPICE_DIR)/pex_DUMP_result; hspice -mp 4 -i ./../pex_TB/tb_10ring10_osc18_FC30.sp
