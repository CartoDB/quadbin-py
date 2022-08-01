VENV=venv
PIP=$(VENV)/bin/pip
PYTHON=$(VENV)/bin/python

init:
	test `command -v python3` || echo Please install python3
	[ -d $(VENV) ] || python3 -m venv $(VENV)
	$(PIP) install -r requirements_dev.txt
	$(PIP) install -e .

lint:
	$(PYTHON) -m black -q quadbin tests setup.py
	$(PYTHON) -m flake8 quadbin tests setup.py

test:
	$(PYTHON) -m pytest tests

publish-pypi:
	rm -rf ./dist/*
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine upload dist/*

publish-test-pypi:
	rm -rf ./dist/*
	$(PYTHON) setup.py sdist bdist_wheel
	$(PYTHON) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose

clean:
	rm -rf venv
