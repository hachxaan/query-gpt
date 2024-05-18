import csv
from django.db import connections
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from .models import Query
import re
import datetime
from django.db import connections

@login_required
def download_results(request, query_id):
    print(".................................. Download Results .................................. ")
    try:
        query = Query.objects.get(pk=query_id)
        
        with connections['platform_db'].cursor() as cursor:
            cursor.execute(query.sql_query)
            field_names = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
        decrypted_results = [
            [
                query.decrypt(item.tobytes()) if isinstance(item, memoryview) and field_names[idx] in [
                    "_email", "_last_name", "_birthdate", "_street_address", 
                    "_address_line_2", "_mobile_phone", "_payroll_daily", "_payroll_hourly", "_payroll_salary"
                ] else item
                for idx, item in enumerate(row)
            ] for row in results
        ]

        filename = re.sub(r'[^\w\s-]', '', query.title).replace(' ', '_') + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M') + '.csv'

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        writer.writerows(decrypted_results)
        
        return response

    except Query.DoesNotExist:
        return render(request, 'error_template.html', {'error': 'Query not found.'})
    except Exception as e:
        # Log the error here if you have logging setup
        print('Exception: ')
        print(str(e))
        return render(request, 'error_template.html', {'error': str(e)})

@login_required
def query_list_download(request):
    print(".................................. Query List Download .................................. ")
    queries = Query.objects.all()
    current_path = request.path
    return render(request, 'queries/queries.html', {'queries': queries, 'user': request.user, 'current_path': current_path})


@login_required
def home(request):
    print(".................................. Home .................................. ")
    current_path = request.path
    return render(request, 'home.html', {'current_path': current_path, 'user': request.user})


@login_required
def execute_query(request, query_id):
    try:
        print(".................................. Execute Query .................................. ")
        query = Query.objects.get(pk=query_id)
        with connections["platform_db"].cursor() as cursor:
            cursor.execute(query.sql_query)
            results = cursor.fetchall()
        return JsonResponse(results, safe=False)
    except Query.DoesNotExist:
        return JsonResponse({"error": "Query not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
