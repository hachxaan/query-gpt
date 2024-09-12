from django.http import HttpResponse, FileResponse
from django.views import View
import os
import traceback
import logging
from .card_report_service import generate_csv_card_report

logger = logging.getLogger(__name__)

class GenerateAndDownloadCSVCardsView(View):
    def get(self, request, *args, **kwargs):
        csv_file_path = None
        try:
            logger.info("Starting CSV card report generation...")
            csv_file_path = generate_csv_card_report()
            logger.info(f"CSV card report generation completed. CSV file path: {csv_file_path}")
            
            if not os.path.exists(csv_file_path):
                error_message = f"Error: CSV file does not exist at path: {csv_file_path}"
                logger.error(error_message)
                return HttpResponse(error_message, status=500)
            
            file_size = os.path.getsize(csv_file_path)
            logger.info(f"CSV file size: {file_size} bytes")
            
            if file_size == 0:
                error_message = f"Error: CSV file is empty at path: {csv_file_path}"
                logger.error(error_message)
                return HttpResponse(error_message, status=500)
            
            logger.info(f"Opening CSV file for response: {csv_file_path}")
            response = FileResponse(open(csv_file_path, 'rb'), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(csv_file_path)}"'
            response['Content-Length'] = file_size
            logger.info(f"FileResponse created with filename: {os.path.basename(csv_file_path)}")
            
            return response
        
        except Exception as e:
            error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            logger.error(error_message)
            return HttpResponse(error_message, status=500)
        
        finally:
            logger.info("Request processing completed")
            if csv_file_path and os.path.exists(csv_file_path):
                try:
                    os.remove(csv_file_path)
                    logger.info(f"Temporary CSV file removed: {csv_file_path}")
                except Exception as e:
                    logger.error(f"Error removing temporary CSV file: {str(e)}")