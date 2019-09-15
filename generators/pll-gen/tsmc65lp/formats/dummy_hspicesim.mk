#=======================================================================
#  format for making form_Makefile
#  This is the point of modification if any needed for Makefile
#  make presim: generates model
#=======================================================================

hspicesim:
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring8_osc8_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring8_osc9_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring8_osc10_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring8_osc8_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring8_osc9_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring8_osc10_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring8_osc8_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring8_osc9_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring8_osc10_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring8_osc8_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring8_osc9_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring8_osc10_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring16_osc8_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring16_osc9_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring16_osc10_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring16_osc8_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring16_osc9_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_8ring16_osc10_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring16_osc8_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring16_osc9_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring16_osc10_FC16.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring16_osc8_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring16_osc9_FC32.sp
	cd $(HSPICE_DIR)/DUMP_result; hspice -mp 4 -i ./../TB/tb_16ring16_osc10_FC32.sp

#1 hspicerfsim:
#@@	@s1 $(HSPICE_DIR)/DUMPrf_result; hspicerf -mp @rm -i ./../TBrf/tbrf_@rdring@mr_o@nr_fc@Nf.sp

