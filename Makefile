# PCB Flow — common tasks. Run `make <target>`.
.PHONY: test example example-check doctor

test:            ## run the full test suite
	python3 -m pytest -q

example:         ## reproduce the worked example end-to-end (regenerate + verify + gerbers)
	python3 tools/reproduce_example.py

example-check:   ## verify the committed example board only (no regeneration)
	python3 tools/reproduce_example.py --check

doctor:          ## check the environment
	python3 tools/doctor.py
