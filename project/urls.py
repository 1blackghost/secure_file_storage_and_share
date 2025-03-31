"""
URL configuration for house_price project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from main.views import home,login,signup,signup_view,login_view,dash,logout,upload_image,get_user_files,download_image
from main.views import download_url,send_data,pass_data,get_file,check_for,request_key,get_my_send
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('login', login, name='login'), 
    path('signup', signup, name='signup'), 
    path("signupData", signup_view, name="signupData"),
    path("loginData", login_view, name="loginData"),
    path("dash", dash, name="dash"),
    path("logout", logout, name="logout"),
    path("upload_image", upload_image, name="upload-image"),
    path('user-files/', get_user_files, name='get_user_files'), 
    path('download', download_image, name='download_image'), 
    path('download_file', download_url, name='download_file'),  
    path('send', send_data, name='send_data'),  
    path('pass_data', pass_data, name='pass_data'),  
    path('get_file', get_file, name='get_file'),  
    path('check_for', check_for, name='check_for'), 
    path('request_key', request_key, name='request_key'),  
    path("get_my_send",get_my_send,name="get_my_send"),


]
