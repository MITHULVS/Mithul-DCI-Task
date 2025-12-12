# from django.db import models
# from django.utils import timezone
#
# class BlogPost(models.Model):
#     title = models.CharField(max_length=200)
#     author = models.CharField(max_length=100)
#     content = models.TextField()
#
#     image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
#
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return self.title


# # Create your models here.
# class Student(models.Model):
#     name = models.CharField(max_length=100)
#     age = models.IntegerField()
#
#
# class ProfilePic(models.Model):
#     image = models.ImageField(upload_to='profile/')


from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)

    def _str_(self):
        return self.title
