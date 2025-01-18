from . import views
from django.urls import path

app_name = 'gym'
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('faq/', views.FaqView.as_view(), name='faq'),
    path('reviews/', views.ReviewsPageView.as_view(), name='reviews'),
    path('submit-review/', views.SubmitReviewView.as_view(), name='submit_review'),
     path('review/<int:pk>/delete/', views.DeleteReviewView.as_view(), name='delete_review'), 
    path('review/<int:pk>/update/', views.UpdateReviewView.as_view(), name='update_review'),
]