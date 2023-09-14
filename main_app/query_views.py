import json
from django.shortcuts import render, redirect
from .models import AllowedField, AllowedTable, Query
from .forms import QueryForm
from marketing_queries.settings import openai_adapter_get_query
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

replacements = {
    'email': '_email',
    'last_name': '_last_name',
    'birthdate': '_birthdate',
    'street_address': '_street_address',
    'address_line_2': '_address_line_2',
    'mobile_phone': '_mobile_phone',
    'payroll_daily': '_payroll_daily',
    'payroll_hourly': '_payroll_hourly',
    'payroll_salary': '_payroll_salary'
}

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

@csrf_exempt
def get_query_from_gpt(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)  # Parse the request body
            requestText = data.get('request', '')  # Get the 'request' field
            
            # Now you can use requestText
            tables_fields = get_tables_fields()
            
            
            try:
                response = openai_adapter_get_query.get_query(tables_fields, requestText)
                return JsonResponse({"sql": response})
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        else:
            return JsonResponse({"error": "Invalid request method."}, status=400)

    except Query.DoesNotExist:
        return JsonResponse({"error": "Query not found."}, status=404)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred: " + str(e)}, status=500)

@csrf_exempt
def query_list(request):
    queries = Query.objects.all()
    return render(request, 'queries/list.html', {'queries': queries})

@csrf_exempt
def query_detail(request, query_id):
    query = Query.objects.get(id=query_id)
    return render(request, 'queries/detail.html', {'query': query})

@csrf_exempt
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

def query_delete(request, query_id):
    query = Query.objects.get(id=query_id)
    if request.method == 'POST':
        query.delete()
        return redirect('query_list')
    return render(request, 'queries/confirm_delete.html', {'object': query})
