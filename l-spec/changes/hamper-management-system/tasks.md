## 1. Database & Schema Initialization

- [x] 1.1 Add `hamper_sizes`, `hampers`, and `hamper_items` table definitions in `app/database.py`.
- [x] 1.2 Add Pydantic schemas for HamperSize, HamperItem, and Hamper creation/responses in `app/schemas.py`.

## 2. API Endpoints Implementation

- [x] 2.1 Implement `app/routers/hampers.py` with `/api/hamper-sizes`, `/api/hampers`, `/api/hampers/{id}`, and admin POST routes.
- [x] 2.2 Register `hampers.router` in `app/main.py`.
