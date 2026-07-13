"""
Demo data seeder for local development only. Guarded by
`settings.environment == "development"` in app/main.py's startup hook,
and by `seed_if_empty`'s own empty-database check below — this never
runs against a database that already has data, so it can't clobber a
real deployment even if ENVIRONMENT were misconfigured.
"""
import secrets
from decimal import Decimal

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models import (
    MenuCategory,
    MenuItem,
    Notification,
    Restaurant,
    RestaurantRole,
    RestaurantStaff,
    RestaurantTable,
    User,
)

ROLE_NAMES = ["owner", "manager", "waiter", "chef", "cashier"]


def _ensure_roles(session: Session) -> dict[str, RestaurantRole]:
    roles = {}
    for name in ROLE_NAMES:
        role = session.exec(select(RestaurantRole).where(RestaurantRole.name == name)).first()
        if not role:
            role = RestaurantRole(name=name)
            session.add(role)
            session.commit()
            session.refresh(role)
        roles[name] = role
    return roles


def create_sample_data(session: Session) -> None:
    roles = _ensure_roles(session)

    admin = User(
        name="Admin PartyPe", email="admin@partype.com", phone="9999999990",
        password_hash=hash_password("admin123"), role="admin", is_admin=True,
        wallet_balance=Decimal("10000.00"),
    )
    merchant = User(
        name="Rajesh Kumar", email="merchant@partype.com", phone="9999999991",
        password_hash=hash_password("merchant123"), role="merchant",
        wallet_balance=Decimal("5000.00"),
    )
    waiter = User(
        name="Priya Singh", email="waiter@partype.com", phone="9999999992",
        password_hash=hash_password("waiter123"), role="waiter",
        wallet_balance=Decimal("500.00"),
    )
    diner = User(
        name="Aarav Sharma", email="demo@partype.com", phone="9999999993",
        password_hash=hash_password("demo123"), role="diner",
        wallet_balance=Decimal("2500.00"),
    )
    session.add_all([admin, merchant, waiter, diner])
    session.commit()
    for u in [admin, merchant, waiter, diner]:
        session.refresh(u)

    restaurants_data = [
        {
            "name": "Spice Route", "address": "12 Connaught Place, New Delhi", "phone": "011-2345-6789",
            "cuisine_type": "Modern Indian", "rating": Decimal("4.6"), "price_range": "₹300-800",
            "description": "Experience the evolution of Indian cuisine. Our signature slow-cooked Dal Makhani is simmered for 24 hours over traditional charcoal.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuDC4IqU0Yzozi3FmVD8eAqPNwK0XJgX-RPXiC1vA-kAjQxqr3J7LCXiQDhI5iiBEKlWSYHDFe0SzcUWQxpnA6tmGEcRi9Gy6_QQQ9DWXkyN27Q_nysK1h-jDV66RpQlxtzpMFzOkdCcnKYaXCyamL-EunXarnII_pVYwaH0qOeEW5Et89btJSQwbUnkuPg0BpHGhEJltQ1i1zZBD3BruxDBVBxYirAG3QJ2AjRK39IL9_GvJNIbu0UNAw7qVtk2fWLZa_IxRGmOXA8",
        },
        {
            "name": "Artisan Kitchen", "address": "45 Indiranagar, Bengaluru", "phone": "080-4567-8901",
            "cuisine_type": "Farm-to-Table", "rating": Decimal("4.8"), "price_range": "₹500-1200",
            "description": "Locally sourced ingredients crafted into seasonal masterpieces. Where food tells the story of its origin.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuA6lRWwX7rqdLNKzDEN0NiJhLnOQvRcVm307pV3Mb_oJcTlkDWcH2klWZ4Rc3x6XFScxqHvmPS3zkUU5XyYO2_3mbOQyQOURSFfBQs3NNockoYAXSSQKvSbfYn8wfKGBJOD4QDDb4mj6Mo7SeJOIq1SUTNv7IxrUb-1v-x7gKrRL22WQFluVBQSiNyDF_x9y1hrSax8ZnrUcX6qujmoYgDW6QvDH8CSn5P2T-IFX396o8uJx5TwEH_OsCawytIqqNNpXnTY9e2wXps",
        },
        {
            "name": "Tokyo Tales", "address": "88 Powai, Mumbai", "phone": "022-6789-0123",
            "cuisine_type": "Japanese", "rating": Decimal("4.4"), "price_range": "₹800-2000",
            "description": "Authentic Japanese gastronomy — from hand-rolled sushi to ramen that warms the soul.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCboTUOOOCc8vJwJQvhI48TF2nU2MLLNG_nM3jY1xhbBVWlH_YxcPvQDJJNlzy7grjtc8SnYlhI_J6TZi2nQovyF8AJshmkPfkDAhN4Rl26nXu553WG3AU-Gd52NI6_NhVN4nLaEgHVwnVEbiw5ukRlsj8mRBjuaobQpyg4pu6qS6RffdAOjnLPNkDXBf0bh4Vxn_YfaJ_KVfXqmiotB_P3dS9y67HBS8uvBpj8zuJ2uhPNE2T9qLfUtbJuUY5cIqyIM7Y_WmFxmpw",
        },
        {
            "name": "Verde Terrace", "address": "22 Bandra West, Mumbai", "phone": "022-9876-5432",
            "cuisine_type": "Mediterranean", "rating": Decimal("4.7"), "price_range": "₹600-1500",
            "description": "A sun-drenched rooftop experience with the finest Mediterranean flavors and spectacular views.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuAXiQB-5ZF7LH8XoC65SvuSQ8YbaXwGsmxAddZMxNLQbiEmn02-Fqhu579xnQiv77LxdUabfspYy6x1sDhCqc0XJ2m3I9gEnrD4_ZlBNGRD9p5os6lo_TK1mQ4o4J5BXliElTdQe24JWQyKXLERkvABSmtmtocqC3UrWg9wlwHXsLL33eh3xyrtXvx6hSm2ZQBt3Jr0328oW57K6LV-mCMPXbawEQXU-OKmJwZvL2elQxn8-BbS07-ABsbvsGEUwnJcCoqdl4pjyCU",
        },
        {
            "name": "Smoke & Soul", "address": "7 Koramangala, Bengaluru", "phone": "080-2233-4455",
            "cuisine_type": "American BBQ", "rating": Decimal("4.5"), "price_range": "₹400-900",
            "description": "Low and slow is the only way. Authentic wood-smoked BBQ with craft beer pairings.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuB-A0zMsdfJDRl1nLCYXIWEW7ksSx5y8DtdUVc7ZyCJW3jCp1OhrU-IPjt0NAkPQLzrS0bqqZcQ6kFy5YYV-hZcJMJzRTr-aFE83gveEnu3UZxMD1LAHQ9K7PjdHsPMg65U4Xv2DjUjuplMMxW-y9kiGU34MgmLjfhwur66q1T619m4IDL3MyZm74axhIXp5w8Skrm6q-fA-08QBfBvAI7wfTZDvbO0lM1Oc2Pw-k8gZqlbgOEmyMNrHqaaNyUwP2-dLodY70DiZOc",
        },
        {
            "name": "Little Italy", "address": "14 Jubilee Hills, Hyderabad", "phone": "040-5566-7788",
            "cuisine_type": "Italian", "rating": Decimal("4.3"), "price_range": "₹350-750",
            "description": "Nonna's recipes, reimagined for the modern palate. Handmade pasta and wood-fired pizza.",
            "image_url": "https://lh3.googleusercontent.com/aida-public/AB6AXuCBp922TUYyqs9_3lDIUbvz_ny_Uz7O22FC1PqEd47s3bkOWoXQL5fBX1dL6q2aXCh6PWRZda_tN6oms_RKjt84SKxBXJJGSYpf_4Fk_biWtSHYVs5A2O5v2R94EwK5C2M8CopRTTPqI4Egj-7I-4vp-FKIYqipbEkQK9XQ3vVzRJB0xKVITi-Dp_hdz3yS7OE2ltKvUeHeBHdG97iivY1L2DJjUe7sO0juJIS-4Rla-rks-VmvPiCDzqWYuEyGco4IOvkPSl7bVWQ",
        },
    ]

    rest_objects = []
    for row in restaurants_data:
        rest = Restaurant(**row)
        session.add(rest)
        rest_objects.append(rest)
    session.commit()
    for rest in rest_objects:
        session.refresh(rest)

    # Ownership: RestaurantStaff row, not a Restaurant.owner_id column
    # (see app/models/restaurant.py for why).
    session.add(RestaurantStaff(restaurant_id=rest_objects[0].id, user_id=merchant.id, role_id=roles["owner"].id))
    session.add(RestaurantStaff(restaurant_id=rest_objects[0].id, user_id=waiter.id, role_id=roles["waiter"].id))
    session.commit()

    for i in range(1, 13):
        status = "occupied" if i in [1, 3, 4, 6] else "available"
        t = RestaurantTable(
            restaurant_id=rest_objects[0].id, number=f"T{i:02d}",
            capacity=4 if i % 2 == 0 else 6, status=status,
            qr_code_token=secrets.token_urlsafe(16),
        )
        session.add(t)
    session.commit()

    # (category name, [(name, desc, price, is_veg), ...])
    menus = {
        0: [
            ("Main Course", [
                ("Butter Chicken", "Creamy tomato-based chicken curry with cashew paste", "645", False),
                ("Dal Makhani", "Black lentils slow-cooked for 24 hours over charcoal", "385", True),
            ]),
            ("Starters", [("Paneer Tikka", "Chargrilled cottage cheese with spiced marinade", "525", True)]),
            ("Breads", [("Garlic Naan", "Freshly baked flatbread with garlic and butter", "145", True)]),
            ("Desserts", [("Gulab Jamun", "Soft milk-solid dumplings in rose-flavoured sugar syrup", "195", True)]),
            ("Beverages", [("Masala Chai", "Traditional spiced tea with ginger and cardamom", "85", True)]),
        ],
        1: [
            ("Starters", [("Burrata Salad", "Fresh burrata with heirloom tomatoes and basil oil", "650", True)]),
            ("Mains", [
                ("Wild Mushroom Pasta", "Hand-rolled tagliatelle with seasonal mushrooms", "780", True),
                ("Pan-Seared Salmon", "Atlantic salmon with lemon butter and capers", "1100", False),
            ]),
            ("Desserts", [("Tiramisu", "Classic Italian dessert with espresso and mascarpone", "420", True)]),
        ],
        2: [
            ("Sashimi", [("Tuna Sashimi", "Premium bluefin tuna, 6 pieces", "950", False)]),
            ("Ramen", [("Wagyu Ramen", "12-hour bone broth with A5 Wagyu and soft egg", "1450", False)]),
            ("Starters", [("Gyoza", "Pan-fried dumplings with pork and cabbage", "380", False)]),
            ("Desserts", [("Matcha Lava Cake", "Warm matcha cake with vanilla ice cream", "520", True)]),
        ],
        3: [
            ("Starters", [
                ("Hummus Platter", "Creamy hummus with pita, olives and feta", "450", True),
                ("Grilled Halloumi", "Cypriot cheese with roasted peppers", "580", True),
            ]),
            ("Mains", [("Lamb Kofta", "Spiced ground lamb skewers with tzatziki", "850", False)]),
            ("Desserts", [("Baklava", "Layered pastry with pistachios and honey syrup", "280", True)]),
        ],
        4: [
            ("Mains", [
                ("Pulled Pork Platter", "12-hour smoked pork with coleslaw and cornbread", "890", False),
                ("BBQ Ribs (Half Rack)", "St. Louis style ribs with house BBQ sauce", "1200", False),
            ]),
            ("Sides", [("Mac & Cheese", "Three-cheese blend with crispy breadcrumb topping", "380", True)]),
            ("Beverages", [("Craft Beer", "Selection of local craft ales and lagers", "350", False)]),
        ],
        5: [
            ("Pizza", [("Margherita Pizza", "San Marzano tomato, buffalo mozzarella, fresh basil", "620", True)]),
            ("Starters", [("Truffle Arancini", "Crispy risotto balls with black truffle and parmesan", "480", True)]),
            ("Pasta", [("Beef Lasagna", "Slow-cooked ragu with handmade pasta sheets", "780", False)]),
            ("Desserts", [("Panna Cotta", "Vanilla cream with seasonal berry compote", "350", True)]),
        ],
    }

    for rest_idx, categories in menus.items():
        rest_id = rest_objects[rest_idx].id
        for order, (cat_name, items) in enumerate(categories):
            category = MenuCategory(restaurant_id=rest_id, name=cat_name, display_order=order)
            session.add(category)
            session.commit()
            session.refresh(category)
            for name, desc, price, is_veg in items:
                session.add(MenuItem(
                    name=name, description=desc, price=Decimal(price), category_id=category.id,
                    is_available=True, is_vegetarian=is_veg, restaurant_id=rest_id,
                ))
        session.commit()

    notifs = [
        Notification(user_id=diner.id, title="Session Complete! ✅", body="Your dinner at Spice Route was split successfully. ₹850 debited.", icon="check_circle"),
        Notification(user_id=diner.id, title="Friend Joined! 👥", body="Priya joined your dining session at Tokyo Tales.", icon="person_add"),
        Notification(user_id=diner.id, title="Offer Alert 🎉", body="Get 20% off at Verde Terrace this weekend with PartyPe.", icon="local_offer"),
    ]
    for n in notifs:
        session.add(n)
    session.commit()

    print("✅ Sample data created successfully.")
    print("📧 Demo accounts: demo@partype.com / demo123, merchant@partype.com / merchant123, waiter@partype.com / waiter123")


def seed_if_empty(session: Session) -> None:
    if not session.exec(select(Restaurant)).first():
        create_sample_data(session)
