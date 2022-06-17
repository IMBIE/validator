import datetime as dt
import calendar


def decimal_year_to_datetime(year: float) -> dt.datetime:
    int_year = int(year)
    year_fraction = year - int_year

    year_days = 366 if calendar.isleap(int_year) else 365
    return dt.datetime(year=int_year, month=1, day=1) + dt.timedelta(
        days=year_fraction * year_days
    )
