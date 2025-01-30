from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView,ListView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Coach
from .forms import CoachForm, BookingForm
from django.urls import reverse_lazy, reverse
from members.models import Booking


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
    

class BookSessionView(FormView):
    form_class = BookingForm
    template_name = 'coaches/book_session.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_form()
        print("Form fields:", form.fields.keys())  # Check if training_time is included
        print("Training Time Field:", form.fields.get("training_time"))
        print("Form fields before rendering:", form.fields.keys())
        coach_id = self.kwargs['coach_id']
        coach = get_object_or_404(Coach, id=coach_id)
        context['booking'] = Booking.objects.all()
        context['coach'] = coach  # No need to override form here
        return context


    def form_valid(self, form):
        # Save the booking and associate it with the service, coach, and user
        booking = form.save(commit=False)
        booking.user = self.request.user
        booking.save()
        
        # Redirect to the success page with the booking_id
        return redirect(reverse('coaches:booking_success', kwargs={'booking_id': booking.id}))

class BookingSuccessView(TemplateView):
    template_name = 'coaches/booking_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking_id = self.kwargs.get('booking_id')  # Get booking_id from URL
        booking = get_object_or_404(Booking, id=booking_id)  # Fetch the booking
        
        context['booking'] = booking  # Pass the booking object to the template
        return context
    
class CancelBookingView(DeleteView):
    model = Booking
    template_name = 'coaches/confirm_cancellation.html'
    context_object_name = 'booking'
    success_url = reverse_lazy('coaches:booking_canceled')  # Redirect to a cancellation confirmation page after success

    def delete(self, request, *args, **kwargs):
        booking = self.get_object()
        # Optional: You can change the status of the booking instead of deleting
        booking.delete()  # Or update status like booking.status = 'canceled' and then save
        return super().delete(request, *args, **kwargs)