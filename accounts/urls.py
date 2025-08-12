from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve
from django.views.generic import TemplateView
 


urlpatterns = [ 
    path('',views.home,name="home"),        
    path('home/',views.home,name="home"),   
    path('contact/',views.contact,name='contact'),  
    path('blog/',views.blog_view,name='blog'),
    path('api/sales-data/', views.get_sales_data, name='get_sales_data'),
    path('api/update-sales/', views.update_sales, name='update_sales'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-success/', TemplateView.as_view(template_name='payment_success.html')),
    path('send-contact-message/', views.send_contact_message, name='send_contact_message'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
