from django.shortcuts import render,redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Product, Category
from django.urls import reverse_lazy
from .forms import ProductForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import csv
from django.core.mail import send_mail
from io import TextIOWrapper
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import CSVUploadForm
from .models import Product, Category, Order, Refferral, Affilliate
from django.utils.text import slugify
from django.db import IntegrityError
import os
import csv
from django.core.files import File
from django.core.files.images import ImageFile
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator



# Create your views here.
class HomeView(TemplateView):
    template_name = 'shop/index.html'


class ProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        """Filter products by category if a category is selected"""
        category_slug = self.request.GET.get("category")
        if category_slug:
            return Product.objects.filter(category__slug=category_slug)
        return Product.objects.all()

    def get_context_data(self, **kwargs):
        """Include all categories in the context for the sidebar"""
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["selected_category"] = self.request.GET.get("category", "")
        return context

class CategoryProductListView(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug")
        category = get_object_or_404(Category, slug=category_slug)
        return Product.objects.filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_category"] = self.kwargs.get("category_slug")  # Highlight active category
        context["categories"] = Category.objects.all()  # Pass all categories
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'

class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/product_form.html'
    success_url = reverse_lazy('shop:product_list')

    def test_func(self):
        return self.request.user.is_staff

class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    fields = ['name', 'description', 'price', 'stock', 'available', 'image']
    template_name = 'shop/product_edit.html'
    success_url = reverse_lazy('shop:product_list')
    
    def test_func(self):
        return self.request.user.is_staff  # Only admin can edit

class ProductDeleteView(UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'shop/product_confirm_delete.html'
    success_url = reverse_lazy('shop:product_list')

    def test_func(self):
        return self.request.user.is_staff 

class CSVUploadView(FormView):
    template_name = 'shop/upload_csv.html'
    form_class = CSVUploadForm
    success_url = reverse_lazy('shop:product_list')

    def form_valid(self, form):
        csv_file = form.cleaned_data['csv_file']
        decoded_file = TextIOWrapper(csv_file, encoding='utf-8')
        reader = csv.DictReader(decoded_file)

        for row in reader:
            category_name = row.get('category')
            category, created = Category.objects.get_or_create(name=category_name)

            # Generate a unique slug
            base_slug = slugify(row.get('name'))
            slug = base_slug
            count = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            product = Product(
                category=category,
                name=row.get('name'),
                slug=slug,
                description=row.get('description'),
                price=row.get('price'),
                stock=row.get('stock'),
                available=row.get('available').lower() in ['true', '1', 'yes'],
            )

            # Handle image field
            image_path = row.get('image_url')
            if image_path:
                image_relative_path = f"product_images/{os.path.basename(image_path)}"
                full_image_path = os.path.join(settings.MEDIA_ROOT, image_relative_path)

                if os.path.exists(full_image_path):  # Check if the image exists in media folder
                    with open(full_image_path, 'rb') as img_file:
                        product.image.save(image_relative_path, ImageFile(img_file), save=True)  # Reopen image file here

            product.save()  # Save product after assigning image

        messages.success(self.request, 'Products uploaded successfully.')
        return super().form_valid(form)



@login_required
def referral_signup(request):
    """Allows a user to become a referee and get a referral code."""
    if Refferral.objects.filter(referrer=request.user).exists():
        messages.info(request, "You already have a referral code!")
    else:
        referral = Refferral.objects.create(referrer=request.user)
        messages.success(request, f"Referral created! Your code: {referral.referral_code}")

    return redirect("referral_dashboard")

def referral_dashboard(request):
    referral, created = Refferral.objects.get_or_create(referrer=request.user)
    
    return render(request, "shop/referral_dashboard.html", {
        "referral": referral
    })


class AffiliateDashboardView(ListView):
    model = Order
    template_name = "shop/referral_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(referrer=self.request.user, commission_paid=False)

@method_decorator(staff_member_required, name='dispatch')
class ReferralListView(ListView):
    model = Affilliate
    template_name = 'shop/referral_list.html'
    context_object_name = 'affiliates'

    def get_queryset(self):
        # Only get affiliates with their respective referrals
        return Affilliate.objects.all()

@method_decorator(staff_member_required, name='dispatch')
class ReferralDetailView(ListView):
    model = Refferral
    template_name = 'shop/referral_detail.html'
    context_object_name = 'referrals'

    def get_queryset(self):
        affiliate_id = self.kwargs.get('pk')
        return Refferral.objects.filter(referrer__id=affiliate_id)
    
@login_required
def send_referral_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        referral = Refferral.objects.get(referrer=request.user)

        # Send referral email (make sure your email settings are correct)
        send_mail(
            subject="Join Our Referral Program",
            message=f"Use this referral link to join: {referral.referral_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, "Referral invitation sent!")
        return redirect("shop:referral_dashboard")

    return redirect("shop:referral_dashboard")

