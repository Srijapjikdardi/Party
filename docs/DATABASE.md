# Database — PostgreSQL / Neon

## Connection management

- **Driver**: `psycopg[binary]` v3, via SQLAlchemy's `postgresql+psycopg://` dialect.
- **Pooling** (`app/db/session.py`, tuned in `app/core/config.py`): `pool_size=5`, `max_overflow=5`, `pool_recycle=300s`, `pool_pre_ping=True`.
  - Neon's free tier has limited compute and autosuspends the endpoint after ~5 min idle; a small pool avoids holding connections Neon has to account for.
  - `pool_pre_ping` issues a cheap `SELECT 1` before handing out a pooled connection, so a connection Neon silently dropped during autosuspend/resume is transparently replaced instead of surfacing as a random query failure mid-request.
  - `pool_recycle=300` retires connections before they get old enough for Neon's own idle-connection timeout to kill them first.
  - Use Neon's **pooled** connection string (PgBouncer, port `6543` in the Neon dashboard) for `DATABASE_URL`, not the direct `:5432` endpoint — see `.env.example`.
- **Session lifecycle**: one `Session` per request, via the `get_session` FastAPI dependency (`app/db/session.py`) — opened at request start, closed at request end, never held across requests.
- **Health check**: `GET /health` runs `check_database_connection()` (a bare `SELECT 1`), reporting `"database": "connected"` or `"unreachable"` alongside overall app status — cheap, no schema dependency, safe to hit frequently from an uptime monitor.

## Schema ownership: Alembic, not create-on-boot

`app/main.py`'s startup hook no longer calls `SQLModel.metadata.create_all()`. Auto-creating tables from whatever the model code currently looks like bypasses migration history and is exactly how dev/staging/prod schemas drift apart. Schema changes now only happen via `alembic upgrade head`, run as an explicit deploy step (or manually in dev — see commands below).

## ER diagram

```mermaid
erDiagram
    RESTAURANT_ROLES ||--o{ RESTAURANT_STAFF : "grants"
    USERS ||--o{ RESTAURANT_STAFF : "works at"
    RESTAURANTS ||--o{ RESTAURANT_STAFF : "staffed by"
    RESTAURANTS ||--o{ RESTAURANT_TABLES : has
    RESTAURANTS ||--o{ MENU_CATEGORIES : has
    RESTAURANTS ||--o{ MENU_ITEMS : sells
    MENU_CATEGORIES ||--o{ MENU_ITEMS : groups
    RESTAURANTS ||--o{ DINING_SESSIONS : hosts
    RESTAURANT_TABLES |o--o{ DINING_SESSIONS : "seated at"
    USERS ||--o{ DINING_SESSIONS : hosts
    DINING_SESSIONS ||--o{ SESSION_PARTICIPANTS : has
    USERS ||--o{ SESSION_PARTICIPANTS : joins
    DINING_SESSIONS |o--o{ CARTS : "scoped to"
    USERS ||--o{ CARTS : owns
    RESTAURANTS ||--o{ CARTS : "ordering from"
    CARTS ||--o{ CART_ITEMS : contains
    MENU_ITEMS ||--o{ CART_ITEMS : "added as"
    RESTAURANTS ||--o{ ORDERS : receives
    USERS |o--o{ ORDERS : places
    DINING_SESSIONS |o--o{ ORDERS : "placed within"
    CARTS |o--o{ ORDERS : "checked out to"
    ORDERS ||--o{ ORDER_ITEMS : contains
    MENU_ITEMS ||--o{ ORDER_ITEMS : "ordered as"
    DINING_SESSIONS ||--o| BILLS : "settled by"
    BILLS ||--o{ BILL_SPLIT_RECORDS : "split into"
    SESSION_PARTICIPANTS ||--o{ BILL_SPLIT_RECORDS : owes
    USERS ||--o{ PAYMENTS : makes
    BILL_SPLIT_RECORDS |o--o{ PAYMENTS : settles
    PAYMENTS ||--o{ PAYMENT_TRANSACTIONS : "gateway events"
    USERS ||--o{ REFRESH_TOKENS : has
    USERS ||--o{ EMAIL_VERIFICATION_TOKENS : has
    USERS ||--o{ PASSWORD_RESET_TOKENS : has
    USERS ||--o{ WALLET_TRANSACTIONS : has
    USERS ||--o{ NOTIFICATIONS : receives

    USERS {
        uuid id PK
        string email UK
        string phone UK
        string role "diner|merchant|waiter|admin (UX hint)"
        numeric wallet_balance
        bool is_email_verified
        int failed_login_attempts
        timestamp locked_until
        timestamp deleted_at "soft delete"
    }
    RESTAURANTS {
        uuid id PK
        string name
        string cuisine_type
        timestamp deleted_at "soft delete"
    }
    RESTAURANT_ROLES {
        int id PK
        string name UK "owner|manager|waiter|chef|cashier"
    }
    RESTAURANT_STAFF {
        int id PK
        uuid restaurant_id FK
        uuid user_id FK
        int role_id FK
        UK "restaurant_id+user_id"
    }
    RESTAURANT_TABLES {
        uuid id PK
        uuid restaurant_id FK
        string qr_code_token UK
        string status
    }
    MENU_CATEGORIES {
        int id PK
        uuid restaurant_id FK
        string name
        UK "restaurant_id+name"
    }
    MENU_ITEMS {
        uuid id PK
        uuid restaurant_id FK
        int category_id FK "nullable, SET NULL"
        numeric price
        timestamp deleted_at "soft delete"
    }
    DINING_SESSIONS {
        uuid id PK
        uuid restaurant_id FK
        uuid table_id FK "nullable, SET NULL"
        uuid host_user_id FK
        string session_code UK
        string status
    }
    SESSION_PARTICIPANTS {
        int id PK
        uuid session_id FK
        uuid user_id FK
        UK "session_id+user_id"
    }
    CARTS {
        int id PK
        uuid session_id FK "nullable"
        uuid user_id FK
        uuid restaurant_id FK
        UK "session_id+user_id"
    }
    CART_ITEMS {
        int id PK
        int cart_id FK
        uuid menu_item_id FK "RESTRICT"
        numeric unit_price "snapshot"
    }
    ORDERS {
        uuid id PK
        uuid session_id FK "nullable, SET NULL"
        uuid user_id FK "nullable"
        uuid restaurant_id FK
        int cart_id FK "nullable, SET NULL"
        numeric total_amount "server-computed"
        string status
    }
    ORDER_ITEMS {
        int id PK
        uuid order_id FK
        uuid menu_item_id FK "RESTRICT"
        numeric unit_price "snapshot"
    }
    BILLS {
        uuid id PK
        uuid session_id FK UK "one bill per session"
        numeric total_amount
        string status
    }
    BILL_SPLIT_RECORDS {
        int id PK
        uuid bill_id FK
        int participant_id FK
        numeric amount_owed
        UK "bill_id+participant_id"
    }
    PAYMENTS {
        uuid id PK
        uuid user_id FK
        int bill_split_record_id FK "nullable"
        string purpose "bill_split|wallet_topup|order_payment"
        string gateway_order_id UK
    }
    PAYMENT_TRANSACTIONS {
        int id PK
        uuid payment_id FK
        string gateway_transaction_id UK
        string event_type
    }
    REFRESH_TOKENS {
        int id PK
        uuid user_id FK
        string token_hash UK
        timestamp revoked_at
    }
    EMAIL_VERIFICATION_TOKENS {
        int id PK
        uuid user_id FK
        string token_hash UK
        timestamp expires_at
        timestamp used_at
    }
    PASSWORD_RESET_TOKENS {
        int id PK
        uuid user_id FK
        string token_hash UK
        timestamp expires_at
        timestamp used_at
    }
    WALLET_TRANSACTIONS {
        int id PK
        uuid user_id FK
        numeric amount
    }
    NOTIFICATIONS {
        int id PK
        uuid user_id FK
        bool is_read
    }
```

## Schema decisions

### UUID vs. integer primary keys

UUID for entities exposed externally — in URLs, QR codes, receipts, or gateway webhooks — where sequential IDs would let someone enumerate other people's data (`/orders/1`, `/orders/2`, ...) and where unguessability has real value: `users`, `restaurants`, `restaurant_tables` (literally what a QR code encodes), `menu_items` (future social sharing), `dining_sessions` (the QR-session flow), `orders`, `bills`, `payments`.

Integer for internal child/join/log rows that are never referenced outside a query the app already scoped by a parent: `restaurant_staff`, `menu_categories`, `session_participants`, `carts`, `cart_items`, `order_items`, `bill_split_records`, `payment_transactions`, `refresh_tokens`, `wallet_transactions`, `notifications`. Smaller, cheaper to index, and nothing external ever needs to guess or avoid guessing one.

### Money as `NUMERIC(10,2)`, not float

Every M2 model used `float` for money (`wallet_balance`, `total_amount`, prices). Floats can't represent most decimal fractions exactly — summing them across a bill split is exactly the kind of aggregation that produces off-by-a-cent errors. All money columns are now `Decimal` / SQL `NUMERIC(10,2)`.

### Server-computed order pricing

The M2 `OrderCreate` schema accepted `unit_price` and `total_amount` directly from the client — a diner's browser could set its own price. `OrderItemCreate` now only accepts `menu_item_id` and `quantity`; `OrderService.create_order` looks up the current `MenuItem.price` server-side and computes `subtotal`/`total_amount` itself. See `app/services/order_service.py`.

### Restaurant Staff / Restaurant Roles, not `Restaurant.owner_id`

M2's `Restaurant` had a single `owner_id` column. A restaurant can have co-owners, managers, waiters, and other staff, and a person can staff more than one restaurant — a single FK can't express that, and adding more single-purpose columns (`manager_id`, `waiter_ids`...) duplicates the same relationship shape N times. `restaurant_staff` normalizes this: one row per `(restaurant, user)` with a `role_id`, unique-constrained so a person has exactly one role per restaurant. `restaurant_roles` is a small static lookup table (`owner`, `manager`, `waiter`, `chef`, `cashier`), seeded once.

`User.role` (`diner`/`merchant`/`waiter`/`admin`) is kept as a lightweight, non-authoritative UX hint the legacy SPA uses to pick which app shell to show at login — not the source of truth for what someone can actually do at a given restaurant. That's `restaurant_staff.role_id`, checked per-restaurant. Both exist because they answer different questions ("what kind of account is this" vs. "what can this person do at restaurant X") and collapsing them into one field would force every future multi-restaurant-staff feature to fight the login-routing use case.

### Menu Categories normalized out of `MenuItem.category`

M2 stored `category` as a free-text string directly on `MenuItem` — duplicated across every item in the same category, no ordering, no way to rename a category without a bulk string update across rows. `menu_categories` is now its own table (`restaurant_id`, `name`, `display_order`), and `MenuItem.category_id` is a nullable FK (`SET NULL` — deleting a category "uncategorizes" its items rather than deleting them). `MenuItemRead.category_name` is a read-only computed property (`MenuItem.category_name` in `app/models/menu_item.py`), joined at read time via `selectinload`, not stored — the name lives in exactly one place.

### Cart / CartItem (new)

M2 had no pre-checkout step — `POST /orders` created an order atomically. `carts`/`cart_items` add an explicit "add to cart, keep browsing" stage. `cart_id` is nullable on `dining_sessions` so a cart can exist outside a session (future takeaway/delivery) without a schema change, and unique-constrained on `(session_id, user_id)` so repeated "add to cart" calls accumulate into one cart.

### Bill / BillSplitRecord (new)

`DiningSession.total_amount` tracks the *live, still-changing* running total while people are still ordering. `Bill` is the frozen snapshot generated once ordering is done — `total_amount` on a session mutates; a bill's total shouldn't once split records are computed against it. `bill_split_records` (one row per session participant per bill) records what each person owes and has paid, unique-constrained on `(bill_id, participant_id)`.

### Payment / PaymentTransaction (new, Razorpay-ready)

`Payment` is generic across purposes (`bill_split`, `wallet_topup`, future `order_payment`) via a `purpose` column rather than three near-identical tables, with nullable `gateway`/`gateway_order_id` fields ready for Razorpay without a schema change when that integration lands. `PaymentTransaction` is an append-only log of gateway events (`created`/`authorized`/`captured`/`failed`/`refunded`) per payment; `gateway_transaction_id` is unique so a retried webhook is a no-op, not a duplicate row — the idempotency Razorpay's webhook docs require.

### RefreshToken, EmailVerificationToken, PasswordResetToken

`refresh_tokens` was added in M3 unused, anticipating this. M4 (`docs/AUTHENTICATION.md`) wires it up: JWT access tokens are stateless (not stored), but refresh tokens are opaque and DB-backed here — only `token_hash` is ever stored, never the raw value, and `revoked_at` supports single-use rotation plus "log out everywhere" on reuse detection, password reset, and password change.

`email_verification_tokens` and `password_reset_tokens` (both new in M4) follow the identical shape: `token_hash` (unique), `expires_at`, `used_at` (nullable — marks single-use consumption), `created_at`. No separate `updated_at` on any of these three tables — `used_at`/`revoked_at` is the only mutation any of them ever gets, so a second timestamp column would just duplicate it.

### Soft delete — only on `users`, `restaurants`, `menu_items`

These three have external references (orders, order items, staff records) that must survive deletion for financial/audit history — you can't let a user's order history reference a `NULL` where the user used to be. Everything else hard-deletes via FK `CASCADE`/`SET NULL`: a deleted cart, session participant, or table has no audit value once gone, so keeping a tombstone row buys nothing and costs storage on Neon's free tier for no reason.

M4 note: a soft-deleted user still holds the DB's `UNIQUE(email)` constraint — application-level duplicate-email checks that filter out soft-deleted rows (as login correctly does) must NOT be reused for registration's duplicate check, or a re-registration attempt under a deleted account's email will crash on that constraint instead of returning a clean 400. See `UserRepository.get_by_email_including_deleted` and `docs/AUTHENTICATION.md`.

### Indexing — deliberately not everything

Every FK is indexed by default *unless* a composite index already covers it via leftmost-prefix (e.g. `dining_sessions.restaurant_id` has no separate single-column index because `ix_dining_sessions_restaurant_status (restaurant_id, status)` already serves restaurant_id-only lookups). Composite indexes exist only where a real, named query pattern needs them: `orders (restaurant_id, status)` for the merchant KDS queue, `orders (user_id, created_at)` for order history, `dining_sessions (restaurant_id, status)` for the merchant dashboard's active-sessions view, `notifications (user_id, is_read)` for the unread-count badge. No index was added speculatively for a column nothing currently queries by.

## Referential integrity — cascade rules at a glance

| Rule | Used for | Why |
|---|---|---|
| `CASCADE` | staff/cart/session-participant/order-item rows, everything whose parent owning it fully | Deleting the parent should delete these — they have no independent meaning. |
| `RESTRICT` | `dining_sessions.restaurant_id`, `orders.menu_item_id` (via order_items), `session_participants.user_id` | Block deletion outright rather than silently losing financial/audit-relevant links; soft-delete the parent instead. |
| `SET NULL` | `dining_sessions.table_id`, `orders.session_id`, `menu_items.category_id` | The child record has independent value and must outlive a parent that's reassigned or removed (a table getting swapped, a session getting torn down, a category being deleted). |

## Commands

```bash
# Migrations (run from backend/)
cd backend
alembic revision --autogenerate -m "description"   # generate a new migration after model changes
alembic upgrade head                                 # apply all pending migrations
alembic downgrade -1                                  # roll back one migration
alembic downgrade base                                # roll back everything
alembic current                                        # show applied revision
alembic history                                         # show migration history
```

Seeding is automatic in development only (`app/main.py`'s startup hook calls `app/seed.py::seed_if_empty`, which no-ops if `restaurants` already has rows) — never runs in `staging`/`production`, and never runs against a non-empty database even if `ENVIRONMENT` were misconfigured.
