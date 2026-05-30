from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, Tag, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
# Create your views here.

def home(request):
    pass
