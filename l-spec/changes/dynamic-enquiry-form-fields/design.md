## Context

The backend validation in `app/schemas.py` and dynamic demo frontend (`demo/enquiry.html`) currently implement basic enquiry handling. To support category-specific requirements (such as minimum quantity rules for corporate/customized, corporate occasion / delegate gifting options, and dedicated category landing page forms without category selection dropdowns), we need enhanced validation models and updated demo pages.

## Goals / Non-Goals

**Goals:**
- Update `EnquiryCreate` schema in `app/schemas.py` with custom Pydantic field validators:
  - Validate `quantity >= 20` when `enquiry_type` is `corporate` or `customized`.
  - Validate required `company_name` for `corporate` enquiries.
- Update `demo/enquiry.html` with accurate fields for:
  - Individual: Name, Phone, Email, Budget, Occasion, Required Date, Customization/Ideas, Reference Image file/URL.
  - Corporate: Name, Phone, Email, Company Name, Occasion Selection (e.g., Festival / Event / Delegate Gifting), Quantity (min 20), Per-item/Total Budget (optional).
  - Customized: Name, Phone, Email, Occasion, Quantity (min 20), Per-item/Total Budget, Ideas/Requirements/Thoughts, Reference Image file/URL.
- Add category-specific demo pages:
  - `demo/individual.html`
  - `demo/corporate.html`
  - `demo/customized.html`
  where the category selector is omitted and the form directly presents category-specific fields.

**Non-Goals:**
- Modifying PostgreSQL database schema (existing `enquiries` table already supports all necessary fields).
- Modifying production frontend framework assets (separate developer project).

## Decisions

- **Validator in Pydantic (`app/schemas.py`)**:
  - Use Pydantic `@field_validator` on `quantity` and `company_name` checking `info.data.get("enquiry_type")`.
  - Rationale: Ensures server-side integrity and clean API error reporting (`HTTP 422 Unprocessable Entity`) if rules are violated.
- **Dedicated Demo Pages vs Dynamic Home Form**:
  - `demo/enquiry.html`: Includes the dynamic dropdown selector for home page testing.
  - `demo/individual.html`, `demo/corporate.html`, `demo/customized.html`: Provide direct dedicated form pages for individual routes.

## Risks / Trade-offs

- **Risk**: Frontend client submitting quantities < 20 for corporate/customized enquiries.
  - **Mitigation**: Clear validation message returned in `HTTP 422` error response and standard HTML5 min attribute on input fields.
