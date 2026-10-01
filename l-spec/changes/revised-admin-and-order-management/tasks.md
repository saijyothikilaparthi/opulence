## 1. Database & Schema Updates

- [x] 1.1 Add `orders` and `gallery_work` tables and update `banners` table columns in `app/database.py`.
- [x] 1.2 Add Pydantic schemas for Order and Gallery item in `app/schemas.py`.

## 2. API Routers Implementation

- [x] 2.1 Implement `app/routers/orders.py` (`GET /api/orders`, `POST /api/admin/orders`, `PUT /api/admin/orders/{id}/status`, `DELETE /api/admin/orders/{id}`).
- [x] 2.2 Implement `app/routers/gallery.py` (`GET /api/gallery`, `POST /api/admin/gallery`, `DELETE /api/admin/gallery/{id}`).
- [x] 2.3 Update banner upload endpoint to accept `event` and `note`, deactivating previous banners.
- [x] 2.4 Register new routers in `app/main.py`.

## 3. Demo Frontend & File Cleanup

- [x] 3.1 Rebuild `demo/admin.html` with tabs for Website Enquiries, Orders Management (Add/Delete/Status), Banner Management, and Work Gallery.
- [x] 3.2 Remove redundant section forms (`demo/individual.html`, `demo/corporate.html`, `demo/customized.html`).
