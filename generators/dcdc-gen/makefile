gen:
	python tools/dcdc-gen.py --specfile test.json --output ./work --platform tsmc65lp --mode verilog

model:
	python tools/dcdc-gen-model.py --platform tsmc65lp

clean:
	git checkout ./flow
	git clean -f -d ./flow