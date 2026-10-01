## Why

1. **Customer Banner Image Fix (`demo/customer.html`)**: The active banner API endpoint was updated to return `data: { ... }` (single active object) instead of `data: [...]` (list). `demo/customer.html` needs to handle the updated object structure to display the active banner correctly.
2. **Website Enquiries Controls & Deletion (`demo/admin.html`, `app/routers/enquiries.py`)**: Admins need to update enquiry status (Pending, Contacted, In-Progress, Converted, Cancelled) and delete unwanted website enquiry records (`DELETE /api/admin/enquiries/{id}`).
3. **Work Gallery Upload Fix (`demo/admin.html`)**: Ensure gallery image uploads work smoothly with proper form data processing.

## What Changes

- **Backend Endpoints (`app/routers/enquiries.py`)**: Add `DELETE /api/admin/enquiries/{id}` endpoint.
- **Customer View (`demo/customer.html`)**: Update script to handle single banner object `json.data` properly.
- **Admin Console (`demo/admin.html`)**:
  - Add status dropdown selector (Pending, Contacted, In-Progress, Converted, Cancelled) for Website Enquiries.
  - Add **Delete** button for Website Enquiries.
  - Fix Work Gallery photo submission payload handling.

## Capabilities

### New Capabilities
- `admin-enquiries-and-banner-fixes`: Enquiry deletion, status update selector, customer banner display fix, and gallery upload fixes.

### Modified Capabilities
*(None)*

## Impact

- `app/routers/enquiries.py`: Added DELETE endpoint.
- `demo/customer.html`: Fixed banner rendering script.
- `demo/admin.html`: Updated enquiry action controls and gallery upload form.
