"""v1 notification hook (replaced by services/notification_service.py)."""

TEMPLATES = {"email": "booking_confirmation_v1", "sms": "booking_sms_legacy"}


def notify_booking(payload, context):
    db = context["db"]
    return [db.insert("outbox", {"channel": "email", "to": payload["customer"],
                                 "template": TEMPLATES["email"], "ref": payload["ref"]})]
