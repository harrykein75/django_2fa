import datetime
import secrets

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, get_user_model
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from datetime import timedelta
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, now

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import json
import base64

def index(request):
    user = request.user
    return render(request, 'index.html', {'user': user})

def if_user_email_valid(request):
    user = request.user
    if not user.email:
        messages.error(request, "Email address is missing. Please contact support for assistance.")
        return redirect('login')

    if get_user_model().objects.filter(email=user.email).count() > 1:
        messages.error(request, "Multiple accounts are using the email ("+user.email+"). Please contact support to resolve this issue.")
        return redirect('login')

    try:
        validate_email(user.email)
    except ValidationError:
        messages.error(request, "The email ("+user.email+") address format is invalid. Please contact support for assistance.")
        return redirect('login')

def generate_otp():
    return str(secrets.randbelow(1000000)).zfill(6)

def send_otp_email(user_email, code, username):
    subject = 'Your 2FA Code'
    message = render_to_string('email/2fa_code.html', {'code': code, 'username': username})
    email = EmailMessage(subject, message, to=[user_email])
    email.content_subtype = "html"
    email.send()

# Encode data to Base64
def encode_to_base64(data):
    json_data = json.dumps(data)
    data_bytes = json_data.encode('utf-8')
    base64_encoded_data = base64.b64encode(data_bytes).decode('utf-8')
    return base64_encoded_data

# Decode Base64 data back to original
def decode_from_base64(encoded_data):
    decoded_bytes = base64.b64decode(encoded_data)
    json_data = decoded_bytes.decode('utf-8')
    data = json.loads(json_data)
    return data

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            if_user_email_valid(request)

            # Check if the user has already completed 2FA in the last 7 days
            twofa_data = request.COOKIES.get('2fa_data')

            if twofa_data:
                decoded_data = decode_from_base64(twofa_data)
                if decoded_data['email'] and decoded_data['last_2fa_date']:
                    last_2fa_date = datetime.datetime.fromisoformat(decoded_data['last_2fa_date'])
                    if decoded_data['email'] == user.email and (now() - last_2fa_date).days <= 7:
                        # Skip 2FA and log the user in if within the 7-day window
                        auth_login(request, user)
                        return redirect('/')  # Redirect to homepage or dashboard

            # Generate OTP and save info in session for 2FA
            code = generate_otp()
            request.session['2fa_user_id'] = user.id
            request.session['2fa_code'] = code
            request.session['2fa_code_generated_at'] = now().isoformat()

            send_otp_email(user.email, code, username)
            return redirect('two_factor')  # Show the 2FA page for OTP input

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

def two_factor_view(request):
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        return redirect('login')  # Safety check

    try:
        user = get_user_model().objects.get(id=user_id)
    except get_user_model().DoesNotExist:
        return redirect('login')

    # Process OTP verification
    if request.method == 'POST':
        code = request.POST.get('code')
        session_code = request.session.get('2fa_code')
        generated_time_str = request.session.get('2fa_code_generated_at')

        if not generated_time_str:
            messages.error(request, 'Session expired. Please login again.')
            return redirect('login')
        generated_time = parse_datetime(generated_time_str)

        if generated_time is not None and not generated_time.tzinfo:
            generated_time = make_aware(generated_time)

        if now() - generated_time > timedelta(minutes=10):
            messages.error(request, 'Code expired. Please login again.')
            return redirect('login')

        if code == session_code:
            # 2FA success! Mark the user as verified for the session.
            auth_login(request, user)

            # Set the 'last_2fa_date' in a cookie that expires in 7 days
            response = redirect('/')  # Redirect to the homepage after successful login

            last_2fa_date = now()  # Get the current time as last_2fa_date
            data = {
                "email": user.email,
                "last_2fa_date": last_2fa_date.isoformat()  # Make sure datetime is stringified (ISO format)
            }
            
            encode_data = encode_to_base64(data)
            expires = now() + datetime.timedelta(days=7)
            response.set_cookie('2fa_data', encode_data, expires=expires)

            return response
        else:
            messages.error(request, 'Invalid code. Please try again.')

    return render(request, 'accounts/two_factor.html', {'email': user.email})

def resend_2fa_code(request):
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please login again.')
        return redirect('login')

    user = get_user_model().objects.get(id=user_id)
    code = generate_otp()
    request.session['2fa_code'] = code
    request.session['2fa_code_generated_at'] = now().isoformat()

    send_otp_email(user.email, code, user.username)
    messages.success(request, 'A new verification code has been sent to your email.')
    return redirect('two_factor')

def logout_view(request):
    auth_logout(request)
    return redirect('login')
