

def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            data[field_name] = getattr(obj, field_name)

    return data
