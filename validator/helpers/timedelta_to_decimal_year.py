import datetime as dt


def timedelta_to_decimal_year(delta: dt.timedelta) -> float:
    """
    convert datetime timedelta to value in decimal years
    """
    return delta.total_seconds() / (60 * 60 * 24 * 365)
