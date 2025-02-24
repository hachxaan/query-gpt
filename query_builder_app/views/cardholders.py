from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def cardholders(request):
    return render(request, 'queries/cardholders.html', {
        'current_path': request.path
    })