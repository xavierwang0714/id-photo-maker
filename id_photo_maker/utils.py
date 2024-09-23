def list_json_keys(json_obj, parent_key=''):
    keys = []
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            keys.append(full_key)
            keys.extend(list_json_keys(v, full_key))
    elif isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            full_key = f"{parent_key}[{i}]"
            keys.extend(list_json_keys(item, full_key))
    return keys