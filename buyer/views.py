import random
from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.conf import settings

from buyer.models import Buyer, Cart
from seller.models import Product
from django.http import HttpResponse

import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest



def index(request):
    try:
        user_object = Buyer.objects.get(email = request.session['email'])
        return render(request,'index.html',{'user':user_object, 'all_products': all_products })
    except:
        return render(request, 'index.html')


def contact(request):
    return render(request,'contact.html')


def about(request):
    return render(request,'about.html')


def working(request):
    return render(request,'working.html')
    
def register(request):
    if request.method == 'GET':
        return render(request,'register.html')
    else:
        try:
            Buyer.objects.get(email = request.POST['email'])
            return render(request,'register.html',{'msg':'Email is already exist'})
        except:    
            global c_otp
            c_otp = random.randrange(1000, 9999)
            global user_info
            user_info = {
                'fname' : request.POST['fname'],
                'lname' : request.POST['lname'],
                'email' : request.POST['email'],
                'password' : request.POST['password'],
                'repwd' : request.POST['repwd']
            }
            u_p = request.POST['password']
            r_p = request.POST['repwd']
            number = False
            u_alpha = False
            l_alpha = False
            special_char = False
            if u_p == r_p:
                for i in u_p:
                    if i in '0123456789':
                        number = True
                    if i.isupper():
                        u_alpha = True
                    if i.islower():
                        l_alpha = True
                    if i in '!@#$%^&*':
                        special_char = True
                if number and u_alpha and l_alpha and special_char and len(u_p)>=8:
                    subject = 'E commerce Registration'
                    message = f'Hi Your OTP is {c_otp}.'
                    email1 = request.POST['email']
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email1] )
                    return render(request, 'otp.html')
                else:
                    msg = """ Must contain at least one number and one uppercase 
                    and lowercase leter and one special symbol, 
                    and at least 8 or more characters. """
                    return render(request, 'register.html', {'msg': msg})
            else:
                msg = "Password do not match."
                return render(request, 'register.html', {'msg': msg})


def otp(request):
    if request.method == 'POST':
        user_otp = request.POST['u_otp']
        user_otp = int(user_otp)
        if c_otp == user_otp:
            Buyer.objects.create(
                passwd = user_info['password'],
                fname = user_info['fname'],
                lname = user_info['lname'],
                email = user_info['email'],
            )
            msg = 'Successfully account created!!'
            return render(request, 'register.html',{'msg':msg})
        else:
            return render(request, 'otp.html', {'msg':'OTP is wrong'})
    else:
        return render(request, 'register.html')


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        f_email = request.POST['email']
        f_pass = request.POST['password'] 
        try:
            user_object = Buyer.objects.get(email = f_email)
            if f_pass == user_object.passwd:
                request.session['email'] = f_email
                all_products = Product.objects.all()
                return render(request, 'index.html',{'user':user_object, 'all_products': all_products})
            else:
                return render(request, 'login.html', {'msg':'Wrong Password!!'})

        except:
            return render(request, 'register.html', {'msg':'Email Not Registered\nSign Up Now!!'})


def logout(request):
    try:
        del request.session['email']
        return render(request,'login.html')
    except:
        return render(request,'login.html')


def profile(request):
    if request.method == 'POST':
        new = {
            'fname' : request.POST['fname'],
            'lname' : request.POST['lname'],
            'passwd' : request.POST['password']
        }
        session_user = Buyer.objects.get(email = request.session['email'])
        session_user.fname = new['fname']
        session_user.lname = new['lname']
        session_user.passwd = new['passwd']
        if request.FILES['pic']:
            session_user.pic = request.FILES['pic']
        session_user.save()
        user_data = Buyer.objects.get(email = request.session['email'])
        return render(request, 'profile.html', {'user':user_data})
    else:
        try:
            user_data = Buyer.objects.get(email = request.session['email'])
            return render(request, 'profile.html', {'user':user_data})
        except:
            return render(request, 'login.html')


def forgot_password(request):
    if request.method == 'GET':
        return render(request, 'forgot_password.html')
    else:
        try:
            user = Buyer.objects.get(email = request.POST['email'])
            p = user.passwd
            send_mail('Forgotton Password', f'Your password is {p}.', settings.EMAIL_HOST_USER, [request.POST['email']])
            return render(request, 'forgot_password.html', {'msg':'Check your Email!!'})

        except:
            return render(request, 'register.html', {'msg':'Email Not Registered!!'})


def cart(request):
    buyer_object = Buyer.objects.get(email = request.session['email'])
    cart_data = Cart.objects.filter(buyer = buyer_object)
    total = 0
    for i in cart_data:
        total += i.product.price
    global final_total
    final_total = total + 100


    currency = 'INR'
    amount = final_total*100  # Rs. 200
 
    razorpay_order = razorpay_client.order.create(dict(amount=amount,  
                                                       currency=currency,
                                                       payment_capture='0'))
 
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'paymenthandler/'
 
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url
    context['cart_data'] = cart_data
    context['total'] = total
    context['final_total'] = final_total

    return render(request, 'cart.html', context = context)


def add_to_cart(request, pk):
    product_object = Product.objects.get(id= pk)
    buyer_object = Buyer.objects.get(email = request.session['email']) 
    Cart.objects.create(
        product = product_object,
        buyer = buyer_object
    )
    global all_products
    all_products = Product.objects.all()

    return render(request, 'index.html' , {'user':buyer_object,'all_products': all_products})


def remove_item(request, pk):
    d_product = Cart.objects.get(id = pk)
    d_product.delete()
    return redirect('cart')



#Payment Process Starts From Here

# authorize razorpay client with API Keys.
razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
 
 
# we need to csrf_exempt this url as
# POST request will be made by Razorpay
# and it won't have the csrf token.
@csrf_exempt
def paymenthandler(request):
 
    # only accept POST request.
    if request.method == "POST":
        try:
           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            # result = razorpay_client.utility.verify_payment_signature(
            #     params_dict)
            # if result is not None:
            amount = final_total * 100  # Rs. 200
            try:

                # capture the payemt
                #razorpay_client.payment.capture(payment_id, amount)

                # render success page on successful caputre of payment
                return render(request, 'paymentsuccess.html')
            except:

                # if there is an error while capturing payment.
                return render(request, 'paymentfail.html')
            
        except:
            # if we don't find the required parameters in POST data
            return HttpResponse('fail')
    else:
        #if other than POST request is made.
        return HttpResponse('method failiure')