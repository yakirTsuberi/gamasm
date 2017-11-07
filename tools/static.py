import datetime


def base_to_dict(query):
    def _create_dict(r):
        return {k: v for k, v in r._asdict().items()}

    if isinstance(query, list):
        return [_create_dict(r) for r in query]
    return _create_dict(query)


def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return str(x.replace(microsecond=0))
    raise TypeError("Unknown type")


if __name__ == '__main__':
    pass
