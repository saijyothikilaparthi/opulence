## 1. Database & Schema Initialization

- [x] 1.1 Add `categories` and `products` table SQL definitions in `app/database.py` inside `init_db()`.
- [x] 1.2 Add Pydantic model schemas for Category and Product requests/responses in `app/schemas.py`.

## 2. API Endpoints Implementation

- [x] 2.1 Implement `app/routers/categories.py` for `GET /api/categories` and `POST /api/admin/categories`.
- [x] 2.2 Implement `app/routers/products.py` for `GET /api/products`, `GET /api/products/{id}`, and `POST /api/admin/products`.
- [x] 2.3 Register new routers in `app/main.py`.
