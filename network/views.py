from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Like, Follower


def index(request):
    if request.method == 'POST':
        user = request.user
        content = request.POST["content"]
        new_post = Post(user=user, content=content)
        new_post.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        for post in Post.objects.all():
            post.likes = len(Like.objects.filter(post=post.id))

        return render(request, "network/index.html", {
            "posts": Post.objects.all()
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, user_id):

    # Check if the user that is watching the page is the profile user
    if user_id == request.user:
        is_user = True
    else:
        is_user = False

    # Check if the user that is watching the page is following the profile user
    if not is_user:
        user_all_following = Follower.objects.filter(follower=request.user.id)
        user_profile_following = user_all_following.filter(following=user_id)
        
        # If the filtered list has no results then the user is not following that user
        if not user_profile_following:
            is_following = False
        else:
            is_following = True

    # Get all the posts of the profile user
    user_posts = Post.objects.filter(user=user_id)

    # Update the likes of each post
    for post in user_posts:
        post.likes = len(Like.objects.filter(post=post.id))

    # Get the lenght of the followers and following users
    followers_n = len(Follower.objects.filter(following=user_id))
    following_n = len(Follower.objects.filter(follower=user_id))

    return render(request, "network/profile.html", {
        "posts": user_posts,
        "is_user": is_user,
        "user": User.objects.get(pk=user_id),
        "followers_n": followers_n,
        "following_n": following_n,
        "is_following": is_following
    })


def follow(request, user_id):
    pass