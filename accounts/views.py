
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
import re
import uuid
# Create your views here.

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user is None:
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)  
        

        user_profile = user.profile

        if user is not None and not user_profile.email_verified:
            token = str(uuid.uuid4())
            user_profile.email_token = token
            user_profile.save()
            send_verification_email(email, token)
            messages.success(request, 'Your account is not verified. A verification email has been sent.')
            return HttpResponseRedirect(request.path_info)
        
        user = authenticate(request, username=user.username, password=password)
        if user is not None and user_profile.email_verified:
            login(request, user)
            return redirect('/accounts/dashboard/')  

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)

    return render(request ,'login.html')


def validate_email_pattern(email):
    # Regular expression to match the forbidden email patterns
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    normalized_email = email.lower()  # Convert email to lowercase
    if re.match(pattern, normalized_email):
        if '+' in normalized_email or '.' in normalized_email.split('@')[0]:
            raise ValidationError("Email pattern not allowed.")
    else:
        raise ValidationError("Invalid email address format.")
    

def signup_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        ip_address = request.META.get('REMOTE_ADDR')

            # Validate email pattern
        try:
            validate_email_pattern(email)
        except ValidationError as e:
            messages.warning(request, str(e))
            return HttpResponseRedirect(request.path_info)
        
        email = email.lower()

        if "oast.fun" in email or "oastify" in email:
            messages.warning(request, 'Temporary emails are not allowed.')
            return HttpResponseRedirect(request.path_info)

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'User with that username already exists.')
            return HttpResponseRedirect(request.path_info)
        
        if User.objects.filter(email=email).exists():
            messages.warning(request, 'User with that email already exists.')
            return HttpResponseRedirect(request.path_info)

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)

        # Generate verification token and sclearend email
        user_profile = Profile.objects.create(user = user)
        token = str(uuid.uuid4())
        user_profile.email_token = token
        user_profile.ip_address = ip_address
        user_profile.save()
        send_verification_email(email, token)
        
        messages.success(request, 'Verification token has been sent to your email.')
        return HttpResponseRedirect(request.path_info)

    return render(request ,'register.html')


@login_required
def dashboard_page(request):
    user = request.user

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Check if email is being updated
        if email and email != user.email:
            messages.warning(request, 'You cannot update you email.')
            return HttpResponseRedirect(request.path_info)

        # Update other fields
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if password:
            user.password = make_password(password)
        
        user.save()
        messages.success(request, 'Account Information updated successfully..')
        return HttpResponseRedirect(request.path_info)
    
    context = {
        'user': user
    }
    return render(request, 'dashboard.html', context)


def send_verification_email(email, email_token):
    subject = '[Gradamic] : Verify Your Email Address'
    email_from = 'Gradamic Team<{}>'.format(settings.EMAIL_HOST_USER)
    message = f"""
    <html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .message {{
            margin-bottom: 20px;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            text-decoration: none;
            border-radius: 5px;
            color: white;
        }}
        .button:hover {{
            background-color: #0056b3;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="message">
        <p>Hi there,</p>
        <p>Welcome to Gradamic!</p>
        <p>To complete your registration and start exploring our platform, <b>please verify your email address by clicking the button below:</b></p>
    </div>
    <div class="action">
        <a href="https://app.gradamic.com/accounts/verify/{email_token}" class="button" style="color:white;">Verify Email Address</a>
    </div>
    <div class="footer">
        <p>If you didn't sign up for an account with Gradamic, you can safely ignore this email.</p>
        <p>For any assistance, feel free to contact our support team at <a href="mailto:gradamic.info@gmail.com">gradamic.info@gmail.com</a>.</p>
        <p>Best regards,<br>Gradamic Team</p>
    </div>
</div>
</body>
</html>
    """
    send_mail(subject, '', email_from, [email], html_message=message)



def verify_email(request, token):
    profile = get_object_or_404(Profile, email_token=token)
    profile.email_verified = True
    profile.save()
    messages.success(request, 'Email Verified successfully..!')
    return redirect('/accounts/dashboard/')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error_message': 'No user with this email exists.'})

        temp_password = get_random_string(length=10)
        user.set_password(temp_password)
        user.save()
        send_password_email(email, temp_password)
        messages.success(request, 'Please check your email to reset your password.')
        return HttpResponseRedirect(request.path_info)

    return render(request, 'forgot_password.html')



def send_password_email(email, temp_password):
    subject = '[Gradamic] : Reset your gradamic password.'
    email_from = 'Gradamic Team<{}>'.format(settings.EMAIL_HOST_USER)
    message = f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Arial, sans-serif;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .message {{
            margin-bottom: 20px;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #007bff;
            text-decoration: none;
            border-radius: 5px;
            color: white;
        }}
        .button:hover {{
            background-color: #0056b3;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
<div class="container">
    <div class="message">
    <p>Hi there,</p>
    <p>We received a request to reset your password for your Gradamic account.</p>
    <p>Your temporary password is: <b>{temp_password}</b></p>
    <p>Please use this temporary password to log in and reset your password.</p>
</div>
<div class="footer">
    <p>If you didn't request a password reset, you can safely ignore this email.</p>
    <p>For any assistance, feel free to contact our support team at <a href="mailto:gradamic.info@gmail.com">gradamic.info@gmail.com</a>.</p>
    <p>Best regards,<br>Gradamic Team</p>
</div>
</div>
</body>
</html>
    """
    send_mail(subject, '', email_from, [email], html_message=message)



def logout_page(request):
    logout(request)
    
    return redirect('/')  