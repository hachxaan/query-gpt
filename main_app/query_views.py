import json
from django.shortcuts import render, redirect
from .models import AllowedField, AllowedTable, Query, process
from .forms import QueryForm
from marketing_queries.settings import openai_adapter_get_query
from marketing_queries.settings import openai_adapter_get_context
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
import string
from django.db.models import Q


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

import csv
import os


data = [
    {"id": i, "nombre": ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}
    for i in range(100)  # 100 Filas de datos de ejemplo
]

def fetch_data(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    
    filtered_data = data[start:start + length]
    response = {
        'draw': draw,
        'recordsTotal': len(data),
        'recordsFiltered': len(data),
        'data': filtered_data,
    }
    return JsonResponse(response)

def table_old(request):
    return render(request, 'datatables_base.html')


def table(request):
    proc = process.objects.first()
    chat_history = proc.get_chat_history() if proc else []

    return render(request, 'datatables_base.html', {'chat_history': chat_history})

def chart(request):
    data = [1, 3, 2, 4]  # Datos de ejemplo para el gráfico
    return render(request, 'tests/hightchart_1.html', {'data': data})



def chat_database(request):
    data = [1, 3, 2, 4]  # Datos de ejemplo para el gráfico
    return render(request, 'chat_database.html', {'data': data})


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

def validate_and_extract(s):
    # Si el string contiene ":\n" lo eliminamos
    if ":\n" in s:
        s = s.split(":\n", 1)[1]

    # Verificamos si el string restante es un JSON válido
    try:
        json.loads(s)
        return s
    except json.JSONDecodeError:
        return None

@csrf_exempt
def config_report(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)  # Parse the request body
            requestText = data.get('prompt', '')  # Get the 'request' field
            try:
                message_json = {
                    "sender": "Carlos",
                    "text": requestText,
                    "request_type": None,
                }
                process_instance = process.get_or_create_by_id(id=1, **message_json)  # Obtener una instancia del modelo

                process_instance.add_formatted_message_to_chat_history(message_j/managerson)

                get_request_type = openai_adapter_get_context.get_context(
                    user_prompt=requestText
                )


                # if get_request_type.get('request_type') = [1,2]: # Query
                # return JsonResponse(json.dumps(get_request_type))
                respuesta = validate_and_extract(get_request_type)

                respuesta = json.loads(respuesta)

                respuesta['query'] = None
                if int(respuesta.get('request_type')) in [1, 2]:
                    tables_fields = get_tables_fields()
                    response = openai_adapter_get_query.get_query(tables_fields, requestText)

                    query = response.get('query')
                    respuesta['query']= query
                    # execute_query(query, 'datos')
                
                process_instance = process.objects.get(id=1)  # Obtener una instancia del modelo
                message_json = {
                    "sender": "GPT",
                    # "text": f"{respuesta.get} respuesta.get('respueta_chat'),
                    "request_type": respuesta.get('request_type'),
                    "query": respuesta['query']
                }
                process_instance.add_formatted_message_to_chat_history(message_json)

                
                return JsonResponse(respuesta)
            
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

@csrf_exempt
def query_list(request):
    if request.user.is_superuser:
        queries = Query.objects.all()
    else:
        queries = Query.objects.filter(Q(author=request.user) | Q(is_public=True))

    current_path = request.path
    return render(request, 'queries/list.html', {
        'queries': queries,
        'current_path': current_path  # Añadir la ruta actual al contexto
    })

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


"""
SELECT u.id, u.first_name, u._email, u._birthdate, u.registration_date, u.last_login_date, u.mobile_phone, u.state, u.company_id, u.payroll_frequency, u.payroll_last_date, u.signup_date, u.inactive, u.terms_conditions, u.promotional_sms, u.promotional_email, u._street_address, u._address_line_2, u._payroll_daily, u._payroll_hourly, u._payroll_salary, u.payroll_type, u.city, u.zip_code, u.promotional_code, u.payroll_active, u._last_name FROM users u JOIN companies c ON u.company_id = c.id WHERE u.inactive = true AND c.white_label_tag = 'insperity'
"""