from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .campaign_form import MailingCampaignForm


from .models import MailingCampaign
from crispy_forms.helper import FormHelper


def mailing_campaign_list(request):
    mailing_campaigns = MailingCampaign.objects.all()
    form = MailingCampaignForm()
    crispy_form = FormHelper(form)
    campaign_count = MailingCampaign.objects.count()
    return render(request, 'list_campaing.html', {
        'mailing_campaigns': mailing_campaigns,
        'form': form,
        "crispy": crispy_form, 
        "campaign_count": campaign_count
    })


def mailing_campaign_create(request):
    if request.method == 'POST':
        form = MailingCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save()
            # Realizar la redirección a la vista que muestra la lista
            print("Redirigiendo a la lista de campañas")
            return redirect(reverse('mailing_campaign_list'))
    else:
        form = MailingCampaignForm()

    # Si no es un POST o el formulario no es válido, vuelve a mostrar el formulario
    return render(request, 'list_campaing.html', {'form': form})


def mailing_campaign_delete(request, pk):
    campaign = get_object_or_404(MailingCampaign, pk=pk)
    if request.method == 'POST':
        # Delete the associated MailingHTML objects
        campaign.mailinghtml_set.all().delete()
        campaign.delete()
        campaign_count = MailingCampaign.objects.count()
    
    return redirect('mailing_campaign_list', campaign_count=campaign_count)
    