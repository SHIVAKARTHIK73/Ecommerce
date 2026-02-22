from fastapi.security import OAuth2PasswordRequestForm
from hashing import verify_password
from auth import create_access_token

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
from models.user import User
from schemas.user import UserCreate
from hashing import hash_password
from fastapi.security import OAuth2PasswordBearer
from auth import verify_token
from models import product
from models.product import Product
from schemas.product import ProductCreate
from models import cart
from models.cart import Cart
from schemas.cart import CartAdd
from models import order
from models.order import Order, OrderItem
from fastapi.middleware.cors import CORSMiddleware





app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Ecommerce API Running"}

@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/auth/me")
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    email = verify_token(token)

    user = db.query(User).filter(User.email == email).first()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

def check_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

@app.post("/products/")
def add_product(
    product: ProductCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    check_admin(user)


    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        image_url=product.image_url,
        category=product.category,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Product added successfully"}
@app.get("/products/")
def get_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()

    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "image_url": p.image_url,
            "category": p.category,
            "stock": p.stock
        })

    return result
@app.get("/products/{product_id}")
def get_single_product(product_id: int, db: Session = Depends(get_db)):

    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "image_url": product.image_url,
        "category": product.category,
        "stock": product.stock
    }
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    updated: ProductCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    check_admin(user)

    product = db.query(Product).filter(Product.id == product_id).first()
    

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = updated.name
    product.description = updated.description
    product.price = updated.price
    product.image_url = updated.image_url
    product.category = updated.category
    product.stock = updated.stock

    db.commit()

    return {"message": "Product updated"}
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    check_admin(user)
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted"}

@app.post("/cart/add")
def add_to_cart(
    item: CartAdd,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(Cart).filter(
        Cart.user_id == user.id,
        Cart.product_id == item.product_id
    ).first()

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = Cart(
            user_id=user.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(cart_item)

    db.commit()

    return {"message": "Added to cart"}

@app.get("/cart/")
def view_cart(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()

    result = []
    total_price = 0

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        item_total = product.price * item.quantity
        total_price += item_total

        result.append({
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": item.quantity,
            "item_total": item_total
        })

    return {
        "cart_items": result,
        "total_price": total_price
    }
@app.put("/cart/update")
def update_cart(
    item: CartAdd,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    cart_item = db.query(Cart).filter(
        Cart.user_id == user.id,
        Cart.product_id == item.product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    cart_item.quantity = item.quantity
    db.commit()

    return {"message": "Cart updated"}
@app.delete("/cart/remove/{product_id}")
def remove_from_cart(
    product_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    cart_item = db.query(Cart).filter(
        Cart.user_id == user.id,
        Cart.product_id == product_id
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not in cart")

    db.delete(cart_item)
    db.commit()

    return {"message": "Item removed from cart"}

@app.post("/orders/")
def place_order(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0

    # Calculate total
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        total_amount += product.price * item.quantity

    # Create order
    new_order = Order(
        user_id=user.id,
        total_amount=total_amount,
        status="Pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Create order items
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        db.add(order_item)

    # Clear cart
    for item in cart_items:
        db.delete(item)

    db.commit()

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_amount": total_amount
    }

@app.get("/orders/")
def get_orders(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    orders = db.query(Order).filter(Order.user_id == user.id).all()

    result = []

    for order in orders:
        result.append({
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
            "created_at": order.created_at
        })

    return result
@app.get("/orders/{order_id}")
def get_single_order(
    order_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()

    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()

    items = []

    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        items.append({
            "product_name": product.name,
            "price": item.price,
            "quantity": item.quantity,
            "item_total": item.price * item.quantity
        })

    return {
        "order_id": order.id,
        "total_amount": order.total_amount,
        "status": order.status,
        "created_at": order.created_at,
        "items": items
    }
