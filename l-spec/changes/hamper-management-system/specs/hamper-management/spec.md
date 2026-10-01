## Purpose

Provides data structures and REST APIs to configure hamper sizes, create hampers, and assign products inside hampers.

## ADDED Requirements

### Requirement: Hamper Sizes Management
The system SHALL support data-driven hamper sizes with capacity limits.

#### Scenario: List hamper sizes
- **WHEN** a request is made to `GET /api/hamper-sizes`
- **THEN** the system SHALL return configured hamper sizes (e.g. Small, Big) with capacity limits.

#### Scenario: Admin create hamper size
- **WHEN** an admin creates a size with name and max capacity
- **THEN** the record SHALL be stored in PostgreSQL and returned with its ID.

### Requirement: Hamper Template and Composition Management
The system SHALL allow creation of hampers and mapping of products inside each hamper.

#### Scenario: Get hamper details with items
- **WHEN** a client requests `GET /api/hampers/{id}`
- **THEN** the system SHALL return the hamper details along with the list of included products and quantities.

#### Scenario: Admin create hamper with items
- **WHEN** an admin posts a new hamper with name, size_id, price, and item product IDs/quantities
- **THEN** the hamper record and its hamper_items entries SHALL be saved.
