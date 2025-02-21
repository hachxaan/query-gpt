from django.http import HttpResponse, FileResponse
from django.views import View
import os
import traceback
import logging
from .migration_balance_service import generate_migration_balance_report
from .scripts.import_accounts import import_accounts_from_solid

logger = logging.getLogger(__name__)

class UpdateBalanceSolidAccounts(View):
    def get(self, request, *args, **kwargs):
        csv_file_path = None
        try:
            logger.info("Starting import accounts from Solid...")
            import_accounts_from_solid()
            logger.info("Import completed successfully")

            logger.info("Starting migration balance report generation...")
            csv_file_path = generate_migration_balance_report()
            
            if not os.path.exists(csv_file_path):
                return HttpResponse("Error: CSV file not generated", status=500)
            
            response = FileResponse(
                open(csv_file_path, 'rb'),
                content_type='text/csv',
                as_attachment=True,
                filename='migration_balance_report.csv'
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return HttpResponse(f"Error generating report: {str(e)}", status=500)
            
        finally:
            if csv_file_path and os.path.exists(csv_file_path):
                os.remove(csv_file_path)