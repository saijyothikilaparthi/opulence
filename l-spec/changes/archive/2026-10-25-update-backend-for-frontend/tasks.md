## 1. Database Schema Updates

- [x] 1.1 Update `app/database.py` to add new columns to the `enquiries` table for personalization details and verify the table is created correctly.
- [x] 1.2 Update `app/database.py` to add a `category` column to the `gallery_work` table and verify the table is created correctly.

## 2. API Endpoint Updates

- [x] 2.1 Update `app/schemas.py` to include the new fields in `EnquiryCreate` and `GalleryCreate` models and verify the models validate correctly.
- [x] 2.2 Update `app/routers/enquiries.py` to accept the new fields in the `POST /api/enquiries` endpoint and verify the endpoint saves the data correctly.
- [x] 2.3 Update `app/routers/gallery.py` to accept the `category` field in the `POST /api/gallery/admin` endpoint and verify the endpoint saves the data correctly.
- [x] 2.4 Update `app/routers/gallery.py` to support filtering by category in the `GET /api/gallery` endpoint and verify the endpoint returns the correct data.

## 3. Admin Dashboard UI Updates

- [x] 3.1 Update `demo/admin.html` to use the same CSS styles, colors, and typography as the frontend website and verify the UI matches the frontend theme.
- [x] 3.2 Update `demo/admin.html` to add a category selection dropdown when uploading a gallery image and verify the category is sent to the backend correctly.

## 4. Frontend Integration

- [x] 4.1 Update `frontend/index.html` and `frontend/js/main.js` to fetch gallery images by category for the "Our Work" section and verify the images are displayed correctly.
- [x] 4.2 Update `frontend/index.html` and `frontend/js/main.js` to fetch gallery images for the homepage carousel and verify the images are displayed correctly.

## 5. WhatsApp Notifications

- [x] 5.1 Implement the `send_whatsapp_notification` function in `app/services/whatsapp.py` to send a notification when a new enquiry is created and verify the notification is sent correctly.