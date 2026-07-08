from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:id>', views.post_details, name='post_details'),
    path('post/<int:id>/like', views.like_post, name='like_post'),
    path('post/create', views.post_create, name='post_create'),
    path('post/update/<int:id>', views.post_update, name='post_update'),
    path('post/delete/<int:id>', views.post_delete, name='post_delete'),

    #user related url
    path('singup/', views.singup_view, name='singup'),
    path('profile/', views.profile_view, name='profile_view'),
    path('login/',auth_views.LoginView.as_view(template_name='user/login.html',redirect_authenticated_user=True),name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='post_list'),name='logout'),
]
