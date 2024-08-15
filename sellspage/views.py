# sellspage/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, ProductForm, UserLoginForm
from .models import SellsPageUser, ListingProduct, Order, Comment, Wishlist, PhotoModel
from django.http import HttpResponse
from django.contrib import messages

@login_required
def profile_edit_view(request, username):
    user = get_object_or_404(SellsPageUser, username=username)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('sellspage:profile', username=user.username)
    else:
        form = UserRegistrationForm(instance=user)
    # todo return render(request, 'sellspage/profile_edit.html', {'form': form, 'user': user})


@login_required
def self_profile(request):
    return redirect('sellspage:profile', username=request.user.username)

@login_required
def add_listing_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.listed_by = request.user
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm()
    return render(request, 'sellspage/addListingProduct.html', {'form': form})

@login_required
def edit_listing_view(request, id):
    product = get_object_or_404(ListingProduct, id=id, listed_by=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm(instance=product)
    return render(request, 'sellspage/edit_listing.html', {'form': form, 'product': product})

@login_required
def delete_listing_view(request, id):
    product = get_object_or_404(ListingProduct, id=id, listed_by=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('sellspage:profile', username=request.user.username)
    return render(request, 'sellspage/delete_listing.html', {'product': product})

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'sellspage/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def order_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'sellspage/order.html', {'orders': orders})

@login_required
def add_comment_view(request, product_id):
    product = get_object_or_404(ListingProduct, id=product_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment')
        if comment_text:
            Comment.objects.create(product=product, user=request.user, comment=comment_text)
            messages.success(request, "Comment added successfully.")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect(product.get_absolute_url())

@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    return redirect('sellspage:profile', username=request.user.username)

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('sellspage:profile', username=user.username)
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = UserLoginForm()
    return render(request, 'sellspage/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('sellspage:login')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful.")
            return redirect('sellspage:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'sellspage/register.html', {'form': form})

def profile_view(request, username) -> HttpResponse:
    user = get_object_or_404(SellsPageUser, username=username)
    context = {
        'user': user,
        'page_data': user.get_page(page_no=request.GET.get('page', 1)),
    }
    return render(request, 'sellspage/profile.html', context)
