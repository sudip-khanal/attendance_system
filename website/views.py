from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm, AddStudentRecord,AttendanceReportForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User, StudentRecord,Attendance
import csv
from datetime import date
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.views.generic.edit import FormView

from website.detection import FaceRecognition


faceRecognition = FaceRecognition()


def home(request):
    return render(request, 'home.html', {})


def Aboutus(request):
    return render(request, 'about.html', {})


def Contactus(request):
    return render(request, 'contact.html', {})

# Multi user registration
def register(request):
    if request.user.is_admin:
        msg = None
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.info(request, 'User Created Succesfully Now Add More Data ')
                return redirect('AddStdData')
            else:
                msg = 'form is not valid'
        else:
            form = SignUpForm()
        return render(request, 'Admin/signup.html', {'form': form, 'msg': msg})
    else:
        messages.success(
            request, "You Must Be Logged In As Admin To View This Page")
        return redirect('home')

# multi user login
def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_admin:
                login(request, user)
                # messages.success(request)
                return redirect('adminpage')
            elif user is not None and user.is_teacher:
                login(request, user)
                # messages.success(request)
                return redirect('teacher')
            elif user is not None and user.is_student:
                login(request, user)
                # messages.success(request)
                return redirect('student')
            else:
                msg = 'invalid Username or Password!! Try Again'
        else:
            msg = 'error validating form'
    return render(request, 'accounts/login.html', {'form': form, 'msg': msg})

# Admin View
def View_admin(request):
    users = User.objects.all()  # Fetch all User objects from the database
    total_user = users.count()  # Count Total users
    total_students = User.objects.filter(
        is_student="1").count()  # count total Students
    total_teachers = User.objects.filter(
        is_teacher="1").count()  # count total Teacher
    total_admins = User.objects.filter(
        is_admin="1").count()  # count total Admins
    userData = {
        'users': users,
        'total_user': total_user,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_admins': total_admins
    }
    if request.user.is_admin:
        return render(request, 'Admin/admin.html', userData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin To View This Page")
        return redirect('home')


# add student record
def AddStdData(request):
    if request.user.is_admin:
        msg = None
        if request.method == 'POST':
            form = AddStudentRecord(request.POST or None)
            if form.is_valid():
                form.save()
                addFace(request.POST.get('user_id'))
                print("IN HERE")
                messages.info(
                    request, "Suceessfully Added The student record !!")
                redirect('Stdata.html')
            else:
                msg = 'form is not valid'
        else:
            form = AddStudentRecord()
        return render(request, 'Admin/adddata.html', {'form': form, 'msg': msg})
    else:
        messages.warning(request, "You Must Be Logged In As Admin To View This Page")
        return redirect('home')

# Face Recognization
def addFace(user_id):
    user_id = user_id
    faceRecognition.faceDetect(user_id)
    faceRecognition.trainFace()
    return redirect('Stdata')

# Face Detection and Mark Attendence
def face(request):
    face = faceRecognition.recognizeFace()
    messages.info(request, "Attendance Marked Successfully...")
    return redirect('attendence')

# students data Table view
def Stdtendance(request):
    Attendences = Attendance.objects.all()  # Fetch all  objects from the database
    AttendanceData = {
        'Attendences': Attendences
    }
    if request.user.is_admin or request.user.is_teacher:
        return render(request, 'Admin/Attendence.html', AttendanceData)
    else:
        messages.warning(request, "You Must Be Logged In As Admin or Teacher To View This Page")
        return redirect('home')

# Attendence record view
def Attendance_record(request):
    if request.user.is_admin or request.user.is_teacher:
        ids = request.StudentRecord.user_id
        data = Attendance.objects.filter(user_id=ids)
        attRecord = {'data': data}
        return render(request, 'Admin/attendancerecord.html', attRecord)
    else:
        messages.warning(request, "You Must Be Logged In As Admin or Teacher View The Page")
        return redirect('home')

# students data Table view
def Std_data(request):
    students = StudentRecord.objects.all()  # Fetch all  objects from the database
    StdData = {
        'students': students
    }
    if request.user.is_admin or request.user.is_teacher:
        return render(request, 'Admin/std.html', StdData)
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher To View This Page")
        return redirect('home')

# individual student record view
def stu_record(request, pk):
    if request.user.is_admin or request.user.is_teacher:
        student_record = StudentRecord.objects.get(id=pk)
        return render(request, 'Admin/record.html', {'student_record': student_record})
    else:
        messages.warning(
            request, "You Must Be Logged In As Admin or Teacher View The Page")
        return redirect('home')

# Delete Student Record
def Delete_Stdrecord(request, pk):
    if request.user.is_admin:
        delete_it = StudentRecord.objects.get(id=pk)
        delete_it.delete()
        messages.warning(request, "Record Deleeted Successfully .....")
        return redirect('Stdata')
    else:
        messages.warning(
            request, "You must have to logged in to delete the records")
        return redirect('home')

# Update Student Record
def Update_Stdrecord(request, pk):
    if request.user.is_admin:
        current_record = StudentRecord.objects.get(id=pk)
        form = AddStudentRecord(request.POST or None, instance=current_record)
        if form.is_valid():
            form.save()
            messages.info(request, "Record Updated Successfully .....")
            return redirect('Stdata')
        return render(request, 'Admin/updateStd.html', {'form': form})
    else:
        messages.warning(
            request, "You must be  logged in to update the records")
        return redirect('home')

#  Teachers Data
def TeaData(request):
    if request.user.is_admin or request.user.is_teacher:
        Teachers = User.objects.filter(is_teacher='1')
        teacherData = {
            'Teachers': Teachers
        }
        return render(request, 'Admin/teacherdata.html', teacherData)
    else:
        messages.warning(request, "You Must Be Logged In View The Page")
        return redirect('home')


def Teacher_record(request, pk):
    if request.user.is_admin or request.user.is_teacher:
        Teachers_record = User.objects.get(id=pk)
        return render(request, 'Admin/teacherRecord.html', {'Teachers_record': Teachers_record})
    else:
        messages.warning(request, "You Must Be Logged In View The Page")
        return redirect('home')
    
def Teacher_delete(request, pk):
    if request.user.is_admin:
        delete_tea = User.objects.get(id=pk)
        delete_tea.delete()
        messages.warning(request, "Record Deleeted Successfully .....")
        return redirect('teacherdata')
    else:
        messages.warning(request, "You Must Be Logged In View The Page")
        return redirect('home')


# Teacher View
def Teacher(request):
    if request.user.is_teacher:
        return render(request, 'Teacher/teacher.html')
    else:
        messages.warning(
            request, "You Must Be Logged In As Teacher To View This Page")
        return redirect('home')

# teacher profile
def teacherprofile(request):
    if request.user.is_teacher:
        teacherid = request.user.id
        tprofile = User.objects.filter(id=teacherid)
        return render(request, 'Teacher/Tprofile.html', {'tprofiles': tprofile})
    else:
        messages.warning(request, "You Must Be Logged In to View This Page")
        return redirect('home')


# Student View
def Student(request):
    if request.user.is_student:
        # to view attendence
        user = request.user.id
        stattendances = Attendance.objects.filter(user_id=user)
    
            
        return render(request, 'Student/student.html', {'stattendances': stattendances})
    else:
        messages.warning(
            request, "You Must Be Logged In As Student to View This Page")
        return redirect('home')

# student profile
def stdprofile(request):
    if request.user.is_student:
        user = request.user.id
        profile = StudentRecord.objects.filter(user_id=user)
        
        return render(request, 'Student/studentprofile.html', {'profiles': profile})
    else:
        messages.warning(request, "You Must Be Logged In to View This Page")
        return redirect('home')



# logout
def logout_user(request):
    logout(request)
    messages.warning(request, "You have been Logged out..")
    return redirect('home')

# generate Attendence report

class AttendanceReportView(FormView):
   
    template_name = 'Student/attendance_report.html'
    form_class = AttendanceReportForm

    def form_valid(self, form):
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        export_format = form.cleaned_data['format']
        num_days = (end_date - start_date).days

        
        # Generate report based on the selected format
        if export_format == 'csv':
            return self.generate_csv_report(start_date, end_date)
        elif export_format == 'pdf':
            return self.generate_pdf_report(start_date, end_date,num_days)
        else:
            # Handle unsupported format gracefully
            return self.render_to_response(self.get_context_data(form=form))

    def generate_csv_report(self, start_date, end_date):
        # Generate CSV report logic using the specified date range
        user = self.request.user.id
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'
        # Write CSV content to the response object
        writer = csv.writer(response)
       
        stattendances = Attendance.objects.filter(user_id=user,date__range=(start_date, end_date))

        #add column heading
        writer.writerow(['UserId','Name','Faculty','Semester','Date','Time','Roll num','Status','Gender'])
        #loop through attendence
        for stat in stattendances:
            writer.writerow([stat.user_id,stat.first_name,stat.faculty,stat.sem,stat.date,stat.time,stat.roll_num,stat.ststus,stat.gender])

        return response

    def generate_pdf_report(self,start_date, end_date,num_days):
        user = self.request.user.id

        # Retrieve attendance records for the user within the specified date range
        stattendances = Attendance.objects.filter(user_id=user, date__range=(start_date, end_date))
        presentdays = stattendances.filter(ststus='Present').count()
        absentdays = num_days - presentdays
        
        # Iterate through the stattendances and retrieve first_name and last_name
        for name in stattendances:
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
            'stattendances': stattendances,
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
        response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'

        # Write the PDF content to the response
        response.write(pdf_file.getvalue())


        return response