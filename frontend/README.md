# PartyPe Web (Next.js 15)

Target architecture for the frontend migration. See `/docs/MIGRATION_PLAN.md`
for the phased plan and screen-by-screen mapping from the legacy SPA
(`frontend/legacy-spa/`).

## Stack

- Next.js 15 (App Router)
- React 19
- TypeScript (strict mode)
- Tailwind CSS
- shadcn/ui component structure (`components/ui/`)

## Setup

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:3000`. API calls to `/api/v1/*` are proxied to
the FastAPI backend at `http://localhost:8000` (see `next.config.ts`).
Run the backend separately: `python run.py` from the repo root.

## Structure

```
app/                    App Router routes (file-system based)
  layout.tsx            Root layout
  page.tsx              Home (restaurant list) — server component
  restaurants/[id]/     Restaurant detail — dynamic route, server component
  auth/sign-in/         Sign-in — client component (form state)
components/ui/          shadcn/ui primitives (button, card, badge)
lib/api-client.ts       Typed fetch wrapper for backend/app/api/v1
lib/utils.ts            cn() class-merging helper
types/api.ts            TS types mirroring backend/app/schemas
legacy-spa/              Pre-migration static SPA + design-reference mockups
                         (still served by the backend at "/", unaffected
                         by anything in this Next.js app)
```

## Adding a shadcn/ui component

This scaffold ships `button`, `card`, and `badge` as real, hand-verified
primitives. Add more the standard way once `npx` has network access in
your environment:

```bash
npx shadcn@latest add input
```

## Commands

```bash
npm run dev         # start dev server
npm run build        # production build
npm run lint          # eslint (next lint)
npm run typecheck   # tsc --noEmit
```
