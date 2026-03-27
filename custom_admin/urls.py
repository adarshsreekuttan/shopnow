
from django.urls import path
from custom_admin import views

urlpatterns = [

    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('pending_products/',views.admin_pending_products,name='pending_products'),
    path('product_view/',views.products_view,name='product_view'),
    path('seller_view/',views.seller_view,name='seller_view'),
    path('order_view/',views.order_view,name='order_view'),
    path('user_view/',views.user_view,name='user_view'),
    path('add_category/',views.add_category,name='add_category'),
    path('category_list/',views.category_list,name='category_list'),
    path('delete_category/<int:id>/',views.delete_category,name='delete_category'),
    path('update_category/<int:id>/',views.update_category,name='update_category'),
    path('deactivate_category/<int:id>/',views.deactivate_category,name='deactivate_category'),
    path('add_subcategory/',views.add_subcategory,name='add_subcategory'),
    path('subcategory_list/',views.subcategory_list,name='subcategory_list'),
    path('activate_category/<int:id>/',views.active_category,name='activate_category'),
    path('update_subcategory/<int:id>/',views.update_subcategory,name='update_subcategory'),
    path('delete_subcategory/<int:id>/',views.delete_subcategory,name='delete_subcategory'),

]
