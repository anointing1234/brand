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
from .models import SalesCounter




logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'index.html',{
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
    })

def contact(request):
    return render(request, 'contact-us.html')



def process_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            plan = data.get('plan')

            # Admin notification email
            admin_message = f"""
            📚 NEW BOOK ORDER – I Am a Brand

            🔹 Email Address: {email}
            🔹 Selected Plan: {plan}

            Please follow up with this customer for confirmation and delivery.

            Regards,
            I Am a Brand Website
            """
            send_mail(
                subject='📘 New Book Order – I Am a Brand',
                message=admin_message,
                from_email=settings.ADMIN_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # Customer confirmation email
            customer_message = f"""
            Dear Customer,

            Thank you for ordering "I Am a Brand"!

            🔹 Order Details:
            - Plan: {plan.title()} Copy
            - Email: {email}

            {'You will receive a download link for your soft copy soon.' if plan == 'soft' else 'Your hard copy will be prepared for shipping. We will contact you soon with delivery details.'}

            If you have any questions, please contact us at {settings.ADMIN_EMAIL}.

            Best regards,
            I Am a Brand Team
            """
            send_mail(
                subject='📘 Your Order Confirmation – I Am a Brand',
                message=customer_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )

            return JsonResponse({'status': 'payment_processed'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


    
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



def get_sales_data(request):
    # Fetch the sales counter record (assuming there's only one; create if it doesn't exist)
    sales = SalesCounter.objects.first()
    if not sales:
        sales = SalesCounter(soft_copy_sold=0, hard_copy_sold=10)
        sales.save()
    return JsonResponse({
        'softCopySold': sales.soft_copy_sold,
        'hardCopySold': sales.hard_copy_sold
    })




def update_sales(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sales = SalesCounter.objects.first()
            if not sales:
                sales = SalesCounter(soft_copy_sold=0, hard_copy_sold=10)
            # Update the fields with the new values from the JS payload
            sales.soft_copy_sold = data.get('softCopySold', sales.soft_copy_sold)
            sales.hard_copy_sold = data.get('hardCopySold', sales.hard_copy_sold)
            sales.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)