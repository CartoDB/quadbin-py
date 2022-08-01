# quadbin-py

Python library for quadbin.

## Install

```bash
pip install quadbin
```

## Usage

```py
>>> import quadbin
>>> longitude = -3.7038
>>> latitude =  40.4168
>>> resolution = 10
>>> quadbin.point_to_cell(longitude, latitude, resolution)
5234261499580514303
```

## API

| Function |
|---|
| `cell_is_valid(index: int) -> bool` |
| `cell_to_tile(index: int) -> {"z","x","y"}` |
| `tile_to_cell(z: int, x: int, y: int) -> [longitude, latitude]` |
| `point_to_cell(longitude: float, latitude: float, resolution: int) -> int` |
| `get_resolution(index: int) -> int` |

## Development

Make commands:

- init: create the environment and install dependencies
- lint: run linter (flake8) + fix (black)
- test: run tests (pytest)
- publish-pypi: publish package in pypi.org
- publish-test-pypi: publish package in test.pypi.org
- clean: remove the environment
