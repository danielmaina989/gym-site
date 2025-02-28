from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from datetime import timedelta
from .models import TrialUser, Membership, Profile
from gym.models import Service
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.contrib.auth.models import User
from affiliates.models import Referral, Affiliate
from .forms import CustomUserCreationForm, TrialUserForm, BookingForm
import random

# Login View
class CustomLoginView(LoginView):
    template_name = 'members/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('gym:index')

# Register View
class RegisterView(View):
    """Handles user registration with an optional referral code."""

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, "members/register.html", {"form": form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            referral_code = form.cleaned_data.get("referral_code")

            if referral_code:
                try:
                    affiliate = Affiliate.objects.get(referral_code=referral_code, status="Active")
                    Referral.objects.create(
                        referred_user=user,
                        referrer=affiliate,
                        referral_code=affiliate.referral_code,
                        status="Completed"
                    )
                except Affiliate.DoesNotExist:
                    messages.error(request, "Invalid or inactive referral code.")
                    return render(request, "members/register.html", {"form": form})

            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("gym:index")

        return render(request, "members/register.html", {"form": form})

# Logout View
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

# Trial Signup View
class TrialSignupView(FormView):
    template_name = 'members/trial_signup.html'
    form_class = TrialUserForm

    def form_valid(self, form):
        user = self.request.user

        # Ensure the user hasn't already used the trial
        if TrialUser.objects.filter(user=user).exists():
            messages.error(self.request, "You have already used your free trial.")
            return redirect(reverse_lazy('members:membership_page'))

        trial_start = now().date()
        trial_end = trial_start + timedelta(days=14)

        # Create TrialUser entry
        TrialUser.objects.create(user=user, trial_start_date=trial_start, trial_end_date=trial_end, status="Active")

        # Create a Membership entry for trial users
        membership, _ = Membership.objects.get_or_create(user=user)
        membership.membership_type = "trial"
        membership.start_date = trial_start
        membership.end_date = trial_end
        membership.save()

        # Send an email notification
        self.send_trial_start_email(user.email, membership)

        messages.success(self.request, "Your free trial has started! Enjoy access to our gym.")
        return redirect(reverse_lazy('members:membership_page'))

    def send_trial_start_email(self, email, membership):
        subject = "Your Free Trial Has Started!"
        message = f"Hello, your free trial has started on {membership.start_date}. It will expire on {membership.end_date}."
        send_mail(subject, message, 'from@example.com', [email], fail_silently=False)

# Book Session View
class BookSessionView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        """Handles booking form submission"""
        service_id = request.POST.get('service_id')

        if not service_id:
            messages.error(request, "Service ID is missing!")
            return redirect(reverse_lazy('members:booking_page'))

        service = get_object_or_404(Service, id=service_id)

        # Check if the user has an active membership
        membership = Membership.objects.filter(user=request.user).first()
        if not membership or membership.end_date < now().date():
            messages.error(request, "You must have an active membership to book a session.")
            return redirect("members:upgrade_membership")

        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.user = request.user
            booking.save()
            messages.success(request, "Your session has been booked successfully!")
            return redirect(reverse_lazy('members:booking_success'))

        return render(request, "members/book_session.html", {"form": form, "service": service})

# Membership Subscription View

class SubscribeMembershipView(LoginRequiredMixin, View):
    """Handles membership subscription process before payment"""
    
    def get(self, request, plan_type):
        """Create or update a pending membership and redirect to payment page"""
        if plan_type not in ["basic", "premium"]:
            messages.error(request, "Invalid membership type.")
            return redirect("members:membership_page")

        membership, created = Membership.objects.get_or_create(
            user=request.user,
            defaults={"membership_type": plan_type, "status": "pending"},
        )

        if not created:
            # Update existing membership if user is upgrading
            membership.membership_type = plan_type
            membership.status = "pending"  # Reset to pending before payment
            membership.save()

        messages.info(request, f"You have selected the {plan_type} membership. Please proceed with payment.")
        
        # ✅ Redirect to payment page for selected plan
        return redirect(reverse("members:payment_page", kwargs={"plan_type": plan_type}))

# Membership Page View
class MembershipPageView(TemplateView):
    template_name = "members/membership_page.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        membership = Membership.objects.filter(user=user).first()

        if membership and membership.membership_type == "trial" and membership.end_date <= now().date():
            return redirect("members:upgrade_membership")  # Redirect user if trial expired

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["membership"] = Membership.objects.filter(user=self.request.user).first()
        return context



class UpgradeMembershipView(TemplateView):
    template_name = "members/upgrade_membership.html"


# Renew Membership View
class RenewMembershipView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        """Handles membership renewal logic."""
        membership = Membership.objects.filter(user=request.user).first()
        
        if membership:
            # Keep the existing plan and extend its duration
            extension_days = 30 if membership.membership_type == "basic" else 365
            membership.end_date = now().date() + timedelta(days=extension_days)
            membership.save()
            messages.success(request, f"Your {membership.membership_type} membership has been renewed successfully!")
        else:
            messages.error(request, "You do not have an active membership to renew.")

        return redirect("members:membership_page")
    

class PaymentView(LoginRequiredMixin, TemplateView):
    template_name = "members/payment_page.html"

    def get_context_data(self, **kwargs):
        """Provide necessary data for the payment page"""
        context = super().get_context_data(**kwargs)
        plan_type = self.kwargs.get("plan_type")

        membership = Membership.objects.filter(
            user=self.request.user, membership_type=plan_type, status="pending"
        ).first()

        if not membership:
            messages.error(self.request, "No pending membership found for payment.")
            return redirect("members:membership_page")

        # Pricing logic
        prices = {"basic": 30, "premium": 50}
        context["amount"] = prices.get(plan_type, 0)
        context["plan_type"] = plan_type
        context["membership"] = membership

        return context

    def post(self, request, *args, **kwargs):
        """Mocks the payment process and updates membership status"""
        plan_type = kwargs.get("plan_type")
        membership = Membership.objects.filter(
            user=request.user, membership_type=plan_type, status="pending"
        ).first()

        if not membership:
            messages.error(request, "No pending membership found for payment.")
            return redirect("members:membership_page")

        # ✅ Simulate payment success (Replace with real payment logic)
        payment_success = random.choice([True, False])  # Simulate 50% chance of success

        if payment_success:
            # ✅ Activate Membership
            membership.status = "active"
            membership.start_date = now().date()
            membership.end_date = now().date() + timedelta(days=30 if plan_type == "basic" else 365)
            membership.save()

            messages.success(request, f"Payment successful! Your {plan_type} membership is now active.")
            return redirect("members:membership_page")
        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect(reverse("members:payment_page", kwargs={"plan_type": plan_type}))
