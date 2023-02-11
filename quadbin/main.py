import json
import math

from .tilecover import get_tiles
from .utils import (
    DIRECTIONS,
    clip_latitude,
    clip_longitude,
    distinct,
    point_to_tile,
    tile_k_ring,
    tile_sibling,
    tile_to_longitude,
    tile_to_latitude,
)

HEADER = 0x4000000000000000
FOOTER = 0xFFFFFFFFFFFFF
B = [
    0x5555555555555555,
    0x3333333333333333,
    0x0F0F0F0F0F0F0F0F,
    0x00FF00FF00FF00FF,
    0x0000FFFF0000FFFF,
    0x00000000FFFFFFFF,
]
S = [1, 2, 4, 8, 16]


def is_valid_index(index):
    """Return True if this is a valid Quadbin index.

    Parameters
    ----------
    index : int

    Returns
    -------
    bool
    """
    header = HEADER
    mode = (index >> 59) & 7
    resolution = (index >> 52) & 0x1F
    unused = FOOTER >> (resolution << 2)
    return (
        index >= 0
        and (index & header == header)
        and mode in [0, 1, 2, 3, 4, 5, 6]
        and resolution >= 0
        and resolution <= 26
        and (index & unused == unused)
    )


def is_valid_cell(cell):
    """Return True if this is a valid Quadbin cell (mode 1).

    Parameters
    ----------
    index : int

    Returns
    -------
    bool
    """
    header = HEADER
    mode = (cell >> 59) & 7
    resolution = (cell >> 52) & 0x1F
    unused = FOOTER >> (resolution << 2)
    return (
        cell >= 0
        and (cell & header == header)
        and mode == 1
        and resolution >= 0
        and resolution <= 26
        and (cell & unused == unused)
    )


def cell_to_tile(cell):
    """Convert a cell into a tile.

    Parameters
    ----------
    cell : int

    Returns
    -------
    tile: tuple (x, y, z)
    """
    # mode = (cell >> 59) & 7
    # extra = (cell >> 57) & 3
    z = cell >> 52 & 31
    q = (cell & FOOTER) << 12
    x = q
    y = q >> 1

    x = x & B[0]
    y = y & B[0]

    x = (x | (x >> S[0])) & B[1]
    y = (y | (y >> S[0])) & B[1]

    x = (x | (x >> S[1])) & B[2]
    y = (y | (y >> S[1])) & B[2]

    x = (x | (x >> S[2])) & B[3]
    y = (y | (y >> S[2])) & B[3]

    x = (x | (x >> S[3])) & B[4]
    y = (y | (y >> S[3])) & B[4]

    x = (x | (x >> S[4])) & B[5]
    y = (y | (y >> S[4])) & B[5]

    x = x >> (32 - z)
    y = y >> (32 - z)

    return (x, y, z)


def tile_to_cell(tile):
    """Convert a tile into a cell.

    Parameters
    ----------
    tile : tuple (x, y, z)

    Returns
    -------
    int
    """
    if tile is None:
        return None

    x, y, z = tile

    x = x << (32 - z)
    y = y << (32 - z)

    x = (x | (x << S[4])) & B[4]
    y = (y | (y << S[4])) & B[4]

    x = (x | (x << S[3])) & B[3]
    y = (y | (y << S[3])) & B[3]

    x = (x | (x << S[2])) & B[2]
    y = (y | (y << S[2])) & B[2]

    x = (x | (x << S[1])) & B[1]
    y = (y | (y << S[1])) & B[1]

    x = (x | (x << S[0])) & B[0]
    y = (y | (y << S[0])) & B[0]

    # -- | (mode << 59) | (mode_dep << 57)
    return HEADER | (1 << 59) | (z << 52) | ((x | (y << 1)) >> 12) | (FOOTER >> (z * 2))


def cell_to_point(cell, geojson=False):
    """Convert a cell into a geographic point.

    Parameters
    ----------
    cell : int
    geojson : bool, optional
        Return the point as a GeoJSON geometry, by default False.

    Returns
    -------
    str
        if geojson is True.
    list
        if geojson is False (default).
    """
    tile = cell_to_tile(cell)

    longitude = tile_to_longitude(tile, 0.5)
    latitude = tile_to_latitude(tile, 0.5)

    if geojson:
        return '{{"type": "Point", "coordinates": {0}}}'.format([longitude, latitude])
    else:
        return [longitude, latitude]


def point_to_cell(longitude, latitude, resolution):
    """Convert a geographic point into a cell.

    Parameters
    ----------
    longitude : float
        Longitude in decimal degrees.
    latitude : float
        Latitude in decimal degrees.
    resolution : int
        The resolution of the cell.

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If the resolution is out of bounds.
    """
    if resolution < 0 or resolution > 26:
        raise ValueError("Invalid resolution: should be between 0 and 26")

    longitude = clip_longitude(longitude)
    latitude = clip_latitude(latitude)

    tile = point_to_tile(longitude, latitude, resolution)

    return tile_to_cell(tile)


def cell_to_boundary(cell, geojson=False):
    """Convert a cell into a geographic polygon.

    Parameters
    ----------
    cell : int
    geojson : bool, optional
        Return the polygon as a GeoJSON geometry, by default False.

    Returns
    -------
    str
        if geojson is True.
    list
        if geojson is False (default).
    """
    bbox = cell_to_bounding_box(cell)

    boundary = [
        [bbox[0], bbox[3]],
        [bbox[0], bbox[1]],
        [bbox[2], bbox[1]],
        [bbox[2], bbox[3]],
        [bbox[0], bbox[3]],
    ]

    if geojson:
        return '{{"type": "Polygon", "coordinates": [{0}]}}'.format(boundary)
    else:
        return boundary


def cell_to_bounding_box(cell):
    """Conver a cell into a geographic bounding box.

    Parameters
    ----------
    cell : int

    Returns
    -------
    list
        Bounding box in degrees [xmin, ymin, xmax, ymax]
    """
    tile = cell_to_tile(cell)

    xmin = tile_to_longitude(tile, 0)
    xmax = tile_to_longitude(tile, 1)
    ymin = tile_to_latitude(tile, 1)
    ymax = tile_to_latitude(tile, 0)

    return [xmin, ymin, xmax, ymax]


def get_resolution(index):
    """Get the resolution of an index.

    Parameters
    ----------
    index : int

    Returns
    -------
    int
    """
    return (index >> 52) & 0x1F


def index_to_string(index):
    """Convert an index into its string representation.

    Parameters
    ----------
    index : int

    Returns
    -------
    str
        The hexadecimal representation of the input decimal integer.
    """
    return hex(index)[2:]


def string_to_index(index):
    """Convert an index into its numeric representation.

    Parameters
    ----------
    index : str

    Returns
    -------
    int
        The decimal representation of the input hexadecimal string.
    """
    return int(index, base=16)


def k_ring(origin, k):
    """Compute the indices within k distance of the origin index.

    Parameters
    ----------
    origin : int
        Origin index.
    k : int
        Distance of the ring.

    Returns
    -------
    list
        Indices in the k-ring.

    Raises
    ------
    ValueError
        If the k distance is negative.
    """
    if k < 0:
        raise ValueError("Invalid negative distance")

    neighbors = tile_k_ring(cell_to_tile(origin), k, extra=False)

    return [tile_to_cell(neighbor) for neighbor in neighbors]


def k_ring_distances(origin, k):
    """Compute the indices and distances within k distance of the origin index.

    Parameters
    ----------
    origin : int
        Origin index.
    k : int
        Distance of the ring.

    Returns
    -------
    list
        Objects with the index and distance in the k-ring.

    Raises
    ------
    ValueError
        If the k distance is negative.
    """
    if k < 0:
        raise ValueError("Invalid negative distance")

    neighbors = tile_k_ring(cell_to_tile(origin), k, extra=True)

    return [
        {"index": tile_to_cell(neighbor[0]), "distance": neighbor[1]}
        for neighbor in neighbors
    ]


def cell_sibling(cell, direction):
    """Compute the sibling cell in a specific direction.

    Parameters
    ----------
    cell : int
    direction : str
        Location of the sibling: "up", "right", "left", "down".

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If a wrong direction is passed.
    """
    direction = direction.lower()
    if direction not in DIRECTIONS:
        raise ValueError("Wrong direction argument passed to sibling")

    tile = cell_to_tile(cell)
    direction = DIRECTIONS[direction]

    return tile_to_cell(tile_sibling(tile, direction))


def cell_to_parent(cell, parent_resolution):
    """Compute the parent cell for a specific resolution.

    Parameters
    ----------
    cell : int
    parent_resolution : int

    Returns
    -------
    int

    Raises
    ------
    ValueError
        If the parent resolution is not valid.
    """
    resolution = get_resolution(cell)

    if parent_resolution < 0 or parent_resolution > resolution:
        raise ValueError("Invalid resolution")

    return (
        (cell & ~(0x1F << 52))
        | (parent_resolution << 52)
        | (FOOTER >> (parent_resolution << 2))
    )


def cell_to_children(cell, children_resolution):
    """Compute the children cells for a specific resolution.

    Parameters
    ----------
    cell : int
    children_resolution : int

    Returns
    -------
    list
        Children cells.

    Raises
    ------
    ValueError
        If the children resolution is not valid.
    """
    resolution = (cell >> 52) & 0x1F

    if (
        children_resolution < 0
        or children_resolution > 26
        or children_resolution <= resolution
    ):
        raise ValueError("Invalid resolution")

    resolution_diff = children_resolution - resolution
    block_range = 1 << (resolution_diff << 1)
    block_shift = 52 - (children_resolution << 1)

    child_base = (cell & ~(0x1F << 52)) | (children_resolution << 52)
    child_base = child_base & ~((block_range - 1) << block_shift)

    children = []
    for x in range(block_range):
        child = child_base | (x << block_shift)
        children.append(child)

    return children


def geometry_to_cells(geometry, resolution):
    """Compute the cells that fill an input geometry.

    Parameters
    ----------
    geometry : str
        Input geometry as GeoJSON.
    resolution : int
        The resolution of the cells.

    Returns
    -------
    list
        Cells intersecting the geometry.
    """
    tiles = []
    geometry = json.loads(geometry)

    if geometry["type"] == "GeometryCollection":
        for geom in geometry["geometries"]:
            tiles += [tile for tile in get_tiles(geom, resolution)]
        tiles = distinct(tiles)
    else:
        tiles = [tile for tile in get_tiles(geometry, resolution)]

    return [tile_to_cell(tile) for tile in tiles]


def vertex_canonical_tile(z, x, y, vertex):
    """Compute tile coordinates of canonical cell for a given vertex.

    The canonical cell is the cell that contains the vertex with a minimum
    value of the index.

    Parameters
    ----------
    z, x, y, vertex : int

    Returns
    -------
    tile: tuple (x, y, z, vertex)
    """
    if x & 1:  # E cell within parent
        if y & 1:  # SE cell within parent
            if vertex == 0:  # NW vertex
                x &= ~1  # x -= 1
                y &= ~1  # y -= 1
                vertex = 3  # -> SE
            elif vertex == 1:  # NE vertex
                y &= ~1  # y -= 1
                vertex = 3  # -> SE
            elif vertex == 2:  # SW vertex
                x &= ~1  # x -= 1
                vertex = 3  # -> SE
            # else: # vertex == 3: # SE vertex, stay there
        else:  # NE cell within parent
            if not (vertex & 1):  # W-side vertex
                x &= ~1  # x -= 1
                vertex += 1  # NW -> NE, SW -> SE
            if not (vertex & 2):  # N-side vertex
                if y > 0:
                    y -= 1
                    vertex += 2  # NE->SE
    else:  # W cell within parent
        if y & 1:  # SW cell within parent
            if not (vertex & 2):  # N-side vertex
                y &= ~1  # y -= 1
                vertex += 2  # NW->SW, NE->SE
            if not (vertex & 1) and x > 0:  # W-side vertex
                if x > 0:
                    x -= 1
                    vertex += 1  # SW->SE
        else:  # NW cell within parent
            if not (vertex & 2):  # N-side vertex
                if y > 0:
                    y -= 1
                    vertex += 2
            if not (vertex & 1):  # W-side vertex
                if x > 0:
                    x -= 1
                    vertex += 1
    return (x, y, z, vertex)


def tile_scalefactor(tile):
    """Inverse of the scale factor at the tile center.

    Parameters
    ----------
    tile : tuple (x, y, z)

    Returns
    -------
    float
    """
    _, y, z = tile
    y_offset = 0.5
    return math.cos(
        2
        * math.pi
        * (
            math.atan(math.exp(-(2 * (y + y_offset) / (1 << z) - 1) * math.pi))
            / math.pi
            - 0.25
        )
    )


REF_AREA = 508164597540055.75
AREA_FACTORS = [
    1.0,
    1.003741849761155,
    1.8970972739048304,
    2.7118085839548,
    3.0342500406694364,
    3.1231014735135538,
    3.1457588045774316,
    3.151449027223487,
    3.1528731677136914,
    3.1532293013524657,
    3.1533183409109418,
    3.1533406011847736,
]


def tile_area(tile):
    """Approximate area of a tile in square meters.

       The area is based on a perfect sphere (WGS84 authalic sphere).

    Parameters
    ----------
    tile : tuple (x, y, z)

    Returns
    -------
    float
    """
    x, y, z = tile
    area_factor = AREA_FACTORS[min(len(AREA_FACTORS) - 1, z)]
    area = area_factor * REF_AREA / (1 << (z << 1))
    center_y = 0 if z == 0 else (1 << (z - 1))
    if y < center_y - 1 or y > center_y:

        def z_factor(y):
            return math.pow(tile_scalefactor((x, y, z)), 2)

        area *= z_factor(y) / z_factor(center_y)

    return area
