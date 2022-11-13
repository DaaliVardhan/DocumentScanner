from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.conf import settings
# Create your views here
from .models import File
from .docscanner import scan 
import os
import cv2

def home(request):
    if request.method=="POST":
        file=request.FILES.get("file")       
        if file:
            obj=File(name=file.name,filepath=file)
            obj.save()
            
            image=scan(fr"./media/files/{file.name}")
            p=r"C:\Users\daali\OneDrive\Desktop\pbl\scan\media\saved"
            if image is None:
                return redirect("/")
            cv2.imwrite(os.path.join(p,file.name),image)
            return render(request,"index.html",{"image":f"{settings.MEDIA_URL}saved/{file.name}"})
        

        return redirect("/")
    return render(request,"index.html")

    