import json
import os
from django.shortcuts import render
from query_builder_app.ai.openai_create_query import OpenAIAPIQueryAdapter
from query_builder_app.forms import QueryForm
from query_builder_app.models.allow_fields import AllowedField
from query_builder_app.models.allow_tables import AllowedTable
from query_builder_app.models.query import Query
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse


openai_adapter_get_query = OpenAIAPIQueryAdapter(os.getenv("OPENAI_API_KEY"))

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


def get_tables_fields():
    # Obtiene todas las tablas permitidas
    tables = AllowedTable.objects.all()

    # Inicializa una lista vacía para almacenar los resultados
    tables_fields = []

    # Itera sobre cada tabla
    for table in tables:
        # Obtiene los campos permitidos para la tabla actual
        fields = AllowedField.objects.filter(table=table)

        # Obtiene los nombres de los campos y los almacena en una lista
        field_names = [field.name for field in fields]

        # Añade la tupla (nombre_de_la_tabla, nombres_de_los_campos) a los resultados
        tables_fields.append((table.name, field_names))

    return tables_fields

@login_required
def get_query_from_gpt(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)  # Parse the request body
            requestText = data.get('request', '')  # Get the 'request' field
            
            # Now you can use requestText
            tables_fields = get_tables_fields()
            
            
            try:
                response = openai_adapter_get_query.get_query(tables_fields, requestText)
                print(type(response))
                print(response)

                print(type(response['query']))
                print(response['query'])

                return JsonResponse({"sql": response['query'], "fields": response['field_info'  ]})
            except Exception as e:
                print(str(e))
                return JsonResponse({"error": str(e)}, status=500)

        else:
            return JsonResponse({"error": "Invalid request method."}, status=400)

    except Query.DoesNotExist:
        return JsonResponse({"error": "Query not found."}, status=404)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred: " + str(e)}, status=500)