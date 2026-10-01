## 1. Backend Validation Update

- [x] 1.1 Update `app/schemas.py` to add validators for `quantity >= 20` when enquiry type is `corporate` or `customized`, and confirm corporate `company_name` requirement.
- [x] 1.2 Test backend validation rules with sample JSON payloads in `app/routers/enquiries.py`.

## 2. Dynamic Frontend Demo Updates

- [x] 2.1 Update `demo/enquiry.html` with dynamic field switching for Individual, Corporate (with delegate gifting options and min quantity 20), and Customized gifting forms.
- [x] 2.2 Create category-specific landing pages (`demo/individual.html`, `demo/corporate.html`, `demo/customized.html`) with pre-set form fields without category selectors.
