#=======================================================================
#  format for making form_Makefile
#  This is the point of modification if any needed for Makefile
#  make presim: generates model
#=======================================================================

pex_hspicesim:
@@	@s2 $(HSPICE_DIR)/@Rd; hspice -mp @mp -i ./../@Td/tb_@mdring@mt_o@nt_FC@nf.sp
