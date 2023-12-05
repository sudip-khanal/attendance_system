from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
import base64
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
import os
import webbrowser
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import AttendanceReportFormAdmin, AttendanceReportFormUser, SignUpForm, LoginForm, TeacherUpdateForm, StudentUpdateForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User, Attendance
from django.contrib.auth import get_user_model
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
import csv
from datetime import date
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO


from website.detection import FaceRecognition


faceRecognition = FaceRecognition()


@login_required(login_url='login_view')
def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user_type = form.cleaned_data['userType']
            if user_type == 'student':
                # Create a student user
                user = form.save(commit=False)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                id = user.id
                addFace(id, request)
                return redirect('adminpage')

            elif user_type == 'teacher':
                # Create a teacher user
                user = form.save(commit=False)
                user.is_staff = False
                user.is_superuser = False
                user.save()
                id = user.id
                addFace(id)
                return redirect('adminpage')

            elif user_type == 'admin':
                # Create an admin user
                user = form.save(commit=False)
                user.is_staff = True
                user.is_superuser = False
                user.save()
                messages.success(
                    request, 'Admin has been registered Successfully!!')
                return redirect('adminpage')
            else:
                msg = 'form is not valid'
    else:
        form = SignUpForm()

    return render(request, 'Admin/signup.html', {'form': form, 'msg': msg})

#  Face Recognization


def addFace(id, request):
    user_id = id
    print("usersid", user_id)
    faceRecognition.faceDetect(user_id)
    faceRecognition.trainFace()
    messages.success(request, 'User has been registered with face data!!')
    return redirect('adminpage')


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.userType == 'student':
                    login(request, user)
                    # Redirect to the student dashboard
                    return redirect('student')
                elif user.userType == 'teacher':
                    login(request, user)
                    # Redirect to the teacher dashboard
                    return redirect('teacher')
                elif user.userType == 'admin':
                    login(request, user)
                    return redirect('adminpage')

            else:
                # Invalid credentials, handle the error or display a message
                msg = 'invalid Username or Password!! Try Again'
    else:
        form = LoginForm()  # Replace 'YourLoginForm' with the name of your login form class

    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})

# Admin View


@login_required(login_url='login_view')
def View_admin(request):
    # Fetch all User objects from the database
    users = get_user_model().objects.all()
    total_user = users.count()  # Count Total users
    total_students = get_user_model().objects.filter(
        userType="student").count()  # count total Students
    total_teachers = get_user_model().objects.filter(
        userType="teacher").count()  # count total Teacher
    total_admins = get_user_model().objects.filter(
        userType="admin").count()  # count total Admins
    userData = {
        'users': users,
        'total_user': total_user,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_admins': total_admins
    }
    if request.user.userType == 'admin':
        return render(request, 'Admin/admin.html', userData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin To View This Page")
        return redirect('login_view')

#  Face Detection and Mark Attendence


def FaceReco(request):
    face_recognition = FaceRecognition()
    # Perform face recognition
    face_recognition.recognizeFace()
    # Check if the attendance was marked successfully
    if face_recognition.mark_attendance:
        messages.success(request, "Attendance Marked Successfully")
    else:
        messages.warning(
            request, " Attendance has already been marked with this face for today.")
    return redirect('AllAdtendance')

# attendence of all users


@login_required(login_url='login_view')
def AllAdtendance(request):
    # Fetch all  objects from the database
    Attendences = Attendance.objects.all()
    AttendanceData = {
        'Attendences': Attendences
    }
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        return render(request, 'Admin/AlluserAtd.html', AttendanceData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher To View This Page")
        return redirect('login_view')

# # students data Table view


@login_required(login_url='login_view')
def Stdtendance(request):
    # Fetch all  objects from the database
    Attendences = Attendance.objects.filter(usertype='student')
    AttendanceData = {
        'Attendences': Attendences
    }
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        return render(request, 'Admin/Attendence.html', AttendanceData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher To View This Page")
        return redirect('login_view')


@login_required(login_url='login_view')
def Teacherattendance(request):
    # Fetch all  objects from the database
    Attendences = Attendance.objects.filter(usertype='teacher')
    AttendanceData = {
        'Attendences': Attendences
    }
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        return render(request, 'Admin/teacterattendence.html', AttendanceData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher To View This Page")
        return redirect('login_view')
# Attendence record view


@login_required(login_url='login_view')
def Attendance_record(request, user):
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        data = Attendance.objects.filter(username=user)
        attRecord = {'datas': data}
        return render(request, 'Admin/attendancerecord.html', attRecord)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher View The Page")
        return redirect('login_view')

# # students data Table view


@login_required(login_url='login_view')
def Std_data(request):
    students = get_user_model().objects.filter(
        userType="student")  # Fetch all  objects from the database
    StdData = {
        'students': students
    }
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        return render(request, 'Admin/std.html', StdData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher To View This Page")
        return redirect('login_view')

# # individual student record view


@login_required(login_url='login_view')
def stu_record(request, pk):
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        student_record = get_user_model().objects.get(id=pk)
        return render(request, 'Admin/record.html', {'student_record': student_record})
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher View The Page")
        return redirect('login_view')

# # Delete Student Record


@login_required(login_url='login_view')
def Delete_Stdrecord(request, pk):
    if request.user.userType == 'admin':
        delete_it = get_user_model().objects.get(id=pk)
        delete_it.delete()
        messages.warning(request, "Record Deleeted Successfully .....")
        return redirect('Stdata')
    else:
        messages.warning(
            request, "You must have to logged in to delete the records")
        return redirect('login_view')

# # Update Student Record


@login_required(login_url='login_view')
def Update_Stdrecord(request, pk):
    if request.user.userType == 'admin':
        current_record = get_user_model().objects.get(id=pk)
        form = StudentUpdateForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.info(request, "Record Updated Successfully .....")
            return redirect('Stdata')
        return render(request, 'Admin/update.html', {'form': form})
    else:
        messages.warning(
            request, "You must be  logged in to update the records")
        return redirect('login_view')

# admins data


@login_required(login_url='login_view')
def admin_data(request):
    students = get_user_model().objects.filter(
        userType="admin")  # Fetch all  objects from the database
    AdmData = {
        'admins': students
    }
    if request.user.userType == 'admin':
        return render(request, 'Admin/detail_admin.html', AdmData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin To View This Page")
        return redirect('login_view')

# #  Teachers Data


@login_required(login_url='login_view')
def TeaData(request):
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        Teachers = get_user_model().objects.filter(userType='teacher')
        teacherData = {
            'Teachers': Teachers
        }
        return render(request, 'Admin/teacherdata.html', teacherData)
    else:
        messages.warning(request, "You Must Be Logged In View The Page")
        return redirect('login_view')


@login_required(login_url='login_view')
def Teacher_record(request, pk):
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        Teachers_record = get_user_model().objects.get(id=pk)
        return render(request, 'Admin/teacherRecord.html', {'Teachers_record': Teachers_record})
    else:
        messages.warning(request, "You Must Be Logged In View The Page")
        return redirect('login_view')


@login_required(login_url='login_view')
def Teacher_delete(request, pk):
    if request.user.userType == 'admin' or request.user.userType == 'teacher':
        delete_tea = get_user_model().objects.get(id=pk)
        delete_tea.delete()
        messages.warning(request, "Record Deleeted Successfully .....")
        return redirect('teacherdata')
    else:
        messages.warning(request, "You Must Be Logged In View The Page")
        return redirect('login_view')


@login_required(login_url='login_view')
def Update_TeacherRecord(request, pk):
    if request.user.userType == 'admin':
        current_record = get_user_model().objects.get(id=pk)
        form = TeacherUpdateForm(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.info(request, "Record Updated Successfully .....")
            return redirect('teacherdata')
        return render(request, 'Admin/update.html', {'form': form})
    else:
        messages.warning(
            request, "You must be  logged in to update the records")
        return redirect('login_view')

# # Teacher View


@login_required(login_url='login_view')
def Teacher(request):
    if request.user.userType == 'teacher':
        # to view attendence
        user = request.user.username
        teacherAttendance = Attendance.objects.filter(username=user)
        return render(request, 'Teacher/teacher.html', {'teacherAttendances': teacherAttendance})
    else:
        messages.warning(
            request, "You Must Be Logged In As Teacher To View This Page")
        return redirect('login_view')

# # teacher profile


@login_required(login_url='login_view')
def teacherprofile(request):
    if request.user.userType == 'teacher':
        teacherid = request.user.id
        tprofile = get_user_model().objects.filter(id=teacherid)
        return render(request, 'Teacher/Tprofile.html', {'tprofiles': tprofile})
    else:
        messages.warning(request, "You Must Be Logged In to View This Page")
        return redirect('login_view')

# # Student View


@login_required(login_url='login_view')
def Student(request):
    if request.user.userType == 'student':
        # to view attendence
        user = request.user.username
        stattendances = Attendance.objects.filter(username=user)
        return render(request, 'Student/student.html', {'stattendances': stattendances})
    else:
        messages.warning(
            request, "You Must Be Logged In As Student to View This Page")
        return redirect('login_view')

# # student profile


@login_required(login_url='login_view')
def stdprofile(request):
    if request.user.userType == 'student':
        user = request.user.id
        print(user)
        profile = get_user_model().objects.filter(id=user)

        return render(request, 'Student/studentprofile.html', {'profiles': profile})
    else:
        messages.warning(request, "You Must Be Logged In to View This Page")
        return redirect('login_view')

# # logout


def logout_user(request):
    logout(request)
    messages.warning(request, "You have been Logged out..")
    return redirect('login_view')


# # generate Attendence report


class AttendanceReportView(LoginRequiredMixin, FormView):
    template_name = 'Admin/report.html' or 'Student/attendance_report.html'
    login_url = '/login_view/'  # Replace with your login URL if different

    def get_form_class(self):
        # Based on the user type (admin or user), return the appropriate form class
        if self.request.user.userType == 'admin':
            return AttendanceReportFormAdmin
        elif self.request.user.userType in ['student', 'teacher']:
            return AttendanceReportFormUser

    def form_valid(self, form):
        user = form.cleaned_data['username']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        export_format = form.cleaned_data['format']
        num_days = (end_date - start_date).days
        # Generate report based on the selected format
        if export_format == 'csv':
            return self.generate_csv_report(start_date, end_date, user)
        elif export_format == 'pdf':
            return self.generate_pdf_report(start_date, end_date, num_days, user)
        else:
            # Handle unsupported format gracefully
            return super().form_valid(form)

    def generate_csv_report(self, start_date, end_date, user):
        print(user)
        # Generate CSV report logic using the specified date range

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        # Write CSV content to the response object
        writer = csv.writer(response)

        stattendances = Attendance.objects.filter(
            username=user, date__range=(start_date, end_date))

        # add column heading
        writer.writerow(['UserName', 'Name', 'Faculty', 'Semester',
                        'Date', 'Time', 'Roll num', 'Status', 'Gender'])
        # loop through attendence
        for stat in stattendances:
            writer.writerow([stat.username, stat.first_name, stat.faculty, stat.sem,
                            stat.date, stat.time, stat.roll_num, stat.ststus, stat.gender])
        return response

    def generate_pdf_report(self, start_date, end_date, num_days, user):
        print(user)

        # Retrieve attendance records for the user within the specified date range
        attendances = Attendance.objects.filter(
            username=user, date__range=(start_date, end_date))
        presentdays = attendances.filter(ststus='Present').count()
        absentdays = num_days - presentdays
        # Initialize f_name and l_name with None or some default values
        f_name = None
        l_name = None
        # Iterate through the stattendances and retrieve first_name and last_name
        for name in attendances:
            f_name = name.first_name
            l_name = name.last_name
        context = {
            'fname': f_name,
            'lname': l_name,
            'start_date': start_date,
            'end_date': end_date,
            'num_days': num_days,
            'presentdays': presentdays,
            'absentdays': absentdays,
            'attendances': attendances,
        }

        # Render the HTML template with context data
        html_content = render_to_string('Student/report.html', context)

        # Create PDF file
        pdf_file = BytesIO()

        # Generate PDF from HTML content
        pisa.CreatePDF(html_content, dest=pdf_file, encoding='UTF-8')

        # Set the position of the PDF file to the beginning
        pdf_file.seek(0)

       # Create the HTTP response with appropriate headers
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="attendance_report.pdf"'

        # Write the PDF content to the response
        response.write(pdf_file.getvalue())
        return response

# opens dataset image folder


def open_Dataset_folder(request):
    folder_name = 'dataset'
    folder_path = os.path.join(settings.BASE_DIR, 'website', folder_name)

    if os.path.exists(folder_path):
        webbrowser.open(folder_path)
    else:
        # Folder doesn't exist
        messages.warning(request, "Folder not found")

    return redirect('adminpage')
