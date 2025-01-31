from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.generic import TemplateView,ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from .models import Coach
from .forms import CoachForm, BookingForm
from django.urls import reverse_lazy, reverse
from members.models import Booking
from django.http import Http404
from django.core.exceptions import PermissionDenied


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
    


class BookSessionView(LoginRequiredMixin, FormView):
    form_class = BookingForm
    template_name = 'coaches/book_session.html'
    login_url = '/accounts/login/'  # Redirect to login if not authenticated

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coach_id = self.kwargs['coach_id']
        coach = get_object_or_404(Coach, id=coach_id)

        if self.request.user.is_authenticated:
            user_bookings = Booking.objects.filter(user=self.request.user, coach=coach)
        else:
            user_bookings = Booking.objects.none()  # No bookings if user is not authenticated

        context['bookings'] = user_bookings
        context['coach'] = coach
        return context

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)

        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.save()
        
        return redirect(reverse('coaches:booking_success', kwargs={'booking_id': booking.id}))

class BookingSuccessView(TemplateView):
    template_name = 'coaches/booking_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')  # Get booking_id from URL
        booking = get_object_or_404(Booking, id=booking_id)  # Fetch the booking
        
        context['booking'] = booking  # Pass the booking object to the template
        return context
    
# views.py

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'coaches/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Fetch bookings for the logged-in user
        return Booking.objects.filter(user=self.request.user)

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