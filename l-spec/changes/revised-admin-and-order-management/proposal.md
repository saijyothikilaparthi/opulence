## Why

The business requirements have been refined:
1. **Forms Cleanup**: Only the main homepage enquiry form (`demo/enquiry.html`) is needed; remove separate section forms (`individual.html`, `corporate.html`, `customized.html`).
2. **Website Enquiries Table**: Submissions from the website registration/enquiry form appear in a dedicated "Website Enquiries" table. Submitting this form triggers a WhatsApp Business notification setup.
3. **Manual Order Management**: Orders received offline (WhatsApp, Instagram, In-person) need a separate "Manual / All Orders" table where admins can manually Add, View, update Status, and Delete orders.
4. **Banner Management Updates**: Banner schema simplified to `image_url`, `event`, `note`. When a new banner is uploaded, deactivate/replace the existing banner so only the latest is active.
5. **Work / Gallery Management**: New feature allowing admins to upload pictures of past work to display in the website gallery, with option to delete unwanted images.

## What Changes

- **Database (`app/database.py`)**:
  - Add `orders` table (`id`, `source`, `customer_name`, `phone`, `email`, `event`, `quantity`, `amount`, `status`, `notes`, `created_at`).
  - Add `gallery_work` table (`id`, `title`, `image_url`, `description`, `created_at`).
  - Update `banners` table schema to include `event` and `note` columns.
- **Endpoints**:
  - Add Orders REST API (`GET /api/orders`, `POST /api/admin/orders`, `PUT /api/admin/orders/{id}/status`, `DELETE /api/admin/orders/{id}`).
  - Add Gallery REST API (`GET /api/gallery`, `POST /api/admin/gallery`, `DELETE /api/admin/gallery/{id}`).
  - Update Banner endpoint (`POST /api/admin/banners`) to accept `event` and `note` fields, and auto-deactivate previous banners.
- **Admin Dashboard UI (`demo/admin.html`)**:
  - **Website Enquiries Tab**: View all form submissions.
  - **Orders Management Tab**: Create offline/WhatsApp orders, update order status, delete orders.
  - **Banner Management Tab**: Upload banner with image, event, note (replaces previous banner).
  - **Gallery / Work Showcase Tab**: Upload and delete gallery work photos.
- **Cleanup**: Remove `demo/individual.html`, `demo/corporate.html`, `demo/customized.html`.

## Capabilities

### New Capabilities
- `order-and-gallery-management`: Order tracking for manual/offline orders, updated banner handling, and work gallery showcase.

### Modified Capabilities
*(None)*

## Impact

- `app/database.py`: New `orders` and `gallery_work` tables, banner migration.
- `app/routers/`: Add `app/routers/orders.py` and `app/routers/gallery.py`.
- `demo/`: Clean up standalone category forms and rebuild `demo/admin.html`.
