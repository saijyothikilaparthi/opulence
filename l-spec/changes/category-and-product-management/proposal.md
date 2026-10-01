## Why

To allow the business and admin dashboard to manage catalog items dynamically without developer intervention, we need dedicated Category and Product management capabilities.

## What Changes

- **Database (`app/database.py`)**: Create `categories` and `products` tables.
- **Schemas (`app/schemas.py`)**: Add Pydantic schemas for Category and Product creation and response models.
- **Routers (`app/routers/categories.py` & `app/routers/products.py`)**:
  - `GET /api/categories`: Public list of active categories.
  - `POST /api/admin/categories`: Admin creation of categories with optional image/slug support.
  - `GET /api/products`: Public product list with optional category filter.
  - `GET /api/products/{id}`: Single product detail view.
  - `POST /api/admin/products`: Admin creation of products with image upload support.

## Capabilities

### New Capabilities
- `catalog-management`: Category and product management REST APIs and storage.

### Modified Capabilities
*(None)*

## Impact

- Database schema additions (`categories`, `products`).
- FastAPI routers registered in `app/main.py`.
