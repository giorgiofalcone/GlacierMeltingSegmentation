"""app_segmentation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('home_forest', views.home_forest, name='home_forest'),
    path('upload_forest', views.upload_forest, name='upload_forest'),
    path('upload', views.upload, name='upload'),
    path('knowledge-base', views.knowledge_base, name='knowledge_base'),
    path('knowledge-base_forest', views.knowledge_base_forest, name='knowledge_base_forest'),
    path('img-info', views.img_info, name='knowledge_base'),
    path('img-info_forest', views.img_info_forest, name='knowledge_base_forest'),
    path('visualize', views.visualize, name='visualize'),
    path('visualize_forest', views.visualize_forest, name='visualize_forest'),
    path('admin/', admin.site.urls),
]# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_URL)
