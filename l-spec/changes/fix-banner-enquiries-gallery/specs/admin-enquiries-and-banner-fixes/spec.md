## Purpose

Provides backend enquiry deletion and updates UI rendering scripts for customer banners, enquiry status controls, and gallery uploads.

## ADDED Requirements

### Requirement: Website Enquiry Deletion
The system SHALL support deleting website enquiry records via REST API.

#### Scenario: Admin deletes enquiry
- **WHEN** an admin calls `DELETE /api/admin/enquiries/{id}`
- **THEN** the enquiry is removed from PostgreSQL and a success message is returned.

### Requirement: Customer Banner View Script
The customer page SHALL properly render single active banner objects returned by `GET /api/banners/active`.

#### Scenario: Display active banner
- **WHEN** `GET /api/banners/active` returns active banner object
- **THEN** `demo/customer.html` displays the image, event title, and note.
