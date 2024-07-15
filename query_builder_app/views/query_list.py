from django.shortcuts import render
from query_builder_app.forms import QueryForm
from query_builder_app.models.query import Query
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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


@login_required
def query_create(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.save(commit=False)
            query.author = request.user  # Establecer el autor como usuario actual
            query.save()
            return redirect('query_list')
    else:
        form = QueryForm(initial={'author': request.user})  # Establecer el valor inicial del autor como usuario actual
    return render(request, 'queries/form.html', {'form': form})

def query_update(request, query_id):
    query = Query.objects.get(id=query_id)
    if request.method == 'POST':
        form = QueryForm(request.POST, instance=query)
        if form.is_valid():
            form.save()
            return redirect('query_list')
    else:
        form = QueryForm(instance=query)
    return render(request, 'queries/form.html', {'form': form})

@login_required
def query_delete(request, query_id):
    query = Query.objects.get(id=query_id)
    if request.method == 'POST':
        query.delete()
        return redirect('query_list')
    return render(request, 'queries/confirm_delete.html', {'object': query})



def redirect_to_home(request, exception=None):
    return redirect('home') 