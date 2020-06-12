gen_12lp:
	./tools/dcdc-gen.py --specfile test.json --output ./work --platform gf12lp

gen_12lp_macro:
	./tools/dcdc-gen.py --specfile test.json --output ./work --platform gf12lp --mode macro

clean:
	./tools/dcdc-gen.py --specfile test.json --output ./work --platform gf12lp --clean

clean_12lp_full:
	./tools/dcdc-gen.py --specfile test.json --output ./work --platform gf12lp --clean --mode full

code_reset:
	git checkout ./flow
	git clean -f -d ./flow
