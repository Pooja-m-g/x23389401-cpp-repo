from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.http import HttpResponseRedirect,HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.conf import settings

def home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})


#for showing login button for admin(by sumit)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')


def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return HttpResponseRedirect('customerlogin')
    return render(request,'ecom/customersignup.html',context=mydict)

#-----------for checking user iscustomer
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()



#---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,CUSTOMER
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-home')
    else:
        return redirect('admin-dashboard')

#---------------------------------------------------------------------------------
#------------------------ ADMIN RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    # for cards on dashboard
    customercount=models.Customer.objects.all().count()
    productcount=models.Product.objects.all().count()
    ordercount=models.Orders.objects.all().count()

    # for recent order tables
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)

    mydict={
    'customercount':customercount,
    'productcount':productcount,
    'ordercount':ordercount,
    'data':zip(ordered_products,ordered_bys,orders),
    }
    return render(request,'ecom/admin_dashboard.html',context=mydict)


# admin view customer table
@login_required(login_url='adminlogin')
def view_customer_view(request):
    customers=models.Customer.objects.all()
    return render(request,'ecom/view_customer.html',{'customers':customers})

# admin delete customer
@login_required(login_url='adminlogin')
def delete_customer_view(request,pk):
    customer=models.Customer.objects.get(id=pk)
    user=models.User.objects.get(id=customer.user_id)
    user.delete()
    customer.delete()
    return redirect('view-customer')


# @login_required(login_url='adminlogin')
# def update_customer_view(request,pk):
#     customer=models.Customer.objects.get(id=pk)
#     user=models.User.objects.get(id=customer.user_id)
#     userForm=forms.CustomerUserForm(instance=user)
#     customerForm=forms.CustomerForm(request.FILES,instance=customer)
#     mydict={'userForm':userForm,'customerForm':customerForm}
#     if request.method=='POST':
#         userForm=forms.CustomerUserForm(request.POST,instance=user)
#         customerForm=forms.CustomerForm(request.POST,instance=customer)
#         if userForm.is_valid() and customerForm.is_valid():
#             user=userForm.save()
#             user.set_password(user.password)
#             user.save()
#             customerForm.save()
#             return redirect('view-customer')
#     return render(request,'ecom/admin_update_customer.html',context=mydict)









@login_required(login_url='adminlogin')
def update_customer_view(request, pk):
    customer = models.Customer.objects.get(id=pk)
    user = models.User.objects.get(id=customer.user_id)
    
    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST, instance=user)
        customerForm = forms.CustomerForm(request.POST, request.FILES, instance=customer)
        
        if userForm.is_valid() and customerForm.is_valid():
            # Save user
            user = userForm.save(commit=False)
            if userForm.cleaned_data.get('password'):
                user.set_password(userForm.cleaned_data.get('password'))
            user.save()
            
            # Save customer with image
            customer = customerForm.save(commit=False)
            if 'profile_pic' in request.FILES:
                customer.profile_pic = request.FILES['profile_pic']
            customer.save()
            
            return redirect('view-customer')
    else:
        userForm = forms.CustomerUserForm(instance=user)
        customerForm = forms.CustomerForm(instance=customer)
    
    mydict = {
        'userForm': userForm,
        'customerForm': customerForm,
        'customer': customer
    }
    return render(request, 'ecom/admin_update_customer.html', context=mydict)











# admin view the product
@login_required(login_url='adminlogin')
def admin_products_view(request):
    products=models.Product.objects.all()
    return render(request,'ecom/admin_products.html',{'products':products})

""" 
# admin add product by clicking on floating button
@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm=forms.ProductForm()
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            productForm.save()
        return HttpResponseRedirect('admin-products')
    return render(request,'ecom/admin_add_products.html',{'productForm':productForm})


 """

import os
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import ProductForm
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

def upload_to_s3(file_path, object_name=None):

    bucket_name = "x23389401-s3"
    if object_name is None:
        object_name = os.path.basename(file_path)

    s3_client = boto3.client('s3', region_name="us-east-1")

    try:
        with open(file_path, "rb") as file_data:
            s3_client.upload_fileobj(file_data, bucket_name, object_name)
        print(f" Successfully uploaded {object_name} to {bucket_name}")
        return True
    except FileNotFoundError:
        print(f" The file {file_path} was not found.")
        return False
    except NoCredentialsError:
        print(" AWS credentials not available.")
        return False
    except PartialCredentialsError:
        print(" Incomplete AWS credentials provided.")
        return False
    except Exception as e:
        print(f" An unexpected error occurred: {e}")
        return False



from django.conf import settings
import os

@login_required(login_url='adminlogin')
def admin_add_product_view(request):
    productForm = forms.ProductForm()
    if request.method == 'POST':
        productForm = forms.ProductForm(request.POST, request.FILES)
        if productForm.is_valid():
            product = productForm.save()

            if product.product_image:  # Assuming model field is named `product_image`
                local_file_path = os.path.join(settings.MEDIA_ROOT, product.product_image.name)
                upload_to_s3(local_file_path, f"product_image/{product.product_image.name}")

        return HttpResponseRedirect('admin-products')
    return render(request, 'ecom/admin_add_products.html', {'productForm': productForm})


@login_required(login_url='adminlogin')
def delete_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    product.delete()
    return redirect('admin-products')


@login_required(login_url='adminlogin')
def update_product_view(request,pk):
    product=models.Product.objects.get(id=pk)
    productForm=forms.ProductForm(instance=product)
    if request.method=='POST':
        productForm=forms.ProductForm(request.POST,request.FILES,instance=product)
        if productForm.is_valid():
            productForm.save()
            return redirect('admin-products')
    return render(request,'ecom/admin_update_product.html',{'productForm':productForm})


@login_required(login_url='adminlogin')
def admin_view_booking_view(request):
    orders=models.Orders.objects.all()
    ordered_products=[]
    ordered_bys=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_by=models.Customer.objects.all().filter(id = order.customer.id)
        ordered_products.append(ordered_product)
        ordered_bys.append(ordered_by)
    return render(request,'ecom/admin_view_booking.html',{'data':zip(ordered_products,ordered_bys,orders)})


@login_required(login_url='adminlogin')
def delete_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    order.delete()
    return redirect('admin-view-booking')

# for changing status of order (pending,delivered...)
@login_required(login_url='adminlogin')
def update_order_view(request,pk):
    order=models.Orders.objects.get(id=pk)
    orderForm=forms.OrderForm(instance=order)
    if request.method=='POST':
        orderForm=forms.OrderForm(request.POST,instance=order)
        if orderForm.is_valid():
            orderForm.save()
            return redirect('admin-view-booking')
    return render(request,'ecom/update_order.html',{'orderForm':orderForm})


# admin view the feedback
@login_required(login_url='adminlogin')
def view_feedback_view(request):
    feedbacks=models.Feedback.objects.all().order_by('-id')
    return render(request,'ecom/view_feedback.html',{'feedbacks':feedbacks})



#---------------------------------------------------------------------------------
#------------------------ PUBLIC CUSTOMER RELATED VIEWS START ---------------------
#---------------------------------------------------------------------------------
def search_view(request):
    # whatever user write in search box we get in query
    query = request.GET['query']
    products=models.Product.objects.all().filter(name__icontains=query)
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'ecom/customer_home.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})
    return render(request,'ecom/index.html',{'products':products,'word':word,'product_count_in_cart':product_count_in_cart})


# any one can add product to cart, no need of signin
def add_to_cart_view(request,pk):
    products=models.Product.objects.all()

    #for cart counter, fetching products ids added by customer from cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        #product_count_in_cart=len(set(counter))
        product_count_in_cart = len(counter)
    else:
        product_count_in_cart=1

    response = render(request, 'ecom/index.html',{'products':products,'product_count_in_cart':product_count_in_cart})
    #response = render(request, 'ecom/index.html', {'products': products, 'product_count_in_cart': product_count_in_cart})

    #adding product id to cookies
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids=="":
            product_ids=str(pk)
        else:
            product_ids=product_ids+"|"+str(pk)
        response.set_cookie('product_ids', product_ids)
    else:
        response.set_cookie('product_ids', pk)

    product=models.Product.objects.get(id=pk)
    messages.info(request, product.name + ' added to cart successfully!')

    return response




""" 

# for checkout of cart
def cart_view(request):
    #for cart counter
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        #product_count_in_cart=len(set(counter))
        product_count_in_cart = len(counter) 
    else:
        product_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    products=None
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)

            #for total price shown in cart
            for p in products:
                total=total+p.price
    return render(request,'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})

 """

from collections import Counter

def cart_view(request):
    product_count_in_cart = 0
    products = []
    total = 0

    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids:
            product_id_list = product_ids.split('|')
            product_count_in_cart = len(product_id_list)

            # Count quantities of each product
            id_counts = Counter(product_id_list)

            # Fetch unique product objects
            unique_ids = list(id_counts.keys())
            products_queryset = models.Product.objects.filter(id__in=unique_ids)

            # Multiply each product price by its quantity
            for product in products_queryset:
                quantity = id_counts[str(product.id)]
                total += product.price * quantity

                # Attach quantity to each product for the template
                product.quantity = quantity
                products.append(product)

    return render(request, 'ecom/cart.html', {
        'products': products,
        'total': total,
        'product_count_in_cart': product_count_in_cart
    })


def remove_from_cart_view(request,pk):
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        product_id_in_cart=product_ids.split('|')
        product_id_in_cart=list(set(product_id_in_cart))
        product_id_in_cart.remove(str(pk))
        products=models.Product.objects.all().filter(id__in = product_id_in_cart)
        #for total price shown in cart after removing product
        for p in products:
            total=total+p.price

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(product_id_in_cart)):
            if i==0:
                value=value+product_id_in_cart[0]
            else:
                value=value+"|"+product_id_in_cart[i]
        response = render(request, 'ecom/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
        if value=="":
            response.delete_cookie('product_ids')
        response.set_cookie('product_ids',value)
        return response


def send_feedback_view(request):
    feedbackForm=forms.FeedbackForm()
    if request.method == 'POST':
        feedbackForm = forms.FeedbackForm(request.POST)
        if feedbackForm.is_valid():
            feedbackForm.save()
            return render(request, 'ecom/feedback_sent.html')
    return render(request, 'ecom/send_feedback.html', {'feedbackForm':feedbackForm})


#---------------------------------------------------------------------------------
#------------------------ CUSTOMER RELATED VIEWS START ------------------------------
#---------------------------------------------------------------------------------
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_home_view(request):
    products=models.Product.objects.all()
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        product_count_in_cart=len(set(counter))
    else:
        product_count_in_cart=0
    return render(request,'ecom/customer_home.html',{'products':products,'product_count_in_cart':product_count_in_cart})

""" 

# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    # if there is no product in cart we will not show address form
    product_in_cart=False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart=True
    #for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter=product_ids.split('|')
        #product_count_in_cart=len(set(counter))
        product_count_in_cart=len(counter)
    else:
        product_count_in_cart=0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # here we are taking address, email, mobile at time of order placement
            # we are not taking it from customer account table because
            # these thing can be changes
            email = addressForm.cleaned_data['Email']
            mobile=addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']
            #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
            total=0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_in_cart=product_ids.split('|')
                    products=models.Product.objects.all().filter(id__in = product_id_in_cart)
                    for p in products:
                        total=total+p.price

            response = render(request, 'ecom/payment.html',{'total':total})
            response.set_cookie('email',email)
            response.set_cookie('mobile',mobile)
            response.set_cookie('address',address)
            return response
    return render(request,'ecom/customer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})


 """





from collections import Counter
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import forms, models  # ensure your forms and models are properly imported

# shipment address before placing order
@login_required(login_url='customerlogin')
def customer_address_view(request):
    # this is for checking whether product is present in cart or not
    product_in_cart = False
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_in_cart = True

    # for counter in cart
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        counter = product_ids.split('|')
        product_count_in_cart = len(counter)
    else:
        product_count_in_cart = 0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # Get form data
            email = addressForm.cleaned_data['Email']
            mobile = addressForm.cleaned_data['Mobile']
            address = addressForm.cleaned_data['Address']

            # Calculate total price considering quantity
            total = 0
            if 'product_ids' in request.COOKIES:
                product_ids = request.COOKIES['product_ids']
                if product_ids != "":
                    product_id_list = product_ids.split('|')
                    product_counter = Counter(product_id_list)  # quantity of each product
                    product_ids_unique = list(product_counter.keys())
                    products = models.Product.objects.filter(id__in=product_ids_unique)
                    for product in products:
                        quantity = product_counter[str(product.id)]
                        total += product.price * quantity

            # Pass total to payment page
            response = render(request, 'ecom/payment.html', {
                'total': total
            })
            response.set_cookie('email', email)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response

    return render(request, 'ecom/customer_address.html', {
        'addressForm': addressForm,
        'product_in_cart': product_in_cart,
        'product_count_in_cart': product_count_in_cart
    })





""" 
# here we are just directing to this view...actually we have to check whther payment is successful or not
#then only this view should be accessed
@login_required(login_url='customerlogin')
def payment_success_view(request):
    # Here we will place order | after successful payment
    # we will fetch customer  mobile, address, Email
    # we will fetch product id from cookies then respective details from db
    # then we will create order objects and store in db
    # after that we will delete cookies because after order placed...cart should be empty
    customer=models.Customer.objects.get(user_id=request.user.id)
    products=None
    email=None
    mobile=None
    address=None
    if 'product_ids' in request.COOKIES:
        product_ids = request.COOKIES['product_ids']
        if product_ids != "":
            product_id_in_cart=product_ids.split('|')
            products=models.Product.objects.all().filter(id__in = product_id_in_cart)
            # Here we get products list that will be ordered by one customer at a time

    # these things can be change so accessing at the time of order...
    if 'email' in request.COOKIES:
        email=request.COOKIES['email']
    if 'mobile' in request.COOKIES:
        mobile=request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address=request.COOKIES['address']

    # here we are placing number of orders as much there is a products
    # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
    # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
    for product in products:
        models.Orders.objects.get_or_create(customer=customer,product=product,status='Pending',email=email,mobile=mobile,address=address)

    # after order placed cookies should be deleted
    response = render(request,'ecom/payment_success.html')
    response.delete_cookie('product_ids')
    response.delete_cookie('email')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response
 """





import requests
import json
from django.http import JsonResponse


def sns_email_send(subject, message,name, product, email, phone):
    SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:721294956586:x23389401-sns"
    
    full_message = f"""New Order details:\n Customer Name: {name}\n Product: {product}\n Email: {email}\n Phone: {phone}\n Message: {message}\n
    """

    try:
        # Use the correct region (eu-west-2)
        sns_client = boto3.client("sns", region_name="us-east-1",)  
        
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=full_message,
            Subject=subject
        )
        
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


from payment_date_time import get_current_datetime




import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Import your models
from ecom import models


def get_current_datetime():
    """Get current formatted datetime"""
    return datetime.now().strftime('%B %d, %Y %I:%M %p')


@login_required(login_url='customerlogin')
def payment_success_view(request):
    """
    Handle successful payment and send order confirmation email via Lambda
    """
    try:
        customer = models.Customer.objects.get(user_id=request.user.id)
        products = None
        email = None
        mobile = None
        address = None

        # Get products from cookies
        if 'product_ids' in request.COOKIES:
            product_ids = request.COOKIES['product_ids']
            if product_ids != "":
                product_id_in_cart = product_ids.split('|')
                products = models.Product.objects.filter(id__in=product_id_in_cart)

        # Get customer details from cookies
        if 'email' in request.COOKIES:
            email = request.COOKIES['email']
        if 'mobile' in request.COOKIES:
            mobile = request.COOKIES['mobile']
        if 'address' in request.COOKIES:
            address = request.COOKIES['address']

        # Validate required data
        if not products:
            logger.error("No products found in cart")
            return redirect('customer-home')

        if not email:
            logger.error("No email found in cookies")
            return redirect('customer-home')

        product_names = []
        total_amount = 0

        # Create orders
        for product in products:
            models.Orders.objects.get_or_create(
                customer=customer,
                product=product,
                status='Pending',
                email=email,
                mobile=mobile,
                address=address
            )
            product_names.append(product.name)
            total_amount += product.price

        # Generate Order ID
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d')}-{str(int(datetime.now().timestamp()))[-6:]}"

        # FIXED: Get customer name correctly
        # If get_name is a method, call it: customer.get_name()
        # If get_name is a property, use: customer.get_name
        # Try both approaches
        try:
            customer_name = customer.get_name()  # Try as method
        except TypeError:
            customer_name = customer.get_name  # Try as property/attribute
        
        logger.info(f"Customer name: {customer_name}")

        # Call Lambda via API Gateway to send email
        email_sent = lambda_send_smtp_email(
            customer_name=customer_name,
            customer_email=email,
            admin_email=getattr(settings, 'ADMIN_EMAIL', 'admin@foodhouse.com'),
            order_id=order_id,
            products=", ".join(product_names),
            total_amount=str(total_amount),
            phone=mobile,
            address=address
        )

        if email_sent:
            logger.info(f"Email sent successfully for order {order_id}")
        else:
            logger.warning(f"Email sending failed for order {order_id}")

        payment_date_time = get_current_datetime()

        # Clear cookies
        response = render(request, 'ecom/payment_success.html', {
            'payment_date_time': payment_date_time,
            'order_id': order_id,
            'email_sent': email_sent
        })
        response.delete_cookie('product_ids')
        response.delete_cookie('email')
        response.delete_cookie('mobile')
        response.delete_cookie('address')
        
        return response

    except models.Customer.DoesNotExist:
        logger.error("Customer not found for user: %s", request.user.id)
        return redirect('customerlogin')
    
    except Exception as e:
        logger.error(f"Error in payment_success_view: {str(e)}")
        return redirect('customer-home')


def lambda_send_smtp_email(customer_name, customer_email, admin_email, 
                               order_id, products, total_amount, phone, address):
    """
    Call Lambda function via API Gateway to send order confirmation emails
    """
    try:
        lambda_api_url = getattr(settings, 'LAMBDA_EMAIL_API_URL', None)
        
        if not lambda_api_url:
            lambda_api_url = "https://mcttxgv2za.execute-api.us-east-1.amazonaws.com/default/x23389401-lambda"
        
        # Prepare payload
        payload = {
            "customer_email": customer_email,
            "admin_email": admin_email,
            "customer_name": customer_name,
            "order_id": order_id,
            "products": products,
            "total_amount": total_amount,
            "phone": phone,
            "address": address
        }

        logger.info(f"Calling Lambda API for order {order_id}")
        logger.info(f"Payload: {json.dumps(payload)}")
        logger.info(f"API URL: {lambda_api_url}")

        # Call API Gateway with explicit timeout
        response = requests.post(
            lambda_api_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )

        logger.info(f"Response Status Code: {response.status_code}")
        logger.info(f"Response Body: {response.text[:500]}")  # Log first 500 chars

        # Check response
        if response.status_code == 200:
            try:
                response_data = response.json()
                logger.info(f"Response JSON: {response_data}")
                
                # Check for success in different response formats
                if response_data.get('success') or response_data.get('customer_email_sent'):
                    logger.info(f"Lambda email sent successfully for {customer_email}")
                    return True
                else:
                    logger.error(f"Lambda returned error: {response_data}")
                    return False
            except json.JSONDecodeError:
                # If response is not JSON, check if it's a success message
                if '"success":true' in response.text or '"success": true' in response.text:
                    logger.info("Lambda email sent successfully (parsed from text)")
                    return True
                logger.error(f"Invalid JSON response from Lambda: {response.text[:200]}")
                return False
        else:
            logger.error(f"Lambda API returned status: {response.status_code}")
            logger.error(f"Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        logger.error("Timeout while calling Lambda API")
        return False
    
    except requests.exceptions.ConnectionError:
        logger.error("Connection error while calling Lambda API")
        return False
    
    except Exception as e:
        logger.error(f"Error calling Lambda: {str(e)}")
        return False










@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_order_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    orders=models.Orders.objects.all().filter(customer_id = customer)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.product.id)
        ordered_products.append(ordered_product)

    return render(request,'ecom/my_order.html',{'data':zip(ordered_products,orders)})






from invoice_pdf_lib.pdf_invoice import create_invoice_pdf, get_invoice_number_from_lambda, generate_invoice_number

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def download_invoice_view(request, orderID, productID):
    """
    View to download invoice as PDF
    """
    try:
        order = models.Orders.objects.get(id=orderID)
        product = models.Product.objects.get(id=productID)
        
        # Get invoice number
        invoice_no = get_invoice_number_from_lambda()
        
        # Get customer name
        customer_name = request.user.get_full_name() or request.user.username
        
        # Prepare data for invoice
        invoice_data = {
            'invoice_no': invoice_no,
            'order_date': order.order_date.strftime('%B %d, %Y %I:%M %p'),
            'customer_name': customer_name,
            'customer_email': order.email,
            'customer_mobile': order.mobile,
            'shipment_address': order.address,
            'order_status': order.status,
            'product_name': product.name,
            'product_price': str(product.price),
            'product_description': product.description,
        }
        
        # Generate PDF
        pdf_content = create_invoice_pdf(invoice_data)
        
        # Return as PDF response
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{invoice_no}.pdf"'
        return response
        
    except models.Orders.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except models.Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error generating invoice: {str(e)}", status=500)


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def preview_invoice_view(request, orderID, productID):
    """
    Preview invoice in HTML before downloading
    """
    try:
        order = models.Orders.objects.get(id=orderID)
        product = models.Product.objects.get(id=productID)
        
        invoice_no = get_invoice_number_from_lambda()
        
        context = {
            'invoice_no': invoice_no,
            'order_date': order.order_date.strftime('%B %d, %Y %I:%M %p'),
            'customer_name': request.user.get_full_name() or request.user.username,
            'customer_email': order.email,
            'customer_mobile': order.mobile,
            'shipment_address': order.address,
            'order_status': order.status,
            'product_name': product.name,
            'product_price': product.price,
            'product_description': product.description,
        }
        return render(request, 'ecom/invoice_preview.html', context)
        
    except models.Orders.DoesNotExist:
        return HttpResponse("Order not found", status=404)
    except models.Product.DoesNotExist:
        return HttpResponse("Product not found", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)








@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def my_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'ecom/my_profile.html',{'customer':customer})


@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('my-profile')
    return render(request,'ecom/edit_profile.html',context=mydict)

