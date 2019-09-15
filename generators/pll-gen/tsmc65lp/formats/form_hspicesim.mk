#=======================================================================
#  format for making form_Makefile
#  This is the point of modification if any needed for Makefile
#  make presim: generates model
#=======================================================================

hspicesim:
@@	@s2 $(HSPICE_DIR)/DUMP_result; hspice -mp @mp -i ./../TB/tb_@mdring@mt_o@nt_FC@nf.sp

#1 hspicerfsim:
#@@	@s1 $(HSPICE_DIR)/DUMPrf_result; hspicerf -mp @rm -i ./../TBrf/tbrf_@rdring@mr_o@nr_fc@Nf.sp

