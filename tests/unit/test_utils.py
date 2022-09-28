from quadbin.utils import point_to_tile, point_to_tile_fraction


def test_point_to_tile_fraction():
    tile = point_to_tile_fraction(-95.93965530395508, 41.26000108568697, 9)
    assert tile[0] == 119.552490234375
    assert tile[1] == 191.47119140625
    assert tile[2] == 9


def test_point_to_tile():
    # X axis
    assert point_to_tile(-180, 0, 0) == (0, 0, 0)
    assert point_to_tile(-180, 85, 2) == (0, 0, 2)
    assert point_to_tile(180, 85, 2) == (0, 0, 2)
    assert point_to_tile(-185, 85, 2) == (3, 0, 2)
    assert point_to_tile(185, 85, 2) == (0, 0, 2)
    # Y axis
    assert point_to_tile(-175, -95, 2) == (0, 3, 2)
    assert point_to_tile(-175, 95, 2) == (0, 0, 2)
    assert point_to_tile(-175, 95, 2) == (0, 0, 2)
