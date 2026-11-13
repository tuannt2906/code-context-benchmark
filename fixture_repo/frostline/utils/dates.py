"""Date helpers. Dates are ISO strings (YYYY-MM-DD) throughout the code base."""

import datetime


def parse_date(text):
    return datetime.date(*[int(p) for p in text.split("-")])


def days_between(start, end):
    return (parse_date(end) - parse_date(start)).days


def is_weekend(text):
    return parse_date(text).weekday() >= 5
