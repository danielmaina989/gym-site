from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # your app views


app_name = 'admin_dashboard'
urlpatterns = [
    path('index/', views.HomeView.as_view(), name='index'),
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('admin/enquiries/', views.EnquiryListView.as_view(), name='enquiry_list'),
    path('admin/enquiries/<int:pk>/reply/', views.EnquiryReplyView.as_view(), name='enquiry_reply'),
    path('follow-up/<int:pk>/', views.FollowUpView.as_view(), name='follow_up'),

]
