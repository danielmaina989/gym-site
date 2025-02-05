from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.generic import TemplateView,ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Coach
from gym.models import Service
from .forms import CoachForm, BookingForm
from django.urls import reverse_lazy, reverse
from members.models import Booking, TrialUser, Membership
from django.http import Http404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.timezone import now
import logging


class CoachListView(ListView):
    model = Coach
    template_name = 'coaches/coach_list.html'
    context_object_name = 'coaches'

class CoachDetailView(DetailView):
    model = Coach
    template_name = 'coaches/coach_detail.html'
    context_object_name = 'coach'


class CoachCreateView(UserPassesTestMixin, CreateView):
    model = Coach
    form_class = CoachForm
    template_name = 'coaches/coach_form.html'
    success_url = reverse_lazy('coaches:coach_list')  # Use reverse_lazy for URL resolution

    def test_func(self):
        # Allow only staff members to access this view
        return self.request.user.is_staff
    
class CoachUpdateView(UpdateView):
    model = Coach
    form_class = CoachForm
    template_name = 'coaches/coach_form.html'
    success_url = reverse_lazy('coaches:coach_list')  # Use reverse_lazy for URL resolution


    def test_func(self):
        return self.request.user.is_staff
    
class CoachDeleteView(UserPassesTestMixin, DeleteView):
    model = Coach
    template_name = 'coaches/coach_confirm_delete.html'
    success_url = reverse_lazy('coaches:coach_list')

    def test_func(self):
        return self.request.user.is_staff
    

# Set up a logger
logger = logging.getLogger(__name__)

class BookSessionView(LoginRequiredMixin, FormView):
    form_class = BookingForm
    template_name = 'coaches/book_session.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coach_id = self.kwargs['coach_id']
        coach = get_object_or_404(Coach, id=coach_id)
        user_bookings = Booking.objects.filter(user=self.request.user, coach=coach)

        context['bookings'] = user_bookings
        context['coach'] = coach
        return context

    def form_valid(self, form):
        user = self.request.user
        context = self.get_context_data()  # Get context for rendering the template

        # Check if user has a membership
        membership = Membership.objects.filter(user=user).first()
        if not membership:
            context['error_message'] = "You need a membership to book a session."
            context['membership_link'] = 'members:membership_page'  # Link to the membership page
            return self.render_to_response(context)  # Return to the same page with error message

        # Check if membership is still active
        if not membership.is_active():
            context['error_message'] = "Your membership has expired. Please renew."
            context['membership_link'] = 'members:membership_page'
            return self.render_to_response(context)

        # Prevent multiple bookings on the same day
        session_date = form.cleaned_data['session_date']
        if Booking.objects.filter(user=user, session_date=session_date).exists():
            context['error_message'] = "You already have a session booked for this date."
            return self.render_to_response(context)

        # Save the booking
        booking = form.save(commit=False)
        booking.user = user
        booking.save()

        messages.success(self.request, "Your booking was successful!")
        return redirect('coaches:booking_success', booking_id=booking.id)

class BookingSuccessView(TemplateView):
    template_name = 'coaches/booking_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')  # Get booking_id from URL
        booking = get_object_or_404(Booking, id=booking_id)  # Fetch the booking
        
        context['booking'] = booking  # Pass the booking object to the template
        return context
    
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'coaches/booking_list.html'
    context_object_name = 'bookings'
    login_url = '/accounts/login/'

    def get_queryset(self):
        """
        Retrieve only the bookings for the logged-in user.
        """
        return Booking.objects.filter(user=self.request.user).order_by('-session_date')

    def get_context_data(self, **kwargs):
        """
        Split bookings into past and upcoming based on session date.
        """
        context = super().get_context_data(**kwargs)
        bookings = self.get_queryset()

        context['upcoming_bookings'] = bookings.filter(session_date__gte=now())
        context['past_bookings'] = bookings.filter(session_date__lt=now())

        return context

class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'coaches/confirm_cancellation.html'
    context_object_name = 'booking'
    success_url = reverse_lazy('coaches:booking_list')  # Redirect after deletion

    def get_object(self, queryset=None):
        """
        Override get_object to fetch the Booking instance using 'booking_id' from the URL.
        """
        booking_id = self.kwargs.get("booking_id")
        if not booking_id:
            raise Http404("Booking ID not provided")
        return get_object_or_404(Booking, id=booking_id)