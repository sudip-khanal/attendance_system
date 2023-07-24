from django.db.models import Q
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from requests import request

from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
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


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
)
OPTIONS_FACULTY = (
    ('', 'Select Faculty'),
    ('BCA', 'BCA'),
    ('BIM', 'BIM'),
    ('BHM', 'BHM'),
    ('BBA', 'BBA'),
    ('BBS', 'BBS'),
)
OPTIONS_SEM = (
    ('', 'Select Semester'),
    ('FIRST', 'FIRST'),
    ('SECOND', 'SECOND'),
    ('THIRD', 'THIRD'),
    ('FOURTH', 'FOURTH'),
    ('FIFTH', 'FIFTH'),
    ('SIXTH', 'SIXTH'),
    ('SEVENTH', 'SEVENTH'),
    ('EIGHTH', 'EIGHTH'),
)
USER_TYPE_CHOICES = [
    ('', 'Select User Type'),
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('admin', 'Admin'),
]


class SignUpForm(UserCreationForm):
    userType = forms.ChoiceField(required=True, choices=USER_TYPE_CHOICES, widget=forms.Select(
        attrs={"class": "form-control"}), label=" Select User Type")
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
    roll_num = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Roll Number", "class": "form-control"}), label="Roll No")
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Phone", "class": "form-control"}), label="Phone No")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Address", "class": "form-control"}), label="Address")
    dob = forms.DateField(required=True, widget=forms.DateInput(
        attrs={'type': 'date', "class": "form-control"}), label="Dob")
    gender = forms.ChoiceField(
        required=True, choices=GENDER_CHOICES, widget=forms.RadioSelect, label="Gender")
    faculty = forms.ChoiceField(required=True, choices=OPTIONS_FACULTY, widget=forms.Select(
        attrs={"class": "form-control"}), label="Faculty")
    semester = forms.ChoiceField(required=True, choices=OPTIONS_SEM, widget=forms.Select(
        attrs={"class": "form-control"}), label="Semester")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['userType', 'first_name', 'last_name', 'username', 'password1', 'password2',
                  'email', 'roll_num', 'phone', 'address', 'dob', 'gender', 'faculty', 'semester']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'userType' in self.data:
            user_type = self.data['userType']
            if user_type == 'admin':
                # Exclude fields for admin user type
                self.fields.pop('roll_num')
                self.fields.pop('phone')
                self.fields.pop('address')
                self.fields.pop('dob')
                self.fields.pop('gender')
                self.fields.pop('faculty')
                self.fields.pop('semester')
            elif user_type == 'teacher':
                # Exclude fields for teacher user type
                self.fields.pop('roll_num')


class AdminSignup(SignUpForm):
    class Meta(SignUpForm.Meta):
        fields = ['userType', 'first_name', 'last_name',
                  'username', 'password1', 'password2', 'email']


class TeacherSignUpForm(SignUpForm):
    class Meta(SignUpForm.Meta):
        fields = ['userType', 'first_name', 'last_name', 'username', 'password1',
                  'password2', 'email', 'phone', 'address', 'dob', 'gender', 'faculty', 'semester']


class StudentSignUpForm(SignUpForm):
    class Meta(SignUpForm.Meta):
        fields = ['userType', 'first_name', 'last_name', 'username', 'password1', 'password2',
                  'email', 'roll_num', 'phone', 'address', 'dob', 'gender', 'faculty', 'semester']

# password change


class MyPasswordChange(PasswordChangeForm):
    old_password = forms.CharField(label=_('Old Password'), strip=False, widget=forms.PasswordInput(
        attrs={'autofocus': True, 'autocomplete': 'current-password', 'class': 'form-control'}))
    new_password1 = forms.CharField(label=_('New Password'), strip=False, widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
                                    help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_('Conform Password'), strip=False, widget=forms.PasswordInput(
        attrs={'autocomplete': 'new-password', 'class': 'form-control'}))


# report form


# Define the choices for the 'format' field
EXPORT_OPTIONS = [('pdf', 'PDF'), ('csv', 'CSV')]


class AttendanceReportFormAdmin(forms.Form):
    username = forms.ChoiceField(
        choices=[],  # Populate the choices dynamically later
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Select username"
    )

    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'format': 'yyyy-mm-dd'}),
        label="From Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'format': 'yyyy-mm-dd'}),
        label="To Date"
    )
    format = forms.ChoiceField(
        required=True,
        choices=EXPORT_OPTIONS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Choose Format"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate the 'username' choices with all usernames
        usernames = User.objects.filter(Q(userType='student') | Q(
            userType='teacher')).values_list('username', flat=True)
        self.fields['username'].choices = [
            (username, username) for username in usernames]


class AttendanceReportFormUser(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control'}),
        required=True,
        label="Username"
    )

    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'format': 'yyyy-mm-dd'}),
        label="From Date"
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control', 'format': 'yyyy-mm-dd'}),
        label="To Date"
    )
    format = forms.ChoiceField(
        required=True,
        choices=EXPORT_OPTIONS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Choose Format"
    )


# update user form


class StudentUpdateForm(forms.ModelForm):
    userType = forms.ChoiceField(required=True, choices=USER_TYPE_CHOICES, widget=forms.Select(
        attrs={"class": "form-control"}), label=" Select User Type")
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control"}))
    roll_num = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Roll Number", "class": "form-control"}), label="Roll No")
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Phone", "class": "form-control"}), label="Phone No")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Address", "class": "form-control"}), label="Address")
    dob = forms.DateField(required=True, widget=forms.DateInput(
        attrs={'type': 'date', "class": "form-control"}), label="Dob")
    gender = forms.ChoiceField(
        required=True, choices=GENDER_CHOICES, widget=forms.RadioSelect, label="Gender")
    faculty = forms.ChoiceField(required=True, choices=OPTIONS_FACULTY, widget=forms.Select(
        attrs={"class": "form-control"}), label="Faculty")
    semester = forms.ChoiceField(required=True, choices=OPTIONS_SEM, widget=forms.Select(
        attrs={"class": "form-control"}), label="Semester")

    class Meta:
        model = User  # Replace with your actual user model
        fields = ['userType', 'first_name', 'last_name', 'username', 'email',
                  'roll_num', 'phone', 'address', 'dob', 'gender', 'faculty', 'semester']


class TeacherUpdateForm(forms.ModelForm):
    userType = forms.ChoiceField(required=True, choices=USER_TYPE_CHOICES, widget=forms.Select(
        attrs={"class": "form-control"}), label=" Select User Type")
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control"}))
    phone = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Phone", "class": "form-control"}), label="Phone No")
    address = forms.CharField(required=True, widget=forms.widgets.TextInput(
        attrs={"placeholder": "Address", "class": "form-control"}), label="Address")
    dob = forms.DateField(required=True, widget=forms.DateInput(
        attrs={'type': 'date', "class": "form-control"}), label="Dob")
    gender = forms.ChoiceField(
        required=True, choices=GENDER_CHOICES, widget=forms.RadioSelect, label="Gender")
    faculty = forms.ChoiceField(required=True, choices=OPTIONS_FACULTY, widget=forms.Select(
        attrs={"class": "form-control"}), label="Faculty")
    semester = forms.ChoiceField(required=True, choices=OPTIONS_SEM, widget=forms.Select(
        attrs={"class": "form-control"}), label="Semester")

    class Meta:
        model = User  # Replace with your actual user model
        fields = ['userType', 'first_name', 'last_name', 'username', 'email',
                  'phone', 'address', 'dob', 'gender', 'faculty', 'semester']
