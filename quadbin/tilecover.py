# flake8: noqa

# Copyright (c) 2014, Morgan Herlocker (JavaScript implementation)
# Copyright (c) 2021-2022, CARTO

from __future__ import division

import json
import math

from .utils import point_to_tile

# TODO: finish refactor


def point_to_tile_hash(coordinates, resolution):
    x, y, z = point_to_tile(coordinates[0], coordinates[1], resolution)
    return to_id(x, y, z)


def hash_tiles_to_tiles(hash_tiles):
    keys = list(set(hash_tiles))
    return [from_id(key) for key in keys]


def get_point_hash_tiles(coordinates, resolution):
    return [point_to_tile_hash(coordinates, resolution)]


def get_multipoint_hash_tiles(coordinates, resolution):
    hash_tiles = []
    for i in range(0, len(coordinates)):
        hash_tiles.append(point_to_tile_hash(coordinates[i], resolution))
    return hash_tiles


def get_linestring_hash_tiles(coordinates, resolution):
    hash_tiles = []
    line_cover(hash_tiles, coordinates, resolution, None)
    return hash_tiles


def get_multilinestring_hash_tiles(coordinates, resolution):
    hash_tiles = []
    for i in range(0, len(coordinates)):
        line_cover(hash_tiles, coordinates[i], resolution, None)
    return hash_tiles


def get_polygon_hash_tiles(coordinates, resolution):
    hash_tiles = []
    polygon_cover(hash_tiles, coordinates, resolution)
    return hash_tiles


def get_multipolygon_hash_tiles(coordinates, resolution):
    hash_tiles = []
    for i in range(0, len(coordinates)):
        polygon_cover(hash_tiles, coordinates[i], resolution)
    return hash_tiles


def get_tiles(geometry, resolution):
    geom = json.loads(geometry)
    hash_tiles = []
    geom_type = geom["type"]
    geom_coordinates = geom["coordinates"]

    get_hash_tiles_function = {
        "Point": get_point_hash_tiles,
        "MultiPoint": get_multipoint_hash_tiles,
        "LineString": get_linestring_hash_tiles,
        "MultiLineString": get_multilinestring_hash_tiles,
        "Polygon": get_polygon_hash_tiles,
        "MultiPolygon": get_multipolygon_hash_tiles,
    }

    if geom_type not in get_hash_tiles_function:
        raise Exception("Geometry type not implemented")

    hash_tiles = get_hash_tiles_function[geom_type](geom_coordinates, resolution)

    return hash_tiles_to_tiles(hash_tiles)


def polygon_cover(tile_hash, geom, zoom):
    intersections = []

    geom_length = len(geom)
    for i in range(0, geom_length):
        ring = []
        line_cover(tile_hash, geom[i], zoom, ring)

        j = 0
        ring_length = len(ring)
        k = ring_length - 1
        while j < ring_length:
            m = (j + 1) % ring_length
            y = ring[j][1]

            #  add interesction if it's not local extremum or duplicate
            if (
                (y > ring[k][1] or y > ring[m][1])
                and (y < ring[k][1] or y < ring[m][1])
                and y != ring[m][1]
            ):
                intersections.append(ring[j])

            k = j
            j += 1

    intersections.sort(key=lambda tile: (tile[1], tile[0]))

    intersections_length = len(intersections)
    for i in range(0, intersections_length, 2):
        #  fill tiles between pairs of intersections
        y = intersections[i][1]
        for x in range(int(intersections[i][0] + 1), int(intersections[i + 1][0])):
            tile_hash.append(to_id(x, y, zoom))


def line_cover(tile_hash, coords, resolution, ring):
    prev_x = None
    prev_y = None
    y = None

    coords_length = len(coords)

    for i in range(0, coords_length - 1):
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
            tile_hash.append(to_id(x, y, resolution))
            # tile_hash[to_id(x, y, resolution)] = True
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

            tile_hash.append(to_id(x, y, resolution))
            # tile_hash[to_id(x, y, resolution)] = True
            if ring is not None and y != prev_y:
                ring.append([x, y])
            prev_x = x
            prev_y = y

    if ring and y == ring[0][1]:
        ring.pop()


def to_id(x, y, z):
    dim = 2 * (1 << int(z))
    return ((dim * y + x) * 32) + z


def from_id(id):
    z = int(id % 32)
    dim = 2 * (1 << z)
    xy = (id - z) / 32
    x = int(xy % dim)
    y = int(((xy - x) / dim) % dim)
    return (x, y, z)


# Tilebelt
def point_to_tile_fraction(longitude, latitude, z):
    sin = math.sin(latitude * math.pi / 180)
    z2 = 1 << z
    x = z2 * (longitude / 360 + 0.5)
    y = z2 * (0.5 - 0.25 * math.log((1 + sin) / (1 - sin)) / math.pi)

    #  Wrap Tile X
    x = x % z2
    if x < 0:
        x = x + z2
    return (x, y, z)
