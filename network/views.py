from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
from django.forms.models import model_to_dict

from .models import User, Post, Like, Follower


def index(request):
    if request.method == 'POST':
        user = request.user
        content = request.POST["content"]
        new_post = Post(user=user, content=content)
        new_post.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        all_posts = Post.objects.all()
        for post in all_posts:
            post.likes = len(Like.objects.filter(post=post.id))

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/index.html", {
            "posts": all_posts,
            "page_obj": page_obj
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
    profile_user = User.objects.get(pk=user_id)
    if profile_user == request.user:
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
    else:
        is_following = False

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
        "profile_user": profile_user,
        "followers_n": followers_n,
        "following_n": following_n,
        "is_following": is_following
    })


@login_required
def follow(request, user_id):
    if request.method == "POST":
            
        # Get the information of the profile user and log-in user
        following_user = User.objects.get(pk=user_id)
        follower_user = User.objects.get(pk=request.user.id)
        
        # Get the list of followers with the log-in user
        user_all_followers = Follower.objects.filter(follower=request.user.id)
        if not user_all_followers:
            user_profile_follower = None

        user_profile_follower = user_all_followers.filter(following=user_id)

        # If the filtered list is empty then it creates the new follower
        if not user_profile_follower:
            new_follower = Follower(following=following_user, follower=follower_user)
            new_follower.save()
        
        # If the list has an item then it will remove it
        else:          
            old_follower = user_profile_follower
            old_follower.delete()

        return HttpResponseRedirect(reverse("profile", args=(user_id)))


@login_required
def following(request):

    following_list = Follower.objects.filter(follower=request.user)
    following_users = []
    for following in following_list:
        if not following in following_users:
            following_users.append(User.objects.get(pk=following.following_id))

    for post in Post.objects.all():
        post.likes = len(Like.objects.filter(post=post.id))

    return render(request, "network/following.html", {
        "following_users": following_users,
        "posts": Post.objects.all()
    })


def get_posts(request):
    posts = list(Post.objects.values())
    return JsonResponse(posts, safe=False)


@login_required
@csrf_exempt
def get_post(request, post_id):

    # Query for requested post
    try:
        post_object = Post.objects.get(pk=post_id)
        post = model_to_dict(post_object)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Return post contents
    if request.method == "GET":
        return JsonResponse(post, safe=False)

    # Update post
    elif request.method == "PUT":

        # Check if the user is the writer and get json information
        if request.user == post_object.user:
            data = json.loads(request.body)

            # Update content
            if data.get("content") is not None:
                post_object.content = data["content"]

            # Save the changes of the post
            post_object.save()
            return HttpResponse(status=204)
        else:

            # Update likes
            data = json.loads(request.body)
            if data.get("likes") is not None:
                post_likes = Like.objects.filter(post=post_object)
                user_likes = post_likes.filter(user=request.user)

                # If the filtered list is empty then it creates the like
                if not user_likes:
                    new_like = Like(post=post_object, user=request.user)
                    new_like.save()
                
                # If the list has an item with the same user and post it will unlike it
                else:          
                    user_likes.delete()

                # Update likes in post
                post_object.likes = len(Like.objects.filter(post=post_object.id))

                # Save the changes of the post
                post_object.save()
                return HttpResponse(status=204)
            else:
                return JsonResponse({"error": "User is not the writer."}, status=404)

    # Email must be via GET or PUT
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)