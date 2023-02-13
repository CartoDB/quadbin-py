# quadbin-py

[![PyPI version](https://badge.fury.io/py/quadbin.svg)](https://badge.fury.io/py/quadbin)
[![PyPI downloads](https://img.shields.io/pypi/dm/quadbin.svg)](https://pypistats.org/packages/quadbin)
[![Tests](https://github.com/cartodb/quadbin-py/actions/workflows/ci.yml/badge.svg)](https://github.com/cartodb/quadbin-py/actions)

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
| `is_valid_index(index)` |
| `is_valid_cell(cell)` |
| `cell_to_tile(cell)` |
| `tile_to_cell(tile)` |
| `cell_to_point(cell, geojson=False)` |
| `point_to_cell(longitude, latitude, resolution)` |
| `cell_to_boundary(cell, geojson=False)` |
| `cell_to_bounding_box(cell)` |
| `get_resolution(index)` |
| `index_to_string(index)` |
| `string_to_index(index)` |
| `k_ring(origin, k)` |
| `k_ring_distances(origin, k)` |
| `cell_sibling(cell, direction)` |
| `cell_to_parent(cell, parent_resolution)` |
| `cell_to_children(cell, children_resolution)` |
| `geometry_to_cells(geometry, resolution)` |
| `cell_area(cell)` |

## Development

Make commands:

- init: create the environment and install dependencies
- lint: run linter (flake8) + fix (black)
- test: run tests (pytest)
- publish-pypi: publish package in pypi.org
- publish-test-pypi: publish package in test.pypi.org
- clean: remove the environment

NOTE: Python2 is supported to enable the usage in platforms like [Amazon Redshift](https://aws.amazon.com/redshift/).