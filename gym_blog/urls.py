# urls.py
from django.urls import path
from . import views

app_name = 'gym_blog'
urlpatterns = [
    path('blog_list/', views.BlogListView.as_view(), name='blog_list'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<slug:slug>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
