gen_65lp:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform tsmc65lp --mode verilog

gen_12lp:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform gf12lp --mode macro

gen_12lp_verilog:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform gf12lp --mode verilog

gen_12lp_macro:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform gf12lp --mode macro

gen_12lp_full:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform gf12lp --mode full

12lp_clean:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform gf12lp --mode macro --clean

gen_sky130:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform sky130 --mode macro

gen_sky130_verilog:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform sky130 --mode verilog

gen_sky130_macro:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform sky130 --mode macro

gen_sky130_full:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform sky130 --mode fulli

sky130_clean:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform sky130 --mode macro --clean
# model:
# 	python tools/temp-sense-gen-model.py --platform tsmc65lp


clean:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform sky130 --mode verilog --clean
	#python tools/temp-sense-gen-model.py --platform tsmc65lp --clean


code_reset:
	git checkout ./flow
	git clean -f -d ./flow
