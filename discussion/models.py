from django.contrib.auth.models import User
from django.db import models
import uuid


class Topic(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    stars = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    starred_by = models.ManyToManyField(User, related_name='starred_topics')  # Track users who starred the topic

    def add_star(self, user):
        if user not in self.starred_by.all():
            self.stars += 1
            self.starred_by.add(user)
            self.save()

    def remove_star(self, user):
        if user in self.starred_by.all():
            self.stars -= 1
            self.starred_by.remove(user)
            self.save()

class Comment(models.Model):
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_comments')
    dislikes = models.ManyToManyField(User, related_name='disliked_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
