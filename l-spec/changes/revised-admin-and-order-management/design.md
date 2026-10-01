## Context

The simplified requirements focus on:
1. Website enquiries vs Manual orders.
2. WhatsApp notification triggered on website enquiry.
3. Banner replacement (single active banner with image, event, note).
4. Gallery work photo management.
5. Removing redundant demo files (`individual.html`, `corporate.html`, `customized.html`).

## Goals / Non-Goals

**Goals:**
- Add `orders` and `gallery_work` tables to PostgreSQL.
- Add `orders.py` and `gallery.py` routers.
- Update `app/routers/enquiries.py` WhatsApp trigger.
- Update `app/routers/banners.py` logic to set previous banners `is_active = FALSE`.
- Rebuild `demo/admin.html`.
- Remove `demo/individual.html`, `demo/corporate.html`, `demo/customized.html`.
