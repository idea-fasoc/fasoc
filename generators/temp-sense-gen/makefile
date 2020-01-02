gen:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform tsmc65lp --mode full

model:
	python tools/temp-sense-gen-model.py --platform tsmc65lp


clean:
	python tools/temp-sense-gen.py --specfile test.json --output ./work --platform tsmc65lp --clean
	#python tools/temp-sense-gen-model.py --platform tsmc65lp --clean


code_reset:
	git checkout ./flow
	git clean -f -d ./flow
