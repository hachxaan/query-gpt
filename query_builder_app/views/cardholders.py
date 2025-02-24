from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connections

@login_required
def cardholders_list(request):
    # Número de registros por página
    per_page = 50
    page_number = request.GET.get('page', 1)
    
    # Consulta a la base de datos banking_operation
    with connections['banking_operation_db'].cursor() as cursor:
        cursor.execute("""
            SELECT id, email, cardholder_id, kyc_status, white_label, 
                active, created_at
            FROM central_payments.cardholder
            ORDER BY created_at DESC
        """)
        columns = [col[0] for col in cursor.description]
        cardholders = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Paginación
    paginator = Paginator(cardholders, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Cardholders List'
    }
    
    return render(request, 'cardholders/cardholders.html', context)

