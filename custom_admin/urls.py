from django.urls import path
from custom_admin import views

urlpatterns = [

    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),

    path('product_view/',views.products_view,name='product_view'),
    path('pending_products/',views.admin_pending_products,name='pending_products'),
    path('edit_product/<int:id>',views.edit_product,name='edit_product'),
    path('delete_product/<int:id>/',views.delete_product,name='delete_product'),
    path('approve_products/<int:id>/',views.approve_products,name='approve_products'),
    path('reject_products/<int:id>/',views.reject_products,name='reject_products'),

    path('category_list/',views.category_list,name='category_list'),
    path('add_category/',views.add_category,name='add_category'),
    path('update_category/<int:id>/',views.update_category,name='update_category'),
    path('delete_category/<int:id>/',views.delete_category,name='delete_category'),
    path('deactivate_category/<int:id>/',views.deactivate_category,name='deactivate_category'),
    path('activate_category/<int:id>/',views.active_category,name='activate_category'),
    path('add_subcategory/',views.add_subcategory,name='add_subcategory'),
    path('update_subcategory/<int:id>/',views.update_subcategory,name='update_subcategory'),
    path('delete_subcategory/<int:id>/',views.delete_subcategory,name='delete_subcategory'),

    path('seller_view/',views.seller_view,name='seller_view'),
    path('seller_detail/<int:id>',views.seller_details,name='seller_details'),
    path('pending_seller',views.pending_seller,name='pending_seller'),
    path('approve_seller/<int:id>/',views.approve_seller,name='approve_seller'),
    path('deactivate_seller/<int:id>/',views.deactivate_seller,name='deactivate_seller'),

    path('order_view/',views.order_view,name='order_view'),
    path('order_details/<int:id>/',views.order_details,name='order_details'),
    path('delete_order/<int:id>/',views.delete_order,name='delete_order'),

    path('user_view/',views.user_view,name='user_view'),

]