# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post, Category
from .forms import PostForm
from django.utils import timezone


class BlogListView(ListView):
    model = Post
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 5

class BlogDetailView(DetailView):
    model = Post
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'

class BlogCategoryView(ListView):
    model = Post
    template_name = 'blog/blog_category.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.objects.filter(category=category)


# Mixin to check if the user is admin or staff
class AdminOrStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'slug', 'author', 'content', 'image', 'pub_date']
    form_class = PostForm  # Ensure you're using the right form
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('gym_blog:blog_list')

    def form_valid(self, form):
        # Here you can add any custom logic before saving
        form.instance.author = self.request.user  # Set the author to the current user
        return super().form_valid(form)

    def get_success_url(self):
        return self.success_url  # Redirect to the blog list page after success

class PostUpdateView(LoginRequiredMixin, AdminOrStaffMixin, UpdateView):
    model = Post
    form_class = PostForm  # Use the updated form
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('gym_blog:blog_list')

class PostDeleteView(LoginRequiredMixin, AdminOrStaffMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('gym_blog:blog_list')
