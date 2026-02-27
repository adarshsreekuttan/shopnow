from django.urls import path
from seller import views


urlpatterns = [
    path('seller_registration',views.seller_registration,name="seller_registration"),
    path('seller_login',views.seller_login,name="seller_login"),
    path('seller_home',views.seller_home,name="seller_home"),
    path('seller_profile',views.seller_profile,name="seller_profile"),
    path('seller_profile_edit',views.seller_profile_edit,name="seller_profile_edit"),
    path('seller_password',views.seller_password,name="seller_password"),
    path('seller_add_product',views.seller_add_product,name="seller_add_product"),
    path('seller_product_view/<str:slug>',views.seller_product_view,name="seller_product_view"),
    path('seller_product_edit/<str:slug>',views.seller_product_edit,name="seller_product_edit"),
]

