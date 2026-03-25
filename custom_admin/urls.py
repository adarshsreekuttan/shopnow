
from django.urls import path
from custom_admin import views

urlpatterns = [

    path('admindashboard/',views.admin_dashboard,name='admin_dash'),
    path('pending_products/',views.admin_pending_products,name='pending_products'),
    path('product_view/',views.products_view,name='product_view'),
    path('seller_view/',views.seller_view,name='seller_view'),
    path('order_view/',views.order_view,name='order_view'),
    path('user_view/',views.user_view,name='user_view')

]
