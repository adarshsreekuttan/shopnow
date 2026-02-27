"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('add_cat/', views.add_category, name='add_cat'),
    path('cat_list/', views.category_list, name='cat_list'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('delete/<int:id>/', views.delete_cat, name='dlt_cat'),
    path('update/<int:id>/', views.update_category, name='upd_cat'),
    path('admindash/', views.admin_dash, name='admin_dash'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('add_subcat/', views.add_subcategory, name='add_subcat'),
    path('subcat_list/', views.sub_categorylist, name='subcat_list'),
]
