from django.db.models.query import ValuesListIterable
from django.http.response import JsonResponse
from django.shortcuts import render,redirect,HttpResponse
from .models import HandleAmounts, Product,Contact,Order,OrderUpdate,Image,Profile,MyOffers , Value_of_one_cash , OrderLimit
from django.http import HttpResponse
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from .PayTm import checksum
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate , login , logout
import http.client
from django.conf import settings
import random
import math


MERCHANT_KEY = 'ebEK@jq4_WiPbAIQ'

def index(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(product_name__icontains=request.GET.get('term'))
        titles = list()
        for product in qs:
            titles.append(product.product_name)
        return JsonResponse(titles , safe=False)
    offers = MyOffers.objects.all()
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds , 'categories':cats , 'offers':offers}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request , 'shop/about.html')

def Category(request , cat):
    categories = Product.objects.values('category')
    cats = {item['category'] for item in categories}
    items = Product.objects.filter(category=cat)
    params = {'items':items , 'category':cat , 'categories':cats}
    return render(request , 'shop/category.html' , params)

def contact(request):
    hello = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        hello = True
        return render(request , 'shop/contact.html' , {'hello':hello})
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        phoneno = request.POST.get('phone', '')
        try:
            order = Order.objects.filter(order_id=orderId, phone=phoneno)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')



def searchmatch(query,item):
    if(query.lower() in item.desc.lower() or query.lower() in item.product_name.lower() or query.lower() in item.category.lower() or query.lower() in item.sub_category.lower() or query.lower() in item.keywords.lower()):
        return True
    else:
        return False


# def search(request):
#     query = request.GET.get('search')
#     allprods = []
#     catprods = Product.objects.values('category' , 'id')
#     cats = {item['category'] for item in catprods}
#     for cat in cats:
#         prodtemp = Product.objects.filter(category = cat)
#         prod = [item for item in prodtemp if searchmatch(query , item)]
#         n = len(prod)
#         nslides = n//4+ceil((n/4)-(n//4))
#         if len(prod)!=0:
#             allprods.append([prod , range(1,nslides) , nslides])
#     params = {'allprods':allprods , 'msg':""}
#     if(len(allprods)==0 or len(query)<2):
#         params = {'msg':"Please make sure to enter relevent query"}
#     return render(request , 'shop/search1.html' , params)

def search(request):
    query = request.GET.get('search')
    allprods = []
    products = Product.objects.all()
    allprods = [item for item in products if searchmatch(query , item)]
    categories = Product.objects.values('category')
    cats = {item['category'] for item in categories}
    params = {'allprods':allprods , 'categories':cats , "msg":""}
    if(len(allprods)==0 or len(query)<2):
        params = {'msg':"Please make sure to enter relevent query"}
    return render(request , 'shop/search.html' , params)

def productView(request,myid):
    product = Product.objects.filter(id = myid)
    return render(request , 'shop/prodView.html' , {'product':product[0] , 'id':myid})


def checkout(request):
    thank = False
    welcome = False
    if request.method == "GET":
        status = request.session.get('status')
        if status == None:
            status = "not verified"
        if status=="not verified":
            color = "red"
        else:
            color = "green"
        return render(request,'shop/checkout.html',{'status':status , 'color':color})

    if request.method == "POST":
        # request.session['status'] = "not verified"
        status = request.session.get('status')
        if status is None:
            status = "not verified"
        if status=="not verified":
            color = "red"
        else:
            color = "green"
        order_limit = OrderLimit.objects.get(id=1)
        flag=False
        if(order_limit.limit_cross==True):
            flag=True
            context = {"msg":"We can not take more orders today, try ordering tomorrow. Thank you very much :)" , "flag":flag}
            return render(request , 'shop/checkout.html' , context)
        items_json = request.POST.get('itemsjson','')
        orders = json.loads(items_json)
        order_list = []
        for i in orders.values():
            order_list.append(i)
        flag=False
        for i in order_list:
            p = Product.objects.get(id = i[3])
            if(p.in_stock<i[0]):
                flag=True
                context = {'msg':'One or more items are out of stock','flag':flag}
                return render(request , 'shop/checkout.html' , context)
            s = p.in_stock
            p.in_stock = s-i[0]
            p.save()
        if(items_json=={}):
            welcome = True
        if request.user.is_authenticated:
            name = request.user.username
            amount = request.POST.get('amount','')
            totalamount = request.POST.get('totalamount','')
            delivering_date  = request.POST.get('delivering-date' , '')
            delivering_time  = request.POST.get('delivering-time' , '')
            cart = request.POST.get('cartitems' , '')
            # print(cart)
            email = request.user.email
            profile = Profile.objects.filter(user=request.user)
            address1 = profile[0].address1
            address2 = profile[0].address2
            city = profile[0].city
            state = profile[0].city
            pin_code = profile[0].pin_code
            phone = profile[0].Phone
        else:
            name = request.POST.get('name','')
            amount = request.POST.get('amount','')
            totalamount = request.POST.get('totalamount','')
            email = request.POST.get('email','')
            address1 = request.POST.get('address1','')
            address2 = request.POST.get('address2','')
            city = request.POST.get('city','')
            state = request.POST.get('state','')
            pin_code = request.POST.get('pin_code','')
            phone = request.POST.get('phone','')
        deliverycharges = 49
        amounts = HandleAmounts.objects.get(id=1)
        if int(amount)>amounts.amount_for_free_delivery:
            deliverycharges = 0
        order = Order(items_json = items_json , name = name , email = email , address1 = address1 , address2 = address2 , city = city , state = state , pin_code = pin_code ,  phone = phone , amount = amount , items_count=len(order_list) , delivering_date = delivering_date , delivering_time = delivering_time , delivery_charges = deliverycharges)
        order.save()
        update = OrderUpdate(order_id = order.order_id , update_desc = "The Order Has Been Placed")
        update.save()
        thank = True
        id = order.order_id
        if int(amount)<=amounts.amount_for_cash_on_delivery:
            if request.POST.get("cod"):
                if request.user.is_authenticated:
                    order = Order.objects.get(order_id=id)
                    order.payment_method = "Cash On Delivery"
                    order.save()
                return render(request , 'shop/checkout.html', {'thank':thank, 'id':id , 'welcome':welcome})
        else:
            if request.POST.get("cod"):
                order.delete()
                return HttpResponse("Sorry, we can't afford Cash On delivery for orders greater than Rs. 6000")
        #request paytm to transfer the amount to your account after payment by the user
        if request.POST.get("online"):
            if request.user.is_authenticated:
                order = Order.objects.get(order_id=id)
                order.payment_method = "Online"
                order.save()
            param_dict= {
                'MID':'rvVdcC49490187028773',
                'ORDER_ID':str(order.order_id),
                'TXN_AMOUNT':str(totalamount),
                'CUST_ID':email,
                'INDUSTRY_TYPE_ID':'Retail',
                'WEBSITE':'WEBSTAGING',
                'CHANNEL_ID':'WEB',
            'CALLBACK_URL':'http://34.71.201.87/handlerequest/',
            }
            param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict , MERCHANT_KEY)
            return render(request , 'shop/paytm.html' , {'param_dict':param_dict , 'thank':thank})
        result1 = False
        result2 = False
        if request.POST.get("money"):
            profile = Profile.objects.get(user=request.user)
            order = Order.objects.get(order_id=id)
            order.payment_method = "MAC Cash"
            order.save()
            value = Value_of_one_cash.objects.get(id=1)
            cash = profile.cash
            cash_used = profile.cash_used
            if int(amount)<=value.value_of_one_cash*cash:
                result1 = True
                val = math.ceil(int(amount)/value.value_of_one_cash)
                cash = cash-val
                profile.cash = cash
                cash_used +=val
                profile.cash_used = cash_used
                profile.save()
                return render(request , 'shop/checkout.html' , {'result1':result1 , 'id':id})
            else:
                result2 = True
                order = Order.objects.get(order_id=id)
                order.delete()
                return render(request , 'shop/checkout.html' , {'result2':result2})

    return render(request , 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    order = False
    #paytm will send you poat request
    form = request.POST
    order = Order.objects.get(order_id=form['ORDERID'])
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i=='CHECKSUMHASH':
            Checksum=form[i]
    verify = checksum.verify_checksum(response_dict,MERCHANT_KEY,Checksum)
    if verify:
        if response_dict['RESPCODE']=='01':
            order = True
        else:
            order.delete()
            order=False
            # return HttpResponse('order was not successful because'+response_dict['RESPMSG'])
    return render(request , 'shop/paymentstatus.html',{'response':response_dict , 'order':order})


def send_otp(mobile , otp):
    conn = http.client.HTTPSConnection("api.msg91.com")
    authkey = settings.AUTH_KEY
    headers = { 'content-type': "application/json" }
    url = "http://control.msg91.com/api/sendotp.php?otp="+otp+"&sender=RishGa&message="+"Your Otp is"+otp+"&mobile="+mobile+"&authkey="+authkey+"&country=91"
    conn.request("GET", url , headers=headers)
    res = conn.getresponse()
    data = res.read()
    return None



def HandleSignup(request):
    if(request.method == "POST"):
        # get the post parameters
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        phone = request.POST['phone']
        address1 = request.POST['address1']
        address2 = request.POST['address2']
        state = request.POST['state']
        city = request.POST['city']
        pin_code = request.POST['pin_code']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        code = str(request.POST['ref_code'])
        #cookies
        request.session['username'] = username
        request.session['fname'] = fname
        request.session['lname'] = lname
        request.session['phone'] = phone
        request.session['address1'] = address1
        request.session['address2'] = address2
        request.session['state'] = state
        request.session['city'] = city
        request.session['pin_code'] = pin_code
        request.session['email'] = email

        usernamec = request.session['username']  
        fnamec = request.session['fname']
        lnamec = request.session['lname']
        phonec = request.session['phone']
        address1c = request.session['address1']
        address2c = request.session['address2']
        statec = request.session['state']
        cityc = request.session['city'] 
        pin_codec = request.session['pin_code']
        emailc = request.session['email']

        context1 = {'usernamec':usernamec , 'fnamec':fnamec , 'lnamec':lnamec , 'phonec':phonec , 'address1c':address1c , 'address2c':address2c , 'statec':statec , 'cityc':cityc , 'pin_codec':pin_codec , 'emailc':emailc}

        try:
            profile = Profile.objects.get(code=code)
            request.session['ref_profile'] = profile.id
        except:
            pass

        profile_id = request.session.get('ref_profile')
        # checks for errorneous inputs
        check_user = User.objects.filter(email=email).first()
        check_profile = Profile.objects.filter(Phone=phone).first()

        if(check_user or check_profile):
            messages.error(request, "User Already Exixts")
            return render(request , 'shop/signup.html' , context1)
        if len(username)>15:
            messages.error(request, "Username must be less than 15 characters")
            return redirect("ShopHome")
            
        if not username.isalnum():
            messages.error(request, "Username should only contain letters and numbers")
            return redirect("ShopHome")

        if pass1 != pass2:
            messages.error(request, "Passwords do not match")
            return redirect("ShopHome")

        # create the user

        myuser = User.objects.create_user(username , email , pass1)
        otp = str(random.randint(1000,9999))
        user_profile = Profile.objects.get(user=myuser)
        myuser.first_name = fname
        myuser.last_name = lname
        user_profile.Phone = phone
        user_profile.otp = otp
        user_profile.address1 = address1
        user_profile.address2 = address2
        user_profile.state = state
        user_profile.city = city
        user_profile.pin_code = pin_code
        user_profile.save()
        send_otp(phone,otp)
        request.session['phone'] = phone
        if profile_id is not None:
            recommended_by_profile = Profile.objects.get(id = profile_id)
            myuser.save()
            registered_user = User.objects.get(id = myuser.id)
            registered_profile = Profile.objects.get(user=registered_user)
            registered_profile.recommended_by = recommended_by_profile.user
            registered_profile.save()
        else:
            myuser.save()
        
        return redirect('otp')
    return render(request , "shop/signup.html")


def Otp(request):
    if 'phone' in request.session:
        mobile = request.session['phone']
        context = {'mobile':mobile}
        if request.method=='POST':
            otp = request.POST.get('otp')
            profile = Profile.objects.filter(Phone=mobile).first()
            if otp == profile.otp:
                return redirect('ShopHome')
            else:
                context = {'message':'Invalid OTP, Please enter correct OTP.' , 'class':'danger' , 'mobile':mobile}
                return render(request , "shop/otp.html" , context)
    else:
        context = {'message':'Your session has expired.' , 'class':'danger'}
        return render(request , "shop/otp.html" , context)
    return render(request , "shop/otp.html" , context)


def HandleLogin(request):
    if request.method == "POST":
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpass']
        user = authenticate(username = loginusername , password = loginpassword)

        if user is not None:
            login(request , user)
            messages.success(request , "Successfully Logged In")
            return redirect('ShopHome')
        else:
            messages.error(request , "Invalid credentials, please try again")
            return redirect('ShopHome')
    return render(request , "shop/login.html")


def ResendOtp(request):
    mobile = request.session['phone']
    otp = str(random.randint(1000,9999))
    profile = Profile.objects.filter(Phone=mobile).first()
    send_otp(mobile,otp)
    profile.otp = otp
    profile.save()
    return render(request , 'shop/otp.html')



def HandleLogout(request):
    logout(request)
    messages.success(request , "Successfully Logged Out")
    return redirect("ShopHome")

def MyRecommendationView(request):
    profile = Profile.objects.get(user=request.user)
    orders = Order.objects.all()
    ordered = []
    code = profile.code
    my_recs = profile.get_recommend_profile()
    for rec in my_recs:
        for order in orders:
            if str(rec.user) == order.name:
                ordered.append(rec.user)
    cash = 5*len(my_recs)
    used = profile.cash_used
    profile.cash = cash-used
    profile.save()
    context = {'my_recs':my_recs , 'code':code , 'cash':cash-used , 'ordered':ordered , 'used':used}
    return render(request , 'shop/my_recs.html' , context)


def MyOrders(request):
    myorders = Order.objects.filter(name=request.user)
    profile = Profile.objects.filter(user=request.user).first()
        
    return render(request , 'shop/myorders.html' , {'myorders':myorders , 'profile':profile})


def Orders_list(request,oid):
    order = Order.objects.filter(order_id=oid).first()
    items = json.loads(order.items_json)
    order_list = []
    product_list = []
    for item in items.values():
        product = Product.objects.filter(id=item[3]).first()
        product_list.append(product)
        order_list.append(item)
    mylist = zip(order_list , product_list)

    return render(request , 'shop/order_list.html' , {'orders':order ,'length':len(order_list) , 'mylist':mylist})

def MyAccount(request):
    profile = Profile.objects.filter(user=request.user).first()
    user = User.objects.filter(username=request.user).first()
    if request.method=="POST":
        user.username = request.POST['username']
        user.first_name = request.POST['fname']
        user.last_name = request.POST['lname']
        profile.address1 = request.POST['address1']
        profile.address2 = request.POST['address2']
        profile.state = request.POST['state']
        profile.city = request.POST['city']
        profile.pin_code = request.POST['pin_code']
        user.email = request.POST['email']
        messages.success(request , "Successfully updated")
        user.save()
        profile.save()
    return render(request , 'shop/myaccount.html' , {'profile':profile})


def Order_Verification(request):
    if request.method=='POST':
        otp = str(random.randint(1000,9999))
        request.session['otp'] = otp
        phone = request.POST['phone']
        request.session['phone'] = phone
        send_otp(phone, otp)
        return redirect('order-otp')
    return HttpResponse("Phone no. detected")

def Order_Otp(request):
    if request.method=="POST":
        otp1 = request.POST['otp']
        otp2 = request.session['otp']
        if otp1==otp2:
            status = "verified"
            request.session['status'] = status
            return redirect('Checkout')
        else:
            status = "not verified"
            request.session['status'] = status
            return render(request, 'shop/order-otp.html')
    return render(request, 'shop/order-otp.html')


