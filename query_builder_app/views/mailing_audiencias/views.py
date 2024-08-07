# query_builder_app/views/mailing_audiencias/views.py

from django.http import HttpResponse, FileResponse
from django.views import View
import os
from .audience_creator_service import generate_csv_files

class GenerateAndDownloadCSVAudiencesView(View):
    def get(self, request, *args, **kwargs):
        try:
            zip_file_path = generate_csv_files()
            
            if not os.path.exists(zip_file_path):
                return HttpResponse("Error generating the zip file.", status=500)

            response = FileResponse(open(zip_file_path, 'rb'), as_attachment=True, filename=os.path.basename(zip_file_path))
            return response
        
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)