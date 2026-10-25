# gallery-categories Specification

## Purpose
Provides support for categorizing gallery images and displaying them dynamically on the frontend based on their category.

## Requirements

### Requirement: Gallery images can be categorized
The system SHALL allow admin users to assign a category to a gallery image when uploading it. The allowed categories MUST match the frontend terminology: "Corporate Gifting", "Celebrations & Bulk", and "Individual Hampers".

#### Scenario: Uploading a gallery image with a category
- **WHEN** an admin uploads a gallery image and selects a category from the updated list
- **THEN** the system saves the image and associates it with the selected category

### Requirement: Frontend can fetch gallery images by category
The system SHALL provide an API endpoint to fetch gallery images filtered by category.

#### Scenario: Fetching gallery images for a specific category
- **WHEN** the frontend requests gallery images for a specific category
- **THEN** the system returns only the images associated with that category

### Requirement: Homepage carousel displays gallery images
The system SHALL provide an API endpoint to fetch gallery images for the homepage carousel.

#### Scenario: Fetching gallery images for the carousel
- **WHEN** the frontend requests gallery images for the carousel
- **THEN** the system returns a list of gallery images to be displayed in the carousel
