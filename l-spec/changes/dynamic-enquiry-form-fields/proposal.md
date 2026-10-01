## Why

The current enquiry form and validation schema enforce a fixed structure that doesn't fully accommodate distinct rules across categories:
1. Category-specific dynamic form fields on the home page (Individual vs Corporate vs Customized).
2. Category-specific business rules (e.g., minimum quantity of 20 for Corporate and Customized; delegate gifting vs occasion selection under corporate).
3. Direct category landing pages where category selection is implicit and preset, hiding the category dropdown and rendering the relevant form fields directly.

Updating backend schemas, API validation, and dynamic HTML test forms ensures a clean API contract for frontend developers while supporting category-specific enquiry submission flows.

## What Changes

- **Schema & Backend Validation (`app/schemas.py`, `app/routers/enquiries.py`)**:
  - Update `EnquiryCreate` schema to validate minimum quantity of 20 for `corporate` and `customized` enquiry types.
  - Support `occasion_type` or `occasion` options including delegate gifting under corporate gifting.
  - Update validation rules for budget and customization details across individual, corporate, and customized categories.
- **Dynamic Frontend / Demo Forms (`demo/enquiry.html`, category-specific demos)**:
  - Enhance dynamic dropdown form behavior on the home page enquiry form.
  - Support direct category-specific forms (where category is preset and dropdown is omitted).

## Capabilities

### New Capabilities
- `enquiry-system`: Dynamic category-based enquiry validation and custom field handling for individual, corporate, and customized gifting.

### Modified Capabilities
*(None)*

## Impact

- `app/schemas.py`: Validation rules for `EnquiryCreate`.
- `app/routers/enquiries.py`: `POST /api/enquiries` logic and request handling.
- `demo/enquiry.html`: Updated demo interface demonstrating dynamic switching and category-specific pre-set forms.
