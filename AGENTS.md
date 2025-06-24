# AGENTS.md
> High-level instructions for AI coding agents (ChatGPT Codex, etc.)  
> **Project:** Offline-First Inventory Management System – Pharmacy/Grocery, Nigeria  
> **Repo owner:** Emmanuel  
> **Last updated:** 2025-06-24

---

## 0. TL;DR for Agents
1. Read this file start-to-finish **before** generating code.  
2. Keep code inside its domain folder (see §2).  
3. Code must pass `npm run lint && npm run test:unit` with zero warnings.  
4. Use Conventional Commit messages (`feat:`, `fix:`, `chore:`, etc.).  
5. Never edit `/infra/db/migrations/*` unless task explicitly says so.  
6. Prefer small PRs (< 300 LOC changed) with screenshot/test evidence.

---

## 1. Repo Layout (monolith-for-now, modular)
```
/frontend          React PWA (CRA-PWA, TypeScript)
  /src
    /inventory     products, warehouses, batch-tracking
    /orders        sales + purchase flows
    /customers     CRM + loyalty
    /auth          login, RBAC, audit trail
    /shared        utils, common hooks
/backend           Node/Express helper APIs (optional)
/infra
  /docker          Dockerfiles, docker-compose.yml
  /db              CouchDB configs, seed + migration scripts
/docs              ERDs, ADRs, API docs
/tests             Vitest unit + Cypress e2e
```

---

## 2. Domain Boundaries
| Domain        | Owns                                                          | Allowed Couplings                                   |
|---------------|--------------------------------------------------------------|-----------------------------------------------------|
| **inventory** | Product, Category, Warehouse, InventoryMovement, Stock utils | Reads `orders` only via shared services             |
| **orders**    | SalesOrder, PurchaseOrder, OrderItem                         | Calls `inventory.reserveStock` / `releaseStock` only|
| **customers** | Customer, LoyaltyProgram, EmailTemplate                      | No inventory mutation                               |
| **auth**      | User, Role, AuditLog                                         | Stateless auth helpers available to all domains     |

> **Agents:** keep DB docs, hooks, tests, and components **inside** their domain.  
> Cross-domain calls go through `src/shared/services/*.ts`.

---

## 3. Code Style & Tooling
- **Language:** TypeScript 5  
- **Formatter:** Prettier (`tabWidth: 2`, `singleQuote: true`)  
- **Lint:** ESLint (Airbnb base + Prettier)  
- **Tests:** Vitest for unit; Cypress for e2e  
- **Git hooks:** Husky + lint-staged (format + tests on pre-push)

---

## 4. Local Dev Commands
| Purpose                 | Command                                  |
|-------------------------|------------------------------------------|
| Install deps            | `npm ci`                                 |
| Start PWA               | `npm start`                              |
| Start CouchDB (Docker)  | `docker compose up couchdb`              |
| Seed sample data        | `npm run seed`                           |
| Run unit tests          | `npm run test:unit`                      |
| Run e2e tests           | `npm run test:e2e`                       |
| Lint & format           | `npm run lint`                           |

---

## 5. Database & Sync Conventions
- Local PouchDB names mirror remote CouchDB names:  
  `inventory_db`, `orders_db`, `customers_db`, `auth_db`  
- Every document stores a `type` field: `<domain>.<entity>`.  
- Add Mango/map-reduce indexes under `/infra/db/indexes`.  
- Never rewrite past migration files in `/infra/db/migrations`.

---

## 6. Testing & QA
1. **Each feature** adds ≥ 1 Vitest test and, if UI-visible, ≥ 1 Cypress test.  
2. Factories live in `/tests/factories`.  
3. PRs fail if per-domain coverage < 80 %.

---

## 7. Commit & PR Rules
- Follow **Conventional Commits**: e.g.  
  `feat(inventory): add batch tracking #42`  
- Link issues; include screenshots/GIFs + test output in PR description.  
- Use the template in `.github/pull_request_template.md`.

---

## 8. Prompt Helper Snippets
- **Create CRUD screen**  
  ```
  TASK: "Add CRUD UI for {Entity}"
  ACCEPTANCE: form validation, sidebar route, tests passing
  ```
- **Add DB index**  
  ```
  TASK: "Add Mango index on {field}"
  STEPS: create _design/{domain}_{field}, unit-test a filtered query
  ```
- **Write forecast util**  
  ```
  TASK: "Implement demandForecast.ts using moving average"
  INPUTS: productId, days
  OUTPUT: number (units)
  TESTS: forecast > 0 for sample history
  ```

---

## 9. Safe-Write Guardrails
- Don’t commit `.env`, secrets, or files > 500 KB.  
- Never modify `/infra/ssl/` or `/docs/adr/*.md` unless explicitly instructed.

---

## 10. Updating This File
When architecture evolves (e.g., you spin out micro-services), update:
1. **Repo Layout** – add new service folders.  
2. **Domain Boundaries** – ensure table remains accurate.  
3. **Testing thresholds** – adjust coverage targets if tooling changes.
