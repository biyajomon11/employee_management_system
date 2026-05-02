from django import forms
from django.contrib.auth.models import User
from .models import Profile, Department, Leave, Task, Attendance, Payroll, PerformanceReview

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.fields:
            self.fields['department'].empty_label = "Select Department"

    class Meta:
        model = Profile
        fields = ['role', 'department', 'job_title', 'phone', 'address', 'salary', 'date_of_joining']
        widgets = {
            'date_of_joining': forms.DateInput(attrs={'type': 'date'}),
        }

class LeaveForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'leave_type' in self.fields:
            self.fields['leave_type'].choices = [('', 'Select Leave Type')] + list(self.fields['leave_type'].choices)[1:]

    class Meta:
        model = Leave
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'assigned_to' in self.fields:
            self.fields['assigned_to'].empty_label = "Select Employee"

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class DepartmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'manager' in self.fields:
            self.fields['manager'].empty_label = "Select Manager"

    class Meta:
        model = Department
        fields = ['name', 'description', 'manager']

class PayrollForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields['user'].empty_label = "Select Employee"

    class Meta:
        model = Payroll
        fields = ['user', 'base_salary', 'bonuses', 'deductions', 'month']

class PerformanceReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'user' in self.fields:
            self.fields['user'].empty_label = "Select Employee"

    class Meta:
        model = PerformanceReview
        fields = ['user', 'rating', 'comments']
