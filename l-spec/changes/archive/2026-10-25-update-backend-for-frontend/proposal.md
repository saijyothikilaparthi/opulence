## Why

The frontend has been updated with new fields for the consultation form (e.g., "personalize your hamper") and a new "Our Work" gallery section that categorizes past work. The backend needs to be updated to support these new frontend features, including dynamic gallery management from the admin dashboard with category selection, and connecting the gallery images to the homepage carousel. Additionally, the admin dashboard UI needs to be updated to match the frontend theme, and WhatsApp notifications need to be sent when a user submits an enquiry.

## What Changes

- **Enquiries**: Update the `enquiries` table and API endpoints to support new fields from the updated frontend consultation form (e.g., personalization details).
- **Gallery**: Update the `gallery_work` table and API endpoints to support categories for gallery images.
- **Admin Dashboard**: Update the admin dashboard UI (`demo/admin.html`) to match the frontend theme.
- **Admin Dashboard - Gallery**: Add the ability to select a category when uploading a gallery image.
- **Frontend Integration**: Connect the backend gallery API to the frontend homepage carousel and "Our Work" section to display images dynamically based on their category.
- **Notifications**: Implement WhatsApp notifications for new enquiries (currently mocked, needs to be functional or properly integrated with the admin dashboard).

## Capabilities

### New Capabilities
- `gallery-categories`: Support for categorizing gallery images and displaying them dynamically on the frontend.
- `admin-theme`: Updated admin dashboard UI to match the frontend theme.

### Modified Capabilities
- `enquiry-management`: Updated to support new fields from the frontend consultation form and send WhatsApp notifications.

## Impact

- `app/database.py`: Schema updates for `enquiries` and `gallery_work` tables.
- `app/schemas.py`: Pydantic model updates for enquiries and gallery work.
- `app/routers/enquiries.py`: API endpoint updates for enquiries.
- `app/routers/gallery.py`: API endpoint updates for gallery work.
- `app/services/whatsapp.py`: Implementation of WhatsApp notifications.
- `demo/admin.html`: UI updates and new gallery category selection.
- `frontend/index.html` and `frontend/js/main.js`: Integration with the updated gallery API.