VENV := venv
PYTHON := python
BIN = $(VENV)/bin
PYTHON_VERSION = $(shell $(PYTHON) -c 'import sys;print(sys.version_info[0])')

init:
	test `command -v $(PYTHON)` || echo Please install $(PYTHON)
	pip install virtualenv
	[ -d $(VENV) ] || virtualenv -p $(PYTHON) $(VENV)
ifeq ($(PYTHON_VERSION),3)
	$(BIN)/pip install -r requirements_dev.txt
	$(BIN)/pre-commit install
else ifeq ($(PYTHON_VERSION),2)
	$(BIN)/pip install -r requirements_dev2.txt
endif
	$(BIN)/pip install -e .

lint:
ifeq ($(PYTHON_VERSION),3)
	$(BIN)/black -q quadbin/ tests/ setup.py
endif
	$(BIN)/flake8 quadbin/ tests/ setup.py

test:
	$(BIN)/pytest --cov=quadbin tests/unit/

test-benchmark:
	$(BIN)/pytest tests/benchmark/ --benchmark-histogram

publish-pypi:
	rm -rf ./dist/*
	$(BIN)/python setup.py sdist bdist_wheel
	$(BIN)/twine upload dist/*

publish-test-pypi:
	rm -rf ./dist/*
	$(BIN)/python setup.py sdist bdist_wheel
	$(BIN)/twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose

clean:
	rm -rf $(VENV)
