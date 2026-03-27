from django.contrib import admin
from django.urls import path
from customer import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/',views.customer_login, name='customer_login'),
    path('register/',views.customer_register, name='customer_register'),
    path('logout', views.customer_logout, name='customer_logout'),

    path('',views.home_view, name='home'),
    path('more-product/<str:slug>/',views.single_product_view, name='single_product'),

    path('profile/', views.profile_page, name='profile_page'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('password-update/', views.password_update, name='password_update'),

    path('view-addresses/', views.view_addresses, name='view_addresses'),
    path('edit-address/<int:id>', views.edit_address, name='edit_address'),
    path('delete-address/<int:id>', views.delete_address, name='delete_address'),
    path('add-new-address/', views.add_new_address, name='add_new_address'),

    path('view-cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:id>', views.add_to_cart, name='add_to_cart'),
    path('delete-cart-item/<int:id>', views.delete_cart_item, name='delete_cart_item'),
    path('clear_all_cart/', views.clear_all_cart, name='clear_all_cart'),
    path('update-cart/<int:id>/<str:action>', views.increment_decrement_cartquantity, name='update_cart'),

    path('view-wishlist/', views.view_wishlist, name='view_wishlist'),
    path('toggle-wishlist/<int:id>', views.toggle_wishlist, name='toggle_wishlist'),
    path('remove-from-wishlist/<int:id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('add-to-cart-from-wishlist/<int:id>', views.add_to_cart_from_wishlist, name='add_to_cart_from_wishlist'),

    path('post-review/<str:slug>/', views.post_review, name='post_review'),

    path('checkout-page/', views.checkout_page, name='checkout_page'),
    path('place-order/', views.place_order, name='place_order'),
    path('view-orders/', views.view_orders, name='view_orders'),
    path('order-success/<int:id>/', views.order_success, name='order_success'),
    path('view-single-order/<int:id>', views.view_single_order, name='view_order_details'),

    path('category/<str:slug>', views.category_filter, name='category_detail'),
    path('subcategory/<slug:slug>/<slug:sub_slug>', views.subcategory_filter, name='subcategory_filter'),
    path('load-subcategories/', views.load_subcategories, name='load_subcategories'),

    path('search', views.search_products, name='search_products'),
    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),

    path('buy-now/<int:id>', views.buy_now, name='buy_now'),

    path('payment-gateway/<int:order_id>/', views.payment_gateway, name='payment_gateway'),
    path('payment-success/', views.payment_success, name='payment_success'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="customer/password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="customer/registration/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="customer/registration/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="customer/registration/password_reset_complete.html"), name="password_reset_complete"),
]
