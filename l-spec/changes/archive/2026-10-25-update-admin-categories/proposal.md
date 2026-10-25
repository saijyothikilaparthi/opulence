## Why

The admin dashboard currently uses category names ("individual", "corporate", "customized") that do not match the terminology used on the frontend homepage ("Collections"). To ensure consistency across the application, the admin dashboard needs to be updated to use the frontend's terminology for categories. Additionally, when gallery images are uploaded, they need to be correctly associated with these new category names so they appear in the appropriate sections on the frontend.

## What Changes

- **Admin Dashboard UI**: Update the category selection dropdown in `demo/admin.html` to use the new category names: "Corporate Gifting", "Celebrations & Bulk", and "Individual Hampers".
- **Gallery Upload Logic**: Ensure that when a gallery image is uploaded with one of these new categories, it is saved correctly in the database.
- **Frontend Integration**: Ensure the frontend correctly fetches and displays gallery images based on these new category names.

## Capabilities

### Modified Capabilities
- `gallery-categories`: Update the allowed category names to match the frontend terminology ("Corporate Gifting", "Celebrations & Bulk", "Individual Hampers").

## Impact

- `demo/admin.html`: Update the `<select>` options for gallery categories.
- `frontend/js/main.js`: Ensure the frontend fetches gallery images using the correct category names if it filters by category.
- `app/database.py` and `app/schemas.py`: No changes needed as the `category` field is a generic string, but the data stored will now use the new names.