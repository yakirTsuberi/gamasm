def base_to_dict(query):
    def _create_dict(r):
        return {k: v for k, v in r._asdict().items()}

    if isinstance(query, list):
        return [_create_dict(r) for r in query]
    return _create_dict(query)
