# MeGen related Env variables are set through the include.mk file
include include.mk

mem_tsmc65lp_verilog: clean  
	
	./bin/MemGen.py --specfile ./SRAM_input_spec.json --outputDir ./work --platform tsmc65lp -m verilog

mem_tsmc65lp_macro: clean
	
	./bin/MemGen.py --specfile ./SRAM_input_spec.json --outputDir ./work --platform tsmc65lp -m macro

mem_gf12lp_verilog: clean
	
	./bin/MemGen.py --specfile ./SRAM_input_spec.json --outputDir ./work --platform gf12lp -m verilog

mem_gf12lp_macro: clean
	
	./bin/MemGen.py --specfile ./SRAM_input_spec.json --outputDir ./work --platform gf12lp -m macro

clean: clean_rundir clean_aprdir
	
clean_rundir:
	@echo "Cleaning : " $(MemGen_ROOT_DIR)	
	rm -rf $(MemGen_ROOT_DIR)/runfiles 
	rm -rf $(MemGen_ROOT_DIR)/work 
	rm -rf $(MemGen_ROOT_DIR)/MemGen.log
clean_aprdir:
	@echo "Cleaning : " $(MemGen_APR_DIR)
	cd $(MemGen_APR_DIR); make bleach_all
