gen_65lp_verilog:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform tsmc65lp --mode verilog
	#python tools/adc-gen.py --specfile adc_data.json --output ./work --platform gf12lp --mode verilog

gen_65lp_macro:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform tsmc65lp --mode macro

gen_65lp_full:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform tsmc65lp --mode full

65lp_clean:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform tsmc65lp --mode macro --clean

gen_12lp_verilog:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform gf12lp --mode verilog

gen_12lp_macro:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform gf12lp --mode macro
	#python tools/adc-gen.py --specfile adc_data.json --output ./work --platform gf12lp --mode verilog

model:
	python tools/adc-gen-model.py --platform gf12lp


clean:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform gf12lp --clean
	#python tools/adc-gen-model.py --platform tsmc65lp --clean


code_reset:
	git checkout ./flow
	git clean -f -d ./flow

