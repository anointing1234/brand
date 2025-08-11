from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from pypaystack2 import Paystack
import uuid
import requests
from django.http import JsonResponse
import logging
import re
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.conf import settings




logger = logging.getLogger(__name__)
# Initialize Paystack
paystack = Paystack(settings.PAYSTACK_SECRET_KEY)

def home(request):
    return render(request, 'index.html')

def contact(request):
    return render(request, 'contact-us.html')



def process_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        plan = data.get('plan')

        # Format message
        message = f"""
        📚 NEW BOOK ORDER – I Am a Brand

        🔹 Email Address: {email}
        🔹 Selected Plan: {plan}

        Please follow up with this customer for confirmation and delivery.

        Regards,
        I Am a Brand Website
        """

        send_mail(
            subject='📘 New Book Order – I Am a Brand',
            message=message,
            from_email=settings.ADMIN_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success'})

    
def send_contact_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        message = data.get('message')

        formatted_message = f"""
        📩 NEW CONTACT MESSAGE – I Am a Brand Website

        🔹 Name: {name}
        🔹 Email: {email}
        🔹 Phone: {phone}

        💬 Message:
        {message}

        Please respond to the user's inquiry promptly.

        Regards,
        I Am a Brand Website
        """

        send_mail(
            subject='📩 New Contact Message – I Am a Brand',
            message=formatted_message,
            from_email=settings.ADMIN_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'error': 'Invalid request'}, status=400)



def blog_view(request):
    return render(request,'blog.html')