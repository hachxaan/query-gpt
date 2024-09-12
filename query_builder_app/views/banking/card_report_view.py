from django.http import HttpResponse, FileResponse
from django.views import View
import os
import traceback
from .card_report_service import generate_csv_card_report

class GenerateAndDownloadCSVCardsView(View):
    def get(self, request, *args, **kwargs):
        try:
            print("Starting CSV card report generation...")
            zip_file_path = generate_csv_card_report()
            print(f"CSV card report generation completed. Zip file path: {zip_file_path}")
            
            if not os.path.exists(zip_file_path):
                error_message = f"Error: Zip file does not exist at path: {zip_file_path}"
                print(error_message)
                return HttpResponse(error_message, status=500)
            
            file_size = os.path.getsize(zip_file_path)
            print(f"Zip file size: {file_size} bytes")
            
            if file_size == 0:
                error_message = f"Error: Zip file is empty at path: {zip_file_path}"
                print(error_message)
                return HttpResponse(error_message, status=500)
            
            print(f"Opening zip file for response: {zip_file_path}")
            with open(zip_file_path, 'rb') as zip_file:
                response = FileResponse(zip_file, as_attachment=True, filename=os.path.basename(zip_file_path))
                print(f"FileResponse created with filename: {os.path.basename(zip_file_path)}")
                
                # Add some headers for debugging
                response['Content-Length'] = file_size
                response['X-File-Name'] = os.path.basename(zip_file_path)
                response['X-File-Size'] = file_size
                
                print("Returning FileResponse")
                return response
        
        except Exception as e:
            error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(error_message)
            return HttpResponse(error_message, status=500)
        
        finally:
            # Clean up the temporary zip file
            if 'zip_file_path' in locals() and os.path.exists(zip_file_path):
                try:
                    os.remove(zip_file_path)
                    print(f"Temporary zip file removed: {zip_file_path}")
                except Exception as e:
                    print(f"Error removing temporary zip file: {str(e)}")