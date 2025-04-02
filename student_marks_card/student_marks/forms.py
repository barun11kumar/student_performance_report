from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from .models import StudentClass, Course, Session, Subject, Student, Marks

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.Select(choices=[
                ('Student', 'Student'),
                ('Teacher', 'Teacher'),
                ('Admin', 'Admin')
            ])
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ChoiceField(choices=[
        ('Student', 'Student'),
        ('Teacher', 'Teacher'),
        ('Admin', 'Admin')
    ], required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Add user to appropriate group
            role = self.cleaned_data['role']
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)
            
            # Create associated Student or Teacher profile if needed
            if role == 'Student':
                Student.objects.create(
                    user=user,
                    student_id=user.username,
                    full_name=f"{user.first_name} {user.last_name}"
                )
            elif role == 'Teacher':
                # Add any teacher-specific profile creation here if needed
                pass
                
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'password']

class ImportDataForm(forms.Form):
    session = forms.ModelChoiceField(queryset=Session.objects.all(), label="Session", required=True)
    student_class = forms.ModelChoiceField(queryset=StudentClass.objects.all(), label="Class", required=True)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Course", required=True)
    excel_file = forms.FileField(label="Upload Excel File")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize student_class queryset
        self.fields['student_class'].queryset = StudentClass.objects.all()
        # Initialize course queryset
        self.fields['course'].queryset = Course.objects.all()

        if 'session' in self.data:
            try:
                session_id = int(self.data.get('session'))
                self.fields['student_class'].queryset = StudentClass.objects.filter(session_id=session_id)
            except (ValueError, TypeError):
                pass
        
        if 'student_class' in self.data:
            try:
                student_class_id = int(self.data.get('student_class'))
                self.fields['course'].queryset = Course.objects.filter(student_class_id=student_class_id)
            except (ValueError, TypeError):
                pass

class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20, required=True)
    session = forms.ModelChoiceField(queryset=Session.objects.all(), required=True)
    student_class = forms.ModelChoiceField(queryset=StudentClass.objects.all(), required=True)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), required=True)
    
    class Meta:
        model = User
        fields = ('student_id', 'session', 'student_class', 'course', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student_id'].widget.attrs.update({'class': 'form-control'})
        self.fields['session'].widget.attrs.update({'class': 'form-control'})
        self.fields['student_class'].widget.attrs.update({'class': 'form-control'})
        self.fields['course'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['student_id']  # Use student_id as username
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
            # Create Student profile
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                session=self.cleaned_data['session'],
                student_class=self.cleaned_data['student_class'],
                course=self.cleaned_data['course']
            )
        return user


