from . import views
from django.urls import path

app_name = 'affiliates'
urlpatterns = [
    path("affiliate/dashboard/", views.AffiliateDashboardView.as_view(), name="affiliate_dashboard"),
    path("dashboard/", views.ReferralDashboardView.as_view(), name="referral_dashboard"),
    path("affiliate/signup/", views.AffiliateSignupView.as_view(), name="affiliate_signup"),
    path("admin-review/", views.AffiliateReviewView.as_view(), name="admin_review"),
    path("approve/<int:pk>/", views.ApproveAffiliateView.as_view(), name="approve_affiliate"),
    path("reject/<int:pk>/", views.RejectAffiliateView.as_view(), name="reject_affiliate"),
    path("affiliate/pending/", views.AffiliatePendingView.as_view(), name="affiliate_pending"),
    path("affiliate/list/", views.AllAffiliatesView.as_view(), name="all_affiliates"),
    path("referral/<str:referral_code>/", views.track_referral_click, name="track_referral"),
    path("send-invite/", views.send_referral_email, name="send_referral_email"),
    path('admin/referrals/', views.ReferralListView.as_view(), name='referral_list'),
    path("admin/referrals/", views.ReferralDetailView.as_view(), name="referral_list"),
]