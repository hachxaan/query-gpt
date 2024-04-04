import io
from typing import Dict, List, Tuple
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404

from file_management.models import MailingFactory
from html_manager.campaign_form import MailingCampaignForm
from html_manager.html_factory import HTMLFactory
from .models import MailingCampaign, MailingHTML
from crispy_forms.helper import FormHelper
import csv
from django.shortcuts import redirect



def import_csv(request, pk):
    if request.method == 'POST':
        csv_file = request.FILES.get('csvFile')
        print(type(csv_file))
        print(csv_file)
        # Process the CSV file here
        csv_data = []
        data = csv_file.read().decode('utf-8')
        file = io.StringIO(data)
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            csv_data.append(row)

        html_factory = HTMLFactory(csv_data)
        mailing_campaign = MailingCampaign.objects.filter(pk=pk).first()
        # Process each row in the CSV data
        for row in csv_data:
            # Generate HTML code for each row
            html_code = html_factory.generate_html(row)
            
            # Create a new MailingHTML object
            mailing_html = MailingHTML(
                mailing_campaign=mailing_campaign,
                white_label=row['white_label'],
                csv_data=str(row),
                html_content=html_code
            )
            # Save the MailingHTML object to the database
            mailing_html.save()
        print("Redirigiendo a la lista de campañas....")
        return redirect('mailing_campaign_list')

    mailing_campaigns = MailingCampaign.objects.all()
    form = MailingCampaignForm()
    crispy_form = FormHelper(form)
    return render(request, 'list_campaing.html', {
        'mailing_campaigns': mailing_campaigns,
        'form': form,
        "crispy": crispy_form,
        "pk_new": pk
    })


def mailing_html_list_by_campaign(request, pk):
    mailing_campaign = get_object_or_404(MailingCampaign, pk=pk)
    mailing_htmls = MailingHTML.objects.filter(mailing_campaign=mailing_campaign) 
    data_json = []
    for mailing_html in mailing_htmls:
        data_json.append({
            'id': mailing_html.id,
            'white_label': mailing_html.white_label,
            'csv_data': mailing_html.csv_data,
            'html_content': mailing_html.html_content,
            'created_at': mailing_html.created_at,
            'updated_at': mailing_html.updated_at
        })

    return JsonResponse(data_json, safe=False)



def delete_mailing_html(request, pk):
    mailing_html = get_object_or_404(MailingHTML, pk=pk)
    mailing_html.delete()
    return redirect('mailing_campaign_list')


def download_html(request, pk):
    mailing_html = get_object_or_404(MailingHTML, pk=pk)
    mailing_campaign = mailing_html.mailing_campaign
    name = mailing_campaign.name
    html_content = mailing_html.html_content
    white_label = mailing_html.white_label
    # Plantilla básica para un documento HTML completo
    html_template = f"""<!doctype html>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml"
            xmlns:o="urn:schemas-microsoft-com:office:office">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Título del Documento</title>
        </head>
        {html_content}
        </html>
        """

    # Crear una respuesta HTTP con el tipo MIME apropiado
    response = HttpResponse(html_template, content_type='application/html')
    # Agregar la cabecera de Content-Disposition para que el navegador trate la respuesta como un archivo descargable
    response['Content-Disposition'] = f'attachment; filename="{white_label}-{name}.html"'

    return response