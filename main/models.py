from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.
class Report(models.Model):
    reportID = models.AutoField(primary_key=True)
    reporterName = models.CharField(max_length=255)
    datetime = models.CharField(max_length=255,null=True)
    operationLineNumber = models.CharField(max_length=255)
    problemDescription = models.TextField()
    status = models.CharField(max_length=255,default='0', null=True)
    confirmedBy = models.CharField(max_length=255, blank=True, null=True)
    sentBy = models.CharField(max_length=255, blank=True, null=True)
    sentTo = models.CharField(max_length=255, blank=True, null=True)
    problemCategory = models.CharField(max_length=255, null=True)
    emailNotifyDate = models.CharField(max_length=255, blank=True, null=True)
    dueDate = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "report"   

# Addition in the admin panel

class OperationLine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    line_no = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.line_no

class Profession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profession_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.profession_name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    operation_line_no = models.ManyToManyField(OperationLine, blank=True)
    profession = models.ManyToManyField(Profession, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
    

# Image 
class Image(models.Model):
    report = models.ForeignKey(Report, related_name='images', on_delete=models.CASCADE)
    imageData = models.ImageField(upload_to='reportImages/', height_field=None, width_field=None, max_length=100, blank=True, null=True)

    class Meta:
        db_table = "image"
