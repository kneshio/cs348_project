from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
    
class Buyer(models.Model):
    buyer_id = models.AutoField(primary_key=True) 
    username = models.CharField(max_length=100, unique = True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username 


class SellerManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)


class Seller(AbstractBaseUser):
    seller_id = models.AutoField(primary_key=True) 
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100) 
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = SellerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username
    
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField()
    quantity = models.IntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['price']),
            models.Index(fields=['seller']), 
            models.Index(fields=['name', 'category', 'price', 'seller']),
        ]

    def __str__(self):
        return self.name