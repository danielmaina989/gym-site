from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # your app views


app_name = 'members'
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='members/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('trial-signup/', views.TrialSignupView.as_view(), name='trial_signup'),
    path('services/<int:service_id>/book/', views.BookSessionView.as_view(), name='book_session'),  # Keep this one
    path('membership/', views.MembershipPageView.as_view(), name='membership_page'),
    path("upgrade/", views.UpgradeMembershipView.as_view(), name="upgrade_membership"),
    path('renew_membership/', views.RenewMembershipView.as_view(), name='renew_membership'),
    path('subscribe/<str:plan_type>/', views.SubscribeMembershipView.as_view(), name='subscribe_membership'),
    path('members/payment/<str:plan_type>/', views.PaymentView.as_view(), name='payment_page')

]

