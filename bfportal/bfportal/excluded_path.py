def custom_preprocessing_hook(endpoints):
    """Exclude paths from openapi spec"""
    filtered = []
    for path, path_regex, method, callback in endpoints:
        if "admin" not in path:
            filtered.append((path, path_regex, method, callback))
    return filtered
