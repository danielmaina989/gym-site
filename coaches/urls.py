from . import views
from django.urls import path

app_name = 'coaches'
urlpatterns = [
    path('coach_list', views.CoachListView.as_view(), name='coach_list'),
    path('<int:pk>/', views.CoachDetailView.as_view(), name='coach_detail'),
    path('add/', views.CoachCreateView.as_view(), name='coach-add'),
    path('<int:pk>/edit/', views.CoachUpdateView.as_view(), name='coach_edit'),  # Edit URL
    path('<int:pk>/delete/', views.CoachDeleteView.as_view(), name='coach_confirm_delete'),
    path('book_session/<int:coach_id>/', views.BookSessionView.as_view(), name='book_session'),
    path('booking-success/<int:booking_id>/', views.BookingSuccessView.as_view(), name='booking_success'),
    path('booking_canceled/<int:booking_id>/', views.CancelBookingView.as_view(), name='booking_canceled'),    
        ]