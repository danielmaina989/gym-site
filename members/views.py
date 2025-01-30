from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView, CreateView
from django.views.generic import TemplateView, View
from .forms import CustomUserCreationForm, TrialUserForm, BookingForm
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from .models import TrialUser
from gym.models import Service



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


# View to handle booking the session

class BookSessionView(View):
    def post(self, request, *args, **kwargs):
        """Handles booking form submission"""
        # Get service_id from the POST data
        service_id = request.POST.get('service_id')
        
        # If service_id is not provided, return an error
        if not service_id:
            return render(request, 'members/book_session.html', {'error': 'Service ID is missing!'})

        # Retrieve the Service object based on the service_id
        service = get_object_or_404(Service, id=service_id)
        
        # Initialize the booking form with POST data
        form = BookingForm(request.POST)
        
        if form.is_valid():
            # Save the form without committing to the database
            booking = form.save(commit=False)
            booking.service = service  # Associate the booking with the selected service
            booking.user = request.user  # Associate the booking with the logged-in user
            booking.save()  # Save the booking object
            
            # Redirect to the booking success page after saving
            return redirect(reverse_lazy('members:booking_success'))  
        
        # If the form is not valid, re-render the page with the form and service details
        return render(request, 'members/book_session.html', {'form': form, 'service': service})
