from django.core.files.base import ContentFile
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.conf import settings
from io import BytesIO
# Create your views here
import json
from PIL import Image
from .models import *
from .docscanner import getResult
from .newscanner import scanimage
import requests
import os
import cv2
import numpy as np
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import base64
def home(request):
    if request.user.is_anonymous:
        return redirect("./login")

    return render(request,"index.html")


@csrf_exempt
def signup(request):
    if request.method=="POST":        
        username=request.POST.get('username')
        password=request.POST.get('password')
        email=request.POST.get('email')
        if username and password and email:
            if User.objects.filter(username=username).exists():
                messages.info(request,"The username already taken")
                return redirect("/")
            elif email and User.objects.filter(email=email).exists():
                messages.info(request,"The email already taken")
                return redirect("/")
            else:
                user=User.objects.create_user(username=username,password=password,email=email)

                if user is not None:
                    messages.success(request,user.username+" successfully registered.")
                    return redirect("/")
    return render(request,"signup.html")


@csrf_exempt
def log(request):


    if request.method=="POST" and request.user.is_anonymous:
        
        username=request.POST.get('username')
        password=request.POST.get('password')
        if username and password:
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,"Login successful")
                return redirect("/")
            else:
                messages.info(request,"The user not found")
                return redirect("/")
        return redirect("/")

    return render(request,"login.html")

def logout_user(request):
    logout(request)
    messages.success(request,"Logout succesful")
    return redirect("/")



def scan(request):  
    if request.user.is_anonymous:
        return redirect("./login")
    if request.method=="POST":       
        file=request.FILES.get("file")       
        if file:
            try:
                obj=OriginalFile(author=request.user,filepath=file)
            except Exception as e:
                print(e)
                redirect("/")

            if obj:
                obj.save()
                # file=OriginalFile.objects.last()
                # image=Image.open(BytesIO(requests.get(f"{request.scheme}://{request.META['HTTP_HOST']}{file}").content))
                image=Image.open(BytesIO(file.read()))
                final=scanimage(np.array(image))

                
                ret, buf = cv2.imencode('.jpg', final)
                content = ContentFile(np.array(buf))
                
                if final is None:
                    return redirect("/")                
                savefileobj=SavedFile(author=request.user)
                savefileobj.filepath.save("output.jpg",content)
                savedfile=SavedFile.objects.filter(author=request.user).last()
                print(savedfile)
            
                print(savedfile)
                return render(request,"index.html",{"image":savedfile})

                
            return redirect("/")
            # image=getResult(file)
            # p=r"C:\Users\daali\OneDrive\Desktop\pbl\scan\media\saved"
            
            # if image is None:
            #     return redirect("/")
            # cv2.imwrite(os.path.join(p,file.name),image)
            # return render(request,"index.html",{"image":f"{settings.MEDIA_URL}saved/{file.name}"})
        

        return redirect("/")
    return render(request,"index.html")

def getList(request):
    if request.method=="GET":
        obj=SavedFile.objects.filter(author=request.user)
        return render(request,"all_img.html",{"images":obj})
    return redirect("/")