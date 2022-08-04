import quadbin


def test_cell_is_valid():
    assert quadbin.cell_is_valid(0) is False
    assert quadbin.cell_is_valid(5209574053332910078) is False
    assert quadbin.cell_is_valid(5209574053332910079) is True


def test_cell_to_tile():
    assert quadbin.cell_to_tile(5209574053332910079) == {"z": 4, "x": 9, "y": 8}


def test_tile_to_cell():
    tile = {"z": 4, "x": 9, "y": 8}
    assert quadbin.tile_to_cell(**tile) == 5209574053332910079


def test_cell_to_point():
    assert quadbin.cell_to_point(5209574053332910079) == [33.75, -11.178401873711776]


def test_point_to_cell():
    assert quadbin.point_to_cell(33.75, -11.178401873711776, 4) == 5209574053332910079


def test_get_resolution():
    assert quadbin.get_resolution(5209574053332910079) == 4
