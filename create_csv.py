
import re 
import os
import datetime
from cryptography.fernet import Fernet

class FernetSingleton:
    class __FernetSingleton:
        def __init__(self):
            key_str = os.getenv('DB_KEY')
            key_bytes = key_str.encode('utf-8')
            key_base64 = key_bytes.decode()
            self.fernet = Fernet(key_base64)
    instance = None

    def __init__(self):
        if not FernetSingleton.instance:
            FernetSingleton.instance = FernetSingleton.__FernetSingleton().fernet

    def __getattr__(self, name):
        return getattr(self.instance, name)   

def create_csv(field_names, data_query, file_name):
    try:
        # query = Query.objects.get(pk=query_id)
        # with connections["platform_db"].cursor() as cursor:
        #     cursor.execute(query.sql_query)
        #     field_names = [desc[0] for desc in cursor.description]
        #     results = cursor.fetchall()

        # Decryption process
        decrypted_results = []
        for row in data_query:
            decrypted_row = []
            for idx, item in enumerate(row):
                if field_names[idx] in ["_email", "_last_name", "_birthdate", "_street_address", "_address_line_2", "_mobile_phone", "_payroll_daily", "_payroll_hourly", "_payroll_salary"]:
                    if isinstance(item, memoryview):
                        decrypted_item = __decrypt(item.tobytes()) if item else None
                        decrypted_row.append(decrypted_item)
                    else:
                        decrypted_row.append(item)
                else:
                    decrypted_row.append(item)
            decrypted_results.append(tuple(decrypted_row))


        return decrypted_results

        # # Generate file name based on query title
        # title = file_name
        # title = re.sub(r"[^\w\s-]", "", title)  # Remove invalid characters
        # title = title.replace(" ", "_")  # Replace spaces with underscores
        # now = datetime.datetime.now()
        # postfix = now.strftime("%Y%m%d%H%M")  # Format: "YYYYMMDDHHMM"
        # filename = f"{title}_{postfix}.csv"

        # response = HttpResponse(content_type="text/csv")
        # response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # writer = csv.writer(response)
        # writer.writerow(field_names)  # Write field names at the beginning
        # for row in decrypted_results:
        #     writer.writerow(row)

        # return response

    except Exception as e:
        return render(request, 'error_template.html', {'error': str(e)})
    

def __decrypt(self, data: bytes):
    fernet = FernetSingleton()
    if data:
        return fernet.decrypt(data).decode()
    else:
        return None