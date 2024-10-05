
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

def custom_json_encoder(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def custom_jsonable_encoder(data):
    return jsonable_encoder(data, default=custom_json_encoder)
