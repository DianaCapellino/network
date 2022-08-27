from django.contrib.auth.models import AbstractUser
from django.db import models
import django.utils.timezone


class User(AbstractUser):

    def __str__(self):
        return f"{self.username}"


class Follower(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers_users")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_users")

    def __str__(self):
        return f"{self.followers.username}"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="writer_user")
    content = models.CharField(max_length=512)
    date = models.DateTimeField(default=django.utils.timezone.now)
    likes = models.IntegerField(default=0)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user} post on {self.date} with {self.likes} likes."


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked_posts")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liker_users")