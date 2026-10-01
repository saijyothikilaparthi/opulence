## Purpose

Provides backend validation and API behavior for category-specific enquiry submissions (Individual, Corporate, and Customized gifting).

## ADDED Requirements

### Requirement: Category-Based Field Validation
The system SHALL validate incoming enquiry submissions according to the specified enquiry category.

#### Scenario: Corporate enquiry validation
- **WHEN** a client submits a `corporate` enquiry
- **THEN** `company_name` MUST be present and non-empty, and `quantity` MUST be at least 20.

#### Scenario: Customized enquiry validation
- **WHEN** a client submits a `customized` enquiry
- **THEN** `quantity` MUST be at least 20 if specified, and custom requirement details or reference images MAY be included.

#### Scenario: Individual enquiry validation
- **WHEN** a client submits an `individual` enquiry
- **THEN** `name` and `phone` are required, and `quantity` defaults to 1 or any user-provided quantity >= 1.

### Requirement: Support Category-Specific Occasions and Options
The system SHALL support occasion selections tailored to the category, including specific event/occasion types such as delegate gifting under corporate gifting.

#### Scenario: Corporate delegate gifting selection
- **WHEN** an enquiry specifies corporate gifting with `occasion` as "Delegate Gifting" or specific event types
- **THEN** the system SHALL record the occasion detail into the enquiry record without error.
