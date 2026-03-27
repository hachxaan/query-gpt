import os
import csv
import io
import logging
import requests
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_MESSAGING_SERVICE_SID = os.getenv('TWILIO_MESSAGING_SERVICE_SID', '')

TWILIO_MESSAGES_URL = (
    f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
)


def send_single_sms(phone_number: str, message: str) -> dict:
    """Send a single SMS via Twilio API. Returns the JSON response."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_MESSAGING_SERVICE_SID]):
        raise ValueError("Twilio credentials are not configured")

    # Normalize phone number: ensure +1 prefix
    phone_number = phone_number.strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    if not phone_number.startswith('+'):
        if not phone_number.startswith('1'):
            phone_number = f"+1{phone_number}"
        else:
            phone_number = f"+{phone_number}"

    response = requests.post(
        TWILIO_MESSAGES_URL,
        data={
            'Body': message,
            'MessagingServiceSid': TWILIO_MESSAGING_SERVICE_SID,
            'To': phone_number,
        },
        auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        timeout=30,
    )

    result = response.json()
    if response.status_code not in (200, 201):
        logger.error("Twilio SMS error to %s: %s", phone_number, result.get('message', ''))
    else:
        logger.info("SMS sent to %s – SID: %s", phone_number, result.get('sid', ''))

    return result


def send_bulk_sms_from_csv(csv_file) -> dict:
    """
    Read a CSV with columns 'Phone Number' and 'SMS Message',
    send each SMS, and return a summary.
    """
    content = csv_file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))

    total = 0
    success = 0
    errors = []

    for row in reader:
        phone = row.get('Phone Number', '').strip()
        message = row.get('SMS Message', '').strip()

        if not phone or not message:
            errors.append({'phone': phone, 'error': 'Missing phone number or message'})
            total += 1
            continue

        try:
            result = send_single_sms(phone, message)
            if result.get('error_code') is None:
                success += 1
            else:
                errors.append({
                    'phone': phone,
                    'error': result.get('message', 'Unknown error'),
                })
        except Exception as e:
            logger.exception("Error sending SMS to %s", phone)
            errors.append({'phone': phone, 'error': str(e)})

        total += 1

    return {
        'total': total,
        'success': success,
        'failed': total - success,
        'errors': errors[:50],  # Limit error details returned
    }
