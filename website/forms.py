from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _


from .models import User,StudentRecord


class LoginForm(forms.Form):
    username = forms.CharField(
        widget= forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


class SignUpForm(UserCreationForm):
     first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
     last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
     username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )
     password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
     password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
     email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control"
            }
        )
    )

     class Meta:
        model = User
        fields = ('first_name','last_name','username', 'email', 'password1', 'password2', 'is_admin', 'is_teacher', 'is_student')

   

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)
OPTIONS_FACULTY = (
        ('BCA', 'BCA'),
        ('BIM', 'BIM'),
        ('BHM', 'BHM'),
        ('BBA', 'BBA'),
        ('BBS', 'BBS'),
    )
OPTIONS_SEM = (
        ('FIRST', 'FIRST'),
        ('SECOND', 'SECOND'),
        ('THIRD', 'THIRD'),
        ('FOURTH', 'FOURTH'),
        ('FIFTH', 'FIFTH'),
        ('SIXTH', 'SIXTH'),
        ('SEVENTH', 'SEVENTH'),
        ('EIGHTH', 'EIGHTH'),
    )

# fetching recenly added user id to maatch it with face id
recent_id =int( User.objects.order_by('-id').values_list('id', flat=True).first())
fname =( User.objects.order_by('-id').values_list('first_name', flat=True).first())
lname =( User.objects.order_by('-id').values_list('last_name', flat=True).first())
mail =( User.objects.order_by('-id').values_list('email', flat=True).first())


#  Full Record Form of the users
class AddStudentRecord(forms.ModelForm):
    user_id = forms.CharField(initial=recent_id,required=True, widget=forms.widgets.TextInput(attrs={"class":"form-control"}), label="User Id")
    first_name = forms.CharField(initial=fname,required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"First Name", "class":"form-control"}), label="First Name")
    last_name = forms.CharField(initial=lname,required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Last Name", "class":"form-control"}), label="Last Name")
    email = forms.CharField(initial=mail,required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Email", "class":"form-control"}), label="Email")
    roll_num = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Roll Number", "class":"form-control"}), label="Roll No")
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Phone", "class":"form-control"}), label="Phone No")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={"placeholder":"Address", "class":"form-control"}), label="Address")
    dob =  forms.DateField(required=True,widget=forms.DateInput(attrs={'type': 'date',"class":"form-control"}),label="Dob")
    gender = forms.ChoiceField(required=True,choices=GENDER_CHOICES, widget=forms.RadioSelect,label="Gender")
    my_faculty = forms.ChoiceField(required=True,choices=OPTIONS_FACULTY, widget=forms.Select(attrs={"class":"form-control"}),label="Faculty")
    sem = forms.ChoiceField(required=True,choices=OPTIONS_SEM , widget=forms.Select(attrs={"class":"form-control"}),label="Semester")
    
    class Meta:
        model = StudentRecord
        exclude = ("user",)

#password change
class MyPasswordChange(PasswordChangeForm):
    old_password =  forms.CharField(label=_('Old Password'),strip=False, widget=forms.PasswordInput(attrs={'autofocus':True,'autocomplete':'current-password', 'class':'form-control'}))
    new_password1 = forms.CharField(label=_('New Password'),strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control'}),
            help_text=password_validation.password_validators_help_text_html())
    new_password2 =forms.CharField(label=_('Conform Password'),strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control'}))




EXPORT_OPTIONS = (
    ('pdf', 'Pdf'),
    ('csv', 'Csv'),
)

class AttendanceReportForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control','format': 'yyyy-mm-dd'}),
        label="From Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control','format': 'yyyy-mm-dd'}),
        label="To Date"
    )
    format = forms.ChoiceField(
        required=True,
        choices=EXPORT_OPTIONS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Choose Format"
    )
