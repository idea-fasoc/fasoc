gen_12lp:
	./tools/scpa_gen.py --specfile test.json --output ./work --platform gf12lp

gen_12lp_macro:
	./tools/scpa_gen.py --specfile test.json --output ./work --platform gf12lp --mode macro

gen_12lp_full:
	./tools/scpa_gen.py --specfile test.json --output ./work --platform gf12lp --mode full

gen_12lp_pex:
	./tools/scpa_gen_pex.py --specfile test.json --output ./work --platform gf12lp --mode pex

model_12lp:
	./tools/scpa_model.py --platform gf12lp

clean_12lp_full:
	./tools/scpa_gen.py --specfile test.json --output ./work --platform gf12lp --clean --mode full
	./tools/scpa_model.py --platform gf12lp --clean

code_reset:
	git checkout ./flow
	git clean -f -d ./flow
