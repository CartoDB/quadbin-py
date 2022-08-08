import pytest
import quadbin


@pytest.mark.parametrize(
    "index,expected",
    [
        (0, False),
        (5209574053332910078, False),
        (6362495557939757055, True),
        (5209574053332910079, True),
    ],
)
def test_is_valid_index(index, expected):
    assert quadbin.is_valid_index(index) is expected


@pytest.mark.parametrize(
    "index,expected",
    [
        (0, False),
        (5209574053332910078, False),
        (6362495557939757055, False),
        (5209574053332910079, True),
    ],
)
def test_is_valid_cell(index, expected):
    assert quadbin.is_valid_cell(index) is expected


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
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.point_to_cell(33.75, -11.178401873711776, -1)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.point_to_cell(33.75, -11.178401873711776, 27)


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
    assert quadbin.k_ring(5209574053332910079, 0) == [
        5209574053332910079,
    ]
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
    assert quadbin.k_ring(5209574053332910079, 2) == [
        5207251884775047167,
        5208008348774957055,
        5208025940961001471,
        5208078717519134719,
        5208096309705179135,
        5207287069147135999,
        5208043533147045887,
        5208061125333090303,
        5208113901891223551,
        5208131494077267967,
        5208799997146955775,
        5209556461146865663,
        5209574053332910079,
        5209626829891043327,
        5209644422077087743,
        5208835181519044607,
        5209591645518954495,
        5209609237704998911,
        5209662014263132159,
        5209679606449176575,
        5208940734635311103,
        5209697198635220991,
        5209714790821265407,
        5209767567379398655,
        5209785159565443071,
    ]
    with pytest.raises(ValueError, match="Invalid negative distance"):
        assert quadbin.k_ring(5209574053332910079, -1)


def test_k_ring_distances():
    assert quadbin.k_ring_distances(5209574053332910079, 0) == [
        {"distance": 0, "index": 5209574053332910079},
    ]
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
    assert quadbin.k_ring_distances(5209574053332910079, 2) == [
        {"distance": 2, "index": 5207251884775047167},
        {"distance": 2, "index": 5208008348774957055},
        {"distance": 2, "index": 5208025940961001471},
        {"distance": 2, "index": 5208078717519134719},
        {"distance": 2, "index": 5208096309705179135},
        {"distance": 2, "index": 5207287069147135999},
        {"distance": 1, "index": 5208043533147045887},
        {"distance": 1, "index": 5208061125333090303},
        {"distance": 1, "index": 5208113901891223551},
        {"distance": 2, "index": 5208131494077267967},
        {"distance": 2, "index": 5208799997146955775},
        {"distance": 1, "index": 5209556461146865663},
        {"distance": 0, "index": 5209574053332910079},
        {"distance": 1, "index": 5209626829891043327},
        {"distance": 2, "index": 5209644422077087743},
        {"distance": 2, "index": 5208835181519044607},
        {"distance": 1, "index": 5209591645518954495},
        {"distance": 1, "index": 5209609237704998911},
        {"distance": 1, "index": 5209662014263132159},
        {"distance": 2, "index": 5209679606449176575},
        {"distance": 2, "index": 5208940734635311103},
        {"distance": 2, "index": 5209697198635220991},
        {"distance": 2, "index": 5209714790821265407},
        {"distance": 2, "index": 5209767567379398655},
        {"distance": 2, "index": 5209785159565443071},
    ]
    with pytest.raises(ValueError, match="Invalid negative distance"):
        assert quadbin.k_ring_distances(5209574053332910079, -1)


def test_cell_sibling():
    assert quadbin.cell_sibling(5192650370358181887, "up") is None  # Res 0
    assert quadbin.cell_sibling(5193776270265024511, "up") is None  # Res 1
    assert quadbin.cell_sibling(5193776270265024511, "left") is None  # Res 1
    assert (
        quadbin.cell_sibling(5193776270265024511, "down") == 5196028070078709759
    )  # Res 1
    assert (
        quadbin.cell_sibling(5193776270265024511, "right") == 5194902170171867135
    )  # Res 1
    assert quadbin.cell_sibling(5194902170171867135, "up") is None  # Res 1
    assert quadbin.cell_sibling(5194902170171867135, "right") is None  # Res 1
    assert (
        quadbin.cell_sibling(5194902170171867135, "down") == 5197153969985552383
    )  # Res 1
    assert (
        quadbin.cell_sibling(5194902170171867135, "left") == 5193776270265024511
    )  # Res 1
    assert (
        quadbin.cell_sibling(5209574053332910079, "up") == 5208061125333090303
    )  # Res 4
    assert (
        quadbin.cell_sibling(5209574053332910079, "down") == 5209609237704998911
    )  # Res 4
    assert (
        quadbin.cell_sibling(5209574053332910079, "left") == 5209556461146865663
    )  # Res 4
    assert (
        quadbin.cell_sibling(5209574053332910079, "right") == 5209626829891043327
    )  # Res 4
    with pytest.raises(ValueError, match="Wrong direction argument passed to sibling"):
        assert quadbin.cell_sibling(5209574053332910079, "wrong")


def test_cell_to_parent():
    assert quadbin.cell_to_parent(5209574053332910079, 4) == 5209574053332910079
    assert quadbin.cell_to_parent(5209574053332910079, 2) == 5200566854078169087
    assert quadbin.cell_to_parent(5209574053332910079, 0) == 5192650370358181887
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_parent(5209574053332910079, 5)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_parent(5209574053332910079, -1)


def test_cell_to_children():
    assert quadbin.cell_to_children(5192650370358181887, 1) == [
        5193776270265024511,
        5196028070078709759,
        5194902170171867135,
        5197153969985552383,
    ]
    assert quadbin.cell_to_children(5209574053332910079, 5) == [
        5214064458820747263,
        5214073254913769471,
        5214068856867258367,
        5214077652960280575,
    ]
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, 27)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, 4)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, -1)


def test_geometry_to_cells():
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
        [-3.70659828186035, 40.409525904775634],
        [-3.71219873428345, 40.413365349070865],
    ]
    geometry = '{{"type":"Polygon","coordinates":[{0}]}}'.format(coordinates)
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
            5265786693164728319,
            5265786693165514751,
            5265786693164204031,
        ]
    )
