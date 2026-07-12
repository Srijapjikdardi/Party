# Next.js 15 Migration Plan

`frontend/legacy-spa/index.html` is a single 1,824-line file: one FastAPI-served HTML page with inline vanilla JS handling routing, state, and every screen. `frontend/` (repo root of the frontend app) now contains the Next.js 15 target scaffold it will be replaced by. Both are live simultaneously — the backend serves the legacy SPA at `/` and mounts `/api/v1` + the legacy `/api` alias so neither breaks while the other is built out.

## Why incremental, not a rewrite-and-swap

The legacy SPA is a working production app. A big-bang rewrite risks a long feature-freeze and a risky cutover. Instead: build the Next.js app to full parity behind a separate URL/subdomain, verify it screen-by-screen against the legacy one, then flip.

## Phase 0 — Scaffold (this milestone, done)

- Next.js 15 (App Router) + React 19 + TypeScript strict + Tailwind + shadcn/ui structure created at `frontend/`.
- Typed API client (`lib/api-client.ts`) and types (`types/api.ts`) wired to `backend/app/api/v1`.
- 3 representative routes built to prove the pattern end-to-end:
  - `app/page.tsx` — home / restaurant list (server component, static-prerendered)
  - `app/restaurants/[id]/page.tsx` — restaurant detail (server component, dynamic route)
  - `app/auth/sign-in/page.tsx` — sign-in (client component, form state, API mutation)
- Verified: `npm run typecheck` clean, `npm run build` succeeds against the live backend, `/` statically prerenders with real data.

## Phase 1 — Screen inventory and mapping

`frontend/legacy-spa/*_final_review/` holds 25 design-reference mockups (one `code.html` + `screen.png` per screen) — this is the source of truth for what needs to be built, not the single-file SPA's internal routing. Map each to a Next.js route before writing code:

| Mockup folder | Target route | Component type |
|---|---|---|
| `partype_home_final_review` | `/` | Server (done, Phase 0) |
| `sign_in_final_review` | `/auth/sign-in` | Client (done, Phase 0) |
| `sign_up_final_review` | `/auth/sign-up` | Client |
| `browse_restaurants_final_review` | `/restaurants` | Server |
| `restaurant_details_final_review` | `/restaurants/[id]` | Server (done, Phase 0) |
| `search_results_final_review` | `/search` | Server + client filters |
| `live_collaborative_session_final_review`, `join_live_session_final_review` | `/sessions/[code]` | Client (needs polling/websocket — see Phase 3) |
| `bill_checkout_final_review`, `bill_checkout_rating_summary` | `/sessions/[code]/checkout` | Client |
| `wallet_payments_final_review`, `profile_wallet_final_review` | `/wallet` | Client (auth-gated) |
| `notifications_final_review` | `/notifications` | Client (auth-gated) |
| `social_discovery_reels_final_review` | `/discover` | Client |
| `waiter_portal_*_final_review` (6 folders) | `/waiter/*` | Client, role-gated |
| `merchant_command_*_final_review` (6 folders) | `/merchant/*` | Client, role-gated |
| `menu_manager_image_limit_subscription`, `premium_social_fintech` | TBD — confirm scope with product owner before building | — |

Rule of thumb: read-only pages with no per-user state → server component (fetch in the component, no client JS shipped for data). Anything with forms, local interaction, or auth-gated live data → client component using `lib/api-client.ts`.

## Phase 2 — Build screens in dependency order

1. Auth (`sign-up`) — needed to test everything else as a real user.
2. Restaurant browsing/search — no auth required, easiest to verify against the backend.
3. Dining sessions + checkout — the core "split the bill" flow, highest business value.
4. Wallet + notifications — auth-gated, depend on a signed-in user existing.
5. Waiter portal — separate role, can be built in parallel by a second contributor once the API client pattern is established.
6. Merchant dashboard — same.

Each screen: build against `docs/ARCHITECTURE.md`'s API contract, compare visually against its `*_final_review/screen.png`, verify against the running backend (not mocked data) before marking done.

## Phase 3 — Cross-cutting concerns to resolve before Phase 2 finishes

- **Auth token storage.** Phase 0's sign-in page sets a plain cookie as a placeholder for the request/response shape. Decide httpOnly cookie (set by a Next.js Route Handler that proxies signin, not the browser directly) vs. client-side state before building any auth-gated screen — this affects every one of them.
- **Live session updates.** `live_collaborative_session_final_review` implies real-time participant/order updates. Current backend has no websocket/SSE endpoint. Needs a backend addition (new `app/api/v1/endpoints/` route) before that screen can be built — decide polling vs. websocket.
- **Role-gating.** Waiter/merchant routes need a route-group layout (`app/(waiter)/layout.tsx`) that checks `user.role` server-side and redirects otherwise.

## Phase 4 — Type generation

Once the API contract stabilizes, replace the hand-maintained `types/api.ts` with types generated from FastAPI's OpenAPI schema (`/openapi.json`) via `openapi-typescript`, so backend schema changes fail the frontend typecheck instead of silently drifting.

## Phase 5 — Cutover

1. All 25 mapped screens built and verified against the live backend.
2. Point the backend's `/` route (or a reverse-proxy in front of both) at the Next.js app instead of `frontend/legacy-spa/index.html`.
3. Remove the `legacy_api_prefix` alias from `backend/app/core/config.py` and `backend/app/main.py`.
4. Delete `frontend/legacy-spa/`.
5. Update `docs/ARCHITECTURE.md` to drop the legacy SPA box from the diagram.

## Explicitly out of scope for this migration

- Database changes (tracked separately — this migration doesn't touch `app/models` or `app/db`).
- Auth scheme replacement (bearer-token-in-memory → JWT) — orthogonal to the frontend framework, tracked as its own backend item.
