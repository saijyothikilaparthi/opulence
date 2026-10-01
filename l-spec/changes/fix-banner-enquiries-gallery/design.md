## Context

Addressing three specific UI / API updates:
1. `demo/customer.html` script expecting list instead of object.
2. `demo/admin.html` missing status selector and delete button on Enquiries tab.
3. `app/routers/enquiries.py` missing DELETE route.

## Goals / Non-Goals

**Goals:**
- Add `DELETE /api/admin/enquiries/{id}` endpoint in `app/routers/enquiries.py`.
- Fix `demo/customer.html`.
- Fix `demo/admin.html` enquiries table actions and gallery upload fetch call.
