from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# user model


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('', 'Select User Type'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]

    userType = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    roll_num = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    dob = models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    faculty = models.CharField(max_length=50)
    semester = models.CharField(max_length=50, null=True)


Attendance_status = (
    ('Present', 'Present'),
    ('Absent', 'Absent'),
)

# attendance modal


class Attendance(models.Model):
    username = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    roll_num = models.CharField(max_length=10)
    gender = models.CharField(max_length=50)
    faculty = models.CharField(max_length=50)
    sem = models.CharField(max_length=50)
    date = models.DateField(auto_now_add=True, null=True)
    time = models.TimeField(auto_now_add=True, null=True)
    ststus = models.CharField(
        choices=Attendance_status, max_length=30, default='Absent')
    usertype = models.CharField(max_length=20)

    def __str__(self):
        return str(f"{self.first_name} {self.last_name}")
