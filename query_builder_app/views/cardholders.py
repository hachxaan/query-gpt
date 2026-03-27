from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connections
import logging

logger = logging.getLogger(__name__)

PER_PAGE = 50


@login_required
def cardholders_list(request):
    page_number = request.GET.get('page', 1)

    try:
        page_number = max(1, int(page_number))
    except (ValueError, TypeError):
        page_number = 1

    offset = (page_number - 1) * PER_PAGE

    try:
        with connections['banking_operation_db'].cursor() as cursor:
            # Count total for pagination
            cursor.execute(
                "SELECT COUNT(*) FROM central_payments.cardholder"
            )
            total_count = cursor.fetchone()[0]

            # Paginated query at DB level
            cursor.execute("""
                SELECT id, email, cardholder_id, kyc_status, white_label,
                    active, created_at
                FROM central_payments.cardholder
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, [PER_PAGE, offset])
            columns = [col[0] for col in cursor.description]
            cardholders = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception:
        logger.exception("Error querying banking_operation_db")
        cardholders = []
        total_count = 0

    paginator = Paginator(range(total_count), PER_PAGE)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'cardholders': cardholders,
        'title': 'Cardholders List',
    }

    return render(request, 'cardholders/cardholders.html', context)

