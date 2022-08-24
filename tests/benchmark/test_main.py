import quadbin

import pytest


@pytest.mark.parametrize("res", [5, 6, 7, 8, 9, 10, 11, 12, 13])
def test_cell_to_children(benchmark, res):
    benchmark(quadbin.cell_to_children, 5209574053332910079, res)


@pytest.mark.parametrize("res", [5, 6, 7, 8, 9, 10, 11, 12, 13])
def test_old_cell_to_children(benchmark, res):
    benchmark(old_cell_to_children, 5209574053332910079, res)


def old_cell_to_children(cell, children_resolution):
    x, y, z = quadbin.cell_to_tile(cell)

    if children_resolution < 0 or children_resolution > 26 or children_resolution <= z:
        raise ValueError("Invalid resolution")

    diff_z = children_resolution - z
    mask = (1 << diff_z) - 1
    min_tile_x = x << diff_z
    max_tile_x = min_tile_x | mask
    min_tile_y = y << diff_z
    max_tile_y = min_tile_y | mask

    children = []
    for x in range(min_tile_x, max_tile_x + 1):
        for y in range(min_tile_y, max_tile_y + 1):
            children.append(quadbin.tile_to_cell((x, y, children_resolution)))

    return children
