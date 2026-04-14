import logging
import psycopg2
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_platform_connection():
    """Connection to platform_db where companies_mailing_exclusion lives."""
    db = settings.DATABASES.get('platform_db', {})
    return psycopg2.connect(
        dbname=db.get('NAME'),
        user=db.get('USER'),
        password=db.get('PASSWORD'),
        host=db.get('HOST'),
        port=db.get('PORT', '5432'),
    )


def get_exclusions(search=None):
    """
    Fetch all companies_mailing_exclusion records with company name.
    Optional search filter on company_id, company name, or reason.
    Returns list of dicts.
    """
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            query = """
                SELECT cme.id, cme.company_id, c.name AS company_name, cme.reason
                FROM companies_mailing_exclusion cme
                LEFT JOIN companies c ON c.id = cme.company_id
            """
            params = []
            if search:
                query += """
                    WHERE c.name ILIKE %s
                       OR cme.reason ILIKE %s
                       OR CAST(cme.company_id AS TEXT) = %s
                """
                params = [f'%{search}%', f'%{search}%', search]
            query += " ORDER BY c.name, cme.company_id"
            cur.execute(query, params)
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()


def get_exclusion_by_id(exclusion_id):
    """Fetch a single exclusion record by id."""
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT cme.id, cme.company_id, c.name AS company_name, cme.reason
                   FROM companies_mailing_exclusion cme
                   LEFT JOIN companies c ON c.id = cme.company_id
                   WHERE cme.id = %s""",
                [exclusion_id]
            )
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            return dict(zip(columns, row)) if row else None
    finally:
        conn.close()


def add_exclusion(company_id, reason=None):
    """Add a single company to the mailing exclusion list. Returns new id."""
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO companies_mailing_exclusion (company_id, reason)
                   SELECT %s, %s
                   WHERE NOT EXISTS (
                       SELECT 1 FROM companies_mailing_exclusion WHERE company_id = %s
                   )
                   RETURNING id""",
                [company_id, reason, company_id]
            )
            result = cur.fetchone()
            conn.commit()
            return result[0] if result else None
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_exclusion(exclusion_id, reason):
    """Update the reason of an existing exclusion."""
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE companies_mailing_exclusion SET reason = %s WHERE id = %s",
                [reason, exclusion_id]
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_exclusion(exclusion_id):
    """Delete a single exclusion record."""
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM companies_mailing_exclusion WHERE id = %s",
                [exclusion_id]
            )
            conn.commit()
            return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def bulk_add_exclusions(entries):
    """
    Bulk add exclusions. entries is a list of (company_id, reason) tuples.
    Skips company_ids that already exist. Returns count of inserted records.
    """
    if not entries:
        return 0
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            # Get existing company_ids to skip duplicates
            company_ids = [e[0] for e in entries]
            cur.execute(
                "SELECT company_id FROM companies_mailing_exclusion WHERE company_id = ANY(%s)",
                [company_ids]
            )
            existing = {row[0] for row in cur.fetchall()}
            new_entries = [(cid, reason) for cid, reason in entries if cid not in existing]
            if not new_entries:
                return 0
            from psycopg2.extras import execute_values
            execute_values(
                cur,
                "INSERT INTO companies_mailing_exclusion (company_id, reason) VALUES %s",
                new_entries
            )
            conn.commit()
            return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def bulk_delete_exclusions(ids):
    """
    Bulk delete exclusions by list of ids.
    Returns count of deleted records.
    """
    if not ids:
        return 0
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM companies_mailing_exclusion WHERE id = ANY(%s)",
                [ids]
            )
            conn.commit()
            return cur.rowcount
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def search_companies(term):
    """
    Search companies by name or id for autocomplete.
    Returns list of {id, name} dicts.
    """
    conn = _get_platform_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id, name FROM companies
                   WHERE name ILIKE %s OR CAST(id AS TEXT) LIKE %s
                   ORDER BY name LIMIT 20""",
                [f'%{term}%', f'{term}%']
            )
            columns = [desc[0] for desc in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        conn.close()
