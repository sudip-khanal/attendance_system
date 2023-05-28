from django.db import models
from django.contrib.auth.models import AbstractUser,User

# Create your models here.

#user model
class User(AbstractUser):
    is_admin= models.BooleanField('Is Admin', default=False)
    is_teacher = models.BooleanField('Is Teacher', default=False)
    is_student = models.BooleanField('Is Student', default=False)

 

#student model
class StudentRecord(models.Model):
    #user = models.OneToOneField(User,null=True,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    roll_num = models.CharField(max_length=10)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    dob =  models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    my_faculty = models.CharField(max_length=50)
    sem = models.CharField(max_length=50)
    def __str__(self):
        return str(f"{self.first_name} {self.last_name}")


Attendance_status= (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )

#attendance modal

class Attendance(models.Model):
    user_id = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    roll_num = models.CharField(max_length=10)
    gender = models.CharField(max_length=50)
    faculty = models.CharField(max_length=50)
    sem = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True, null = True)
    time = models.TimeField(auto_now_add=True, null = True)
    ststus = models.CharField(choices=Attendance_status,max_length=30,default='Absent')

    def __str__(self):
        return str(f"{self.first_name} {self.last_name}")