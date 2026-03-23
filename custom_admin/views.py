from django.shortcuts import render,redirect
from django.contrib.auth import login,logout
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from seller.models import Category, SubCategory
from custom_admin.models import AdminLogin


# Create your views here.

