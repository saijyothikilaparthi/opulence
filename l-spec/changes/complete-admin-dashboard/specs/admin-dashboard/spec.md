## Purpose

Provides management update APIs and a unified web admin console for managing banners, enquiries, categories, products, and hampers.

## ADDED Requirements

### Requirement: Admin Entity Management Endpoints
The system SHALL provide REST APIs to update enquiry status, categories, products, and hampers.

#### Scenario: Update enquiry status
- **WHEN** an admin sends `PUT /api/admin/enquiries/{id}/status` with `{"status": "contacted"}`
- **THEN** the enquiry status is updated in PostgreSQL.

#### Scenario: Update category or product
- **WHEN** an admin sends `PUT /api/admin/categories/{id}` or `PUT /api/admin/products/{id}`
- **THEN** the record is updated in PostgreSQL.

### Requirement: Unified Admin Dashboard
The system SHALL provide a web dashboard under `/demo/admin.html` with tabs to view and manage Banners, Enquiries, Categories, Products, and Hampers.

#### Scenario: Admin views enquiries list
- **WHEN** the admin opens the Enquiries tab in `/demo/admin.html`
- **THEN** all submitted enquiries are loaded and displayed with status update controls.
