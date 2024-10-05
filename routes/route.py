import json
from fastapi import APIRouter , Query , HTTPException , Body , Path ,UploadFile ,Form , File , FastAPI , Depends
from models.Product import Product , Cart
from models.cart import CartItem
from models.user import User
from config.database import collections
from schema.schemas import list_serial_product
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from _func import quick_sort , quick_sort_high_low , linear_search , get_password_hash , verify_password #,create_access_token 
import base64
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authentication import SECRET_KEY , ALGORITHM ,ACCESS_TOKEN_EXPIRE_MINUTES 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from costom_json import custom_jsonable_encoder


app = FastAPI()

# Configure CORS
origins = ["http://localhost:3000", "http://192.168.56.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()


@router.get("/")
async def get_products():
    products = list_serial_product(collections["product"].find())
    return products

@router.get("/sort/byPriceToHigh")
async def get_products_sortbyprice():
    products = list_serial_product(collections["product"].find())
    sorted_productsToHigh = quick_sort(products)
    return sorted_productsToHigh

@router.get("/sort/byPriceToLow")
async def get_products_sortbyprice():
    products = list_serial_product(collections["product"].find())
    sorted_productsToLow = quick_sort_high_low(products)
    return sorted_productsToLow

@router.get("/sort/byLimitPrice/{price}")
async def get_product_sortbylimitprice(price: float):
    products = list_serial_product(collections["product"].find())
    products = [product for product in products if product['price'] <= price]
    products = quick_sort(products)
    return products


@router.post("/")
async def post_product(
    name: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    type: str = Form(...),
    image_base64: str = Form(...),  # Handle image upload
):
    # Create a new product document with the image_base64 field properly set
    new_product = {
        "name": name,
        "price": price,
        "quantity": quantity,
        "type": type,
        "image_base64": image_base64  # Set the image_base64 field
    }

    # Insert the new product into the database
    inserted_product = collections["product"].insert_one(new_product)

    return {"message": "Product created successfully", "product_id": str(inserted_product.inserted_id)}



@router.put("/{id}")
async def put_product(id: str, product: Product):
    # Assuming 'collections' is a MongoDB collection
    # Use the 'update_one' method to update the document
    result = collections["product"].update_one(
        {"_id": ObjectId(id)},
        {"$set": dict(product)}
    )

    # Check if the update was successful
    if result.modified_count == 1:
        # Return the updated product
        return dict(product)
    else:
        # Product not found or update failed
        return {"message": "Product not found or update failed"}


@router.delete("/{id}")
async def delete_product(id: str):
    # Convert the ID to ObjectId
    object_id = ObjectId(id)

    # Try to find and delete the product
    result = collections["product"].find_one_and_delete({"_id": object_id})

    if result:
        return {"message": "Product deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@router.get("/search/product")
async def search_product_by_name_or_type(product_name_or_type: str):
    # Access the 'product' collection
    products = list_serial_product(collections["product"].find())

    # Use linear search to find products with matching names
    matching_products = linear_search(products, product_name_or_type)
    
    # Sort the matching products by price using Quick Sort
    sorted_products = quick_sort(matching_products)
    
    # You can further process 'sorted_products' as needed
    return sorted_products


shopping_cart = Cart(items=[])

@router.get("/cart")
async def view_cart():
    # Retrieve cart items from the "cart" collection
    cart_items = list(collections["cart"].find({}))

    # Create a list to store the details of items in the cart
    cart_details = []

    total_price = 0.0

    for cart_item in cart_items:
        # Retrieve product details based on the product_id stored in the cart
        product = collections["product"].find_one({"_id": cart_item["product_id"]})

        if product:
            item_price = product["price"]
            item_quantity = cart_item["quantity"]
            item_total_price = item_price * item_quantity

            total_price += item_total_price

            cart_details.append({
                "product_id": str(product["_id"]),
                "name": product["name"],
                "price": item_price,
                "quantity_in_cart": item_quantity,
                "item_total_price": item_total_price
            })

    return {"cart_items": cart_details, "total_price": total_price}

@router.post("/cart/add")
async def add_to_cart(product_id: str = Form(...), quantity: int = Form(...)):
    try:
        product_id = ObjectId(product_id)  # Ensure that the provided `product_id` is a valid ObjectId
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid product_id")

    # Check if the product is already in the cart
    cart_item = collections["cart"].find_one({"product_id": product_id})

    if cart_item:
        # Update quantity if the product is already in the cart
        new_quantity = cart_item["quantity"] + quantity
        collections["cart"].update_one(
            {"_id": ObjectId(cart_item["_id"])},
            {"$set": {"quantity": new_quantity}},
        )
    else:
        # Create a new cart item if it's not in the cart
        collections["cart"].insert_one(
            {"product_id": product_id, "quantity": quantity}
        )

    return {"message": "Item added to cart successfully"}


@router.post("/cart/remove/quantity")
async def remove_quantity_from_cart(product_id: str = Form(...), quantity: int = Form(...)):
    # Ensure that the provided `product_id` is a valid ObjectId
    try:
        product_id = ObjectId(product_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid product_id")

    # Check if the product is in the cart
    cart_item = collections["cart"].find_one({"product_id": product_id})

    if cart_item:
        current_quantity = cart_item["quantity"]

        # Ensure that the quantity to remove is not greater than the current quantity in the cart
        if quantity >= current_quantity:
            # If the quantity to remove is greater or equal to the current quantity, remove the entire item
            collections["cart"].delete_one({"_id": cart_item["_id"]})
            return {"message": f"Product {product_id} completely removed from the cart"}
        else:
            # Update the quantity in the cart by subtracting the specified quantity
            new_quantity = current_quantity - quantity
            collections["cart"].update_one(
                {"_id": cart_item["_id"]},
                {"$set": {"quantity": new_quantity}}
            )
            return {"message": f"{quantity} units of Product {product_id} removed from the cart"}
    else:
        raise HTTPException(status_code=404, detail="Product not found in the cart")


@router.post("/cart/checkout")
async def checkout_cart():
    # Retrieve cart items from the "cart" collection
    cart_items = list(collections["cart"].find({}))

    # Create a list to store the details of items in the cart
    cart_details = []

    for cart_item in cart_items:
        # Retrieve product details based on the product_id stored in the cart
        product = collections["product"].find_one({"_id": cart_item["product_id"]})

        if product:
            item_price = product["price"]
            item_quantity = cart_item["quantity"]

            # Ensure that the product has enough quantity in stock for the checkout
            if product["quantity"] >= item_quantity:
                # Update the product quantity in the "product" collection
                new_quantity = product["quantity"] - item_quantity
                collections["product"].update_one(
                    {"_id": product["_id"]},
                    {"$set": {"quantity": new_quantity}}
                )

                cart_details.append({
                    "product_id": str(product["_id"]),
                    "name": product["name"],
                    "price": item_price,
                    "quantity_in_cart": item_quantity
                })

                # Remove the product from the cart since it's been checked out
                collections["cart"].delete_one({"_id": cart_item["_id"]})
            else:
                return {"message": f"Insufficient stock for Product {product['_id']}"}

    return {"message": "Checkout successful", "cart_items": cart_details}

@router.post("/register")
async def register_user(user: User):
    # Check if the username is already in use
    if collections["user"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    # In a real application, you would hash the password and store the user data in MongoDB
    hashed_password = get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "password": hashed_password,
        "wishlist": [],
    }
    collections["user"].insert_one(user_data)
    return {"message": "User registered successfully"}


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Check if the user exists
    user = collections["user"].find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Generate an access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}













