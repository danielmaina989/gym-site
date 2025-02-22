from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # your app views


app_name = 'members'
urlpatterns = [
    # Other app URLs...
    path('login/', auth_views.LoginView.as_view(template_name='members/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('trial-signup/', views.TrialSignupView.as_view(), name='trial_signup'),
    path('book_session/', views.BookSessionView.as_view(), name='book_session'),
    path('services/<int:service_id>/book/', views.BookSessionView.as_view(), name='book_session'),
    path('membership/', views.MembershipPageView.as_view(), name='membership_page'),
    path('renew_membership/', views.RenewMembershipView.as_view(), name='renew_membership'),
    path('activate_trial/', views.ActivateTrialView.as_view(), name='activate_trial'), 
    path('subscribe/<str:plan_type>/', views.SubscribeMembershipView.as_view(), name='subscribe_membership'),
    
]
