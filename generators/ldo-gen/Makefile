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

model_8hp:
	./tools/ldo_model.py --platform gfbicmos8hp

clean:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp --clean

clean_full:
	./tools/ldo_gen.py --specfile test.json --output ./work --platform tsmc65lp --clean --mode full
	./tools/ldo_model.py --platform tsmc65lp --clean

code_reset:
	git checkout ./flow
	git clean -f -d ./flow
