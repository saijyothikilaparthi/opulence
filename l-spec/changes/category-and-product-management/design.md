## Context

To support category browsing on the customer frontend and catalog management in the admin dashboard, we need clean relational models for `categories` and `products`.

## Goals / Non-Goals

**Goals:**
- Add PostgreSQL tables `categories` and `products` in `app/database.py`.
- Add Pydantic schemas in `app/schemas.py`.
- Create modular FastAPI routers `app/routers/categories.py` and `app/routers/products.py` and mount them in `app/main.py`.

**Non-Goals:**
- Full hamper builder or multi-item hamper inventory tracking (handled in subsequent hamper stage).

## Decisions

- **Relational Integrity**: Foreign key `category_id REFERENCES categories(id) ON DELETE SET NULL`.
- **Image Storage**: Reuse local `uploads/` static storage pattern for product and category image assets.
