from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from .forms import ChangePasswordForm

class ChangePasswordView(PasswordChangeView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('home')  # Cambia 'home' por la URL a la que deseas redirigir después de cambiar la contraseña
    template_name = 'change_password.html'


class LoginFromView(LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     password = request.POST['password']
    #     username = request.POST['username']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['temp'] = 'X'
        return  context


