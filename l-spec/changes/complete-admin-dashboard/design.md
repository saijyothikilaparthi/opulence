## Context

All core entities (banners, enquiries, categories, products, hampers) exist in the backend. We now add missing PUT endpoints and build a unified dashboard page.

## Goals / Non-Goals

**Goals:**
- Add `PUT` endpoints in `app/routers/` for status and entity updates.
- Rewrite `demo/admin.html` with clean responsive CSS tabs:
  1. Enquiries Management (View details, update status)
  2. Categories Management (Add, view list)
  3. Products Management (Add product, view list)
  4. Hampers & Sizes Management (Add hamper size, assemble hamper)
  5. Banner Management (Upload & view active banners)

## Decisions

- **Single Page Application (SPA) layout for demo admin**: HTML5 tabs with vanilla JavaScript `fetch()` calls.
