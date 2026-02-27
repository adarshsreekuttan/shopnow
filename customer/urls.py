from django.contrib import admin
from django.urls import path
from customer import views

urlpatterns = [
    path('login/',views.customer_login, name='customer_login'),
    path('register/',views.customer_register, name='customer_register'),
    path('home/',views.home_view, name='home'),
    path('more-product/<str:slug>/',views.single_product_view, name='single_product'),
    path('profile/', views.profile_page, name='profile_page'),
    path('logout', views.customer_logout, name='customer_logout'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('password-update/', views.password_update, name='password_update'),
    path('view-addresses/', views.view_addresses, name='view_addresses'),
    path('edit-address/<int:id>', views.edit_address, name='edit_address'),
    path('delete-address/<int:id>', views.delete_address, name='delete_address'),
    path('add-new-address/', views.add_new_address, name='add_new_address'),
]