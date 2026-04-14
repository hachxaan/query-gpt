import os
import logging

import psycopg2
from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tag and service swap mappings for cardholder payroll/prepaid override
# ---------------------------------------------------------------------------
PREPAID_TO_PAYROLL_TAGS = {
    'ALLPrepaid': 'ALLPayroll',
    'NWAPrepaid': 'NWAPayroll',
    'PrepaidCard': 'PayrollCard',
    'ActivePrepaidCardholder': 'ActivePayrollCardholder',
}
PAYROLL_TO_PREPAID_TAGS = {v: k for k, v in PREPAID_TO_PAYROLL_TAGS.items()}

PREPAID_TO_PAYROLL_SERVICES = {
    'ALL_Prepaid': 'ALL_Payroll',
    'NWA_Prepaid': 'NWA_Payroll',
}
PAYROLL_TO_PREPAID_SERVICES = {v: k for k, v in PREPAID_TO_PAYROLL_SERVICES.items()}


# ---------------------------------------------------------------------------
# Database connections
# ---------------------------------------------------------------------------
def get_platform_connection():
    """Connection to the platform DB where vw_mailings views live."""
    db = settings.DATABASES.get('platform_db', {})
    return psycopg2.connect(
        dbname=db.get('NAME'),
        user=db.get('USER'),
        password=db.get('PASSWORD'),
        host=db.get('HOST'),
        port=db.get('PORT', '5432'),
    )


def get_banking_connection():
    """Connection to banking_operation DB (read-only) for cardholder data."""
    return psycopg2.connect(
        dbname=os.environ.get('NAME_BANKING_OPERATION_READ_ONLY', 'banking_operation'),
        user=os.environ.get('USER_BANKING_OPERATION_READ_ONLY'),
        password=os.environ.get('PASSWORD_BANKING_OPERATION_READ_ONLY'),
        host=os.environ.get('HOST_BANKING_OPERATION_READ_ONLY'),
        port=os.environ.get('PORT_BANKING_OPERATION_READ_ONLY', '5432'),
        options='-c search_path={}'.format(
            os.environ.get('SCHEMA_BANKING_OPERATION_READ_ONLY', 'central_payments')
        ),
    )


# ---------------------------------------------------------------------------
# Cardholder payroll lookup
# ---------------------------------------------------------------------------
def get_cardholder_payroll_map():
    """
    Fetch user_id and program_id from cardholder table in banking_operation DB.
    Returns dict {user_id: is_payroll} where is_payroll is True
    if program_id contains 'PAYROLL' (case-insensitive).
    """
    conn = get_banking_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, program_id FROM cardholder")
            return {
                row[0]: 'PAYROLL' in (row[1] or '').upper()
                for row in cur.fetchall()
            }
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Tag / file_name swap helpers
# ---------------------------------------------------------------------------
def _swap_tags(tag_mailing, swap_map):
    """Swap tags in a comma-separated tag string using the given mapping."""
    if not tag_mailing:
        return tag_mailing
    tags = tag_mailing.split(',')
    swapped = [swap_map.get(t, t) for t in tags]
    swapped.sort()
    return ','.join(swapped)


def _swap_file_name_service(file_name, swap_map):
    """Swap the code_service portion in a file_name string."""
    if not file_name:
        return file_name
    for old, new in swap_map.items():
        if '_{}_'.format(old) in file_name:
            return file_name.replace('_{}_'.format(old), '_{}_'.format(new))
    return file_name


# ---------------------------------------------------------------------------
# Audience queries
# ---------------------------------------------------------------------------
def get_audiences_by_company():
    """
    Queries vw_mailings_v5 to retrieve audience data grouped by company.
    Returns (columns, rows) tuple.
    """
    conn = get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vw_mailings_v5 ORDER BY file_name")
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            return columns, rows
    finally:
        conn.close()


def get_audiences_by_wl_and_services():
    """
    Queries vw_mailings_by_white_label_and_services, applies cardholder-based
    payroll/prepaid override, and returns (columns, rows) tuple.

    Override logic:
    - No cardholder record → keep companies.payroll_card default
    - cardholder.program_id contains 'PAYROLL' → Payroll
    - cardholder.program_id does not contain 'PAYROLL' → Prepaid
    """
    # 1. Fetch cardholder payroll map from banking_operation DB
    try:
        cardholder_map = get_cardholder_payroll_map()
    except Exception:
        logger.exception(
            "Failed to fetch cardholder payroll map from banking_operation DB. "
            "Falling back to companies.payroll_card defaults."
        )
        cardholder_map = {}

    # 2. Query the view
    conn = get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM vw_mailings_by_white_label_and_services "
                "ORDER BY file_name"
            )
            columns = [desc[0] for desc in cur.description]
            rows = [list(row) for row in cur.fetchall()]
    finally:
        conn.close()

    # 3. If no cardholder data, return as-is
    if not cardholder_map:
        return columns, rows

    # 4. Post-process: apply cardholder overrides
    user_id_idx = columns.index('User ID')
    payroll_card_idx = columns.index('payroll_card')
    tags_idx = columns.index('Tags')
    file_name_idx = columns.index('file_name')

    for row in rows:
        user_id = row[user_id_idx]

        if user_id not in cardholder_map:
            continue

        new_is_payroll = cardholder_map[user_id]
        current_is_payroll = row[payroll_card_idx]

        if new_is_payroll == current_is_payroll:
            continue

        # Override payroll_card
        row[payroll_card_idx] = new_is_payroll

        if new_is_payroll:
            # Was Prepaid → now Payroll
            row[tags_idx] = _swap_tags(row[tags_idx], PREPAID_TO_PAYROLL_TAGS)
            row[file_name_idx] = _swap_file_name_service(
                row[file_name_idx], PREPAID_TO_PAYROLL_SERVICES
            )
        else:
            # Was Payroll → now Prepaid
            row[tags_idx] = _swap_tags(row[tags_idx], PAYROLL_TO_PREPAID_TAGS)
            row[file_name_idx] = _swap_file_name_service(
                row[file_name_idx], PAYROLL_TO_PREPAID_SERVICES
            )

    return columns, rows
