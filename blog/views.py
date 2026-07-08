from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category, Tag, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .forms import PostForm, CommentForm, UpdateProfileForm
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required


def post_list(request):
    #category, tasg, searching, pagination --> post dekhate hobe

    category_query = request.GET.get('category', '').strip()
    tag_query = request.GET.get('tag', '').strip()
    search_query = request.GET.get('q', '').strip()

    posts = Post.objects.all().order_by('-created_at')

    # search
    if category_query:
        posts = posts.filter(category__name__iexact=category_query)

    if tag_query:
        posts = posts.filter(tag__name__iexact=tag_query).distinct()

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query)
            | Q(content__icontains=search_query)
            | Q(category__name__icontains=search_query)
            | Q(tag__name__icontains=search_query)
        ).distinct()

    #pagination
    #perpage 5 posts
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'search_query': search_query,
        'category_query': category_query,
        'tag_query': tag_query,
    }


    return render(request, 'blog/post_list.html', context)



def post_details(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_details', id=post.id)
    else:
        comment_form = CommentForm()

    comments = post.comment_set.all().order_by('-created_at')

    if request.user.is_authenticated:
        is_liked = post.liked_users.filter(id=request.user.id).exists()
    else:
        is_liked = False

    like_count = post.liked_users.count()

    post.view_count += 1
    post.save()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'like_count': like_count,
    }

    return render(request, 'blog/post_details.html', context)


@login_required
def like_post(request, id):
    post = get_object_or_404(Post, id=id)

    if post.liked_users.filter(id=request.user.id).exists():
        post.liked_users.remove(request.user)
    else:
        post.liked_users.add(request.user)

    return redirect('post_details', id=post.id)


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()   # This saves selected tags
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'blog/post_create.html', {'form': form})


def post_update(request, id):
    post = get_object_or_404(Post, id=id)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()   # This updates tags
            return redirect('post_details', id=post.id)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_create.html', {'form': form})

def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect('post_list')


def singup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('post_list')
    
    else:
        form = UserCreationForm
    
    return render(request, 'user/signup.html', {'form' : form})

def profile_view(request):
    section = request.GET.get('section', 'profile')
    context = {'section' : section}

    if section == 'posts':
        posts = Post.objects.filter(author= request.user)
        context['posts'] = posts

    elif section == 'update':
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('/profile?section=update')
        else:
            form = UpdateProfileForm(instance=request.user)

        context['form'] = form

    return render(request, 'user/profile.html', context)