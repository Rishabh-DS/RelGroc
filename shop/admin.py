from django.contrib import admin
from .models import OrderLimit, Product , Image , Contact , Order , OrderUpdate , Profile , MyOffers ,Value_of_one_cash , HandleAmounts
# Register your models here.
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(OrderUpdate)
admin.site.register(Profile)
admin.site.register(MyOffers)
admin.site.register(HandleAmounts)
admin.site.register(Value_of_one_cash)
admin.site.register(OrderLimit)