## Context

The user provided the official frontend application inside `Opulence/`. We move `Opulence/frontend` to `frontend/` and `Opulence/README.md` to `README.md`, delete `Opulence/`, mount `frontend/` in `app/main.py`, and wire `frontend/js/main.js` to the REST APIs.

## Goals / Non-Goals

**Goals:**
- Move `Opulence/frontend/` to `frontend/` and `Opulence/README.md` to `README.md`, then remove `Opulence/`.
- Mount `frontend/` in `app/main.py`.
- Remove sample customer files in `demo/` (`customer.html`, `enquiry.html`, `individual.html`, `corporate.html`, `customized.html`) while preserving `demo/admin.html`.
- Update `frontend/js/main.js` to:
  1. Post enquiry modal submissions to `POST /api/enquiries`.
  2. Fetch `GET /api/banners/active` and update seasonal announcement text and banner image.
  3. Fetch `GET /api/gallery` and populate work gallery images.

## Decisions

- **Preserve Admin Dashboard (`demo/admin.html`)**: Leave `demo/admin.html` mounted under `/demo` for backend management.
