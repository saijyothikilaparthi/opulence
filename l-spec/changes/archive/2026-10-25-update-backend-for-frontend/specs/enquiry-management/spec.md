## Purpose

Updates the enquiry management system to support new fields from the frontend consultation form and send WhatsApp notifications.

## ADDED Requirements

### Requirement: Enquiries support personalization details
The system SHALL allow users to submit personalization details (e.g., "personalize your hamper") when creating an enquiry.

#### Scenario: Submitting an enquiry with personalization details
- **WHEN** a user submits an enquiry with personalization details
- **THEN** the system saves the personalization details with the enquiry

### Requirement: WhatsApp notifications for new enquiries
The system SHALL send a WhatsApp notification to the admin when a new enquiry is submitted.

#### Scenario: Sending a WhatsApp notification
- **WHEN** a new enquiry is successfully created
- **THEN** the system sends a WhatsApp notification containing the enquiry details to the admin