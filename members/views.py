from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView, CreateView
from django.views.generic import TemplateView
from .forms import CustomUserCreationForm, TrialUserForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from .models import TrialUser



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


# tial user logic
class TrialSignupView(TemplateView):
    template_name = 'members/trial_signup.html'

class TrialSignupView(FormView):
    template_name = 'members/trial_signup.html'  # Optional: Use a specific template for rendering this form
    form_class = TrialUserForm
    success_url = reverse_lazy('gym:index')  # Redirect after successful signup

    def form_valid(self, form):
        # Save the form and handle any additional logic
        form.save()
        return super().form_valid(form)

def update_trial_status():
    trials = TrialUser.objects.filter(status="Active")
    for trial in trials:
        if trial.trial_end_date < date.today():
            trial.status = "Expired"
            trial.save()


