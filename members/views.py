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
from datetime import date, timedelta
from .models import TrialUser, Membership, Profile
from gym.models import Service
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from affiliates.models import Referral, Affiliate
from .forms import CustomUserCreationForm



# Login View
class CustomLoginView(LoginView):
    template_name = 'members/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('gym:index')

# Register View

class RegisterView(FormView):
    template_name = "members/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("gym:index")

    def form_valid(self, form):
        user = form.save()
        
        referral_code = self.request.GET.get("ref")
        if referral_code:
            try:
                referrer = Affiliate.objects.get(referral_code=referral_code)
                Referral.objects.create(referrer=referrer, referred_user=user, status="Joined")
            except Affiliate.DoesNotExist:
                pass

        login(self.request, user)
        return super().form_valid(form)

# Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            return self.get(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


# trial user logic
class TrialSignupView(FormView):
    template_name = 'members/trial_signup.html'
    form_class = TrialUserForm
    success_url = reverse_lazy('gym:index')

    def form_valid(self, form):
        user = self.request.user

        # Check if the user has an active membership
        if not Membership.objects.filter(user=user, status="Active").exists():
            messages.error(self.request, "You need an active membership to start a free trial.")
            return self.render_to_response(self.get_context_data(form=form))

        # Ensure the user has not already used the free trial
        if TrialUser.objects.filter(user=user).exists():
            messages.error(self.request, "You have already used your free trial.")
            return self.render_to_response(self.get_context_data(form=form))

        # Create the trial user
        trial_user = form.save(commit=False)
        trial_user.user = user
        trial_user.trial_start_date = now().date()
        trial_user.trial_end_date = now().date() + timedelta(days=14)
        trial_user.status = "Active"
        trial_user.save()

        messages.success(self.request, "Your 14-day free trial has started!")
        return super().form_valid(form)


def update_trial_status():
    trials = TrialUser.objects.filter(status="Active")
    for trial in trials:
        if trial.trial_end_date < now().date():
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


# membership view

class SubscribeMembershipView(View):
    def get(self, request, plan_type):
        user = request.user
        end_date = now().date() + timedelta(days=30 if plan_type == "monthly" else 365)

        membership, created = Membership.objects.get_or_create(user=user)
        membership.membership_type = plan_type
        membership.end_date = end_date
        membership.save()

        messages.success(request, f"Your {plan_type} membership is now active!")
        return HttpResponseRedirect(reverse_lazy('coaches:booking_list'))


class ActivateTrialView(View):
    def get(self, request):
        user = request.user

        # Check if user has already used a trial
        if TrialUser.objects.filter(user=user).exists():
            messages.error(request, "You have already used your free trial.")
            return redirect(reverse_lazy('members:membership_page'))

        # Activate trial for 14 days
        trial_end = now().date() + timedelta(days=14)
        TrialUser.objects.create(user=user, trial_end_date=trial_end)

        # Ensure the user has a Membership entry set to "trial"
        membership, created = Membership.objects.get_or_create(user=user)
        membership.membership_type = "trial"
        membership.start_date = now().date()
        membership.end_date = trial_end
        membership.save()

        messages.success(request, "Your free trial has started! Enjoy access to our gym.")
        return redirect(reverse_lazy('members:membership_page'))


# views.py


class TrialSignupView(FormView):
    template_name = 'members/trial_signup.html'  # Your form's template
    form_class = TrialUserForm

    def form_valid(self, form):
        user = self.request.user

        # Check if the user already has a trial membership
        if Membership.objects.filter(user=user, membership_type="trial").exists():
            messages.error(self.request, "You have already used your free trial.")
            return redirect(reverse_lazy('members:membership_page'))

        # Create or retrieve the user's profile if it does not exist
        if not hasattr(user, 'profile'):
            profile = Profile.objects.create(user=user, phone_number=form.cleaned_data.get('phone_number'))
        else:
            profile = user.profile  # Use existing profile

        # Now create the trial membership for the user
        trial_end = now().date() + timedelta(days=14)
        membership, created = Membership.objects.get_or_create(user=user)
        membership.membership_type = "trial"
        membership.start_date = now().date()
        membership.end_date = trial_end
        membership.save()

        # Send an email notification (optional)
        self.send_trial_start_email(user.email, membership)

        messages.success(self.request, "Your free trial has started! Enjoy access to our gym.")
        return redirect(reverse_lazy('members:membership_page'))

    def form_invalid(self, form):
        # Handle form errors (optional)
        return self.render_to_response(self.get_context_data(form=form))

    def send_trial_start_email(self, email, membership):
        subject = "Your Free Trial Has Started!"
        message = f"Hello, your free trial has started on {membership.start_date}. It will expire on {membership.end_date}."
        from django.core.mail import send_mail
        send_mail(subject, message, 'from@example.com', [email], fail_silently=False)

class MembershipPageView(LoginRequiredMixin, TemplateView):
    template_name = 'members/membership_page.html'
    login_url = '/accounts/login/'  # Redirect to login if not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the user's membership
        try:
            membership = Membership.objects.get(user=self.request.user)
            context['membership'] = membership
        except Membership.DoesNotExist:
            context['membership'] = None

        return context



class RenewMembershipView(LoginRequiredMixin, TemplateView):
    template_name = 'members/renew_membership.html'
    login_url = '/accounts/login/'  # Redirect to login if not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if the user has an existing membership
        try:
            membership = Membership.objects.get(user=self.request.user)
            context['membership'] = membership
        except Membership.DoesNotExist:
            # Handle the case where the user does not have a membership
            context['membership'] = None  # No membership found
            context['error_message'] = 'You do not have an active membership. Please sign up for one.'
        
        return context

    def post(self, request, *args, **kwargs):
        # Handle the membership renewal
        try:
            membership = Membership.objects.get(user=request.user)
            membership.end_date = timezone.now().date() + timedelta(days=365)  # Renew for 1 year
            membership.save()
            return redirect('members:membership_page')  # Redirect back to the membership page after renewing
        except Membership.DoesNotExist:
            # If no membership exists, redirect to the sign-up page or show an error
            return redirect('members:membership_page')  # Or you can redirect them to a page to sign up for a membership


