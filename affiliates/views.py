from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from .forms import AffiliateApplicationForm
from shop.models import Order
from .models import Referral, Affiliate


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

class AffiliateDashboardView(LoginRequiredMixin, ListView):
    """Affiliate Dashboard - Shows orders linked to an affiliate."""
    model = Order
    template_name = "affiliates/referral_orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        """Only allow affiliates with ACTIVE status to access the dashboard."""
        user = self.request.user

        try:
            affiliate = Affiliate.objects.get(user=user)
            if affiliate.status != "Active":
                messages.error(self.request, "You need an active affiliate account to access the dashboard.")
                return redirect("affiliates:affiliate_signup")  # Redirect to sign-up if not active
            return Order.objects.filter(referrer=affiliate, commission_paid=False)
        except Affiliate.DoesNotExist:
            messages.error(self.request, "You are not part of the affiliate program.")
            return redirect("affiliates:affiliate_signup")

    def dispatch(self, request, *args, **kwargs):
        """Redirect non-affiliates to the signup page before loading the view"""
        if not Affiliate.objects.filter(user=request.user).exists():
            messages.error(request, "You must sign up as an affiliate first.")
            return redirect("affiliates:affiliate_signup")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(staff_member_required, name='dispatch')
class ReferralListView(ListView):
    model = Affiliate
    template_name = "affiliates/referral_list.html"
    context_object_name = "affiliates"

@method_decorator(staff_member_required, name='dispatch')
class ReferralDetailView(ListView):
    model = Referral
    template_name = "affiliates/referral_detail.html"
    context_object_name = "referrals"

    def get_queryset(self):
        affiliate_id = self.kwargs.get("pk")
        return Referral.objects.filter(referrer__id=affiliate_id)


def send_referral_email(request):
    """Allows affiliates to send referral invitations via email."""
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            affiliate = Affiliate.objects.get(user=request.user)
            referral_link = f"http://127.0.0.1:8000/register/?ref={affiliate.referral_code}"

            send_mail(
                subject="Join Our Affiliate Program!",
                message=f"Hey! Join our referral program and earn commissions. Sign up using this link: {referral_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )

            messages.success(request, "Referral invitation sent!")
        except Affiliate.DoesNotExist:
            messages.error(request, "You are not part of the affiliate program.")

    return redirect("affiliates:affiliate_dashboard")

