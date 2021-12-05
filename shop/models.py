from django.db import models
from djongo import models
from django.contrib.auth.models import User
from .utils import generate_ref_code
from datetime import datetime

# Create your models here.


class Image(models.Model):
    name = models.CharField(max_length=100)
    image1 = models.ImageField(upload_to='shop/images' , default = "")
    image2 = models.ImageField(upload_to='shop/images' , default = "")
    image3 = models.ImageField(upload_to='shop/images' , default = "")
    image4 = models.ImageField(upload_to='shop/images' , default = "") 

    def __str__(self):
        return self.name



class Product(models.Model):
    objects = models.Manager()
    id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.CharField(max_length=50 , default = "")
    sub_category = models.CharField(max_length=50 , default = "")
    desc = models.CharField(max_length=3000)
    specifications = models.TextField(default='' , blank=True)
    pub_date = models.DateField()
    images = models.ForeignKey(Image , on_delete=models.CASCADE , default=0)
    max_retail_price = models.FloatField(blank=True)
    price = models.FloatField(default = 0.0,blank=True)
    discount = models.IntegerField(blank=True)
    size = models.CharField(max_length=100 , default=0)
    no_of_items_in_a_pack = models.IntegerField(default=1)
    keywords = models.TextField(max_length=5000 , default="" , blank=True)
    in_stock = models.IntegerField(blank = True , default=0)

    def __str__(self):
        return f"{self.product_name} ({self.price}) {self.id}"


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.TextField()


    def __str__(self):
        return f"{self.name} {self.msg_id}"


class HandleAmounts(models.Model):
    amount_for_free_delivery = models.IntegerField()
    amount_for_cash_on_delivery = models.IntegerField()


class Order(models.Model):
    objects = models.Manager()
    order_id = models.AutoField(primary_key = True)
    items_json = models.TextField(max_length=500000)
    items_count = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    delivery_charges = models.IntegerField(default=49)
    total_amount = models.IntegerField(default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=90)
    address1 = models.CharField(max_length=90)
    address2 = models.CharField(max_length=90 , default = "")
    city = models.CharField(max_length=90)
    state = models.CharField(max_length=90)
    phone = models.CharField(max_length=15)
    pin_code = models.CharField(max_length=90)
    date = models.DateTimeField(auto_now_add=True)
    delivering_date = models.CharField(max_length=90 , default='')
    delivering_time = models.CharField(max_length=90 , default='')
    payment_method = models.CharField(max_length=30 , default='')

    def __str__(self):
        return f"{self.name} ({self.order_id})" + "..."


class OrderUpdate(models.Model):
    objects = models.Manager()
    update_id= models.AutoField(primary_key=True)
    order_id= models.IntegerField(default="")
    update_desc= models.CharField(max_length=5000)
    timestamp= models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f"{self.update_desc} + ({self.order_id})"


class MyOffers(models.Model):
    image = models.ImageField(upload_to='shop/images' , default = "")
    heading = models.CharField(max_length=500)
    description = models.CharField(max_length=1000)

class Value_of_one_cash(models.Model):
    value_of_one_cash = models.IntegerField(default=10)

    def __str__(self):
        return f"{self.value_of_one_cash}"


class Profile(models.Model):
    objects = models.Manager()
    user = models.OneToOneField(User , on_delete = models.CASCADE)
    address1 = models.TextField(max_length=5000 , default='')
    address2 = models.TextField(max_length=5000 , default='Not Available')
    state = models.CharField(max_length=50 , default='')
    city = models.CharField(max_length=50 , default='')
    pin_code = models.CharField(max_length=10 , default='')
    Phone  = models.IntegerField(default=10)
    code = models.CharField(max_length=12 , blank=True)
    cash = models.IntegerField(default=0)
    cash_used = models.IntegerField(default = 0)
    recommended_by = models.ForeignKey(User , on_delete=models.CASCADE , blank=True , null=True , related_name='ref_by')
    otp = models.CharField(max_length=6 , default=0)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}-{self.code}"

    def get_recommend_profile(self):
        qs = Profile.objects.all()
        my_recs = []
        for profile in qs:
            if profile.recommended_by == self.user:
                my_recs.append(profile)
        return my_recs


    def save(self , *args , **kwargs):
        if self.code=="":
            code = generate_ref_code()
            self.code = code
        super().save(*args , **kwargs)


class OrderLimit(models.Model):
    limit_cross = models.BooleanField()
