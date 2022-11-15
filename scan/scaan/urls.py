
import os 
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # path("",views.home,name="home"),
    path("login/",views.log,name="login"),
    path("signup/",views.signup,name="signup"),
    path("",views.scan,name="scan"),
    path("get/",views.getList,name="gallery"),
    path("logout/",views.logout_user,name='logout'),
    
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

