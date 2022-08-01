ABS_MAX_LONGITUDE = 180.0
ABS_MAX_LATITUDE = 85.051129


def clip_number(num, a, b):
    return max(min(num, b), a)
