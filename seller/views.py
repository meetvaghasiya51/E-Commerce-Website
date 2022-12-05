from random import random
from xml.dom.minidom import parseString
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from seller.models import Product, Seller
import random


# Create your views here.
def seller_index(request):
    return render(request,'seller_index.html')


def seller_contact(request):
    return render(request,'seller_contact.html')


def seller_about(request):
    return render(request,'seller_about.html')


def seller_register(request):
    if request.method == 'GET':
        return render(request,'seller_register.html')
    else:
        try:
            Seller.objects.get(email = request.POST['email'])
            return render(request,'seller_register.html',{'msg':'Email is already exist'})
        except:    
            global c_otp
            c_otp = random.randrange(1000, 9999)
            global user_info
            user_info = {
                'first_name' : request.POST['first_name'],
                'last_name' : request.POST['last_name'],
                'email' : request.POST['email'],
                'gst_number' : request.POST['gst_number'],
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
                    subject = 'E-commerce Seller Registration'
                    message = f'Hi Your OTP is {c_otp}.'
                    email1 = request.POST['email']
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email1] )
                    return render(request, 'seller_otp.html')
                else:
                    msg = """ Must contain at least one number and one uppercase 
                    and lowercase leter and one special symbol, 
                    and at least 8 or more characters. """
                    return render(request, 'seller_register.html', {'msg': msg})
            else:
                msg = "Password do not match."
                return render(request, 'seller_register.html', {'msg': msg})


def seller_otp(request):
    if request.method == 'POST':
        user_otp = request.POST['u_otp']
        user_otp = int(user_otp)
        if c_otp == user_otp:
            Seller.objects.create(
                passwd = user_info['password'],
                first_name = user_info['first_name'],
                last_name = user_info['last_name'],
                email = user_info['email'],
            )
            msg = 'Successfully account created!!'
            return render(request, 'seller_register.html',{'msg':msg})
        else:
            return render(request, 'seller_otp.html', {'msg':'OTP is wrong'})
    else:
        return render(request, 'seller_register.html') 


def seller_login(request):
    if request.method == 'GET':
        return render(request,'seller_login.html')
    else:
        f_email = request.POST['email']
        f_pass = request.POST['password']
        try:
            user_object = Seller.objects.get(email = f_email)
            if f_pass == user_object.passwd:
                request.session['email'] = f_email
                return render(request, 'seller_index.html',{'user':user_object})
            else:
                return render(request, 'seller_login.html',{'msg':'Wrong Password'})
        except:
            return render(request, 'seller_register.html',{'msg':'Email Not Registred\n Sing Up Now!!'})


def seller_logout(request):
    try:
        del request.session['email']
        return render(request,'seller_login.html')
    except:
        return render(request,'seller_login.html')


def add_product(request):
    if request.method == 'POST':
        seller_object = Seller.objects.get(email = request.session['email'])
        Product.objects.create(
            name = request.POST['name'],
            description = request.POST['description'],
            price = request.POST['price'],
            seller = seller_object,
            quantity = request.POST['quantity'],
            pic = request.FILES['pic']
        )
        return render(request, 'add_product.html')
    else:
        return render(request, 'add_product.html')


def my_product(request):
    seller_object = Seller.objects.get(email = request.session['email'])
    seller_product = Product.objects.filter(seller = seller_object)
    return render(request, 'my_product.html', {'my_product': seller_product}) 