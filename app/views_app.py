from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    print(".................................. Home .................................. ")
    current_path = request.path
    return render(request, 'home.html', {'current_path': current_path, 'user': request.user})