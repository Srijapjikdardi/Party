from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, create_engine, select
from typing import List, Optional
from pathlib import Path
from . import models, crud
from .auth import verify_password, create_token, get_user_id_from_token, revoke_token

# ──────────────────────────────────────────────────────────
# DATABASE SETUP
# ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/partype.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# ──────────────────────────────────────────────────────────
# AUTH HELPER
# ──────────────────────────────────────────────────────────
def get_current_user(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)) -> models.User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    user_id = get_user_id_from_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = crud.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def get_optional_user(authorization: Optional[str] = Header(None), session: Session = Depends(get_session)) -> Optional[models.User]:
    try:
        return get_current_user(authorization, session)
    except HTTPException:
        return None

# ──────────────────────────────────────────────────────────
# APP
# ──────────────────────────────────────────────────────────
app = FastAPI(title="PartyPe API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(models.Restaurant)).first():
            crud.create_sample_data(session)

# Serve frontend
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = BASE_DIR / "frontend" / "index.html"
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=200)

# ──────────────────────────────────────────────────────────
# HEALTH
# ──────────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {"status": "ok", "app": "PartyPe API v2"}

# ──────────────────────────────────────────────────────────
# AUTH ROUTES
# ──────────────────────────────────────────────────────────
@app.post("/api/auth/signup", response_model=dict)
def signup(user_data: models.UserCreate, session: Session = Depends(get_session)):
    existing = crud.get_user_by_email(session, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(session, user_data)
    token = create_token(user.id)
    return {"token": token, "user": models.UserRead.from_orm(user)}

@app.post("/api/auth/signin", response_model=dict)
def signin(creds: models.UserLogin, session: Session = Depends(get_session)):
    user = crud.get_user_by_email(session, creds.email)
    if not user or not verify_password(creds.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id)
    return {"token": token, "user": models.UserRead.from_orm(user)}

@app.post("/api/auth/signout")
def signout(authorization: Optional[str] = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        revoke_token(authorization.split(" ", 1)[1])
    return {"message": "Signed out"}

@app.get("/api/users/me", response_model=models.UserRead)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

# ──────────────────────────────────────────────────────────
# RESTAURANTS
# ──────────────────────────────────────────────────────────
@app.get("/api/restaurants", response_model=List[models.RestaurantRead])
def read_restaurants(skip: int = 0, limit: int = 100, cuisine: Optional[str] = None, session: Session = Depends(get_session)):
    return crud.get_restaurants(session, skip=skip, limit=limit, cuisine=cuisine)

@app.get("/api/restaurants/{restaurant_id}", response_model=models.RestaurantRead)
def read_restaurant(restaurant_id: int, session: Session = Depends(get_session)):
    restaurant = crud.get_restaurant(session, restaurant_id=restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@app.get("/api/restaurants/{restaurant_id}/menu", response_model=List[models.MenuItemRead])
def read_menu(restaurant_id: int, session: Session = Depends(get_session)):
    return crud.get_menu_items_by_restaurant(session, restaurant_id=restaurant_id)

@app.get("/api/restaurants/{restaurant_id}/tables", response_model=List[models.TableRead])
def read_tables(restaurant_id: int, session: Session = Depends(get_session)):
    return crud.get_tables_by_restaurant(session, restaurant_id=restaurant_id)

# ──────────────────────────────────────────────────────────
# DINING SESSIONS
# ──────────────────────────────────────────────────────────
@app.post("/api/sessions", response_model=models.DiningSessionRead)
def create_session(data: models.DiningSessionCreate, session: Session = Depends(get_session)):
    return crud.create_dining_session(session, data)

@app.get("/api/sessions/{session_id}", response_model=models.DiningSessionRead)
def read_session(session_id: int, session: Session = Depends(get_session)):
    ds = crud.get_dining_session(session, session_id)
    if not ds:
        raise HTTPException(status_code=404, detail="Session not found")
    return ds

@app.post("/api/sessions/join/{session_code}", response_model=models.DiningSessionRead)
def join_session(session_code: str, current_user: models.User = Depends(get_current_user), session: Session = Depends(get_session)):
    ds = crud.join_dining_session(session, session_code.upper(), current_user.id)
    if not ds:
        raise HTTPException(status_code=404, detail="Session not found or not active")
    return ds

@app.get("/api/sessions/{session_id}/participants", response_model=List[models.SessionParticipantRead])
def read_participants(session_id: int, session: Session = Depends(get_session)):
    return crud.get_session_participants(session, session_id)

# ──────────────────────────────────────────────────────────
# ORDERS
# ──────────────────────────────────────────────────────────
@app.post("/api/orders", response_model=models.OrderRead)
def create_order(order: models.OrderCreate, session: Session = Depends(get_session)):
    return crud.create_order(session=session, order=order)

@app.get("/api/orders/{order_id}", response_model=models.OrderRead)
def read_order(order_id: int, session: Session = Depends(get_session)):
    order = crud.get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/orders/user/{user_id}", response_model=List[models.OrderRead])
def read_user_orders(user_id: int, session: Session = Depends(get_session)):
    return crud.get_orders_by_user(session, user_id)

@app.patch("/api/orders/{order_id}/status", response_model=models.OrderRead)
def update_status(order_id: int, update: models.OrderStatusUpdate, session: Session = Depends(get_session)):
    order = crud.update_order_status(session, order_id, update.status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ──────────────────────────────────────────────────────────
# WALLET
# ──────────────────────────────────────────────────────────
@app.get("/api/wallet", response_model=dict)
def get_wallet(current_user: models.User = Depends(get_current_user), session: Session = Depends(get_session)):
    transactions = crud.get_wallet_transactions(session, current_user.id)
    return {
        "balance": current_user.wallet_balance,
        "transactions": [models.WalletTransactionRead.from_orm(t) for t in transactions]
    }

@app.post("/api/wallet/topup", response_model=models.WalletTransactionRead)
def wallet_topup(topup: models.WalletTopup, current_user: models.User = Depends(get_current_user), session: Session = Depends(get_session)):
    if topup.amount <= 0 or topup.amount > 50000:
        raise HTTPException(status_code=400, detail="Invalid amount")
    txn = crud.topup_wallet(session, current_user.id, topup.amount, topup.payment_method)
    return txn

@app.post("/api/wallet/pay", response_model=dict)
def wallet_pay(body: dict, current_user: models.User = Depends(get_current_user), session: Session = Depends(get_session)):
    amount = body.get("amount", 0)
    description = body.get("description", "Payment")
    success = crud.pay_from_wallet(session, current_user.id, amount, description)
    if not success:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    return {"success": True, "message": "Payment successful"}

# ──────────────────────────────────────────────────────────
# NOTIFICATIONS
# ──────────────────────────────────────────────────────────
@app.get("/api/notifications", response_model=List[models.NotificationRead])
def get_notifications(current_user: models.User = Depends(get_current_user), session: Session = Depends(get_session)):
    return crud.get_notifications(session, current_user.id)

@app.post("/api/notifications/read-all")
def mark_notifications_read(current_user: models.User = Depends(get_current_user), session: Session = Depends(get_session)):
    crud.mark_all_read(session, current_user.id)
    return {"message": "All notifications marked as read"}

# ──────────────────────────────────────────────────────────
# MERCHANT ENDPOINTS
# ──────────────────────────────────────────────────────────
@app.get("/api/merchant/orders", response_model=List[models.OrderRead])
def merchant_orders(restaurant_id: int, limit: int = 50, session: Session = Depends(get_session)):
    return crud.get_orders_by_restaurant(session, restaurant_id, limit)

@app.get("/api/merchant/tables", response_model=List[models.TableRead])
def merchant_tables(restaurant_id: int, session: Session = Depends(get_session)):
    return crud.get_tables_by_restaurant(session, restaurant_id)

@app.patch("/api/merchant/tables/{table_id}/status")
def update_table_status(table_id: int, body: dict, session: Session = Depends(get_session)):
    table = crud.update_table_status(session, table_id, body.get("status", "available"))
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return models.TableRead.from_orm(table)

@app.get("/api/merchant/analytics")
def merchant_analytics(restaurant_id: int, session: Session = Depends(get_session)):
    orders = crud.get_orders_by_restaurant(session, restaurant_id, limit=200)
    total_revenue = sum(o.total_amount for o in orders)
    delivered = [o for o in orders if o.status == "delivered"]
    pending = [o for o in orders if o.status in ("pending", "confirmed", "preparing")]
    return {
        "total_revenue": total_revenue,
        "total_orders": len(orders),
        "delivered_orders": len(delivered),
        "pending_orders": len(pending),
        "avg_order_value": total_revenue / len(orders) if orders else 0,
    }