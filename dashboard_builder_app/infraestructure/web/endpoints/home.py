# dashboard_builder_app/views/home.py



from django.shortcuts import render
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from dashboard_builder_app.infraestructure.persistence.models.dashboard import DashboardModel

@csrf_exempt
def home(request):
    print(".................................. Home of Dashboar Builder .................................. ")
    if request.user.is_authenticated:
        dashboards = DashboardModel.objects.all()
    else:
        dashboards = DashboardModel.objects.filter(Q(user_id=request.user.id) | Q(is_public=True))


    current_path = request.path
    return render(request, 'dashboard_builder/home.html', {'dashboards': dashboards, 'user': request.user, 'current_path': current_path})
    

