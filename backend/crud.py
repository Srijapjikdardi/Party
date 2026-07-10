from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from . import models
from .auth import hash_password

# ──────────────────────────────────────────────────────────
# USERS
# ──────────────────────────────────────────────────────────
def get_user_by_email(session: Session, email: str) -> Optional[models.User]:
    return session.exec(select(models.User).where(models.User.email == email)).first()

def get_user_by_id(session: Session, user_id: int) -> Optional[models.User]:
    return session.get(models.User, user_id)

def create_user(session: Session, user_data: models.UserCreate) -> models.User:
    user = models.User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        wallet_balance=500.0,  # Welcome bonus
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    # Add welcome notification
    notif = models.Notification(
        user_id=user.id,
        title="Welcome to PartyPe! 🎉",
        body="Your account is ready. You have ₹500 in your wallet to get started.",
        icon="celebration"
    )
    session.add(notif)
    session.commit()
    return user

# ──────────────────────────────────────────────────────────
# RESTAURANTS
# ──────────────────────────────────────────────────────────
def get_restaurants(session: Session, skip: int = 0, limit: int = 100, cuisine: Optional[str] = None) -> List[models.Restaurant]:
    query = select(models.Restaurant).where(models.Restaurant.is_active == True).offset(skip).limit(limit)
    if cuisine:
        query = query.where(models.Restaurant.cuisine_type == cuisine)
    return session.exec(query).all()

def get_restaurant(session: Session, restaurant_id: int) -> Optional[models.Restaurant]:
    return session.get(models.Restaurant, restaurant_id)

def get_menu_items_by_restaurant(session: Session, restaurant_id: int) -> List[models.MenuItem]:
    statement = select(models.MenuItem).where(
        models.MenuItem.restaurant_id == restaurant_id,
        models.MenuItem.is_available == True
    )
    return session.exec(statement).all()

# ──────────────────────────────────────────────────────────
# TABLES
# ──────────────────────────────────────────────────────────
def get_tables_by_restaurant(session: Session, restaurant_id: int) -> List[models.Table]:
    return session.exec(select(models.Table).where(models.Table.restaurant_id == restaurant_id)).all()

def get_table(session: Session, table_id: int) -> Optional[models.Table]:
    return session.get(models.Table, table_id)

def update_table_status(session: Session, table_id: int, status: str) -> Optional[models.Table]:
    table = session.get(models.Table, table_id)
    if table:
        table.status = status
        session.add(table)
        session.commit()
        session.refresh(table)
    return table

# ──────────────────────────────────────────────────────────
# DINING SESSIONS
# ──────────────────────────────────────────────────────────
def create_dining_session(session: Session, data: models.DiningSessionCreate) -> models.DiningSession:
    dining_session = models.DiningSession(
        restaurant_id=data.restaurant_id,
        table_id=data.table_id,
        host_user_id=data.host_user_id,
    )
    session.add(dining_session)
    session.commit()
    session.refresh(dining_session)
    # Auto-add host as participant
    participant = models.SessionParticipant(
        session_id=dining_session.id,
        user_id=data.host_user_id,
    )
    session.add(participant)
    # Update table status
    if data.table_id:
        table = session.get(models.Table, data.table_id)
        if table:
            table.status = "occupied"
            session.add(table)
    session.commit()
    return dining_session

def get_dining_session(session: Session, session_id: int) -> Optional[models.DiningSession]:
    return session.get(models.DiningSession, session_id)

def get_dining_session_by_code(session: Session, code: str) -> Optional[models.DiningSession]:
    return session.exec(select(models.DiningSession).where(models.DiningSession.session_code == code)).first()

def join_dining_session(session: Session, session_code: str, user_id: int) -> Optional[models.DiningSession]:
    dining_session = get_dining_session_by_code(session, session_code)
    if not dining_session or dining_session.status != "active":
        return None
    # Check already joined
    existing = session.exec(
        select(models.SessionParticipant).where(
            models.SessionParticipant.session_id == dining_session.id,
            models.SessionParticipant.user_id == user_id
        )
    ).first()
    if not existing:
        participant = models.SessionParticipant(
            session_id=dining_session.id,
            user_id=user_id,
        )
        session.add(participant)
        session.commit()
    return dining_session

def get_session_participants(session: Session, session_id: int) -> List[models.SessionParticipant]:
    return session.exec(select(models.SessionParticipant).where(models.SessionParticipant.session_id == session_id)).all()

# ──────────────────────────────────────────────────────────
# ORDERS
# ──────────────────────────────────────────────────────────
def create_order(session: Session, order: models.OrderCreate) -> models.Order:
    order_dict = order.dict()
    order_items = order_dict.pop("order_items", [])
    db_order = models.Order(**order_dict)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    for item in order_items:
        item["order_id"] = db_order.id
        db_item = models.OrderItem(**item)
        session.add(db_item)
    session.commit()
    session.refresh(db_order)
    return db_order

def get_order(session: Session, order_id: int) -> Optional[models.Order]:
    return session.get(models.Order, order_id)

def get_orders_by_user(session: Session, user_id: int) -> List[models.Order]:
    return session.exec(select(models.Order).where(models.Order.user_id == user_id).order_by(models.Order.created_at.desc())).all()

def get_orders_by_restaurant(session: Session, restaurant_id: int, limit: int = 50) -> List[models.Order]:
    return session.exec(select(models.Order).where(models.Order.restaurant_id == restaurant_id).order_by(models.Order.created_at.desc()).limit(limit)).all()

def update_order_status(session: Session, order_id: int, status: str) -> Optional[models.Order]:
    order = session.get(models.Order, order_id)
    if order:
        order.status = status
        order.updated_at = datetime.utcnow()
        session.add(order)
        session.commit()
        session.refresh(order)
    return order

# ──────────────────────────────────────────────────────────
# WALLET
# ──────────────────────────────────────────────────────────
def get_wallet_transactions(session: Session, user_id: int) -> List[models.WalletTransaction]:
    return session.exec(
        select(models.WalletTransaction).where(models.WalletTransaction.user_id == user_id).order_by(models.WalletTransaction.created_at.desc()).limit(20)
    ).all()

def topup_wallet(session: Session, user_id: int, amount: float, method: str) -> models.WalletTransaction:
    user = session.get(models.User, user_id)
    user.wallet_balance += amount
    session.add(user)
    txn = models.WalletTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type="credit",
        description=f"Wallet top-up via {method}",
        reference_id=f"TXN{int(datetime.utcnow().timestamp())}"
    )
    session.add(txn)
    session.commit()
    session.refresh(txn)
    return txn

def pay_from_wallet(session: Session, user_id: int, amount: float, description: str) -> bool:
    user = session.get(models.User, user_id)
    if user.wallet_balance < amount:
        return False
    user.wallet_balance -= amount
    session.add(user)
    txn = models.WalletTransaction(
        user_id=user_id,
        amount=amount,
        transaction_type="debit",
        description=description,
        reference_id=f"PAY{int(datetime.utcnow().timestamp())}"
    )
    session.add(txn)
    session.commit()
    return True

# ──────────────────────────────────────────────────────────
# NOTIFICATIONS
# ──────────────────────────────────────────────────────────
def get_notifications(session: Session, user_id: int) -> List[models.Notification]:
    return session.exec(
        select(models.Notification).where(models.Notification.user_id == user_id).order_by(models.Notification.created_at.desc())
    ).all()

def mark_all_read(session: Session, user_id: int):
    notifs = session.exec(select(models.Notification).where(models.Notification.user_id == user_id, models.Notification.is_read == False)).all()
    for n in notifs:
        n.is_read = True
        session.add(n)
    session.commit()

# ──────────────────────────────────────────────────────────
# SAMPLE DATA SEEDER
# ──────────────────────────────────────────────────────────
def create_sample_data(session: Session):
    # Default users
    admin = models.User(
        name="Admin PartyPe",
        email="admin@partype.com",
        phone="9999999990",
        password_hash=hash_password("admin123"),
        role="admin",
        wallet_balance=10000.0
    )
    merchant = models.User(
        name="Rajesh Kumar",
        email="merchant@partype.com",
        phone="9999999991",
        password_hash=hash_password("merchant123"),
        role="merchant",
        wallet_balance=5000.0
    )
    waiter = models.User(
        name="Priya Singh",
        email="waiter@partype.com",
        phone="9999999992",
        password_hash=hash_password("waiter123"),
        role="waiter",
        wallet_balance=500.0
    )
    diner = models.User(
        name="Aarav Sharma",
        email="demo@partype.com",
        phone="9999999993",
        password_hash=hash_password("demo123"),
        role="diner",
        wallet_balance=2500.0
    )
    session.add_all([admin, merchant, waiter, diner])
    session.commit()
    for u in [admin, merchant, waiter, diner]:
        session.refresh(u)

    # Restaurants
    restaurants_data = [
        {
            "name": "Spice Route",
            "address": "12 Connaught Place, New Delhi",
            "phone": "011-2345-6789",
            "cuisine_type": "Modern Indian",
            "rating": 4.6,
            "price_range": "₹300-800",
            "description": "Experience the evolution of Indian cuisine. Our signature slow-cooked Dal Makhani is simmered for 24 hours over traditional charcoal.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDC4IqU0Yzozi3FmVD8eAqPNwK0XJgX-RPXiC1vA-kAjQxqr3J7LCXiQDhI5iiBEKlWSYHDFe0SzcUWQxpnA6tmGEcRi9Gy6_QQQ9DWXkyN27Q_nysK1h-jDV66RpQlxtzpMFzOkdCcnKYaXCyamL-EunXarnII_pVYwaH0qOeEW5Et89btJSQwbUnkuPg0BpHGhEJltQ1i1zZBD3BruxDBVBxYirAG3QJ2AjRK39IL9_GvJNIbu0UNAw7qVtk2fWLZa_IxRGmOXA8",
            "owner_id": merchant.id
        },
        {
            "name": "Artisan Kitchen",
            "address": "45 Indiranagar, Bengaluru",
            "phone": "080-4567-8901",
            "cuisine_type": "Farm-to-Table",
            "rating": 4.8,
            "price_range": "₹500-1200",
            "description": "Locally sourced ingredients crafted into seasonal masterpieces. Where food tells the story of its origin.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuA6lRWwX7rqdLNKzDEN0NiJhLnOQvRcVm307pV3Mb_oJcTlkDWcH2klWZ4Rc3x6XFScxqHvmPS3zkUU5XyYO2_3mbOQyQOURSFfBQs3NNockoYAXSSQKvSbfYn8wfKGBJOD4QDDb4mj6Mo7SeJOIq1SUTNv7IxrUb-1v-x7gKrRL22WQFluVBQSiNyDF_x9y1hrSax8ZnrUcX6qujmoYgDW6QvDH8CSn5P2T-IFX396o8uJx5TwEH_OsCawytIqqNNpXnTY9e2wXps",
            "owner_id": None
        },
        {
            "name": "Tokyo Tales",
            "address": "88 Powai, Mumbai",
            "phone": "022-6789-0123",
            "cuisine_type": "Japanese",
            "rating": 4.4,
            "price_range": "₹800-2000",
            "description": "Authentic Japanese gastronomy — from hand-rolled sushi to ramen that warms the soul.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCboTUOOOCc8vJwJQvhI48TF2nU2MLLNG_nM3jY1xhbBVWlH_YxcPvQDJJNlzy7grjtc8SnYlhI_J6TZi2nQovyF8AJshmkPfkDAhN4Rl26nXu553WG3AU-Gd52NI6_NhVN4nLaEgHVwnVEbiw5ukRlsj8mRBjuaobQpyg4pu6qS6RffdAOjnLPNkDXBf0bh4Vxn_YfaJ_KVfXqmiotB_P3dS9y67HBS8uvBpj8zuJ2uhPNE2T9qLfUtbJuUY5cIqyIM7Y_WmFxmpw",
            "owner_id": None
        },
        {
            "name": "Verde Terrace",
            "address": "22 Bandra West, Mumbai",
            "phone": "022-9876-5432",
            "cuisine_type": "Mediterranean",
            "rating": 4.7,
            "price_range": "₹600-1500",
            "description": "A sun-drenched rooftop experience with the finest Mediterranean flavors and spectacular views.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAXiQB-5ZF7LH8XoC65SvuSQ8YbaXwGsmxAddZMxNLQbiEmn02-Fqhu579xnQiv77LxdUabfspYy6x1sDhCqc0XJ2m3I9gEnrD4_ZlBNGRD9p5os6lo_TK1mQ4o4J5BXliElTdQe24JWQyKXLERkvABSmtmtocqC3UrWg9wlwHXsLL33eh3xyrtXvx6hSm2ZQBt3Jr0328oW57K6LV-mCMPXbawEQXU-OKmJwZvL2elQxn8-BbS07-ABsbvsGEUwnJcCoqdl4pjyCU",
            "owner_id": None
        },
        {
            "name": "Smoke & Soul",
            "address": "7 Koramangala, Bengaluru",
            "phone": "080-2233-4455",
            "cuisine_type": "American BBQ",
            "rating": 4.5,
            "price_range": "₹400-900",
            "description": "Low and slow is the only way. Authentic wood-smoked BBQ with craft beer pairings.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuB-A0zMsdfJDRl1nLCYXIWEW7ksSx5y8DtdUVc7ZyCJW3jCp1OhrU-IPjt0NAkPQLzrS0bqqZcQ6kFy5YYV-hZcJMJzRTr-aFE83gveEnu3UZxMD1LAHQ9K7PjdHsPMg65U4Xv2DjUjuplMMxW-y9kiGU34MgmLjfhwur66q1T619m4IDL3MyZm74axhIXp5w8Skrm6q-fA-08QBfBvAI7wfTZDvbO0lM1Oc2Pw-k8gZqlbgOEmyMNrHqaaNyUwP2-dLodY70DiZOc",
            "owner_id": None
        },
        {
            "name": "Little Italy",
            "address": "14 Jubilee Hills, Hyderabad",
            "phone": "040-5566-7788",
            "cuisine_type": "Italian",
            "rating": 4.3,
            "price_range": "₹350-750",
            "description": "Nonna's recipes, reimagined for the modern palate. Handmade pasta and wood-fired pizza.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCBp922TUYyqs9_3lDIUbvz_ny_Uz7O22FC1PqEd47s3bkOWoXQL5fBX1dL6q2aXCh6PWRZda_tN6oms_RKjt84SKxBXJJGSYpf_4Fk_biWtSHYVs5A2O5v2R94EwK5C2M8CopRTTPqI4Egj-7I-4vp-FKIYqipbEkQK9XQ3vVzRJB0xKVITi-Dp_hdz3yS7OE2ltKvUeHeBHdG97iivY1L2DJjUe7sO0juJIS-4Rla-rks-VmvPiCDzqWYuEyGco4IOvkPSl7bVWQ",
            "owner_id": None
        },
    ]

    rest_objects = []
    for r in restaurants_data:
        rest = models.Restaurant(**r)
        session.add(rest)
        rest_objects.append(rest)
    session.commit()
    for r in rest_objects:
        session.refresh(r)

    # Tables for Spice Route
    for i in range(1, 13):
        status = "occupied" if i in [1, 3, 4, 6] else "available"
        t = models.Table(restaurant_id=rest_objects[0].id, number=f"T{i:02d}", capacity=4 if i % 2 == 0 else 6, status=status)
        session.add(t)
    session.commit()

    # Menu items per restaurant
    menus = {
        0: [  # Spice Route
            ("Butter Chicken", "Creamy tomato-based chicken curry with cashew paste", 645, "Main Course", True, False),
            ("Paneer Tikka", "Chargrilled cottage cheese with spiced marinade", 525, "Starters", True, True),
            ("Garlic Naan", "Freshly baked flatbread with garlic and butter", 145, "Breads", True, True),
            ("Dal Makhani", "Black lentils slow-cooked for 24 hours over charcoal", 385, "Main Course", True, True),
            ("Gulab Jamun", "Soft milk-solid dumplings in rose-flavoured sugar syrup", 195, "Desserts", True, True),
            ("Masala Chai", "Traditional spiced tea with ginger and cardamom", 85, "Beverages", True, True),
        ],
        1: [  # Artisan Kitchen
            ("Burrata Salad", "Fresh burrata with heirloom tomatoes and basil oil", 650, "Starters", True, True),
            ("Wild Mushroom Pasta", "Hand-rolled tagliatelle with seasonal mushrooms", 780, "Mains", True, True),
            ("Pan-Seared Salmon", "Atlantic salmon with lemon butter and capers", 1100, "Mains", True, False),
            ("Tiramisu", "Classic Italian dessert with espresso and mascarpone", 420, "Desserts", True, True),
        ],
        2: [  # Tokyo Tales
            ("Tuna Sashimi", "Premium bluefin tuna, 6 pieces", 950, "Sashimi", True, False),
            ("Wagyu Ramen", "12-hour bone broth with A5 Wagyu and soft egg", 1450, "Ramen", True, False),
            ("Gyoza", "Pan-fried dumplings with pork and cabbage", 380, "Starters", True, False),
            ("Matcha Lava Cake", "Warm matcha cake with vanilla ice cream", 520, "Desserts", True, True),
        ],
        3: [  # Verde Terrace
            ("Hummus Platter", "Creamy hummus with pita, olives and feta", 450, "Starters", True, True),
            ("Grilled Halloumi", "Cypriot cheese with roasted peppers", 580, "Starters", True, True),
            ("Lamb Kofta", "Spiced ground lamb skewers with tzatziki", 850, "Mains", True, False),
            ("Baklava", "Layered pastry with pistachios and honey syrup", 280, "Desserts", True, True),
        ],
        4: [  # Smoke & Soul
            ("Pulled Pork Platter", "12-hour smoked pork with coleslaw and cornbread", 890, "Mains", True, False),
            ("BBQ Ribs (Half Rack)", "St. Louis style ribs with house BBQ sauce", 1200, "Mains", True, False),
            ("Mac & Cheese", "Three-cheese blend with crispy breadcrumb topping", 380, "Sides", True, True),
            ("Craft Beer", "Selection of local craft ales and lagers", 350, "Beverages", True, False),
        ],
        5: [  # Little Italy
            ("Margherita Pizza", "San Marzano tomato, buffalo mozzarella, fresh basil", 620, "Pizza", True, True),
            ("Truffle Arancini", "Crispy risotto balls with black truffle and parmesan", 480, "Starters", True, True),
            ("Beef Lasagna", "Slow-cooked ragu with handmade pasta sheets", 780, "Pasta", True, False),
            ("Panna Cotta", "Vanilla cream with seasonal berry compote", 350, "Desserts", True, True),
        ],
    }

    for rest_idx, items in menus.items():
        rest_id = rest_objects[rest_idx].id
        for name, desc, price, cat, avail, veg in items:
            item = models.MenuItem(
                name=name, description=desc, price=price, category=cat,
                is_available=avail, is_vegetarian=veg, restaurant_id=rest_id
            )
            session.add(item)
    session.commit()

    # Sample notifications for demo user
    notifs = [
        models.Notification(user_id=diner.id, title="Session Complete! ✅", body="Your dinner at Spice Route was split successfully. ₹850 debited.", icon="check_circle"),
        models.Notification(user_id=diner.id, title="Friend Joined! 👥", body="Priya joined your dining session at Tokyo Tales.", icon="person_add"),
        models.Notification(user_id=diner.id, title="Offer Alert 🎉", body="Get 20% off at Verde Terrace this weekend with PartyPe.", icon="local_offer"),
    ]
    for n in notifs:
        session.add(n)
    session.commit()

    print("✅ Sample data created successfully.")
    print("📧 Demo accounts: demo@partype.com / demo123, merchant@partype.com / merchant123, waiter@partype.com / waiter123")
