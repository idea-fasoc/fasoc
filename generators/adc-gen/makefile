gen:
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

