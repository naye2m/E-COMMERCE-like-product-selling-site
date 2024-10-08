from django.urls import path
from . import views

app_name = "sellspage"

urlpatterns = [
    # path('', views.self_profile, name='self_profile'),
    path('', views.self_profile, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('profile/', views.self_profile, name='self_profile_'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<str:username>/', views.profile_view, name='profile'),

    path('listings', views.listings_view, name='listings'),
    path('listing/add/', views.add_listing_product_view, name='add_listing_product'),
    path('listing/<int:id>/', views.listing_detail_view, name='listing_detail'), # todo : imp
    path('listing/<int:id>/', views.listing_detail_view, name='product_detail'), # todo : imp
    path('listing/<int:id>/edit/', views.edit_listing_view, name='edit_listing'),
    path('listing/<int:id>/delete/', views.delete_listing_view, name='delete_listing'),
    # todo path('listing/<int:id>/order/', views.order_view, name='place_order'),
    # todo path('listing/<int:id>/wishlist/', views.wishlist_view, name='wishlist'),

    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('order/', views.order_view, name='order'),
    

    path('comment/add/<int:product_id>/', views.add_comment_view, name='add_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment_view, name='delete_comment'),
]
