from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .forms import AffiliateApplicationForm
from shop.models import Order
from .models import Referral, Affiliate, SentReferral
import csv
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.timezone import now
from .models import SentReferral, Affiliate, Referral


class AffiliateSignupView(LoginRequiredMixin, View):
    """Allows a user to become an affiliate and get a referral code."""

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is already an affiliate
        affiliate = Affiliate.objects.filter(user=user).first()

        if affiliate:
            if affiliate.status == "Pending":
                messages.info(request, "Your affiliate request is still pending approval.")
                return redirect("affiliates:affiliate_pending")
            elif affiliate.status == "Active":
                messages.success(request, "You are already an active affiliate.")
                return redirect("affiliates:affiliate_dashboard")

        form = AffiliateApplicationForm()
        return render(request, "affiliates/affiliate_signup.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = AffiliateApplicationForm(request.POST)
        if form.is_valid():
            affiliate = form.save(commit=False)
            affiliate.user = request.user
            affiliate.status = "Pending"
            affiliate.save()

            messages.success(request, "Your affiliate request has been submitted for approval.")
            return redirect("affiliates:affiliate_pending")

        return render(request, "affiliates/affiliate_signup.html", {"form": form})


class AffiliateReviewView(UserPassesTestMixin, ListView):
    """Displays all pending affiliates for admin review."""
    model = Affiliate
    template_name = "affiliates/admin_review.html"
    context_object_name = "affiliates"

    def test_func(self):
        """Ensure only admins can access this page."""
        return self.request.user.is_staff

    def get_queryset(self):
        """Show only affiliates with pending status."""
        return Affiliate.objects.filter(status="Pending")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_count"] = context["affiliates"].count()
        return context


class ApproveAffiliateView(UserPassesTestMixin, View):
    """Approve an affiliate request."""
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        affiliate = get_object_or_404(Affiliate, pk=pk)
        affiliate.status = "Active"
        affiliate.save()
        messages.success(request, f"{affiliate.user.username} has been approved as an affiliate.")
        return redirect("affiliates:admin_review")

class RejectAffiliateView(UserPassesTestMixin, View):
    """Reject an affiliate request."""
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        affiliate = get_object_or_404(Affiliate, pk=pk)
        affiliate.status = "Rejected"
        affiliate.save()
        messages.warning(request, f"{affiliate.user.username} has been rejected as an affiliate.")
        return redirect("affiliates:admin_review")


class AffiliateReviewView(UserPassesTestMixin, ListView):
    """Displays all affiliates for admin review."""
    model = Affiliate
    template_name = "affiliates/admin_review.html"
    context_object_name = "affiliates"

    def test_func(self):
        """Ensure only admins can access this page."""
        return self.request.user.is_staff

class ApproveAffiliateView(UserPassesTestMixin, View):
    """Approve an affiliate request."""
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        affiliate = get_object_or_404(Affiliate, pk=pk)
        affiliate.status = "Active"
        affiliate.save()
        messages.success(request, f"{affiliate.user.username} has been approved as an affiliate.")
        return redirect("affiliates:admin_review")

class RejectAffiliateView(UserPassesTestMixin, View):
    """Reject an affiliate request."""
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        affiliate = get_object_or_404(Affiliate, pk=pk)
        affiliate.status = "Rejected"
        affiliate.save()
        messages.warning(request, f"{affiliate.user.username} has been rejected as an affiliate.")
        return redirect("affiliates:admin_review")


class AffiliatePendingView(TemplateView):
    template_name = "affiliates/affiliate_pending.html"


class ReferralDashboardView(TemplateView):
    template_name = "affiliates/affiliate_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            affiliate = Affiliate.objects.get(user=user)
        except Affiliate.DoesNotExist:
            messages.error(user, "You are not part of the affiliate program. Please sign up first.")
            return redirect("affiliates:affiliate_signup")  # Ensure correct namespace

        # Redirect to 'pending' page if their affiliate request is not yet approved
        if affiliate.status == "Pending":
            messages.info(user, "Your affiliate request is still pending approval.")
            return redirect("affiliates:affiliate_pending")

        # Redirect to 'rejected' page if their request was denied
        if affiliate.status == "Rejected":
            messages.warning(user, "Your affiliate application was rejected. Contact support for assistance.")
            return redirect("affiliates:affiliate_rejected")

        # Get referral data if user is an active affiliate
        referrals = Referral.objects.filter(referrer=affiliate)
        context["affiliate"] = affiliate
        context["referrals"] = referrals
        return context



def track_referral_click(request, referral_code):
    try:
        referral = Referral.objects.get(referral_code=referral_code)
        referral.clicks += 1
        referral.save()
        return redirect("members:register")  # Redirect to registration page
    except Referral.DoesNotExist:
        messages.error(request, "Invalid referral link.")
        return redirect("gym:index")

def update_commission():
    top_affiliates = Affiliate.objects.filter(total_earnings__gte=500)
    top_affiliates.update(commission_rate=10.0)



class AllAffiliatesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Allows admin/staff to see all registered affiliates."""
    model = Affiliate
    template_name = "affiliates/all_affiliates.html"
    context_object_name = "affiliates"

    def test_func(self):
        """Only allow staff/admins to access this page."""
        return self.request.user.is_staff

@method_decorator(staff_member_required, name="dispatch")
class AffiliateDetailView(DetailView):
    """Admin view to show an affiliate's details, earnings, referrals, and payment info."""
    model = Affiliate
    template_name = "affiliates/admin_affiliate_detail.html"
    context_object_name = "affiliate"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["referrals"] = Referral.objects.filter(referrer=self.object)
        return context


@method_decorator(staff_member_required, name="dispatch")
class ReferralCSVExportView(View):
    """Exports affiliate earnings and referral details as CSV."""

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="affiliate_earnings.csv"'

        writer = csv.writer(response)
        writer.writerow(["Affiliate Username", "Total Earnings", "Referral Code", "Referred Users", "Referral Status"])

        affiliates = Affiliate.objects.all()
        for affiliate in affiliates:
            referrals = Referral.objects.filter(referrer=affiliate)
            for referral in referrals:
                writer.writerow([
                    affiliate.user.username,
                    affiliate.total_earnings,
                    affiliate.referral_code,
                    referral.referred_user.username,
                    referral.status
                ])

        return response


@method_decorator(staff_member_required, name="dispatch")
class SendAffiliateEmailView(View):
    """Admin view to send an email to an affiliate."""

    def post(self, request, pk):
        affiliate = get_object_or_404(Affiliate, pk=pk)
        message = request.POST.get("message")

        if not message:
            messages.error(request, "Email message cannot be empty.")
            return redirect("affiliates:admin_affiliate_detail", pk=pk)

        send_mail(
            subject="Important Update Regarding Your Affiliate Account",
            message=message,
            from_email="admin@fitnesscenter.com",
            recipient_list=[affiliate.user.email],
        )

        messages.success(request, "Email sent successfully!")
        return redirect("affiliates:admin_affiliate_detail", pk=pk)



class AffiliateDashboardView(LoginRequiredMixin, ListView):
    """Affiliate Dashboard - Shows orders, referrals, and pending invites."""
    model = Order
    template_name = "affiliates/affiliate_dashboard.html"
    context_object_name = "orders"

    def get_queryset(self):
        """Filter orders linked to the affiliate (only unpaid commissions)."""
        user = self.request.user

        try:
            affiliate = Affiliate.objects.get(user=user)
            if affiliate.status != "Active":
                messages.error(self.request, "You need an active affiliate account to access the dashboard.")
                return Order.objects.none()

            # ✅ Corrected: Get orders where the referrer is the affiliate
            return Order.objects.filter(referral__referrer=affiliate, commission_paid=False)
        except Affiliate.DoesNotExist:
            messages.error(self.request, "You are not part of the affiliate program.")
            return Order.objects.none()

    def get_context_data(self, **kwargs):
        """Pass affiliate data, referrals, and pending invites to the template."""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        try:
            affiliate = Affiliate.objects.get(user=user)
            context["affiliate"] = affiliate  # ✅ Pass affiliate object
            context["referrals"] = Referral.objects.filter(referrer=affiliate)  # ✅ Registered referrals
            context["pending_invites"] = SentReferral.objects.filter(affiliate=affiliate, registered=False)  # ✅ Pending invites
        except Affiliate.DoesNotExist:
            context["affiliate"] = None
            context["referrals"] = []
            context["pending_invites"] = []

        return context



@method_decorator(staff_member_required, name='dispatch')
class ReferralListView(ListView):
    model = Affiliate
    template_name = "affiliates/referral_list.html"
    context_object_name = "affiliates"


class ReferralDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View to show details of a specific referral."""
    model = Referral
    template_name = "affiliates/referral_detail.html"
    context_object_name = "referral"

    def test_func(self):
        """Ensure the user is an active affiliate."""
        return Affiliate.objects.filter(user=self.request.user, status="Active").exists()

    def get_queryset(self):
        """Ensure the affiliate can only view their own referrals."""
        return Referral.objects.filter(referrer__user=self.request.user)



def send_referral_email(request):
    """Sends referral email, ensuring the email is not already referred or registered."""
    if request.method == "POST":
        email = request.POST.get("email")
        user = request.user

        try:
            affiliate = Affiliate.objects.get(user=user)
        except Affiliate.DoesNotExist:
            messages.error(request, "You are not an affiliate.")
            return redirect("affiliates:affiliate_dashboard")

        # ✅ 1. Check if the email belongs to an existing user
        if User.objects.filter(email=email).exists():
            messages.warning(request, f"{email} is already registered.")
            return redirect("affiliates:affiliate_dashboard")

        # ✅ 2. Check if this affiliate has already referred this email
        if SentReferral.objects.filter(email=email, affiliate=affiliate).exists():
            messages.warning(request, f"{email} has already been invited.")
            return redirect("affiliates:affiliate_dashboard")

        # ✅ 3. Save the email in SentReferral
        SentReferral.objects.create(email=email, affiliate=affiliate, sent_at=now(), registered=False)

        # ✅ 4. Send the referral email
        send_mail(
            subject="Join Our Fitness Center - Get Started!",
            message=f"Hello!\n\n{user.username} invited you to join FitnessCenter. Sign up using this link: https://fitnesscenter.com/register/?ref={affiliate.referral_code}",
            from_email="noreply@fitnesscenter.com",
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, f"Referral email sent to {email}.")
        return redirect("affiliates:affiliate_dashboard")
