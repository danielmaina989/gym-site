from django.shortcuts import render

# Create your views here.
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView, CreateView
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Login View
class CustomLoginView(LoginView):
    template_name = 'members/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('gym:index')

# Register View
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'members/register.html'
    success_url = reverse_lazy('members:login')

# Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self.get(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)