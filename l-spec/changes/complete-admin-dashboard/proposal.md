## Why

The admin needs a single dashboard interface (`/demo/admin.html`) to manage all backend entities:
1. Promotional Banners
2. Customer Enquiries (View, Status Updates)
3. Categories (Add, Edit, View)
4. Products (Add, Edit, View)
5. Hampers & Hamper Sizes (Create sizes, assemble hampers)

## What Changes

- **Admin Routers (`app/routers/`)**:
  - Add update endpoints: `PUT /api/admin/enquiries/{id}/status`, `PUT /api/admin/categories/{id}`, `PUT /api/admin/products/{id}`, `PUT /api/admin/hampers/{id}`.
- **Unified Admin Interface (`demo/admin.html`)**:
  - Transform `demo/admin.html` into a tabbed navigation dashboard allowing full CRUD management of Banners, Enquiries, Categories, Products, and Hampers.

## Capabilities

### New Capabilities
- `admin-dashboard`: Unified web administration console and management endpoints for all business entities.

### Modified Capabilities
*(None)*

## Impact

- `app/routers/enquiries.py`, `app/routers/categories.py`, `app/routers/products.py`, `app/routers/hampers.py`: Added PUT/update handlers.
- `demo/admin.html`: Complete tabbed administration interface.
