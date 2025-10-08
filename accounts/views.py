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
from .models import SalesCounter,BlogPost,CustomUser, UserSale
from django.conf.urls.static import static
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'index.html',{
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
    })



def why_preorder(request):
    return render(request,'why_preordered.html')




def sales_page(request, user):
    template_map = {
        'mary': 'sales/mary_sales.html',
        'jasmine': 'sales/jasmine_sales.html',
        'stella': 'sales/stella_sales.html',
        'john': 'sales/sales.html',
    }
    template_name = template_map.get(user.lower(), 'sales/sales.html')
    return render(request, template_name, {
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY
    })



def contact(request):
    return render(request, 'contact-us.html')



def process_user_payment(request):
    if request.method == 'POST':
        try:
            print("\n--- PROCESS USER PAYMENT STARTED ---")

            # Try JSON first
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                print("✅ Received JSON data:", data)
            else:
                # Fallback to form data
                data = request.POST
                print("✅ Received form data:", data)

            email = data.get('email')
            plan = data.get('plan') or data.get('book_type')
            referring_user = data.get('referring_user')
            page_name = data.get('page_name')
            transaction_id = data.get('transaction_id')

            print(f"📩 Email: {email}")
            print(f"📘 Plan: {plan}")
            print(f"👤 Referring User: {referring_user}")
            print(f"📄 Page Name: {page_name}")
            print(f"💳 Transaction ID: {transaction_id}")

            if not transaction_id:
                print("❌ Transaction ID missing")
                return JsonResponse({'error': 'Transaction ID missing'}, status=400)

            # Verify Paystack transaction
            print("🔍 Verifying Paystack transaction...")
            paystack = requests.get(
                f"https://api.paystack.co/transaction/verify/{transaction_id}",
                headers={"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            )
            paystack_response = paystack.json()
            print("✅ Paystack verification response:", paystack_response)

            if paystack_response.get('status') and paystack_response['data']['status'] == 'success':
                amount = paystack_response['data']['amount'] / 100  # kobo → naira
                amount_formatted = f"{amount:,.0f}"  # ✅ format to ₦10,000 style
                print(f"💰 Raw Amount: ₦{amount}")
                print(f"💰 Formatted Amount: ₦{amount_formatted}")

                book_type = 'soft_copy' if plan in ['Ebook/PDF', 'soft_copy'] else 'hard_copy'
                referrer_name = referring_user if referring_user else "Anonymous"

                print(f"📖 Book Type: {book_type}")

                # Save to UserSale
                print("🗃️ Saving to UserSale...")
                UserSale.objects.create(
                    book_type=book_type,
                    page_name=page_name,
                    amount=amount,
                    transaction_id=transaction_id,
                    referring_user=referrer_name,
                    buyer_email=email
                )
                print("✅ UserSale record saved successfully.")

                # Update SalesCounter
                print("📊 Updating SalesCounter...")
                sales = SalesCounter.objects.first()
                if not sales:
                    print("⚠️ No SalesCounter found — creating a new one.")
                    sales = SalesCounter(soft_copy_sold=0, hard_copy_sold=10)
                if book_type == 'soft_copy':
                    sales.soft_copy_sold += 1
                else:
                    sales.hard_copy_sold += 1
                sales.save()
                print("✅ SalesCounter updated successfully.")

                # Prepare email
                print("✉️ Preparing confirmation email...")
                delivery_date = "November 1, 2025"
                support_email = "info@iamabrandthebook.com"
                logo_path = static('assets/images/logo_white.png')
                logo_url = f"{settings.SITE_URL.rstrip('/')}{logo_path}"
                subject = "📘 Your Order Confirmation – I Am a Brand"
                from_email = getattr(settings, "EMAIL_HOST_USER", "noreply@iamabrand.com")
                to = [email]

                print(f"📧 From: {from_email}")
                print(f"📬 To: {to}")

                # Plain text email content
                text_content = f"""
                Dear Customer,

                Thank you for ordering "I Am a Brand The Book"!

                🔹 Plan: {plan}
                🔹 Txn ID: {transaction_id}
                🔹 Amount: ₦{amount_formatted}

                {"You will receive your download link on " + delivery_date + "." if plan in ['Ebook/PDF','soft_copy'] else "Your hard copy will be shipped and you should receive it by " + delivery_date + "."}

                For issues or more enquiries, kindly contact us at {support_email}.

                Regards,
                I Am a Brand Team
                """

                # HTML email content
                html_content = f"""
                <html>
                  <body style="font-family: Arial, sans-serif; color:#333; line-height:1.6;">
                    <div style="max-width:600px; margin:auto; padding:20px; border:1px solid #eee; border-radius:10px;">
                      <div style="text-align:center; margin-bottom:20px;">
                        <img src="{logo_url}" alt="I Am a Brand Logo" style="height:60px;">
                        <h2 style="color:#0a3d62;">I AM A BRAND</h2>
                      </div>
                      <p><strong>Dear Customer,</strong></p>
                      <p>Thank you for ordering <strong>"I Am a Brand"</strong>!</p>
                      <ul style="list-style-type:none; padding:0;">
                        <li>📘 <strong>Plan:</strong> {plan}</li>
                        <li>🧾 <strong>Txn ID:</strong> {transaction_id}</li>
                        <li>💵 <strong>Amount:</strong> ₦{amount_formatted}</li>
                      </ul>
                      <p>
                        {"You will receive your <b>download link</b> on <strong>" + delivery_date + "</strong>." if plan in ['Ebook/PDF','soft_copy'] else "Your <b>hard copy</b> will be shipped and you should receive it by <strong>" + delivery_date + "</strong>."}
                      </p>
                      <p style="margin-top:15px;">
                        For issues or more enquiries, kindly contact us at 
                        <a href="mailto:{support_email}" style="color:#0a3d62; text-decoration:none;">{support_email}</a>.
                      </p>
                      <p>Regards,<br><strong>I Am a Brand Team</strong></p>
                    </div>
                  </body>
                </html>
                """

                # Send email
                print("🚀 Sending email now...")
                msg = EmailMultiAlternatives(subject, text_content, from_email, to)
                msg.attach_alternative(html_content, "text/html")
                send_result = msg.send()
                print("✅ Email send result:", send_result)

                print("--- PROCESS COMPLETED SUCCESSFULLY ---\n")
                return JsonResponse({'status': 'payment_processed'})

            else:
                print("❌ Paystack verification failed:", paystack_response)
                return JsonResponse({'error': 'Transaction verification failed'}, status=400)

        except Exception as e:
            print("🔥 Exception caught during payment processing:", str(e))
            logger.error("Payment processing error", exc_info=True)
            return JsonResponse({'error': str(e)}, status=400)

    print("❌ Invalid request method")
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
    # Get the selected category from the GET parameter
    selected_category = request.GET.get('category', None)
    
    # Fetch all unique categories for the dropdown
    categories = BlogPost.objects.values('category').distinct()
    
    # Fetch blog posts, filtered by category if provided, ordered by published_at
    if selected_category and selected_category != 'all':
        posts = BlogPost.objects.filter(category=selected_category).order_by('-published_at')
    else:
        posts = BlogPost.objects.all().order_by('-published_at')
    
    # Context for the template
    context = {
        'posts': posts,
        'categories': categories,
        'selected_category': selected_category,
    }
    
    return render(request, 'blog.html', context)


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    contents = post.contents.all()  # thanks to related_name="contents"
    return render(request, "blog_detail.html", {"post": post, "contents": contents})


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
