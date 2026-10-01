## Why

The user provided the official frontend application files in the `Opulence/` directory (`Opulence/frontend/` and `Opulence/README.md`). We need to:
1. Move `frontend/` and `README.md` to the root project directory (`/home/sai_jyothi/gift-backend/frontend/` and `/home/sai_jyothi/gift-backend/README.md`).
2. Remove the now empty/redundant `Opulence/` wrapper directory.
3. Clean up sample/demo customer HTML files (`demo/customer.html`, `demo/enquiry.html`, `demo/individual.html`, `demo/corporate.html`, `demo/customized.html`) while preserving `demo/admin.html` for backend administration.
4. Mount `frontend/` as static assets in FastAPI (`app/main.py`) or connect API endpoints in `frontend/js/main.js`.
5. Connect the backend endpoints dynamically:
   - **Active Banner / Announcement**: Fetch `GET /api/banners/active` and render the seasonal announcement banner on `frontend/index.html`.
   - **Work Showcase Gallery**: Fetch `GET /api/gallery` and render gallery photos dynamically on `frontend/index.html`.
   - **Enquiry Form Submission**: Connect form in `frontend/js/main.js` to `POST /api/enquiries`.

## What Changes

- **Directory Restructuring**: Move files from `Opulence/` to root, remove `Opulence/`.
- **FastAPI Static Mount (`app/main.py`)**: Mount `/` or `/site` for the production frontend (`frontend/`).
- **Frontend JavaScript (`frontend/js/main.js`)**: Connect enquiry form submission to `POST /api/enquiries`, fetch and render active banner in seasonal announcement section, and fetch & render work gallery images.
- **Cleanup**: Remove temporary sample customer HTML files from `demo/` except `demo/admin.html`.

## Capabilities

### New Capabilities
- `opulence-frontend-integration`: Real production frontend static site integration and API wiring for enquiries, active banners, and work gallery.

### Modified Capabilities
*(None)*

## Impact

- `frontend/`: Real production frontend site.
- `app/main.py`: Mounted static directory for frontend.
- `frontend/js/main.js`: API integration scripts for banner, enquiry, and gallery endpoints.
