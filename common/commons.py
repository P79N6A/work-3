import datetime
import time
"""公用的方法"""


def to_dict(obj, attrs):
    res = {}
    for attr in attrs:
        value = getattr(obj, attr)
        res[attr] = value if value is not None else ""
    return res


def datetime_2_timestamp(date):
    """datetime转时间戳"""
    if isinstance(date, datetime.datetime):
        return int(time.mktime(date.timetuple()))
    return None
