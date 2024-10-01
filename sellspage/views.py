# sellspage/views.py

from django.shortcuts import render, redirect, get_object_or_404

# from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse

from .forms import UserRegistrationForm, ProductForm, UserLoginForm
from .models import SellsPageUser, Product, Order, Comment, Wishlist, PhotoModel
from .utils import filter_dict


def login_required(view_func):
    """Custom decorator to check if the user is logged in."""
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect to the login page if not authenticated
            return redirect(reverse('salespage:login'))  # Change 'login' to your login URL name
    return _wrapped_view


def listings_view(request, pageNo=None):
    all_listings = Product.objects.all().order_by('-id')
    paginator = Paginator(all_listings, 10)  # Show 10 listings per page
    page_number = pageNo or request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'sellspage/listings.html', {'page_obj': page_obj})


@login_required
# def profile_edit_view(request, username):
def profile_edit_view(request):
    user = get_object_or_404(SellsPageUser, username=request.user.username)
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("sellspage:profile", username=user.username)
    else:
        form = UserRegistrationForm(instance=user)
    # todo : make a profile edit templete
    return render(request, "sellspage/profile_edit.html", {"form": form, "user": user})


def listing_detail_view(request, id):
    # print(id)
    product = get_object_or_404(Product, id=id)
    user = request.user if request.user.is_authenticated else None
    liked = user and product.likes.filter(id=user.id).exists()

    context = {
        "product": product,
        "liked": liked,
        "profile_type": "Seller" if product.listed_by.is_seller else "Customer",
    }

    return render(request, "sellspage/product.html", context)
    return render(request, "sellspage/listing_detail.html", context)


def self_profile(request):
    if request.user is None or not request.user.is_authenticated:
        return redirect("sellspage:login")
    return redirect("sellspage:profile", username=request.user.username)


@login_required
def add_listing_product_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.listed_by = request.user
            product.save()
            messages.success(request, "Product added successfully.")
            return redirect(reverse("sellspage:profile", args=[request.user.username]))
            # return redirect(product.get_absolute_url())
    else:
        form = ProductForm()
        # print(str(form["product_type"]))
        # print(form,form.product_type.field.queryset)
    return render(request, "sellspage/addListingProduct.html", {"form": form})


@login_required
def edit_listing_view(request, id):
    product = get_object_or_404(Product, id=id, listed_by=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect(product.get_absolute_url())
    else:
        form = ProductForm(instance=product)
    return render(
        request, "sellspage/edit_listing.html", {"form": form, "product": product}
    )


@login_required
def delete_listing_view(request, id):
    product = get_object_or_404(Product, id=id, listed_by=request.user)
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("sellspage:profile", username=request.user.username)
    return render(request, "sellspage/delete_listing.html", {"product": product})


@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(
        request, "sellspage/wishlist.html", {"wishlist_items": wishlist_items}
    )


@login_required
def order_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "sellspage/order.html", {"orders": orders})


@login_required
def add_comment_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        comment_text = request.POST.get("comment")
        if comment_text:
            Comment.objects.create(
                product=product, user=request.user, comment=comment_text
            )
            messages.success(request, "Comment added successfully.")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect(product.get_absolute_url())


@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == "POST":
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    return redirect("sellspage:profile", username=request.user.username)


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect("sellspage:profile", username=user.username)
            else:
                messages.error(request, "Invalid credentials.")
    else:
        form = UserLoginForm()
    return render(request, "sellspage/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("sellspage:login")


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful.")
            return redirect("sellspage:login")
    else:
        form = UserRegistrationForm()
    return render(request, "sellspage/register.html", {"form": form})


def profile_view(request, username) -> HttpResponse:
    user = get_object_or_404(SellsPageUser, username=username)
    context = {
        "isThisPageUser": user.username == request.user.username,
        "user": user,
        "page_data": user.get_page(page_no=request.GET.get("page", 1)),
    }
    return render(request, "sellspage/profile.html", context)
