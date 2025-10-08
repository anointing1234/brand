"""
URL configuration for iambd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.views.static import serve 
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
# Import your sitemap
from accounts.sitemaps import StaticViewSitemap   # adjust app name if different

sitemaps_dict = {
    "static": StaticViewSitemap,
}

# Simple robots.txt view
def robots_txt(request):
    content = (
        "User-Agent: *\n"
        "Disallow:\n"
        f"Sitemap: https://iamabrandthebook.com/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('accounts.urls')),

   # Sitemap
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps_dict}, name="sitemap"),

    # Robots.txt
    path("robots.txt", robots_txt, name="robots_txt"),


    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]
