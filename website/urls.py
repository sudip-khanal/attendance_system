from django.urls import path
from . import views
from . forms import MyPasswordChange

from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout_user, name='logout'),
    path('about_us/', views.Aboutus, name='about_us'),
    path('contact_us/', views.Contactus, name='contact_us'),
    path('login_view/', views.login_view, name='login_view'),
    path('signup/', views.register, name='signup'),
    path('adminpage/', views.View_admin, name='adminpage'),
    path('teacher/', views.Teacher, name='teacher'),
 
    path('tprofile',views.teacherprofile,name='tprofile'),
    path('student/', views.Student, name='student'),
    path('stprofile/',views.stdprofile,name='stprofile'),
    path('face/',views.addFace,name='face'),
    path('faceReconization/',views.FaceReco,name='faceReconization'),
    path('Stdata/',views.Std_data,name='Stdata'),
    path('record/<int:pk>', views.stu_record,name='record'),
    path('deleteStudent/<int:pk>', views.Delete_Stdrecord,name='deleteStudent'),
    path('UpdateStudent/<int:pk>', views.Update_Stdrecord,name='UpdateStudent'),
    path('teacherdata/',views.TeaData,name='teacherdata'),
    path('tearecord/<int:pk>', views.Teacher_record,name='tearecord'),
    path('tearecordDelete/<int:pk>', views.Teacher_delete,name='tearecordDelete'),
    path('updateteacher/<int:pk>',views.Update_TeacherRecord,name='updateteacher'),
    
    path('password_reset/',auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html'),name='password_reset'),
    path('password_reset_confirm/<slug:uidb64>/<slug:token>/',auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password_reset_done/',auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),name='password_reset_complete'),

    path('passwordchange/',auth_views.PasswordChangeView.as_view(template_name='accounts/changepassword.html',form_class =MyPasswordChange,success_url='/passwordchangedone/'),name='passwordchange'),
    path('passwordchangedone/',auth_views.PasswordChangeView.as_view(template_name='accounts/changepassworddone.html'),name='passwordchangedone'),

    path('attendence/', views.Stdtendance,name='attendence'),
    path('Recordattendance/<slug:user>',views.Attendance_record,name='Recordattendance'),
    path('attendance_report/',views.AttendanceReportView.as_view(), name='attendance_report'),

]
    
  