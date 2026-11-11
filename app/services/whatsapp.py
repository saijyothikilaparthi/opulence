import logging
import os
from typing import Any

import requests

logger = logging.getLogger("whatsapp_service")


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _clean(value: Any, fallback: str = "N/A", limit: int = 200) -> str:
    text = str(value).strip() if value not in (None, "") else fallback
    if not text:
        text = fallback
    return text[:limit]


def build_enquiry_message(enquiry_data: dict) -> str:
    enquiry_type = _clean(enquiry_data.get("enquiry_type"), "ENQUIRY").upper()
    name = _clean(enquiry_data.get("name"))
    phone = _clean(enquiry_data.get("phone"))
    company = _clean(enquiry_data.get("company_name"))
    place = _clean(enquiry_data.get("place"))
    quantity = _clean(enquiry_data.get("quantity"))
    budget = enquiry_data.get("budget")
    budget_text = f"₹{budget}" if budget not in (None, "") else "N/A"
    occasion = _clean(enquiry_data.get("occasion") or enquiry_data.get("theme"))
    ref = _clean(enquiry_data.get("id"))
    file_url = _clean(enquiry_data.get("file_url"), fallback="")

    lines = [
        "New Gift Enquiry Received",
        f"Ref: #{ref}",
        f"Type: {enquiry_type}",
        f"Customer: {name}",
        f"Phone: {phone}",
        f"Company: {company}",
        f"Place: {place}",
        f"Quantity: {quantity}",
        f"Budget: {budget_text}",
        f"Occasion/Theme: {occasion}",
    ]
    if file_url:
        lines.append(f"Reference: {file_url}")
    return "\n".join(lines)


def _send_meta(enquiry_data: dict, message: str) -> bool:
    token = os.getenv("WHATSAPP_TOKEN") or os.getenv("META_WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID") or os.getenv("META_PHONE_NUMBER_ID")
    admin_to = os.getenv("WHATSAPP_ADMIN_TO") or os.getenv("ADMIN_WHATSAPP_NUMBER")
    if not all([token, phone_number_id, admin_to]):
        logger.warning("WhatsApp (Meta) skipped: missing WHATSAPP_TOKEN/WHATSAPP_PHONE_NUMBER_ID/WHATSAPP_ADMIN_TO")
        return False

    api_version = os.getenv("WHATSAPP_API_VERSION", "v19.0")
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    template_name = (os.getenv("WHATSAPP_TEMPLATE_NAME") or "").strip()

    if template_name:
        lang = os.getenv("WHATSAPP_TEMPLATE_LANG", "en")
        param_names = [p.strip() for p in os.getenv("WHATSAPP_TEMPLATE_PARAM_FIELDS", "enquiry_type,name,phone,quantity,occasion,place,id").split(",") if p.strip()]
        values = {
            "id": _clean(enquiry_data.get("id")),
            "enquiry_type": _clean(enquiry_data.get("enquiry_type"), "ENQUIRY").upper(),
            "name": _clean(enquiry_data.get("name")),
            "phone": _clean(enquiry_data.get("phone")),
            "company_name": _clean(enquiry_data.get("company_name")),
            "place": _clean(enquiry_data.get("place")),
            "quantity": _clean(enquiry_data.get("quantity")),
            "budget": _clean(enquiry_data.get("budget")),
            "occasion": _clean(enquiry_data.get("occasion") or enquiry_data.get("theme")),
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": admin_to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": lang},
                "components": [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": values.get(name, "N/A")} for name in param_names],
                }],
            },
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": admin_to,
            "type": "text",
            "text": {"preview_url": False, "body": message[:4096]},
        }

    response = requests.post(url, headers=headers, json=payload, timeout=12)
    if response.ok:
        logger.info("WhatsApp (Meta) sent: %s", response.text)
        return True
    logger.error("WhatsApp (Meta) failed %s: %s", response.status_code, response.text)
    return False


def _send_twilio(enquiry_data: dict, message: str) -> bool:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g. whatsapp:+14155238886
    admin_to = os.getenv("WHATSAPP_ADMIN_TO") or os.getenv("ADMIN_WHATSAPP_NUMBER")
    if not all([account_sid, auth_token, from_number, admin_to]):
        logger.warning("WhatsApp (Twilio) skipped: missing Twilio/WHATSAPP_ADMIN_TO env vars")
        return False

    to_number = admin_to if str(admin_to).startswith("whatsapp:") else f"whatsapp:+{str(admin_to).lstrip('+')}"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    response = requests.post(
        url,
        data={"From": from_number, "To": to_number, "Body": message[:1600]},
        auth=(account_sid, auth_token),
        timeout=12,
    )
    if response.ok:
        logger.info("WhatsApp (Twilio) sent: %s", response.text[:500])
        return True
    logger.error("WhatsApp (Twilio) failed %s: %s", response.status_code, response.text)
    return False


def _send_webhook(enquiry_data: dict, message: str) -> bool:
    webhook_url = os.getenv("WHATSAPP_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("WhatsApp (webhook) skipped: missing WHATSAPP_WEBHOOK_URL")
        return False
    headers = {"Content-Type": "application/json"}
    secret = os.getenv("WHATSAPP_WEBHOOK_SECRET")
    if secret:
        headers["X-Webhook-Secret"] = secret
    payload = {"message": message, "enquiry": enquiry_data}
    response = requests.post(webhook_url, headers=headers, json=payload, timeout=12)
    if response.ok:
        logger.info("WhatsApp (webhook) sent: %s", response.status_code)
        return True
    logger.error("WhatsApp (webhook) failed %s: %s", response.status_code, response.text)
    return False


def send_whatsapp_notification(enquiry_data: dict) -> bool:
    """
    Sends admin WhatsApp notification for a new enquiry.
    Safe by design: never raises; enquiry DB save/admin dashboard flow remains unaffected.
    """
    try:
        provider = (os.getenv("WHATSAPP_PROVIDER", "meta") or "meta").strip().lower()
        enabled = _truthy(os.getenv("WHATSAPP_ENABLED", "false"))
        message = build_enquiry_message(enquiry_data or {})
        logger.info("WhatsApp enquiry notification prepared (provider=%s, enabled=%s)\n%s", provider, enabled, message)

        if not enabled:
            return False
        if provider == "meta":
            return _send_meta(enquiry_data or {}, message)
        if provider == "twilio":
            return _send_twilio(enquiry_data or {}, message)
        if provider == "webhook":
            return _send_webhook(enquiry_data or {}, message)

        logger.error("Unsupported WHATSAPP_PROVIDER: %s", provider)
        return False
    except Exception as exc:
        logger.exception("Failed to send WhatsApp notification: %s", exc)
        return False
