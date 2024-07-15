from django.shortcuts import render
from django.db.models import Q
from query_builder_app.models.query import Query
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def query_list_download(request):
    print(".................................. Query List Download .................................. ")
    if request.user.is_superuser:
        queries = Query.objects.all()
    else:
        queries = Query.objects.filter(Q(author_id=request.user.id) | Q(is_public=True))

    current_path = request.path
    return render(request, 'queries/queries.html', {'queries': queries, 'user': request.user, 'current_path': current_path})

