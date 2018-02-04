import datetime

COMPANIES = {
    'cellcom': 'סלקום',
    'partner': 'פרטנר',
    'pelephon': 'פלאפון',
    'mobile_012': '012 מובייל',
    'hot_mobile': 'הוט מובייל',
    'golan_telecom': 'גולן טלקום',
    'rami_levi': 'רמי לוי'
}


def base_to_dict(query):
    def _create_dict(r):
        return {k: v for k, v in r._asdict().items()}

    if isinstance(query, list):
        return [_create_dict(r) for r in query]
    return _create_dict(query)


def datetime_handler(x):
    if isinstance(x, datetime.datetime) or isinstance(x, datetime.date):
        if isinstance(x, datetime.datetime):
            x = x.replace(microsecond=0)
        return str(x)


def verify_request(request, params):
    if params is not None:
        return all(p in params for p in request.json)


if __name__ == '__main__':
    pass
