from django.views.generic import TemplateView, CreateView, DetailView, ListView
from django.shortcuts import redirect, render, get_object_or_404
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from .models import Review, Service
from gym_blog.models import Post
from .forms import ReviewForm, ContactForm, ServiceForm, ReviewReplyForm
from coaches.models import Coach
from django.views.generic.edit import FormView
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings


class HomeView(TemplateView):
    template_name = 'gym/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the latest 3 services, reviews, blog posts, and coaches
        context['services'] = Service.objects.all()[:3]
        context['reviews'] = Review.objects.all()[:3]
        context['latest_blogs'] = Post.objects.order_by('-pub_date')[:3]
        context['coaches'] = Coach.objects.all()[:3]  # Add this line to fetch all coaches
        return context


class AboutView(TemplateView):
    template_name = "gym/about.html"

class FaqView(TemplateView):
    template_name = "gym/faq.html"


class ReviewsPageView(View):
    def get(self, request):
        reviews = Review.objects.order_by('-created_at')
        return render(request, 'gym/reviews.html', {'reviews': reviews})
    
class SubmitReviewView(CreateView):
    form_class = ReviewForm
    template_name = 'gym/submit_review.html'

    def form_valid(self, form):
        form.save()
        return redirect('gym:reviews')
    
class ReplyReviewView(UserPassesTestMixin, UpdateView):
    model = Review
    form_class = ReviewReplyForm
    template_name = "gym/reply_review.html"

    def form_valid(self, form):
        review = form.save()
        messages.success(self.request, f"Reply added to {review.name}'s review!")
        return redirect('gym:reviews')

    def test_func(self):
        return self.request.user.is_staff

class UpdateReviewView(UserPassesTestMixin, UpdateView):
    model = Review
    template_name = 'gym/update_review.html'
    fields = ['name', 'comment', 'rating']
    success_url = reverse_lazy('gym:reviews')

    def test_func(self):
        return self.request.user.is_staff

class DeleteReviewView(UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'gym/confirm_delete.html'
    success_url = reverse_lazy('gym:reviews')

    def test_func(self):
        return self.request.user.is_staff


class ContactView(FormView):
    template_name = "gym/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy('gym:about')

    def form_valid(self, form):
        enquiry = form.save()

        # Send email notification to admin
        send_mail(
            subject="New Enquiry Submitted",
            message=f"A new enquiry has been submitted by {enquiry.name}.\n\nMessage: {enquiry.message}\n\nPlease log in to respond.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],  # Set this in your settings.py
            fail_silently=False,
        )

        return super().form_valid(form)
    
# services
# Check if the user is an admin
def admin_check(user):
    return user.is_staff

class ServiceListView(ListView):
    model = Service
    template_name = 'gym/service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return Service.objects.filter(is_active=True)

class ServiceDetailView(DetailView):
    model = Service
    template_name = 'gym/service_detail.html'
    context_object_name = 'service'

    def get(self, request, pk):
        service = get_object_or_404(Service, pk=pk)
        return render(request, 'gym/service_detail.html', {'service': service})


class ServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'gym/service_form.html'
    success_url = reverse_lazy('service_list')  # Redirect to the service list page after successful creation

    # Only allow admins to create services
    def test_func(self):
        return self.request.user.is_staff

class ServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'gym/service_form.html'
    success_url = reverse_lazy('gym:service_list')  # Redirect to the service list page after successful update

    # Only allow admins to update services
    def test_func(self):
        return self.request.user.is_staff

class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Service
    template_name = 'gym/service_confirm_delete.html'
    success_url = reverse_lazy('service_list')  # Redirect to the service list page after successful deletion

    # Only allow admins to delete services
    def test_func(self):
        return self.request.user.is_staff
