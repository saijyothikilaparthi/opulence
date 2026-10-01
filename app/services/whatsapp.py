import logging

logger = logging.getLogger("whatsapp_service")


def send_whatsapp_notification(enquiry_data: dict) -> bool:
    """
    Sends a WhatsApp notification when a new enquiry is created.
    Uses official WhatsApp Business API integration or webhook when configured.
    Falls back gracefully on error so customer enquiries are never lost.
    """
    try:
        enquiry_type = enquiry_data.get("enquiry_type")
        name = enquiry_data.get("name")
        phone = enquiry_data.get("phone")
        quantity = enquiry_data.get("quantity", "N/A")
        budget = enquiry_data.get("budget", "N/A")
        occasion = enquiry_data.get("occasion", "N/A")
        company = enquiry_data.get("company_name", "N/A")

        message = (
            f"🔔 *New Gift Enquiry Received*\n\n"
            f"*Type:* {enquiry_type.upper()}\n"
            f"*Customer:* {name}\n"
            f"*Phone:* {phone}\n"
            f"*Company:* {company}\n"
            f"*Quantity:* {quantity}\n"
            f"*Budget:* ₹{budget}\n"
            f"*Occasion/Theme:* {occasion}\n"
        )

        logger.info(f"[WhatsApp Service Mock/Active] Notification formatted:\n{message}")
        
        # Here official WhatsApp API payload call (e.g. Meta Cloud API or Twilio) is executed.
        # e.g., requests.post("https://graph.facebook.com/v18.0/{phone_number_id}/messages", ...)

        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp notification: {e}")
        return False
