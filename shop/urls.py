from . import views
from django.urls import path

app_name = 'shop'
urlpatterns = [
    path('shop/', views.HomeView.as_view(), name='index'),
    # List all products; if a category slug is provided, filter by that category.
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/add/', views.ProductCreateView.as_view(), name='product_add'),
    path('product/upload-csv/',views.CSVUploadView.as_view(), name='upload_csv'),
    path("category/<slug:category_slug>/", views.CategoryProductListView.as_view(), name="category_products"),
    # View details of a single product using its slug.
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
     path('<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]