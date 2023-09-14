import csv
from django.db import connections
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from .models import Query

# from django.core.exceptions import ObjectDoesNotExist


def home(request):
    # return render(request, "queries.html")
    queries = Query.objects.all()
    return render(request, 'queries.html', {'queries': queries, 'user': request.user})


@login_required
def execute_query(request, query_id):
    try:
        query = Query.objects.get(pk=query_id)
        with connections["platform_db"].cursor() as cursor:
            cursor.execute(query.sql_query)
            results = cursor.fetchall()
        return JsonResponse(results, safe=False)
    except Query.DoesNotExist:
        return JsonResponse({"error": "Query not found."}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


import re
import datetime

@login_required
def download_results(request, query_id):
    try:
        query = Query.objects.get(pk=query_id)
        with connections["platform_db"].cursor() as cursor:
            cursor.execute(query.sql_query)
            field_names = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()

        # Decryption process
        decrypted_results = []
        for row in results:
            decrypted_row = []
            for idx, item in enumerate(row):
                if field_names[idx] in ["_email", "_last_name", "_birthdate", "_street_address", "_address_line_2", "_mobile_phone", "_payroll_daily", "_payroll_hourly", "_payroll_salary"]:
                    if isinstance(item, memoryview):
                        decrypted_item = query.decrypt(item.tobytes()) if item else None
                        decrypted_row.append(decrypted_item)
                    else:
                        decrypted_row.append(item)
                else:
                    decrypted_row.append(item)
            decrypted_results.append(tuple(decrypted_row))

        # Generate file name based on query title
        title = query.title
        title = re.sub(r"[^\w\s-]", "", title)  # Remove invalid characters
        title = title.replace(" ", "_")  # Replace spaces with underscores
        now = datetime.datetime.now()
        postfix = now.strftime("%Y%m%d%H%M")  # Format: "YYYYMMDDHHMM"
        filename = f"{title}_{postfix}.csv"

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(field_names)  # Write field names at the beginning
        for row in decrypted_results:
            writer.writerow(row)

        return response
    except Query.DoesNotExist:
        return render(request, 'error_template.html', {'error': 'Query not found.'})
    except Exception as e:
        return render(request, 'error_template.html', {'error': str(e)})

# @login_required
# def download_results(request, query_id):
#     try:
#         query = Query.objects.get(pk=query_id)
#         with connections["platform_db"].cursor() as cursor:
#             cursor.execute(query.sql_query)
#             field_names = [desc[0] for desc in cursor.description]
#             results = cursor.fetchall()

#         # Decryption process
#         decrypted_results = []
#         for row in results:
#             decrypted_row = []
#             for idx, item in enumerate(row):
#                 if field_names[idx] in ["_email", "_last_name", "_birthdate", "_street_address", "_address_line_2", "_mobile_phone", "_payroll_daily", "_payroll_hourly", "_payroll_salary"]:
#                     if isinstance(item, memoryview):
#                         decrypted_item = query.decrypt(item.tobytes()) if item else None
#                         decrypted_row.append(decrypted_item)
#                     else:
#                         decrypted_row.append(item)
#                 else:
#                     decrypted_row.append(item)
#             decrypted_results.append(tuple(decrypted_row))

#         # Generate file name based on query title
#         title = query.title
#         title = re.sub(r"[^\w\s-]", "", title)  # Remove invalid characters
#         title = title.replace(" ", "_")  # Replace spaces with underscores
#         now = datetime.datetime.now()
#         postfix = now.strftime("%Y%m%d%H%M")  # Format: "YYYYMMDDHHMM"
#         filename = f"{title}_{postfix}.csv"

#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = f'attachment; filename="{filename}"'

#         writer = csv.writer(response)
#         writer.writerow(field_names)  # Write field names at the beginning
#         for row in decrypted_results:
#             writer.writerow(row)

#         return response
#     except Query.DoesNotExist:
#         return JsonResponse({"error": "Query not found."}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# @login_required
# def download_results(request, query_id):
#     try:
#         query = Query.objects.get(pk=query_id)
#         with connections["platform_db"].cursor() as cursor:
#             cursor.execute(query.sql_query)
#             field_names = [desc[0] for desc in cursor.description]
#             results = cursor.fetchall()

#         # Decryption process
#         decrypted_results = []
#         for row in results:
#             decrypted_row = []
#             for idx, item in enumerate(row):
#                 if field_names[idx] in ["_email", "_last_name", "_birthdate", "_street_address", "_address_line_2", "_mobile_phone", "_payroll_daily", "_payroll_hourly", "_payroll_salary"]:
#                     if isinstance(item, memoryview):
#                         decrypted_item = query.decrypt(item.tobytes()) if item else None
#                         decrypted_row.append(decrypted_item)
#                     else:
#                         decrypted_row.append(item)
#                 else:
#                     decrypted_row.append(item)
#             decrypted_results.append(tuple(decrypted_row))

#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="results.csv"'

#         writer = csv.writer(response)
#         writer.writerow(field_names)  # Write field names at the beginning
#         for row in decrypted_results:
#             writer.writerow(row)

#         return response
#     except Query.DoesNotExist:
#         return JsonResponse({"error": "Query not found."}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



# @login_required
# def download_results(request, query_id):
#     try:
#         query = Query.objects.get(pk=query_id)
#         with connections["platform_db"].cursor() as cursor:
#             cursor.execute(query.sql_query)
#             results = cursor.fetchall()

#         # Decryption process
#         decrypted_results = []
#         for row in results:
#             decrypted_row = []
#             for item in row:
#                 print(item)
#                 print(type(item))
#                 if isinstance(item, memoryview):
#                     decrypted_item = query.decrypt(item) if item else None
#                     decrypted_row.append(decrypted_item)
#                 else:
#                     decrypted_row.append(item)
#             decrypted_results.append(tuple(decrypted_row))        

#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="results.csv"'

#         writer = csv.writer(response)
#         for row in decrypted_results:
#             writer.writerow(row)

#         return response
#     except Query.DoesNotExist:
#         return JsonResponse({"error": "Query not found."}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)



# @login_required
# def download_results(request, query_id):
#     try:
#         query = Query.objects.get(pk=query_id)
#         with connections["platform_db"].cursor() as cursor:
#             cursor.execute(query.sql_query)
#             results = cursor.fetchall()

#         response = HttpResponse(content_type="text/csv")
#         response["Content-Disposition"] = 'attachment; filename="results.csv"'

#         writer = csv.writer(response)
#         for row in results:
#             writer.writerow(row)

#         return response
#     except Query.DoesNotExist:
#         return JsonResponse({"error": "Query not found."}, status=404)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)
