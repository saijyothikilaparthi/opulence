## Context

The frontend has been updated with new fields for the consultation form and a new "Our Work" gallery section that categorizes past work. The backend needs to be updated to support these new frontend features, including dynamic gallery management from the admin dashboard with category selection, and connecting the gallery images to the homepage carousel. Additionally, the admin dashboard UI needs to be updated to match the frontend theme, and WhatsApp notifications need to be sent when a user submits an enquiry.

## Goals / Non-Goals

**Goals:**
- Update the `enquiries` table and API endpoints to support new fields from the updated frontend consultation form.
- Update the `gallery_work` table and API endpoints to support categories for gallery images.
- Update the admin dashboard UI (`demo/admin.html`) to match the frontend theme.
- Add the ability to select a category when uploading a gallery image in the admin dashboard.
- Connect the backend gallery API to the frontend homepage carousel and "Our Work" section to display images dynamically based on their category.
- Implement WhatsApp notifications for new enquiries.

**Non-Goals:**
- Do not change the frontend code (HTML, CSS, JS) except for integrating the updated backend API.
- Do not add a frontend interface for managing banners (keep it in the admin dashboard).

## Decisions

- **Database Schema Updates**: Add new columns to the `enquiries` table for personalization details and to the `gallery_work` table for categories.
- **API Endpoint Updates**: Update the `POST /api/enquiries` endpoint to accept the new fields and the `GET /api/gallery` endpoint to support filtering by category.
- **Admin Dashboard UI**: Update the `demo/admin.html` file to use the same CSS styles, colors, and typography as the frontend website.
- **WhatsApp Notifications**: Implement the `send_whatsapp_notification` function in `app/services/whatsapp.py` to send a notification when a new enquiry is created.

## Risks / Trade-offs

- **Risk**: The frontend integration might break if the API endpoints are not updated correctly.
  - **Mitigation**: Test the API endpoints thoroughly before integrating them with the frontend.
- **Risk**: The WhatsApp notification service might fail or be rate-limited.
  - **Mitigation**: Implement error handling and fallback mechanisms in the `send_whatsapp_notification` function.