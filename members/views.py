from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login
from django.http import HttpResponse
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
import stripe
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas



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
            return redirect("members:payment_page", plan_type=plan_type)

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
        context["today"] = now().date()
        return context


class UpgradeMembershipView(TemplateView):
    template_name = "members/upgrade_membership.html"


# Renew Membership View
class RenewMembershipView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        membership = Membership.objects.filter(user=user, status="active").first()

        if not membership:
            messages.error(request, "You don't have an active membership to renew.")
            return redirect("members:membership_page")

        # Extend the membership by **30 days** for both plans
        membership.end_date += timedelta(days=30)
        membership.save()

        messages.success(request, f"Your {membership.membership_type} membership has been renewed until {membership.end_date}.")
        return redirect("members:payment_success", plan_type=membership.membership_type)

class PaymentView(View):
    def post(self, request, *args, **kwargs):
        user = request.user
        plan_type = kwargs.get("plan_type")
        prices = {"basic": 3000, "premium": 5000}  # Amount in cents (Stripe uses smallest currency unit)

        if plan_type not in prices:
            messages.error(request, "Invalid membership type.")
            return redirect("members:membership_page")

        # Check if user already has a membership
        existing_membership = Membership.objects.filter(user=user, status="active").first()

        if existing_membership:
            if existing_membership.membership_type == plan_type:
                messages.warning(request, "You already have this membership.")
                return redirect("members:membership_page")
            elif existing_membership.membership_type == "basic" and plan_type == "premium":
                messages.info(request, "You're upgrading to a premium membership.")
            elif existing_membership.membership_type == "premium" and plan_type == "basic":
                messages.warning(request, "You're downgrading to a basic membership. Some features may be lost.")

        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        success_url = request.build_absolute_uri(reverse("members:payment_success", kwargs={"plan_type": plan_type}))
        cancel_url = request.build_absolute_uri(reverse("members:membership_page"))

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": f"{plan_type.capitalize()} Membership"},
                        "unit_amount": prices[plan_type],  # Amount in cents
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return redirect(session.url)
        except stripe.error.StripeError as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect("members:membership_page")



class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        plan_type = kwargs.get("plan_type")

        # Check if the user already has an active membership
        membership = Membership.objects.filter(user=user, status="active").first()

        if membership:
            if membership.membership_type == plan_type:
                messages.info(request, "Your membership is already active.")
            else:
                messages.success(request, f"Membership upgraded to {plan_type}!")

            # Update membership details
            membership.membership_type = plan_type
            membership.start_date = now().date()
            membership.end_date = now().date() + timedelta(days=30 if plan_type == "basic" else 365)
            membership.save()
        else:
            # Create a new membership if none exists
            membership = Membership.objects.create(
                user=user,
                membership_type=plan_type,
                status="active",
                start_date=now().date(),
                end_date=now().date() + timedelta(days=30 if plan_type == "basic" else 365)
            )
            messages.success(request, f"Payment successful! Your {plan_type} membership is now active.")

        # Redirect to the success page with membership details
        return render(request, "members/payment_success.html", {"membership": membership})



class DownloadMembershipCardView(View):
    def get(self, request, *args, **kwargs):
        user = request.user

        # Get user's premium membership
        membership = Membership.objects.filter(user=user, membership_type="premium", status="active").first()
        if not membership:
            return HttpResponse("You do not have an active premium membership.", status=403)

        # Create the PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="membership_card.pdf"'

        # Generate the PDF
        p = canvas.Canvas(response, pagesize=letter)
        p.setFont("Helvetica-Bold", 16)

        p.drawString(200, 750, "🏋️ Gym Membership Card 🏋️")
        p.setFont("Helvetica", 12)
        p.drawString(100, 700, f"Member Name: {user.get_full_name() or user.username}")
        p.drawString(100, 680, f"Membership Type: {membership.membership_type.capitalize()}")
        p.drawString(100, 660, f"Start Date: {membership.start_date}")
        p.drawString(100, 640, f"End Date: {membership.end_date}")
        p.drawString(100, 620, f"Status: Active ✅")

        p.showPage()
        p.save()

        return response
