gen:
	tools/cdc-gen.py --specfile test.json --output ./work --platform tsmc65lp --mode verilog

model:
	python tools/temp-sense-gen-model.py --platform tsmc65lp

clean:
	git checkout ./flow
	git clean -f -d ./flow