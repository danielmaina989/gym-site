from django.views.generic import TemplateView, CreateView
from django.shortcuts import redirect, render
from django.views.generic.edit import DeleteView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import View
from .models import Review, Service
from gym_blog.models import Post
from .forms import ReviewForm, ContactForm
from django.views.generic.edit import FormView
from django.contrib import messages


class HomeView(TemplateView):
    template_name = 'gym/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the latest 3 services and blog posts
        context['services'] = Service.objects.all()[:3]
        context['latest_blogs'] = Post.objects.order_by('-pub_date')[:3]  # Adjust based on your model field
        return context


class AboutView(TemplateView):
    template_name = "gym/about.html"

class FaqView(TemplateView):
    template_name = "gym/faq.html"


class ReviewsPageView(View):
    def get(self, request):
        reviews = Review.objects.all()
        return render(request, 'gym/reviews.html', {'reviews': reviews})

class SubmitReviewView(CreateView):
    form_class = ReviewForm
    template_name = 'gym/submit_review.html'

    def form_valid(self, form):
        form.save()
        return redirect('gym:reviews')

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
        form.save()
        return super().form_valid(form)
