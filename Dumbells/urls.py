from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gym.urls')),  # Root URL points to the 'gym' app.
    path('members/', include('members.urls')),  # Members app at /members/
    path('dashboard/', include('admin_dashboard.urls')),  # Admin dashboard at /dashboard/
    path('blog/', include('gym_blog.urls')),  # Blog at /blog/
    path('coaches/', include('coaches.urls')),  # Coaches at /coaches/
    path('shop/', include('shop.urls')),  # Shop at /shop/
    path("cart/", include("cart.urls", namespace="cart")),
    path("affiliates/", include("affiliates.urls", namespace="affiliates")),
]

# Add media file serving in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
