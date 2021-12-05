from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView,LogoutView

urlpatterns = [
    path("" , views.index , name = 'ShopHome'),
    path("about/" , views.about , name = 'AboutUs'),
    path("contact/" , views.contact , name = 'contact'),
    path("tracker/" , views.tracker , name = 'Tracker'),
    path("search/" , views.search , name = 'Search'),
    path("products/<int:myid>" , views.productView , name = 'ProductView'),
    path("checkout/" , views.checkout , name = 'Checkout'),
    path("login/" , views.HandleLogin, name = 'HandleLogin'),
    path("recommendedprofiles/" , views.MyRecommendationView, name = 'My_Recs'),
    path("signup/" , views.HandleSignup , name = 'HandleSignup'),
    path("logout/" , views.HandleLogout , name = "HandleLogout"),
    path("resend-otp/" , views.ResendOtp , name = "Resendotp"),
    path("otp/" , views.Otp , name = 'otp'),
    path("handlerequest/" , views.handlerequest , name = 'HandleRequest'),
    path("myorders/" , views.MyOrders , name = 'MyOrders'),
    path("myaccount/" , views.MyAccount , name = 'MyAccount'),
    path("myorders/order_list/<int:oid>" , views.Orders_list , name = 'Orders_list'),
    path("category/<str:cat>" , views.Category , name = 'category_item'),
    path("order-verification/" , views.Order_Verification , name = 'order-verification'),
    path("order-otp/" , views.Order_Otp , name = 'order-otp'),
    
]