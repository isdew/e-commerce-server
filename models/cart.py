from pydantic import BaseModel

class CartItem(BaseModel):
    product_id: str  # This will store the ObjectId of the product
    quantity: int


