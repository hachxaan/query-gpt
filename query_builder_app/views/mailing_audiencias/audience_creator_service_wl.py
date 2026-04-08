from datetime import datetime

from .audience_common import generate_audiences_zip


def generate_csv_files_by_wl_and_services():
    """Main function to process audiences grouped by white_label and code_service."""
    query = """
    SELECT 
    "Email Address", 
    "Last Name", 
    "First Name", 
    "User ID", 
    "White Label", 
    "Label Customer Service", 
    "Tags", 
    "Card Number", 
    "Company Name",
    "code_service",
    "tag_mailing",
    "file_name"
    FROM vw_mailings_by_white_label_and_services
    ORDER BY "file_name"
    """

    today_date = datetime.now().strftime('%Y%m%d')
    return generate_audiences_zip(query, f"files_wl_{today_date}")
