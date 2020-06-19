gen_65lp:
	python tools/cdc-gen.py --specfile test.json --output ./work --platform tsmc65lp --mode verilog

gen_12lp:
	python tools/cdc-gen.py --specfile test.json --output ./work --platform gf12lp --mode macro

# model:
# 	python tools/temp-sense-gen-model.py --platform tsmc65lp

clean:
	git checkout ./flow
	git clean -f -d ./flow