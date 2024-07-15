from django.shortcuts import render
from query_builder_app.models.query import Query
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

@csrf_exempt
def query_list(request):
    if request.user.is_superuser:
        queries = Query.objects.all()
    else:
        queries = Query.objects.filter(Q(author_id=request.user_id) | Q(is_public=True))

    current_path = request.path
    return render(request, 'queries/list.html', {
        'queries': queries,
        'current_path': current_path  # Añadir la ruta actual al contexto
    })