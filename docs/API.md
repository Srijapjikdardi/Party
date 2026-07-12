# API Reference

Base URL: `/api/v1` (canonical). `/api` serves the identical routes as a legacy alias — see `docs/ARCHITECTURE.md#api-versioning`.

Interactive docs (Swagger UI): `http://localhost:8000/docs`
OpenAPI schema: `http://localhost:8000/openapi.json`

## Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | — | Create account. Returns `{token, user}`. |
| POST | `/auth/signin` | — | Returns `{token, user}`. |
| POST | `/auth/signout` | Bearer | Revokes the token. |
| GET | `/users/me` | Bearer | Current user profile. |

Auth is a bearer token in the `Authorization` header, issued in-memory (see `docs/ARCHITECTURE.md`'s "explicitly out of scope" note — JWT migration is a separate backend item).

## Restaurants

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/restaurants?skip=&limit=&cuisine=` | — | List, paginated, optional cuisine filter. |
| GET | `/restaurants/{id}` | — | Detail. |
| GET | `/restaurants/{id}/menu` | — | Available menu items. |
| GET | `/restaurants/{id}/tables` | — | Tables. |

## Dining sessions

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/sessions` | — | Create a dining session; host auto-joins as participant. |
| GET | `/sessions/{id}` | — | Detail. |
| POST | `/sessions/join/{code}` | Bearer | Join by session code. |
| GET | `/sessions/{id}/participants` | — | List participants. |

## Orders

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/orders` | — | Create an order with nested `order_items`. |
| GET | `/orders/{id}` | — | Detail. |
| GET | `/orders/user/{user_id}` | — | Orders for a user, newest first. |
| PATCH | `/orders/{id}/status` | — | Update status (`pending` → `confirmed` → `preparing` → `ready` → `delivered`, or `cancelled`). |

## Wallet

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/wallet` | Bearer | `{balance, transactions}`. |
| POST | `/wallet/topup` | Bearer | Amount must be `0 < amount <= 50000`. |
| POST | `/wallet/pay` | Bearer | Debits if sufficient balance, else 400. |

## Notifications

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/notifications` | Bearer | Newest first. |
| POST | `/notifications/read-all` | Bearer | Marks all as read. |

## Merchant

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/merchant/orders?restaurant_id=&limit=` | — | Orders for a restaurant. |
| GET | `/merchant/tables?restaurant_id=` | — | Tables for a restaurant. |
| PATCH | `/merchant/tables/{id}/status` | — | Body: `{"status": "available"\|"occupied"\|"reserved"\|"billing"}`. |
| GET | `/merchant/analytics?restaurant_id=` | — | Revenue/order aggregates. |

None of the merchant/waiter routes are role-gated yet at the API layer — see `docs/MIGRATION_PLAN.md` Phase 3.
