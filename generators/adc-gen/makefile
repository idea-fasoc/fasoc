gen:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform tsmc65lp --mode verilog

model:
	python tools/adc-gen-model.py --platform tsmc65lp


clean:
	python tools/adc-gen.py --specfile adc_data.json --output ./work --platform tsmc65lp --clean
	#python tools/adc-gen-model.py --platform tsmc65lp --clean


code_reset:
	git checkout ./flow
	git clean -f -d ./flow

