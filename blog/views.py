from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, Tag, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm, CommentForm
from django.db.models import Q
from django.core.paginator import Paginator


def post_list(request):
    #category, tasg, searching, pagination --> post dekhate hobe

    categoryQ = request.GET.get('category')
    tagQ = request.GET.get('tag')
    searchQ = request.GET.get('q')

    posts = Post.objects.all()

    # search
    if categoryQ:
        posts = posts.filter(category__name = categoryQ)

    if tagQ:
        posts = posts.filter(tag__name = tagQ)

    if searchQ:
        posts = posts.filter(
            Q(title__icontains = searchQ)
            | Q(content__icontains = searchQ)
            | Q(tag__name__icontains = searchQ)
            | Q(category__name__icontains = searchQ)
        ).distinct()

    #pagination
    paginator = Paginator(posts, 5) #perpage 5 posts
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj' : page_obj,
        'categories' : Category.objects.all(),
        'tags' : Tag.objects.all(),
        'search_query' : searchQ,
        'category_query' : categoryQ,
        'tag_query' : tagQ
    }

    return render(request, '', context)