import json

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
    tile_area,
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
        | (FOOTER >> (parent_resolution << 1))
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


def cell_area(cell):
    """Approximate area of a cell in square meters.

       The area is based on a perfect sphere (WGS84 authalic sphere).

    Parameters
    ----------
    cell : int

    Returns
    -------
    float
    """
    return tile_area(cell_to_tile(cell))
