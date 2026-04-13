from django.urls import path
from seller import views

urlpatterns = [
    path('seller_registration', views.seller_registration, name="seller_registration"),
    path('seller_login', views.seller_login, name="seller_login"),
    path('seller_logout', views.seller_logout, name="seller_logout"),
    path('password_reset', views.password_reset, name="password_reset"),

    path('seller_home', views.seller_home, name="seller_home"),
    path('seller_profile', views.seller_profile, name="seller_profile"),
    path('seller_profile_edit', views.seller_profile_edit, name="seller_profile_edit"),

    path('seller_add_product', views.seller_add_product, name="seller_add_product"),
    path('seller_product_view/<str:slug>', views.seller_product_view, name="seller_product_view"),
    path('seller_product_edit/<str:slug>', views.seller_product_edit, name="seller_product_edit"),
    path('product_delete/<int:id>', views.product_delete, name='product_delete'),
    path('product-control', views.product_control, name='product_control'),

    path('set_primary_img/<int:id>', views.set_primary_img, name='set_primary_img'),
    path('rejected-product', views.rejected_product, name='rejected_product'),
    path('reject_product_edit/<str:slug>', views.reject_product_edit, name='reject_product_edit'),

    path('seller_approval', views.seller_approval, name="seller_approval"),
    path('under-review-products', views.under_review_products, name='under_review_products'),
    path('pending_product_delete/<int:id>', views.pending_product_delete, name='pending_product_delete'),
    path('pending_edit/<str:slug>', views.pending_edit, name='pending_edit'),

    path('seller_orders', views.seller_orders, name='seller_orders'),
    path('seller_single_order/<int:id>', views.seller_single_order, name='seller_single_order'),
    path('seller_order_status/<int:id>', views.seller_order_status, name='seller_order_status'),

    path('pending_order', views.pending_order, name='pending_order'),
    path('ongoing_order', views.ongoing_order, name='ongoing_order'),
    path('finished_order', views.finished_order, name='finished_order'),

    path('coupon', views.coupon, name='coupon'),
    path('add_coupon', views.add_coupon, name='add_coupon'),
    path('coupon_active', views.coupon_active, name='coupon_active'),
    path('coupon_pending', views.coupon_pending, name='coupon_pending'),
    path('coupon_delete/<int:id>', views.coupon_delete, name='coupon_delete'),

    path('ajax/load_subcategory', views.load_subcategory, name='load_subcategory'),
    path('message', views.message, name='message'),
    path('testing', views.testing, name='testing'),

    path('view-reviews', views.view_reviews, name='view_reviews'),

]