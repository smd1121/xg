import datetime


def timestamp_to_str(time_s: int, time_ns: int) -> str:
    dt = datetime.datetime.fromtimestamp(time_s)
    microseconds = time_ns // 1000
    dt = dt + datetime.timedelta(microseconds=microseconds)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
