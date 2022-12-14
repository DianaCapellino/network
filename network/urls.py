
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:user_id>", views.profile, name="profile"),
    path("profile/<str:user_id>/follow", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("posts", views.get_posts, name="get_posts"),
    path("post/<str:post_id>", views.get_post, name="get_post"),
    path("post/<str:post_id>/like", views.like, name="like"),
    path("likes", views.get_likes, name="get_likes")
]
