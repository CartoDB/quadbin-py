import pytest
import quadbin


def test_is_valid_index():
    assert quadbin.is_valid_index(0) is False
    assert quadbin.is_valid_index(5209574053332910078) is False
    assert quadbin.is_valid_index(6362495557939757055) is True
    assert quadbin.is_valid_index(5209574053332910079) is True


def test_is_valid_cell():
    assert quadbin.is_valid_cell(0) is False
    assert quadbin.is_valid_cell(5209574053332910078) is False
    assert quadbin.is_valid_cell(6362495557939757055) is False
    assert quadbin.is_valid_cell(5209574053332910079) is True


def test_cell_to_tile():
    tile = (9, 8, 4)
    assert quadbin.cell_to_tile(5209574053332910079) == tile


def test_tile_to_cell():
    tile = (9, 8, 4)
    assert quadbin.tile_to_cell(tile) == 5209574053332910079


def test_cell_to_point():
    coordinates = [33.75, -11.178401873711776]
    assert quadbin.cell_to_point(5209574053332910079) == coordinates
    assert quadbin.cell_to_point(
        5209574053332910079, geojson=True
    ) == '{{"type": "Point", "coordinates": {0}}}'.format(coordinates)


def test_point_to_cell():
    assert quadbin.point_to_cell(33.75, -11.178401873711776, 4) == 5209574053332910079


def test_cell_to_boundary():
    coordinates = [
        [22.5, 0.0],
        [22.5, -21.943045533438166],
        [45.0, -21.943045533438166],
        [45.0, 0.0],
        [22.5, 0.0],
    ]
    assert quadbin.cell_to_boundary(5209574053332910079) == coordinates
    assert quadbin.cell_to_boundary(
        5209574053332910079, geojson=True
    ) == '{{"type": "Polygon", "coordinates": [{0}]}}'.format(coordinates)


def test_cell_to_bounding_box():
    assert quadbin.cell_to_bounding_box(5209574053332910079) == [
        22.5,
        -21.943045533438166,
        45.0,
        0.0,
    ]


def test_get_resolution():
    assert quadbin.get_resolution(5209574053332910079) == 4


def test_index_to_string():
    assert quadbin.index_to_string(5209574053332910079) == "484c1fffffffffff"


def test_string_to_index():
    assert quadbin.string_to_index("484c1fffffffffff") == 5209574053332910079


def test_k_ring():
    assert quadbin.k_ring(5209574053332910079, 1) == [
        5208043533147045887,
        5208061125333090303,
        5208113901891223551,
        5209556461146865663,
        5209574053332910079,
        5209626829891043327,
        5209591645518954495,
        5209609237704998911,
        5209662014263132159,
    ]


def test_k_ring_distances():
    assert quadbin.k_ring_distances(5209574053332910079, 1) == [
        {"distance": 1, "index": 5208043533147045887},
        {"distance": 1, "index": 5208061125333090303},
        {"distance": 1, "index": 5208113901891223551},
        {"distance": 1, "index": 5209556461146865663},
        {"distance": 0, "index": 5209574053332910079},
        {"distance": 1, "index": 5209626829891043327},
        {"distance": 1, "index": 5209591645518954495},
        {"distance": 1, "index": 5209609237704998911},
        {"distance": 1, "index": 5209662014263132159},
    ]


def test_cell_sibling():
    assert quadbin.cell_sibling(5209574053332910079, "left") == 5209556461146865663
    assert quadbin.cell_sibling(5209574053332910079, "right") == 5209626829891043327
    assert quadbin.cell_sibling(5209574053332910079, "up") == 5208061125333090303
    assert quadbin.cell_sibling(5209574053332910079, "down") == 5209609237704998911


def test_cell_to_parent():
    assert quadbin.cell_to_parent(5209574053332910079, 4) == 5209574053332910079
    assert quadbin.cell_to_parent(5209574053332910079, 2) == 5200566854078169087
    assert quadbin.cell_to_parent(5209574053332910079, 0) == 5192650370358181887
    with pytest.raises(Exception):
        assert quadbin.cell_to_parent(5209574053332910079, 5)
    with pytest.raises(Exception):
        assert quadbin.cell_to_parent(5209574053332910079, -1)


def test_cell_to_children():
    assert quadbin.cell_to_children(5209574053332910079, 5) == [
        5260204365332873215,
        5264707964537143295,
        5260204365334970367,
        5264707964537667583,
    ]
    with pytest.raises(Exception):
        assert quadbin.cell_to_children(5209574053332910079, 27)
    with pytest.raises(Exception):
        assert quadbin.cell_to_children(5209574053332910079, 4)
    with pytest.raises(Exception):
        assert quadbin.cell_to_children(5209574053332910079, -1)


def test_geometry_to_cells():
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
        [-3.70659828186035, 40.409525904775634],
        [-3.71219873428345, 40.413365349070865],
    ]
    geometry = '{{"type":"Polygon","coordinates":[{0}]}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 17) == [
        5265786693163941887,
        5265786693164466175,
        5265786693153193983,
        5265786693164728319,
        5265786693165514751,
        5265786693164204031,
    ]
