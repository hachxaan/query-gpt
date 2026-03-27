import os
import csv
import io
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_MESSAGING_SERVICE_SID = os.getenv('TWILIO_MESSAGING_SERVICE_SID', '')

TWILIO_MESSAGES_URL = (
    f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
)

MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds
COURTESY_DELAY = 1  # seconds between each API call


def _get_twilio_session():
    """Create a requests Session with retry logic for transient errors."""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.auth = HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    return session


def _log_twilio_config():
    """Log Twilio configuration status (without exposing full secrets)."""
    sid_preview = f"{TWILIO_ACCOUNT_SID[:6]}...{TWILIO_ACCOUNT_SID[-4:]}" if len(TWILIO_ACCOUNT_SID) > 10 else '(empty)'
    token_set = 'SET' if TWILIO_AUTH_TOKEN else 'EMPTY'
    msid_preview = f"{TWILIO_MESSAGING_SERVICE_SID[:6]}...{TWILIO_MESSAGING_SERVICE_SID[-4:]}" if len(TWILIO_MESSAGING_SERVICE_SID) > 10 else '(empty)'
    logger.debug("Twilio config -> SID: %s | Token: %s | MessagingSID: %s | URL: %s",
                 sid_preview, token_set, msid_preview, TWILIO_MESSAGES_URL)


def send_single_sms(phone_number: str, message: str) -> dict:
    """Send a single SMS via Twilio API. Returns the JSON response."""
    _log_twilio_config()

    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_MESSAGING_SERVICE_SID]):
        logger.error("Twilio credentials missing: SID=%s TOKEN=%s MSID=%s",
                     bool(TWILIO_ACCOUNT_SID), bool(TWILIO_AUTH_TOKEN),
                     bool(TWILIO_MESSAGING_SERVICE_SID))
        raise ValueError("Twilio credentials are not configured")

    # Normalize phone number: ensure +1 prefix
    original_phone = phone_number
    phone_number = phone_number.strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
    if not phone_number.startswith('+'):
        if not phone_number.startswith('1'):
            phone_number = f"+1{phone_number}"
        else:
            phone_number = f"+{phone_number}"

    logger.info("Sending SMS -> To: %s (original: %s) | Message length: %d",
                phone_number, original_phone, len(message))

    payload = {
        'Body': message,
        'MessagingServiceSid': TWILIO_MESSAGING_SERVICE_SID,
        'To': phone_number,
    }
    logger.debug("Twilio request payload: %s", {k: v if k != 'Body' else f'{v[:50]}...' for k, v in payload.items()})

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            session = _get_twilio_session()
            response = session.post(
                TWILIO_MESSAGES_URL,
                data=payload,
                timeout=30,
            )
            break  # Success — exit retry loop
        except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
            last_error = e
            logger.warning("Twilio attempt %d/%d failed for %s: %s",
                           attempt, MAX_RETRIES, phone_number, e)
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF * attempt
                logger.info("Retrying in %d seconds...", wait)
                time.sleep(wait)
            else:
                logger.error("Twilio GAVE UP after %d attempts for %s: %s",
                             MAX_RETRIES, phone_number, e)
                raise
        except requests.RequestException as e:
            logger.error("Twilio HTTP request failed for %s: %s", phone_number, e)
            raise

    logger.info("Twilio response -> HTTP %d for %s", response.status_code, phone_number)

    try:
        result = response.json()
    except ValueError:
        logger.error("Twilio returned non-JSON response: %s", response.text[:500])
        return {'error_code': 'INVALID_RESPONSE', 'message': response.text[:200]}

    if response.status_code not in (200, 201):
        logger.error("Twilio SMS FAILED to %s -> HTTP %d | code: %s | message: %s",
                     phone_number, response.status_code,
                     result.get('code', 'N/A'), result.get('message', 'N/A'))
        logger.debug("Twilio full error response: %s", result)
        return {
            'error_code': result.get('code', response.status_code),
            'message': result.get('message', 'Unknown Twilio error'),
        }
    else:
        logger.info("Twilio SMS OK to %s -> SID: %s | Status: %s",
                    phone_number, result.get('sid', 'N/A'), result.get('status', 'N/A'))

    return result


def send_bulk_sms_from_csv(csv_file, output_dir=None, input_filename=None) -> dict:
    """
    Read a CSV with columns 'Phone Number' and 'SMS Message',
    send each SMS, and return a summary.
    Failed numbers are written to <input_filename>_fail.csv.
    """
    content = csv_file.read()
    if isinstance(content, bytes):
        content = content.decode('utf-8')

    reader = csv.DictReader(io.StringIO(content))

    total = 0
    success = 0
    errors = []

    fieldnames = reader.fieldnames
    logger.info("Bulk SMS CSV headers: %s", fieldnames)

    if not fieldnames or 'Phone Number' not in fieldnames or 'SMS Message' not in fieldnames:
        logger.error("CSV missing required columns. Found: %s | Expected: 'Phone Number', 'SMS Message'", fieldnames)
        return {'total': 0, 'success': 0, 'failed': 0, 'errors': [{'phone': '', 'error': 'CSV missing required columns'}]}

    for row in reader:
        phone = row.get('Phone Number', '').strip()
        message = row.get('SMS Message', '').strip()

        if not phone or not message:
            logger.warning("Bulk SMS row %d skipped: phone=%r message_len=%d", total + 1, phone, len(message))
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
        time.sleep(COURTESY_DELAY)

    logger.info("Bulk SMS finished: total=%d success=%d failed=%d", total, success, total - success)
    if errors:
        logger.warning("Bulk SMS errors (first 10): %s", errors[:10])

    # Write fail CSV
    if errors and output_dir and input_filename:
        base_name = input_filename.rsplit('.', 1)[0] if '.' in input_filename else input_filename
        fail_filename = f"{base_name}_fail.csv"
        fail_path = os.path.join(output_dir, fail_filename)
        try:
            with open(fail_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['Phone Number', 'Error'])
                writer.writeheader()
                for err in errors:
                    writer.writerow({'Phone Number': err.get('phone', ''), 'Error': err.get('error', '')})
            logger.info("Fail CSV written: %s (%d rows)", fail_path, len(errors))
        except Exception:
            logger.exception("Failed to write fail CSV: %s", fail_path)

    return {
        'total': total,
        'success': success,
        'failed': total - success,
        'errors': errors[:50],
    }
