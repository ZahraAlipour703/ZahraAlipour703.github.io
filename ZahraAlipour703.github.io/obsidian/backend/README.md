---
tags: [backend, stable]
updated: 2026-05-22
---

# Backend

`next16-claude-starter` is frontend-first, but it now has a server **API
layer**: Next.js Route Handlers under `src/app/api/`. There is still no
database or authentication.

## What exists

- **API endpoints** — `app/api/**/route.ts` Route Handlers. Convention and
  rules: [[api-architecture]].
- **Env validation** — `src/env.ts` (zod), public vs server-only split.
- **Shared API helpers** — `src/lib/api/` (`handle`, `ApiError`) and the
  client-side `src/lib/api-client.ts`.

## What does not exist yet

- Database & ORM
- Authentication
- Server Actions (the project default for mutations is still TBD — currently
  everything goes through `app/api`)

## When more backend is added

- `database-schema.md` — tables, relations, migrations
- `auth.md` — authentication flow & session handling

Also: add deps to [[tech-stack]], record an ADR in [[decisions-log]], update
[[data-flow]], add a [[changelog]] entry.

> [!tip] Deployment target
> The repo targets **Vercel**. Route handlers run on Fluid Compute (Node.js) —
> do not use the Edge runtime. Prefer Vercel-native options (Marketplace
> databases like Neon Postgres, Clerk for auth).

## Related

[[api-architecture]] · [[system-overview]] · [[tech-stack]] · [[environment-variables]]
