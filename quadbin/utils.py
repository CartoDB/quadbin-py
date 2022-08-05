import math

MAX_LONGITUDE = 180.0
MIN_LONGITUDE = -MAX_LONGITUDE
MAX_LATITUDE = 85.051129
MIN_LATITUDE = -MAX_LATITUDE


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
    z = resolution
    powz = 1 << z
    tanlat = math.tan(math.pi / 4.0 + latitude / 2.0 * math.pi / 180.0)
    x = int(math.floor(powz * ((longitude / 360.0) + 0.5))) & (powz - 1)
    y = int(math.floor(powz * (0.5 - (math.log(tanlat) / (2 * math.pi))))) & (powz - 1)

    return (x, y, z)
