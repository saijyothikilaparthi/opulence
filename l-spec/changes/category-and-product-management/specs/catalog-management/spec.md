## Purpose

Provides storage and REST API endpoints for managing categories and gift products.

## ADDED Requirements

### Requirement: Category Management
The system SHALL store gift categories and provide APIs to create and list active categories.

#### Scenario: List active categories
- **WHEN** a request is made to `GET /api/categories`
- **THEN** the system SHALL return all active categories sorted by name.

#### Scenario: Admin create category
- **WHEN** an admin posts a new category with a `name`
- **THEN** the system SHALL create the category record in PostgreSQL and return its ID.

### Requirement: Product Management
The system SHALL store products associated with categories and provide APIs to manage and retrieve them.

#### Scenario: List products by category
- **WHEN** a client requests `GET /api/products?category_id=1`
- **THEN** the system SHALL return only active products belonging to category ID 1.

#### Scenario: Get single product details
- **WHEN** a client requests `GET /api/products/{id}` for an existing product
- **THEN** the system SHALL return the detailed product record or HTTP 404 if not found.
