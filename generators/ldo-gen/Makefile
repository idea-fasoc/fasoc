gen_65lp:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp

gen_65lp_macro:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp --mode macro

gen_65lp_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp --mode full

model_65lp:
	./tools/ldo_model.py --platform tsmc65lp

gen_8hp:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gfbicmos8hp

gen_8hp_macro:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gfbicmos8hp --mode macro

gen_8hp_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gfbicmos8hp --mode full

model_8hp:
	./tools/ldo_model.py --platform gfbicmos8hp

gen_12lp:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gf12lp

gen_12lp_macro:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gf12lp --mode macro

gen_12lp_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gf12lp --mode full

model_12lp:
	./tools/ldo_model.py --platform gf12lp

clean:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp --clean

clean_65lp_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp --clean --mode full
	./tools/ldo_model.py --platform tsmc65lp --clean

clean_8hp_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gfbicmos8hp --clean --mode full
	./tools/ldo_model.py --platform gfbicmos8hp --clean

clean_12lp_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform gf12lp --clean --mode full
	./tools/ldo_model.py --platform gf12lp --clean

code_reset:
	git checkout ./flow
	git clean -f -d ./flow
