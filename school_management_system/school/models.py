from django.db import models

# Create your models here.
class student(models.Model):
    # id = models.AutoField()
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    email = models.EmailField(null=True , blank=True)
    address = models.ImageField(null=True , blank=True)
