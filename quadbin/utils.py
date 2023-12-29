import math

MAX_LONGITUDE = 180.0
MIN_LONGITUDE = -MAX_LONGITUDE
MAX_LATITUDE = 89.0
MIN_LATITUDE = -MAX_LATITUDE

UP = 0
RIGHT = 1
LEFT = 2
DOWN = 3

DIRECTIONS = {"up": UP, "right": RIGHT, "left": LEFT, "down": DOWN}


def clip_number(num, lower, upper):
    """Limit input number by lower and upper limits.

    Parameters
    ----------
    num : float
    lower : float
    upper : float

    Returns
    -------
    float
    """
    return max(min(num, upper), lower)


def clip_longitude(longitude):
    """Limit longitude bounds.

    Parameters
    ----------
    longitude : float

    Returns
    -------
    float
    """
    return clip_number(longitude, MIN_LONGITUDE, MAX_LONGITUDE)


def clip_latitude(latitude):
    """Limit latitude by the web mercator bounds.

    Parameters
    ----------
    latitude : float

    Returns
    -------
    float
    """
    return clip_number(latitude, MIN_LATITUDE, MAX_LATITUDE)


def tile_to_longitude(tile, offset):
    """Compute the longitude for a tile with an offset.

    Parameters
    ----------
    tile : tuple (x, y, z)
    offset : float
        Inner position of the tile. From 0 to 1.

    Returns
    -------
    longitude : float
    """
    x, _, z = tile
    return 180 * (2.0 * (x + offset) / (1 << z) - 1.0)


def tile_to_latitude(tile, offset):
    """Compute the latitude for a tile with an offset.

    Parameters
    ----------
    tile : tuple (x, y, z)
    offset : float
        Inner position of the tile. From 0 to 1.

    Returns
    -------
    latitude : float
    """
    _, y, z = tile
    expy = math.exp(-(2.0 * (y + offset) / (1 << z) - 1) * math.pi)
    return 360 * (math.atan(expy) / math.pi - 0.25)


def point_to_tile(longitude, latitude, resolution):
    """Compute the tile for a longitude and latitude in a specific resolution.

    Parameters
    ----------
    longitude : float
        Longitude in decimal degrees.
    latitude : float
        Latitude in decimal degrees.
    resolution : int
        The resolution of the tile.

    Returns
    -------
    tile: tuple (x, y, z)
    """
    x, y, z = point_to_tile_fraction(longitude, latitude, resolution)

    x = int(math.floor(x))
    y = int(math.floor(y))

    return (x, y, z)


def point_to_tile_fraction(longitude, latitude, resolution):
    """Compute the tile in fractions for a longitude and latitude in a specific resolution.

    Parameters
    ----------
    longitude : float
        Longitude in decimal degrees.
    latitude : float
        Latitude in decimal degrees.
    resolution : int
        The resolution of the tile.

    Returns
    -------
    tile: tuple (x, y, z)
    """
    z = resolution
    z2 = 1 << z
    sinlat = math.sin(latitude * math.pi / 180.0)
    x = z2 * (longitude / 360.0 + 0.5)
    yfraction = 0.5 - 0.25 * math.log((1 + sinlat) / (1 - sinlat)) / math.pi
    y = clip_number(z2 * yfraction, 0, z2 - 1)

    # Wrap Tile x
    x = x % z2
    x = x + z2 if x < 0 else x

    return (x, y, z)


def tile_sibling(tile, direction):
    """Compute the sibling tile in a specific direction.

    Parameters
    ----------
    tile : tuple (x, y, z)
    direction : int
        0 up, 1 right, 2, left, 3, down

    Returns
    -------
    tuple (x, y, z)
    """
    x, y, z = tile

    if z == 0:
        return None

    tiles_per_level = 2 << (z - 1)

    if direction == UP:
        if y > 0:
            y = y - 1
        else:
            return None

    if direction == RIGHT:
        if x < tiles_per_level - 1:
            x = x + 1
        else:
            return None

    if direction == LEFT:
        if x > 0:
            x = x - 1
        else:
            return None

    if direction == DOWN:
        if y < tiles_per_level - 1:
            y = y + 1
        else:
            return None

    return x, y, z


def tile_k_ring(origin, k, extra=False):
    """Compute the tiles within k distance of the origin tile.

    Parameters
    ----------
    origin : tuple (x, y, z)
        Origin tile.
    k : int
        Distance of the ring.
    extra : bool
        If True return the extra tuple (tile, distance).
        Otherwise, return only the tile.

    Returns
    -------
    list
        Tiles in the k-ring.
    """
    corner_tile = origin

    # Traverse to top left corner
    for i in range(k):
        corner_tile = tile_sibling(corner_tile, LEFT)
        corner_tile = tile_sibling(corner_tile, UP)

    neighbors = []
    traversal_tile = 0

    for j in range(k * 2 + 1):
        traversal_tile = corner_tile
        for i in range(k * 2 + 1):
            if extra:
                neighbors.append((traversal_tile, chebishev_distance([i, j], [k, k])))
            else:
                neighbors.append(traversal_tile)
            traversal_tile = tile_sibling(traversal_tile, RIGHT)
        corner_tile = tile_sibling(corner_tile, DOWN)

    return neighbors


def chebishev_distance(u, v):
    """Compute the Chebishev distance between two 2D points."""
    return max(abs(u[0] - v[0]), abs(u[1] - v[1]))


def distinct(array):
    """Return distinct values of an array."""
    return list(set(array))


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
