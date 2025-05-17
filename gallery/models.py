
from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
class Image(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)

    submitter = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=50, null=True, blank=True)
    tags = models.ManyToManyField(Tag)
    likes = models.ManyToManyField(User, related_name='liked_images', blank=True) 

    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()


class Collection(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    images = models.ManyToManyField(Image)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.name