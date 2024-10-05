from passlib.context import CryptContext

from datetime import datetime, timedelta
from authentication import SECRET_KEY , ALGORITHM ,ACCESS_TOKEN_EXPIRE_MINUTES



def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]['price']
        less_than_pivot = []
        greater_than_pivot = []
        
        for item in arr[1:]:
            if item['price'] < pivot:
                less_than_pivot.append(item)
            else:
                greater_than_pivot.append(item)
        
        sorted_less = quick_sort(less_than_pivot)
        sorted_greater = quick_sort(greater_than_pivot)
        
        return sorted_less + [arr[0]] + sorted_greater



def quick_sort_high_low(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]['price']
        less_than_pivot = []
        greater_than_pivot = []
        
        for item in arr[1:]:
            if item['price'] < pivot:
                less_than_pivot.append(item)
            else:
                greater_than_pivot.append(item)
        
        sorted_greater = quick_sort_high_low(greater_than_pivot)
        sorted_less = quick_sort_high_low(less_than_pivot)
        
        return sorted_greater + [arr[0]] + sorted_less

    

def linear_search(products, search_name):
    matching_products = []
    for product in products:
        if search_name.lower() in product['name'].lower() or search_name.lower() in product.get('type', '').lower():
            matching_products.append(product)
    return matching_products


def calculate_cart_total(cart, products):
    total = 0.0
    for cart_item in cart.items:
        product = next((p for p in products if str(p['_id']) == cart_item.product_id), None)
        if product:
            total += product['price'] * cart_item.quantity
    return total

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Token functions for authentication
#def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt







