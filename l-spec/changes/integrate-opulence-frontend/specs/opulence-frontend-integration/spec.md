## Purpose

Integrates the official Opulence production frontend and connects it to the FastAPI backend endpoints for enquiries, active seasonal banners, and work gallery.

## ADDED Requirements

### Requirement: Opulence Frontend Static Serving
The backend SHALL serve the production frontend files from `frontend/` at the root/static web path.

#### Scenario: User visits frontend website
- **WHEN** a user opens the home URL
- **THEN** the system SHALL serve `frontend/index.html` along with its assets (`css/`, `js/`, `assets/`).

### Requirement: Seasonal Announcement Banner Integration
The home page (`frontend/index.html`) SHALL fetch `GET /api/banners/active` and display the current active seasonal announcement.

#### Scenario: Dynamic banner display
- **WHEN** the home page loads
- **THEN** `js/main.js` calls `GET /api/banners/active` and populates the seasonal announcement section.

### Requirement: Work Gallery Integration
The home page (`frontend/index.html`) SHALL fetch `GET /api/gallery` and render the work gallery items uploaded by the admin.

#### Scenario: Dynamic gallery display
- **WHEN** the home page loads
- **THEN** `js/main.js` calls `GET /api/gallery` and inserts gallery image cards into the work gallery grid.

### Requirement: Production Enquiry Submission
All modal enquiry forms across the site SHALL submit data via HTTP POST to `POST /api/enquiries`.

#### Scenario: Customer submits enquiry modal
- **WHEN** a visitor submits the enquiry modal form
- **THEN** `js/main.js` sends `POST /api/enquiries` with customer brief data and displays success confirmation.
