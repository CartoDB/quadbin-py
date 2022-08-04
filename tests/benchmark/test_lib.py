import quadbin


def test_point_to_cell(benchmark):
    result = benchmark(quadbin.point_to_cell, 33.75, -11.178401873711776, 4)
    assert result == 5209574053332910079
