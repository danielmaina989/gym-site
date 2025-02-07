from django.shortcuts import render
from django.views.generic import ListView,TemplateView, UpdateView
from gym.models import Review
from django.urls import path, reverse_lazy
from django.contrib import admin
from django.shortcuts import redirect
from django import forms
from django.contrib.auth.mixins import UserPassesTestMixin
from gym.models import ContactSubmission
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings

class HomeView(TemplateView):
    template_name = "admin_dashboard/index.html"

class ReviewListView(ListView):
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'



class EnquiryListView(UserPassesTestMixin, ListView):
    model = ContactSubmission
    template_name = "admin_dashboard/enquiry_list.html"
    context_object_name = "enquiries"

    def test_func(self):
        return self.request.user.is_staff  # Only staff can access this view


class EnquiryReplyView(UserPassesTestMixin, UpdateView):
    model = ContactSubmission
    fields = ['admin_reply']  # Use correct field name
    template_name = "admin_dashboard/enquiry_reply.html"
    success_url = reverse_lazy('admin_dashboard:enquiry_list')

    def form_valid(self, form):
        enquiry = form.save(commit=False)
        enquiry.responded_at = now()
        enquiry.is_replied = True  # Mark as replied
        enquiry.save()

        # Send reply email to the user
        send_mail(
            subject=f"Response to Your Enquiry - {enquiry.enquiry_type}",
            message=f"Dear {enquiry.name},\n\n{enquiry.admin_reply}\n\nBest Regards,\n[Your Gym Name]",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enquiry.email],
            fail_silently=False,
        )

        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_staff  # Only staff can access


class FollowUpView(UpdateView):
    model = ContactSubmission
    fields = ['follow_up']  # Only the follow-up field is required
    template_name = "admin_dashboard/follow_up.html"
    success_url = reverse_lazy('admin_dashboard:enquiry_list')

    def form_valid(self, form):
        enquiry = form.save(commit=False)
        enquiry.follow_up_at = now()  # Set the follow-up timestamp
        enquiry.save()

        # Send follow-up email to the user
        send_mail(
            subject=f"Follow-Up on Your Enquiry - {enquiry.enquiry_type}",
            message=f"Dear {enquiry.name},\n\n{enquiry.follow_up}\n\nBest Regards,\n[Your Gym Name]",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enquiry.email],
            fail_silently=False,
        )

        return super().form_valid(form)
