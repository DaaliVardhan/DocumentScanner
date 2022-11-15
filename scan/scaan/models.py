from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4 as u
import os

# Create your models here.

def get_uploadfile_path(instance,filename):
    ext=filename.split('.')[-1]
    file=f"{instance.author}_uploadedFile{str(u())[:5]}.{ext}"
    return os.path.join(instance.directory,file)

def get_savedfile_path(instance,filename):
    ext=filename.split(".")[-1]
    file=f"{instance.author}_savedFile{str(u())[:5]}.{ext}"
    return os.path.join(instance.directory,file)
class OriginalFile(models.Model):
    id=models.AutoField(primary_key=True)
    author=models.ForeignKey(User,verbose_name="Username",on_delete=models.CASCADE)
    name=models.CharField(max_length=500)
    directory='files/'
    filepath=models.FileField(upload_to=get_uploadfile_path,null=True)

    def __str__(self):
        return "/media/"+str(self.filepath)
        
class SavedFile(models.Model):
    id=models.AutoField(primary_key=True)
    author=models.ForeignKey(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=500)
    directory="saved/"
    filepath=models.FileField(upload_to=get_savedfile_path,null=True)

    def __str__(self) -> str:
        return "/media/"+str(self.filepath)

