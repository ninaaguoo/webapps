from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#data model for post 
class Post(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    creation_time = models.DateTimeField()

    def __str__(self):
        return f"Entry(id={self.id})"
    
class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    following = models.ManyToManyField(User, related_name="followers")

    def __str__(self):
        return f"Entry(id={self.id})"
    
class Comment(models.Model):
    text = models.CharField(max_length=200)
    creation_time = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="comment_creators")
    post = models.ForeignKey(Post,  on_delete=models.PROTECT, related_name="comments")