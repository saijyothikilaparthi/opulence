## Purpose

Provides backend and admin console support for separate website enquiry tracking, manual offline order management, single active banner replacement, and work gallery showcase.

## ADDED Requirements

### Requirement: Manual Order Management
The system SHALL store manual/offline orders (WhatsApp/Instagram) and allow admins to add, list, update status, and delete orders.

#### Scenario: Admin adds manual order
- **WHEN** an admin posts a new order with customer_name, phone, event, amount, and status
- **THEN** the order record is created in PostgreSQL and assigned an ID.

#### Scenario: Admin deletes an order
- **WHEN** an admin issues `DELETE /api/admin/orders/{id}`
- **THEN** the order record is permanently removed from PostgreSQL.

### Requirement: Single Active Banner Replacement
The system SHALL deactivate existing banners when a new banner with `event` and `note` is uploaded.

#### Scenario: Single banner replacement
- **WHEN** an admin uploads a new banner
- **THEN** all previous banners are marked inactive (`is_active = FALSE`) so only the newly uploaded banner remains active.

### Requirement: Work Gallery Management
The system SHALL allow admins to upload images of past work to display in the website gallery and delete unwanted work images.

#### Scenario: Upload work picture
- **WHEN** an admin uploads an image to `POST /api/admin/gallery`
- **THEN** the image is saved to disk and recorded in the gallery database table.

#### Scenario: Delete work picture
- **WHEN** an admin issues `DELETE /api/admin/gallery/{id}`
- **THEN** the gallery entry and file reference are removed.
