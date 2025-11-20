from datetime import datetime

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj
