from django.views.generic import View
from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from shop.settings import EMAIL_HOST_USER
from django.contrib import messages, auth
from .models import *
from django.utils import timezone
from datetime import timedelta
from .forms import VendorApplyForm

# Create your views here.

User = get_user_model()  # Get the active user model

class Signup(View):
    def get(self, request):
        return render(request, 'user/signup.html')

    def post(self, request):
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        if User.objects.filter(email=email).exists():
            return HttpResponse('Email already exists')
        if User.objects.filter(username=username).exists():
            return HttpResponse('Username already exists')

        user = User.objects.create_user(email=email, username=username, first_name=first_name, last_name=last_name)

        generate_verification = random.randint(100000, 999999)
        user.otp = generate_verification
        user.otp_created_at = timezone.now()  # Store the timestamp when OTP was generated
        user.save()

        subject = "OTP Verification"
        body = f"Your verification code is: {generate_verification}"
        from_email = EMAIL_HOST_USER
        to_email = email
        send_now = send_mail(subject, body, from_email, [to_email])
        
        if send_now:
            messages.success(request, 'Successfully sent OTP. Verify your email here.')
            return redirect('verifyit')

        return render(request, 'user/signup.html')


from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend

class Verify(View):
    def get(self, request):
        return render(request, 'user/verify.html')

    def post(self, request):
        entered_otp = request.POST['otp']
        try:
            user = User.objects.get(otp=entered_otp, is_email_verified=False)
            if user.otp_created_at >= timezone.now() - timedelta(minutes=5):
                user.is_email_verified = True
                user.save()
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Success, You are logged in. Create your account here.')
                return redirect('registerit')
            else:
                return HttpResponse('The verification code has expired. Please try again.')
        except User.DoesNotExist:
            return HttpResponse('Invalid verification code.')




# class Verify(View):
#     def get(self, request):
#         return render(request, 'user/verify.html')

#     def post(self, request):
#         entered_otp = request.POST['otp']
#         try:
#             user = User.objects.get(otp=entered_otp, is_email_verified=False)
#             if user.otp_created_at >= timezone.now() - timedelta(minutes=5):
#                 user.is_email_verified = True
#                 user.save()
#                 login(request, user)
#                 messages.success(request, 'Success, You are logged in. Create your account here.')
#                 return redirect('registerit')
#             else:
#                 return HttpResponse('The verification code has expired. Please try again.')
#         except User.DoesNotExist:
#             return HttpResponse('Invalid verification code.')




class Register(View):
    def get(self, request):
        return render(request, 'user/page-register.html')
    
    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'User not authenticated')
            return HttpResponse('user_not_authenticated') 
        user = request.user
        entered_username = request.POST.get('username')
        entered_email = request.POST.get('email').lower().strip()
        
        if entered_username != user.username:
            return HttpResponse('username_mismatch')
        
        if entered_email == user.email.lower():
            return HttpResponse('email_mismatch')

        password = request.POST.get('password')
        confirm_password = request.POST.get('password')
        if password and confirm_password:
            if password == confirm_password:
                user.set_password(password)
            else:
                messages.error(request, 'Password mismatch')
                return HttpResponse('password_mismatch')  

        # Update vendor status if box is chosen in the form
        is_vendor = request.POST.get('is_vendor') == 'on'
        if is_vendor:
            user.is_vendor = True  # Set to False if wish to restrict access until approved
            user.vendor_application_status = 'pending'
            user.save()
            login(request, user)
            return redirect('apply') 
        else:
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful')
            # return redirect(request, 'account')
            return render(request, 'dash/page-account.html')
        



class UserAccount(View):
    def get(self, request):
        return render(request, 'dash/page-account.html')

    def post(self, request):
        pass    
        


class VendorApply(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'User not authenticated')
            return redirect('login')
        
        form = VendorApplyForm()  # Create an empty form instance
        return render(request, 'dash/vendor-apply.html', {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'User not authenticated')
            return redirect('login')

        # Retrieve the logged-in user
        user = request.user

        # Initialize the form with the POST data
        form = VendorApplyForm(request.POST)

        if form.is_valid():
            # Update the user's fields with the form data
            user.business_name = form.cleaned_data['business_name']
            user.location = form.cleaned_data['location']
            user.registration_no = form.cleaned_data['registration_no']
            user.registering_body = form.cleaned_data['registering_body']
            user.business_description = form.cleaned_data['business_description']
            user.website_url = form.cleaned_data['website_url']

            # Update user's vendor status
            is_vendor = form.cleaned_data.get('is_vendor')
            if is_vendor:
                user.is_vendor = False
                user.vendor_application_status = 'pending'

            # Save the user instance
            user.save()

            return redirect('account')
        else:
            messages.error(request, 'Please fill all required fields')
            return render(request, 'dash/vendor-apply.html', {'form': form})


class VendorPage(View):
    def get(self, request):
        return render(request, 'dash/vendor-dashboard.html')
    
    def post(self, request):
        pass



class Home(View):
    def get(self, request):
        return render(request, 'index.html')



class Login(View):
    def get(self, request):
        return render(request, 'user/page-login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Retrieve the user by email
            user = User.objects.get(email=email)

            # Check if the user is a superuser
            if user.is_superuser and user.check_password(password):
                # Log in the superuser if password match
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Welcome back')
                return redirect('account')
            if not password:
                messages.error(request, 'Invalid input')
                return redirect('login')

            else:
                # For regular users, check email verification
                user = User.objects.filter(is_email_verified=True).first()

                if password and email:
                    user = authenticate(request, email=email, password=password)
                    if user:
                        login(request, user)
                        messages.success(request, 'Welcome back!')
                        if user.is_vendor:
                            messages.success(request, 'Welcome back, Vendor!')
                            return redirect('vendor')
                        else:
                            return redirect('account')
                    else:
                        messages.error(request, 'Invalid input')
                        return redirect('login')    

        except User.DoesNotExist:
            messages.success(request, 'Sign up to get started')
            return redirect('signup')


def Logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')



#  class Register(View):

#     def get(self, request):
        
#         return render(request, 'user/page-register.html')

#     def post(self, request):
#         # Ensure the user is logged in
#         if not request.user.is_authenticated:
#             # return HttpResponse('user_not_authenticated')
#             messages.error(request, 'user_not_authenticated')

#         # Retrieve the logged-in user
#         user = request.user

#         # Retrieve the username entered in the form
#         entered_username = request.POST.get('username')
#         entered_email = request.POST.get('email')

#         # Check if the entered username matches the username of the logged-in user
#         if entered_username != user.username:
#             return HttpResponse('username_mismatch')
#             # messages.error(request, 'username mismatch')
        
#         if entered_email != user.email:
#             return HttpResponse('email_mismatch')
#             # messages.error(request, 'email mismatch')

#         # Check if passwords match
#         password = request.POST['password']
#         confirm_password = request.POST['password2']
#         if password and password == confirm_password:
#             user.set_password(password)

#         # Update vendor status if the field is present in the form
#         is_vendor = request.POST.get('is_vendor') == 'on'
#         if is_vendor:
#             user.is_vendor = False
#             user.vendor_application_status = 'pending'
            
#             user.save()
#             # Log the user in
#             login(request, user)
#             # Redirect to the vendor application page
#             return redirect('vendor_application_url')  # Replace with your actual vendor application URL
#         else:
#             user.save()
#             # Log the user in
#             login(request, user)
#             # Render the user dashboard with a success message
#             messages.success(request, 'Registration successful')
#             return render(request, 'user_dashboard.html')    


#         # Redirect to the dashboard page
#         # messages.success(request, 'Welcome to you Dashboard, proceed to update your profile')




# def signin_view(request):
#     #This is for signing in a user
#     if request.method == "POST":
#         email = request.POST["email"]
#         password = request.POST["password"]
#         user = auth.authenticate(email=email, password=password)
#         if user is not None:
#             auth.login(request, user)
#             return redirect("success")
            
#         else:
#             messages.error(
#                 request,
#                 "Invalid credentials or User doesn't exists",
#                 fail_silently=True, extra_tags='warning'
#             )
#     return render(request, "sign_in.html")
# def success_view(request):
#     """This is for displaying success page"""
#     return render(request, "success_page.html")
# def signup_view(request):
#     """This is for signing in a user"""
#     if request.method == "POST":
#         first_name = request.POST["first_name"]
#         email = request.POST["email"]
#         password = request.POST["password"]
#         if CustomUser.objects.filter(email=email).exists():  # checks if an email exists
#             messages.error(request, f"The email {email} exists", fail_silently=True)
            
#         else:
#             CustomUser.objects.create_user(
#                 first_name=first_name, email=email, password=password
#             )
#             user = auth.authenticate(email=email, password=password)
#             auth.login(request, user)
#             return redirect("success")
#     return render(request, "sign_up.html")
# def logout_view(request):
#     """This is for logging out a user"""
#     auth.logout(request)
#     return redirect("sign-in")

