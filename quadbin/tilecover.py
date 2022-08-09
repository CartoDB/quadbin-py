# Copyright (c) 2014, Morgan Herlocker (JavaScript implementation)
# Copyright (c) 2021-2022, CARTO

from __future__ import division

import math

from .utils import distinct, point_to_tile, point_to_tile_fraction


def get_tiles(geometry, resolution):
    """Compute the tiles that fill an input geometry.

    Parameters
    ----------
    geometry : dict
        Input geometry as GeoJSON.
    resolution : int
        The resolution of the cells.

    Returns
    -------
    list
        Tiles intersecting the geometry.

    Raises
    ------
    Exception
        If the geometry type is not supported.
    """
    tiles_hashes = []
    geom_type = geometry["type"]
    geom_coordinates = geometry["coordinates"]

    get_tiles_hashes_function = {
        "Point": get_point_tiles_hashes,
        "MultiPoint": get_multipoint_tiles_hashes,
        "LineString": get_linestring_tiles_hashes,
        "MultiLineString": get_multilinestring_tiles_hashes,
        "Polygon": get_polygon_tiles_hashes,
        "MultiPolygon": get_multipolygon_tiles_hashes,
    }

    if geom_type not in get_tiles_hashes_function:
        raise Exception("Geometry type not implemented")

    tiles_hashes = get_tiles_hashes_function[geom_type](geom_coordinates, resolution)

    return tiles_hashes_to_tiles(tiles_hashes)


def get_point_tiles_hashes(coordinates, resolution):
    """Compute tile hash for a Point.

    Returns
    -------
    list
    """
    return point_cover(coordinates, resolution)


def get_multipoint_tiles_hashes(coordinates, resolution):
    """Compute tile hash for a MultiPoint.

    Returns
    -------
    list
    """
    return [
        tile_hash
        for i in range(len(coordinates))
        for tile_hash in point_cover(coordinates[i], resolution)
    ]


def get_linestring_tiles_hashes(coordinates, resolution):
    """Compute tile hash for a LineString.

    Returns
    -------
    list
    """
    return line_cover(coordinates, resolution)


def get_multilinestring_tiles_hashes(coordinates, resolution):
    """Compute tile hash for a MultiLineString.

    Returns
    -------
    list
    """
    return [
        tile_hash
        for i in range(len(coordinates))
        for tile_hash in line_cover(coordinates[i], resolution)
    ]


def get_polygon_tiles_hashes(coordinates, resolution):
    """Compute tile hash for a Polygon.

    Returns
    -------
    list
    """
    return polygon_cover(coordinates, resolution)


def get_multipolygon_tiles_hashes(coordinates, resolution):
    """Compute tile hash for a MultiPolygon.

    Returns
    -------
    list
    """
    return [
        tile_hash
        for i in range(len(coordinates))
        for tile_hash in polygon_cover(coordinates[i], resolution)
    ]


def point_cover(coordinates, resolution):
    """Return the tiles hashes that cover a point.

    Returns
    -------
    list
    """
    x, y, z = point_to_tile(coordinates[0], coordinates[1], resolution)
    return [to_tile_hash(x, y, z)]


def line_cover(coords, resolution, ring=None):
    """Return the tiles hashes that cover a line.

    Returns
    -------
    list
    """
    tiles_hashes = []
    prev_x = None
    prev_y = None
    y = None

    for i in range(len(coords) - 1):
        start = point_to_tile_fraction(coords[i][0], coords[i][1], resolution)
        stop = point_to_tile_fraction(coords[i + 1][0], coords[i + 1][1], resolution)
        x0 = start[0]
        y0 = start[1]
        x1 = stop[0]
        y1 = stop[1]
        dx = x1 - x0
        dy = y1 - y0

        if dy == 0 and dx == 0:
            continue

        sx = 1 if dx > 0 else -1
        sy = 1 if dy > 0 else -1
        x = math.floor(x0)
        y = math.floor(y0)
        t_max_x = float("inf") if dx == 0 else abs(((1 if dx > 0 else 0) + x - x0) / dx)
        t_max_y = float("inf") if dy == 0 else abs(((1 if dy > 0 else 0) + y - y0) / dy)
        tdx = float("inf") if dx == 0 else abs(sx / dx)
        tdy = float("inf") if dy == 0 else abs(sy / dy)

        if x != prev_x or y != prev_y:
            tiles_hashes.append(to_tile_hash(x, y, resolution))
            if ring is not None and y != prev_y:
                ring.append([x, y])
            prev_x = x
            prev_y = y

        while t_max_x < 1 or t_max_y < 1:
            if t_max_x < t_max_y:
                t_max_x += tdx
                x += sx
            else:
                t_max_y += tdy
                y += sy

            tiles_hashes.append(to_tile_hash(x, y, resolution))
            if ring is not None and y != prev_y:
                ring.append([x, y])
            prev_x = x
            prev_y = y

    if ring and y == ring[0][1]:
        ring.pop()

    return tiles_hashes


def polygon_cover(geom, zoom):
    """Return the tiles hashes that cover a polygon.

    Returns
    -------
    list
    """
    tiles_hashes = []
    intersections = []

    for i in range(len(geom)):
        ring = []
        tiles_hashes += line_cover(geom[i], zoom, ring)

        ring_length = len(ring)
        k = ring_length - 1
        for j in range(ring_length):
            m = (j + 1) % ring_length
            y = ring[j][1]

            #  add intersection if it's not local extremum or duplicate
            if (
                (y > ring[k][1] or y > ring[m][1])
                and (y < ring[k][1] or y < ring[m][1])
                and y != ring[m][1]
            ):
                intersections.append(ring[j])

            k = j

    intersections.sort(key=lambda tile: (tile[1], tile[0]))

    for i in range(0, len(intersections), 2):
        #  fill tiles between pairs of intersections
        y = intersections[i][1]
        for x in range(int(intersections[i][0] + 1), int(intersections[i + 1][0])):
            tiles_hashes.append(to_tile_hash(x, y, zoom))

    return tiles_hashes


def to_tile_hash(x, y, z):
    """Compute a hash from the tile.

    Returns
    -------
    int
    """
    dim = 2 * (1 << z)
    return ((dim * y + x) * 32) + z


def from_tile_hash(tile_hash):
    """Compute a tile from the hash.

    Returns
    -------
    tuple (x, y, z)
    """
    z = int(tile_hash % 32)
    dim = 2 * (1 << z)
    xy = (tile_hash - z) / 32
    x = int(xy % dim)
    y = int(((xy - x) / dim) % dim)
    return (x, y, z)


def tiles_hashes_to_tiles(tiles_hashes):
    """Obtain a list of tiles from a list of tiles .

    Returns
    -------
    list
    """
    return [from_tile_hash(tile_hash) for tile_hash in distinct(tiles_hashes)]
