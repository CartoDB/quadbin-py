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
    bbox = quadbin.cell_to_bounding_box(5211632339100106751)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]
    bbox = quadbin.cell_to_bounding_box(5212472365983727615)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]
    bbox = quadbin.cell_to_bounding_box(5226055182877458431)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]
    bbox = quadbin.cell_to_bounding_box(5264708239044902911)
    assert bbox[0] < bbox[2]
    assert bbox[1] < bbox[3]


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
    # Res 0
    assert quadbin.cell_sibling(5192650370358181887, "up") is None
    assert quadbin.cell_sibling(5193776270265024511, "up") is None
    # Res 1
    assert quadbin.cell_sibling(5193776270265024511, "left") is None
    assert quadbin.cell_sibling(5193776270265024511, "down") == 5196028070078709759
    assert quadbin.cell_sibling(5193776270265024511, "right") == 5194902170171867135
    assert quadbin.cell_sibling(5194902170171867135, "up") is None
    assert quadbin.cell_sibling(5194902170171867135, "right") is None
    assert quadbin.cell_sibling(5194902170171867135, "down") == 5197153969985552383
    assert quadbin.cell_sibling(5194902170171867135, "left") == 5193776270265024511
    assert quadbin.cell_sibling(5209574053332910079, "up") == 5208061125333090303
    # Res 4
    assert quadbin.cell_sibling(5209574053332910079, "down") == 5209609237704998911
    assert quadbin.cell_sibling(5209574053332910079, "left") == 5209556461146865663
    assert quadbin.cell_sibling(5209574053332910079, "right") == 5209626829891043327
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
    assert sorted(quadbin.cell_to_children(5192650370358181887, 1)) == sorted(
        [
            5193776270265024511,
            5196028070078709759,
            5194902170171867135,
            5197153969985552383,
        ]
    )
    assert sorted(quadbin.cell_to_children(5209574053332910079, 5)) == sorted(
        [
            5214064458820747263,
            5214073254913769471,
            5214068856867258367,
            5214077652960280575,
        ]
    )
    assert sorted(quadbin.main.cell_to_children(5209574053332910079, 6)) == sorted(
        [
            5218564759913234431,
            5218565859424862207,
            5218566958936489983,
            5218568058448117759,
            5218569157959745535,
            5218570257471373311,
            5218571356983001087,
            5218572456494628863,
            5218573556006256639,
            5218574655517884415,
            5218575755029512191,
            5218576854541139967,
            5218577954052767743,
            5218579053564395519,
            5218580153076023295,
            5218581252587651071,
        ]
    )
    assert sorted(quadbin.main.cell_to_children(5209574053332910079, 7)) == sorted(
        [
            5223067534906884095,
            5223067809784791039,
            5223068084662697983,
            5223068359540604927,
            5223068634418511871,
            5223068909296418815,
            5223069184174325759,
            5223069459052232703,
            5223069733930139647,
            5223070008808046591,
            5223070283685953535,
            5223070558563860479,
            5223070833441767423,
            5223071108319674367,
            5223071383197581311,
            5223071658075488255,
            5223071932953395199,
            5223072207831302143,
            5223072482709209087,
            5223072757587116031,
            5223073032465022975,
            5223073307342929919,
            5223073582220836863,
            5223073857098743807,
            5223074131976650751,
            5223074406854557695,
            5223074681732464639,
            5223074956610371583,
            5223075231488278527,
            5223075506366185471,
            5223075781244092415,
            5223076056121999359,
            5223076330999906303,
            5223076605877813247,
            5223076880755720191,
            5223077155633627135,
            5223077430511534079,
            5223077705389441023,
            5223077980267347967,
            5223078255145254911,
            5223078530023161855,
            5223078804901068799,
            5223079079778975743,
            5223079354656882687,
            5223079629534789631,
            5223079904412696575,
            5223080179290603519,
            5223080454168510463,
            5223080729046417407,
            5223081003924324351,
            5223081278802231295,
            5223081553680138239,
            5223081828558045183,
            5223082103435952127,
            5223082378313859071,
            5223082653191766015,
            5223082928069672959,
            5223083202947579903,
            5223083477825486847,
            5223083752703393791,
            5223084027581300735,
            5223084302459207679,
            5223084577337114623,
            5223084852215021567,
        ]
    )
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, 27)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, 4)
    with pytest.raises(ValueError, match="Invalid resolution"):
        assert quadbin.cell_to_children(5209574053332910079, -1)


def test_geometry_to_cells_point():
    coordinates = [-3.71219873428345, 40.413365349070865]
    geometry = '{{"type":"Point","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert quadbin.geometry_to_cells(geometry, 17) == [5265786693163941887]
    assert quadbin.geometry_to_cells(geometry, 26) == [5306319089810035706]


def test_geometry_to_cells_multipoint():
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
    ]
    geometry = '{{"type":"MultiPoint","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693153193983,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 26)) == sorted(
        [
            5306319089810035706,
            5306319089799501962,
        ]
    )


def test_geometry_to_cells_linestring():
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
    ]
    geometry = '{{"type":"LineString","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892418453503,
            5274793892418486271,
            5274793892418469887,
            5274793892418568191,
            5274793892418600959,
            5274793892418961407,
            5274793892407771135,
            5274793892407803903,
            5274793892407902207,
            5274793892407885823,
            5274793892407918591,
        ]
    )


def test_geometry_to_cells_multilinestring():
    coordinates = [
        [
            [-3.71219873428345, 40.413365349070865],
            [-3.7144088745117, 40.40965661286395],
        ],
        [
            [-3.714215755462646, 40.41297324565437],
            [-3.710868358612061, 40.412041990883246],
        ],
    ]
    geometry = '{{"type":"MultiLineString","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
            5265786693152669695,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892418453503,
            5274793892418486271,
            5274793892418469887,
            5274793892418568191,
            5274793892418600959,
            5274793892418961407,
            5274793892407771135,
            5274793892407803903,
            5274793892407902207,
            5274793892407885823,
            5274793892407918591,
            5274793892407263231,
            5274793892407279615,
            5274793892418584575,
            5274793892418633727,
            5274793892418650111,
        ]
    )


def test_geometry_to_cells_polygon():
    coordinates = [
        [
            [-3.71219873428345, 40.413365349070865],
            [-3.7144088745117, 40.40965661286395],
            [-3.70659828186035, 40.409525904775634],
            [-3.71219873428345, 40.413365349070865],
        ]
    ]
    geometry = '{{"type":"Polygon","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
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
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892407771135,
            5274793892407803903,
            5274793892407885823,
            5274793892407902207,
            5274793892407918591,
            5274793892407934975,
            5274793892418453503,
            5274793892418469887,
            5274793892418486271,
            5274793892418502655,
            5274793892418535423,
            5274793892418551807,
            5274793892418568191,
            5274793892418584575,
            5274793892418600959,
            5274793892418617343,
            5274793892418633727,
            5274793892418650111,
            5274793892418666495,
            5274793892418682879,
            5274793892418830335,
            5274793892418863103,
            5274793892418879487,
            5274793892418961407,
            5274793892418977791,
            5274793892418994175,
            5274793892419010559,
            5274793892419026943,
            5274793892419043327,
            5274793892419059711,
            5274793892419076095,
            5274793892419092479,
            5274793892419108863,
            5274793892419125247,
            5274793892419141631,
            5274793892419158015,
            5274793892419174399,
            5274793892419190783,
            5274793892419207167,
            5274793892419223551,
            5274793892419239935,
            5274793892419256319,
            5274793892419272703,
            5274793892419289087,
            5274793892419321855,
            5274793892419338239,
            5274793892419354623,
            5274793892419371007,
            5274793892419387391,
            5274793892419403775,
            5274793892419420159,
            5274793892419436543,
            5274793892419452927,
            5274793892419469311,
            5274793892420042751,
            5274793892420141055,
            5274793892420157439,
            5274793892420173823,
            5274793892420190207,
        ]
    )


def test_geometry_to_cells_multipolygon():
    coordinates = [
        [
            [
                [-3.71219873428345, 40.413365349070865],
                [-3.7144088745117, 40.40965661286395],
                [-3.70659828186035, 40.409525904775634],
                [-3.71219873428345, 40.413365349070865],
            ],
            [
                [-3.7118983268737793, 40.4116172037252],
                [-3.7120914459228516, 40.41015493512173],
                [-3.710278272628784, 40.41096367978466],
                [-3.7118983268737793, 40.4116172037252],
            ],
        ],
        [
            [
                [-3.708035945892334, 40.411176075761475],
                [-3.70863676071167, 40.409003069883845],
                [-3.7063729763031006, 40.41048170181224],
                [-3.708035945892334, 40.411176075761475],
            ]
        ],
    ]
    geometry = '{{"type":"MultiPolygon","coordinates":{0}}}'.format(coordinates)
    assert quadbin.geometry_to_cells(geometry, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry, 17)) == sorted(
        [
            5265786693153193983,
            5265786693163941887,
            5265786693164204031,
            5265786693164466175,
            5265786693164728319,
            5265786693165514751,
            5265786693166301183,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry, 19)) == sorted(
        [
            5274793892407771135,
            5274793892407803903,
            5274793892407885823,
            5274793892407902207,
            5274793892407918591,
            5274793892407934975,
            5274793892418453503,
            5274793892418469887,
            5274793892418486271,
            5274793892418502655,
            5274793892418535423,
            5274793892418551807,
            5274793892418568191,
            5274793892418584575,
            5274793892418600959,
            5274793892418617343,
            5274793892418633727,
            5274793892418650111,
            5274793892418666495,
            5274793892418682879,
            5274793892418830335,
            5274793892418863103,
            5274793892418879487,
            5274793892418961407,
            5274793892418977791,
            5274793892418994175,
            5274793892419010559,
            5274793892419026943,
            5274793892419043327,
            5274793892419059711,
            5274793892419076095,
            5274793892419092479,
            5274793892419108863,
            5274793892419125247,
            5274793892419141631,
            5274793892419158015,
            5274793892419174399,
            5274793892419190783,
            5274793892419207167,
            5274793892419223551,
            5274793892419239935,
            5274793892419256319,
            5274793892419272703,
            5274793892419289087,
            5274793892419305471,
            5274793892419321855,
            5274793892419338239,
            5274793892419354623,
            5274793892419371007,
            5274793892419387391,
            5274793892419403775,
            5274793892419420159,
            5274793892419436543,
            5274793892419452927,
            5274793892419469311,
            5274793892420009983,
            5274793892420042751,
            5274793892420059135,
            5274793892420108287,
            5274793892420141055,
            5274793892420157439,
            5274793892420173823,
            5274793892420190207,
            5274793892420861951,
            5274793892420878335,
        ]
    )


def test_geometry_to_cells_geometrycollection():
    coordinates = [-3.7118983268737793, 40.4116172037252]
    geometry_point = '{{"type":"Point","coordinates":{0}}}'.format(coordinates)
    coordinates = [
        [-3.71219873428345, 40.413365349070865],
        [-3.7144088745117, 40.40965661286395],
    ]
    geometry_linestring = '{{"type":"LineString","coordinates":{0}}}'.format(
        coordinates
    )
    geometry_collection = (
        '{{"type":"GeometryCollection","geometries":[{0}, {1}]}}'.format(
            geometry_point, geometry_linestring
        )
    )
    assert quadbin.geometry_to_cells(geometry_collection, 0) == [5192650370358181887]
    assert quadbin.geometry_to_cells(geometry_collection, 10) == [5234261499580514303]
    assert sorted(quadbin.geometry_to_cells(geometry_collection, 17)) == sorted(
        [
            5265786693163941887,
            5265786693164466175,
            5265786693153193983,
        ]
    )
    assert sorted(quadbin.geometry_to_cells(geometry_collection, 19)) == sorted(
        [
            5274793892407771135,
            5274793892407803903,
            5274793892407885823,
            5274793892407902207,
            5274793892407918591,
            5274793892418453503,
            5274793892418469887,
            5274793892418486271,
            5274793892418568191,
            5274793892418600959,
            5274793892418666495,
            5274793892418961407,
        ]
    )


@pytest.mark.parametrize(
    "tile,expected",
    [
        ((0, 0, 0), 508164597540055.75),
        ((1, 0, 1), 127516518279497.16),
        ((0, 1, 1), 127516518279497.11),
        ((0, 0, 2), 3354306636925.9023),
        ((2, 1, 2), 60252354543011.56),
        ((2, 2, 2), 60252354543011.56),
        ((1, 3, 2), 3354306636925.902),
        ((7, 0, 3), 405347921787.1127),
        ((3, 1, 3), 1893932149859.4053),
        ((7, 2, 3), 7940839890420.507),
        ((1, 3, 3), 21531954963610.305),
        ((2, 4, 3), 21531954963610.305),
        ((6, 5, 3), 7940839890420.51),
        ((7, 6, 3), 1893932149859.4014),
        ((3, 7, 3), 405347921787.1137),
        ((5, 0, 4), 68847216295.91176),
        ((5, 1, 4), 150015920630.08636),
        ((9, 2, 4), 324359672843.66473),
        ((11, 3, 4), 689700245764.4768),
        ((12, 4, 4), 1415535456168.1387),
        ((3, 5, 4), 2703138561407.3833),
        ((9, 6, 4), 4507012722233.37),
        ((12, 7, 4), 6023040823252.668),
        ((9, 8, 4), 6023040823252.664),
        ((7, 9, 4), 4507012722233.373),
        ((1, 10, 4), 2703138561407.385),
        ((3, 11, 4), 1415535456168.1404),
        ((1, 12, 4), 689700245764.4747),
        ((2, 13, 4), 324359672843.66516),
        ((8, 14, 4), 150015920630.0866),
        ((4, 15, 4), 68847216295.91222),
        ((2, 0, 5), 14160505713.702057),
        ((18, 4, 5), 66957044671.40606),
        ((4, 8, 5), 297109634630.5034),
        ((14, 12, 5), 1008646311011.379),
        ((14, 16, 5), 1549853128285.9084),
        ((3, 20, 5), 780011091373.6311),
        ((1, 24, 5), 207289317396.88107),
        ((31, 28, 5), 45530712164.63003),
        ((23, 0, 6), 3210498445.8824654),
        ((34, 8, 6), 15204878147.827898),
        ((18, 16, 6), 67965167366.12873),
        ((17, 24, 6), 237461340707.57086),
        ((52, 32, 6), 390274232638.2269),
        ((32, 40, 6), 208783733329.56433),
        ((4, 48, 6), 56765895703.36641),
        ((27, 56, 6), 12538056116.820728),
        ((81, 0, 7), 764328456.2867869),
        ((4, 16, 7), 3622540506.9648323),
        ((126, 32, 7), 16248126209.176235),
        ((121, 48, 7), 57545410795.20297),
        ((57, 64, 7), 97745045568.05563),
        ((72, 80, 7), 53957641045.31359),
        ((61, 96, 7), 14849099728.531345),
        ((95, 112, 7), 3289546290.2144575),
        ((138, 0, 8), 186467048.6535538),
        ((19, 32, 8), 884078744.6901459),
        ((193, 64, 8), 3971905493.817118),
        ((201, 96, 8), 14160339910.8699),
        ((27, 128, 8), 24447304143.76936),
        ((148, 160, 8), 13711772787.766005),
        ((148, 192, 8), 3797054754.548408),
        ((174, 224, 8), 842465672.8105292),
        ((14, 0, 9), 46050330.23509074),
        ((196, 64, 9), 218372534.04884157),
        ((137, 128, 9), 981880701.56478),
        ((505, 192, 9), 3511936869.1768293),
        ((491, 256, 9), 6112516398.900173),
        ((213, 320, 9), 3455862981.7418623),
        ((167, 384, 9), 960025220.6932801),
        ((388, 448, 9), 213171250.2341762),
        ((448, 0, 10), 11442422.668480542),
        ((418, 128, 10), 54265162.87777075),
        ((457, 256, 10), 244093752.50473356),
        ((574, 384, 10), 874472509.6180239),
        ((728, 512, 10), 1528172250.3897524),
        ((675, 640, 10), 867463180.0306838),
        ((994, 768, 10), 241361844.3184481),
        ((289, 896, 10), 53615013.34380896),
        ((2021, 0, 11), 2851875.6549530826),
        ((1772, 256, 11), 13525475.896024764),
        ((113, 512, 11), 60852040.82694955),
        ((1877, 768, 11), 218179599.71270698),
        ((1691, 1024, 11), 382045759.5605321),
        ((869, 1280, 11), 217303430.58745173),
        ((1443, 1536, 11), 60510553.14499288),
        ((1262, 1792, 11), 13444207.546244394),
        ((405, 0, 12), 711880.1518172809),
        ((868, 512, 12), 3376278.427660119),
        ((598, 1024, 12), 15191626.424900804),
        ((2839, 1536, 12), 54490111.52470787),
        ((1358, 2048, 12), 95511608.45103554),
        ((268, 2560, 12), 54380590.292608134),
        ((4, 3072, 12), 15148940.490946993),
        ((46, 3584, 12), 3366119.894625659),
        ((72, 0, 13), 177834.09803959142),
        ((6103, 1024, 13), 843433.9941112136),
        ((6838, 2048, 13), 3795236.185658999),
        ((3122, 3072, 13), 13615681.06317344),
        ((4012, 4096, 13), 23877912.64783286),
        ((4822, 5120, 13), 13601990.906296989),
        ((2784, 6144, 13), 3789900.44473846),
        ((2225, 7168, 13), 842164.1778174711),
        ((12132, 0, 14), 44441.5417196901),
        ((11618, 2048, 14), 210779.09098281202),
        ((3407, 4096, 14), 948475.4032619242),
        ((1244, 6144, 14), 3403064.522131492),
        ((8783, 8192, 14), 5969478.820397914),
        ((1901, 10240, 14), 3401353.2524307016),
        ((12185, 12288, 14), 947808.4356725625),
        ((8108, 14336, 14), 210620.3639580674),
        ((14689, 0, 15), 11108.263187119439),
        ((1726, 4096, 15), 52684.84955532187),
        ((5651, 8192, 15), 237077.15538302113),
        ((19195, 12288, 15), 850659.1693733177),
        ((9510, 16384, 15), 1492369.7462518667),
        ((13382, 20480, 15), 850445.2606563419),
        ((24101, 24576, 15), 236993.7844349456),
        ((11169, 28672, 15), 52665.00867800594),
        ((7292, 0, 16), 2776.8005542784613),
        ((31685, 8192, 16), 13169.972161726404),
        ((45857, 16384, 16), 59264.077539137535),
        ((61186, 24576, 16), 212651.42262138167),
        ((23968, 32768, 16), 373092.4391340615),
        ((33538, 40960, 16), 212624.6840333054),
        ((28645, 49152, 16), 59253.65617023244),
        ((46470, 57344, 16), 13167.492052404968),
        ((120813, 0, 17), 694.1669856280457),
        ((74912, 16384, 17), 3292.33802293761),
        ((11500, 32768, 17), 14815.368009842998),
        ((30813, 49152, 17), 53161.18446727011),
        ((17988, 65536, 17), 93273.10994449603),
        ((116865, 81920, 17), 53157.84214334298),
        ((74693, 98304, 17), 14814.065339102703),
        ((130625, 114688, 17), 3292.0280091507925),
        ((156343, 0, 18), 173.53760240416173),
        ((16949, 32768, 18), 823.0651292155519),
        ((207451, 65536, 18), 3703.7605831585784),
        ((175018, 98304, 18), 13290.08721953591),
        ((189809, 131072, 18), 23318.277496005037),
        ((69596, 163840, 18), 13289.669429339378),
        ((131755, 196608, 18), 3703.597749243366),
        ((194095, 229376, 18), 823.0263775324452),
        ((456398, 0, 19), 43.38388261963919),
        ((255164, 65536, 19), 205.7638602834703),
        ((496698, 131072, 19), 925.9299685042733),
        ((254518, 196608, 19), 3322.4956929142404),
        ((331731, 262144, 19), 5829.569374549895),
        ((233238, 327680, 19), 3322.4434690965386),
        ((415557, 393216, 19), 925.9096142673413),
        ((346447, 458752, 19), 205.75901633678478),
        ((991324, 0, 20), 10.845905913090053),
        ((9697, 131072, 20), 51.440662297569574),
        ((5314, 262144, 20), 231.48121997891653),
        ((23851, 393216, 20), 830.6206592040279),
        ((737269, 524288, 20), 1457.3923436601747),
        ((572526, 655360, 20), 830.6141312184599),
        ((52044, 786432, 20), 231.47867569299893),
        ((58443, 917504, 20), 51.4400568296431),
        ((1889412, 0, 21), 2.7114683806069366),
        ((711837, 262144, 21), 12.860127728127763),
        ((657038, 524288, 21), 57.87014596251734),
        ((255406, 786432, 21), 207.6547568007845),
        ((696547, 1048576, 21), 364.3480858946535),
        ((400497, 1310720, 21), 207.6539408247401),
        ((1523531, 1572864, 21), 57.86982793356335),
        ((1211319, 1835008, 21), 12.860052049235128),
        ((584591, 0, 22), 0.6778660821146193),
        ((1353047, 524288, 22), 3.215027201573707),
        ((2756290, 1048576, 22), 14.467516611460995),
        ((2285964, 1572864, 22), 51.91363819170339),
        ((3018232, 2097152, 22), 91.08702147901639),
        ((637827, 2621440, 22), 51.91353620368485),
        ((2343081, 3145728, 22), 14.4674768633863),
        ((3745818, 3670016, 22), 3.2150177453530335),
    ],
)
def test_tile_area(tile, expected):
    assert quadbin.tile_area(tile) == pytest.approx(expected, rel=1.5e-1)
