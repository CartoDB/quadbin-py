import math

from .utils import ABS_MAX_LONGITUDE, ABS_MAX_LATITUDE, clip_number


def cell_is_valid(index):
    header = 0x4000000000000000
    mode = (index >> 59) & 7
    resolution = (index >> 52) & 0x1F
    unused = 0xFFFFFFFFFFFFF >> (resolution << 2)
    return (
        index >= 0
        and (index & header == header)
        and mode in [0, 1, 2, 3, 4, 5, 6]
        and resolution >= 0
        and resolution <= 26
        and (index & unused == unused)
    )


def cell_to_tile(index):
    b = [
        0x5555555555555555,
        0x3333333333333333,
        0x0F0F0F0F0F0F0F0F,
        0x00FF00FF00FF00FF,
        0x0000FFFF0000FFFF,
        0x00000000FFFFFFFF,
    ]
    s = [1, 2, 4, 8, 16]

    # mode = (index >> 59) & 7
    # extra = (index >> 57) & 3
    z = index >> 52 & 31
    q = (index & 0xFFFFFFFFFFFFF) << 12
    x = q
    y = q >> 1
    x = x & b[0]
    y = y & b[0]

    x = (x | (x >> s[0])) & b[1]
    y = (y | (y >> s[0])) & b[1]

    x = (x | (x >> s[1])) & b[2]
    y = (y | (y >> s[1])) & b[2]

    x = (x | (x >> s[2])) & b[3]
    y = (y | (y >> s[2])) & b[3]

    x = (x | (x >> s[3])) & b[4]
    y = (y | (y >> s[3])) & b[4]

    x = (x | (x >> s[4])) & b[5]
    y = (y | (y >> s[4])) & b[5]

    x = x >> (32 - z)
    y = y >> (32 - z)
    return {"z": z, "x": x, "y": y}


def tile_to_cell(z, x, y):
    x = x << (32 - z)
    y = y << (32 - z)

    b = [
        0x5555555555555555,
        0x3333333333333333,
        0x0F0F0F0F0F0F0F0F,
        0x00FF00FF00FF00FF,
        0x0000FFFF0000FFFF,
    ]
    s = [1, 2, 4, 8, 16]

    x = (x | (x << s[4])) & b[4]
    y = (y | (y << s[4])) & b[4]

    x = (x | (x << s[3])) & b[3]
    y = (y | (y << s[3])) & b[3]

    x = (x | (x << s[2])) & b[2]
    y = (y | (y << s[2])) & b[2]

    x = (x | (x << s[1])) & b[1]
    y = (y | (y << s[1])) & b[1]

    x = (x | (x << s[0])) & b[0]
    y = (y | (y << s[0])) & b[0]

    # -- | (mode << 59) | (mode_dep << 57)
    return (
        0x4000000000000000
        | (1 << 59)
        | (z << 52)
        | ((x | (y << 1)) >> 12)
        | (0xFFFFFFFFFFFFF >> (z * 2))
    )


def cell_to_point(index):
    tile = cell_to_tile(index)

    expy = math.exp(-(2.0 * (tile["y"] + 0.5) / (1 << tile["z"]) - 1) * math.pi)
    longitude = 180 * (2.0 * (tile["x"] + 0.5) / (1 << tile["z"]) - 1.0)
    latitude = 360 * (math.atan(expy) / math.pi - 0.25)

    return [longitude, latitude]


def point_to_cell(longitude, latitude, resolution):
    if resolution < 0 or resolution > 26:
        raise Exception("Invalid resolution: should be between 0 and 26")

    longitude = clip_number(longitude, -ABS_MAX_LONGITUDE, ABS_MAX_LONGITUDE)
    latitude = clip_number(latitude, -ABS_MAX_LATITUDE, ABS_MAX_LATITUDE)

    z = resolution
    powz = 1 << z
    tanlat = math.tan(math.pi / 4.0 + latitude / 2.0 * math.pi / 180.0)
    x = int(math.floor(powz * ((longitude / 360.0) + 0.5))) & (powz - 1)
    y = int(math.floor(powz * (0.5 - (math.log(tanlat) / (2 * math.pi))))) & (powz - 1)

    return tile_to_cell(z, x, y)


def get_resolution(index):
    return (index >> 52) & 0x1F
