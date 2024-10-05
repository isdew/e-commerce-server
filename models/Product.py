from pydantic import BaseModel
from models.cart import CartItem
from typing import List


class Product(BaseModel):
    name: str 
    price: float 
    quantity: int 
    type: str 
    image_base64: str 
     



class Cart(BaseModel):
    items: List[CartItem]
     




