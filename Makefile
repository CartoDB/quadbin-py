VENV=venv
BIN=$(VENV)/bin

init:
	test `command -v python3` || echo Please install python3
	[ -d $(VENV) ] || python3 -m venv $(VENV)
	$(BIN)/pip install -r requirements_dev.txt
	$(BIN)/pip install -e .
	$(BIN)/pre-commit install

lint:
	$(BIN)/black -q quadbin/ tests/ setup.py
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
	rm -rf venv
