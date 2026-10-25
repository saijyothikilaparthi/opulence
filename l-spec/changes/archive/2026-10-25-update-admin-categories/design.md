## Context

See proposal.md for motivation. The admin dashboard currently uses generic category names ("individual", "corporate", "customized") for gallery uploads, which do not match the frontend's "Collections" terminology ("Corporate Gifting", "Celebrations & Bulk", "Individual Hampers").

## Goals / Non-Goals

**Goals:**
- Update the category selection dropdown in the admin dashboard to use the new terminology.
- Ensure the frontend correctly fetches and displays gallery images based on these new category names.

**Non-Goals:**
- Do not change the database schema (the `category` field is already a string).
- Do not migrate existing data (assuming this is a fresh setup or existing data can be manually updated if needed).

## Decisions

- **Admin Dashboard UI**: Update the `<select id="workCategory">` options in `demo/admin.html` to use the new category names as both the `value` and the display text.
- **Frontend Integration**: Update `frontend/js/main.js` to ensure that if it filters by category, it uses the new names. The frontend currently fetches all gallery images and displays them, but we need to ensure the category displayed on the tile matches the new terminology.

## Risks / Trade-offs

- **Risk**: Existing gallery images in the database might have the old category names.
  - **Mitigation**: This is acceptable for now, as new uploads will use the correct names. If necessary, a manual database update can be performed later.