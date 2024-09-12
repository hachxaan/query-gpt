from django.http import HttpResponse, FileResponse
from django.views import View
import os
import traceback
import logging
from .card_report_service import generate_csv_card_report
from django.core.files import File

logger = logging.getLogger(__name__)

class GenerateAndDownloadCSVCardsView(View):
    def get(self, request, *args, **kwargs):
        zip_file_path = None
        try:
            logger.info("Starting CSV card report generation...")
            zip_file_path = generate_csv_card_report()
            logger.info(f"CSV card report generation completed. Zip file path: {zip_file_path}")
            
            if not os.path.exists(zip_file_path):
                error_message = f"Error: Zip file does not exist at path: {zip_file_path}"
                logger.error(error_message)
                return HttpResponse(error_message, status=500)
            
            file_size = os.path.getsize(zip_file_path)
            logger.info(f"Zip file size: {file_size} bytes")
            
            if file_size == 0:
                error_message = f"Error: Zip file is empty at path: {zip_file_path}"
                logger.error(error_message)
                return HttpResponse(error_message, status=500)
            
            logger.info(f"Opening zip file for response: {zip_file_path}")
            with open(zip_file_path, 'rb') as f:
                file = File(f)
                response = FileResponse(file, content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(zip_file_path)}"'
                response['Content-Length'] = file_size
                logger.info(f"FileResponse created with filename: {os.path.basename(zip_file_path)}")
                return response
        
        except Exception as e:
            error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            logger.error(error_message)
            return HttpResponse(error_message, status=500)
        
        finally:
            # We don't remove the file here anymore
            logger.info("Request processing completed")