from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Department, Attendance, Leave, Payroll, Task, PerformanceReview
from .forms import UserForm, ProfileForm, LeaveForm, TaskForm, DepartmentForm, PayrollForm, PerformanceReviewForm
from django.utils import timezone
from functools import wraps
from django.db.models import Sum, Count, Avg

# Decorators for RBAC
def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "You do not have permission to access this page.")
                return redirect('dashboard')
        return _wrapped_view
    return decorator

# Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'employees/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_redirect(request):
    role = request.user.profile.role
    if role == 'ADMIN':
        return redirect('admin_dashboard')
    elif role == 'MANAGER':
        return redirect('manager_dashboard')
    else:
        return redirect('employee_dashboard')

# Admin Views
@login_required
@role_required(['ADMIN'])
def admin_dashboard(request):
    total_users = User.objects.count()
    total_departments = Department.objects.count()
    pending_leaves = Leave.objects.filter(status='PENDING').count()
    
    # Attendance Summary (Today)
    today = timezone.now().date()
    present_today = Attendance.objects.filter(date=today, check_in__isnull=False).count()
    
    # Payroll Summary (Total net pay for current month)
    current_month = timezone.now().strftime('%B')
    total_payroll = Payroll.objects.filter(month=current_month).aggregate(Sum('net_pay'))['net_pay__sum'] or 0
    
    context = {
        'total_users': total_users,
        'total_departments': total_departments,
        'pending_leaves': pending_leaves,
        'present_today': present_today,
        'total_payroll': total_payroll,
    }
    return render(request, 'employees/admin_dashboard.html', context)

# User Management
@login_required
@role_required(['ADMIN'])
def user_list(request):
    users = User.objects.all().select_related('profile')
    return render(request, 'employees/user_list.html', {'users': users})

@login_required
@role_required(['ADMIN'])
def user_create(request):
    if request.method == 'POST':
        u_form = UserForm(request.POST)
        p_form = ProfileForm(request.POST)
        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save(commit=False)
            user.set_password(u_form.cleaned_data['password'])
            user.save()
            # Profile is created by signal, but we update it with p_form data
            profile = user.profile
            p_form_instance = ProfileForm(request.POST, instance=profile)
            if p_form_instance.is_valid():
                p_form_instance.save()
            messages.success(request, "User created successfully.")
            return redirect('user_list')
    else:
        u_form = UserForm()
        p_form = ProfileForm()
    return render(request, 'employees/user_form.html', {'u_form': u_form, 'p_form': p_form, 'title': 'Create User'})

@login_required
@role_required(['ADMIN'])
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        u_form = UserForm(request.POST, instance=user)
        p_form = ProfileForm(request.POST, instance=user.profile)
        # Make password optional for edit
        u_form.fields['password'].required = False
        
        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save(commit=False)
            password = u_form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            else:
                # If password is not provided, keep the old one
                user.password = User.objects.get(pk=user.pk).password
            user.save()
            p_form.save()
            messages.success(request, "User updated successfully.")
            return redirect('user_list')
    else:
        u_form = UserForm(instance=user)
        u_form.fields['password'].required = False
        p_form = ProfileForm(instance=user.profile)
    return render(request, 'employees/user_form.html', {'u_form': u_form, 'p_form': p_form, 'title': 'Edit User'})

@login_required
@role_required(['ADMIN'])
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('user_list')

# Department Management
@login_required
@role_required(['ADMIN'])
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'employees/department_list.html', {'departments': departments})

@login_required
@role_required(['ADMIN'])
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully.")
            return redirect('department_list')
    else:
        form = DepartmentForm()
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Create Department'})

@login_required
@role_required(['ADMIN'])
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully.")
            return redirect('department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'employees/department_form.html', {'form': form, 'title': 'Edit Department'})

@login_required
@role_required(['ADMIN'])
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.delete()
    messages.success(request, "Department deleted successfully.")
    return redirect('department_list')

# Payroll Management
@login_required
@role_required(['ADMIN'])
def payroll_list(request):
    payrolls = Payroll.objects.all().order_by('-payment_date')
    return render(request, 'employees/payroll_list.html', {'payrolls': payrolls})

@login_required
@role_required(['ADMIN'])
def payroll_create(request):
    if request.method == 'POST':
        form = PayrollForm(request.POST)
        if form.is_valid():
            payroll = form.save(commit=False)
            payroll.net_pay = payroll.base_salary + payroll.bonuses - payroll.deductions
            payroll.save()
            messages.success(request, "Payroll record created.")
            return redirect('payroll_list')
    else:
        form = PayrollForm()
    return render(request, 'employees/payroll_form.html', {'form': form})

@login_required
def payroll_payslip(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    # Check if user is admin OR the employee themselves
    if request.user.profile.role != 'ADMIN' and request.user != payroll.user:
        messages.error(request, "You do not have permission to view this payslip.")
        return redirect('dashboard')
    return render(request, 'employees/payroll_payslip.html', {'payroll': payroll})

# Reports
@login_required
@role_required(['ADMIN'])
def reports_overview(request):
    return render(request, 'employees/reports_overview.html')

@login_required
@role_required(['ADMIN'])
def attendance_report(request):
    today = timezone.localdate()
    # Get all staff (Employees and Managers)
    employees = User.objects.filter(profile__role__in=['EMPLOYEE', 'MANAGER']).select_related('profile', 'profile__department')
    
    # Get today's attendance records
    attendance_today = Attendance.objects.filter(date=today).select_related('user')
    attendance_map = {a.user_id: a for a in attendance_today}
    
    # Build list with status
    report_list = []
    for emp in employees:
        att = attendance_map.get(emp.id)
        report_list.append({
            'employee': emp,
            'status': att.status if att else 'ABSENT',
            'check_in': att.check_in if att else None,
            'check_out': att.check_out if att else None,
        })
        
    attendance_stats = Attendance.objects.filter(date=today).values('status').annotate(count=Count('id'))
    
    return render(request, 'employees/attendance_report.html', {
        'report_list': report_list,
        'attendance_stats': attendance_stats,
        'today': today
    })

@login_required
@role_required(['ADMIN'])
def payroll_report(request):
    payroll_history = Payroll.objects.values('month').annotate(total_pay=Sum('net_pay'))
    return render(request, 'employees/payroll_report.html', {'payroll_history': payroll_history})

@login_required
@role_required(['ADMIN'])
def performance_report(request):
    performance_data = PerformanceReview.objects.values('user__username').annotate(avg_rating=Avg('rating'))
    return render(request, 'employees/performance_report.html', {'performance_data': performance_data})

# Manager Views
@login_required
@role_required(['MANAGER', 'ADMIN'])
def manager_dashboard(request):
    dept = request.user.profile.department
    team_members = Profile.objects.filter(department=dept).exclude(user=request.user).select_related('user')
    tasks = Task.objects.filter(assigned_by=request.user).order_by('-created_at')[:5]
    pending_leaves = Leave.objects.filter(user__profile__department=dept, status='PENDING').count()
    
    # Today's attendance for team
    today = timezone.localdate()
    if dept:
        team_attendance = Attendance.objects.filter(date=today, user__profile__department=dept).select_related('user')
    else:
        team_attendance = Attendance.objects.none()
        
    attendance_map = {a.user_id: a for a in team_attendance}
    
    present_count = team_attendance.filter(status='PRESENT').count()
    
    # Prepare team list with attendance status
    team_list = []
    for member in team_members:
        att = attendance_map.get(member.user_id)
        team_list.append({
            'profile': member,
            'attendance': att,
        })
    
    context = {
        'team_list': team_list,
        'tasks': tasks,
        'department': dept,
        'pending_leaves': pending_leaves,
        'present_count': present_count,
        'total_team': team_members.count(),
    }
    return render(request, 'employees/manager_dashboard.html', context)

@login_required
@role_required(['MANAGER', 'ADMIN'])
def user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    # If manager, check if employee is in the same department
    if request.user.profile.role == 'MANAGER' and user.profile.department != request.user.profile.department:
        messages.error(request, "You can only view profiles of employees in your department.")
        return redirect('manager_dashboard')
    
    tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')[:5]
    attendance = Attendance.objects.filter(user=user).order_by('-date')[:5]
    leaves = Leave.objects.filter(user=user).order_by('-start_date')[:5]
    
    context = {
        'employee': user,
        'tasks': tasks,
        'attendance': attendance,
        'leaves': leaves,
    }
    return render(request, 'employees/user_profile.html', context)

@login_required
@role_required(['MANAGER', 'ADMIN'])
def manager_mark_attendance(request, user_id):
    user_to_mark = get_object_or_404(User, id=user_id)
    # Check if manager is in the same department
    if request.user.profile.role != 'ADMIN' and request.user.profile.department != user_to_mark.profile.department:
        messages.error(request, "You can only mark attendance for employees in your department.")
        return redirect('manager_dashboard')
    
    today = timezone.localdate()
    attendance, created = Attendance.objects.get_or_create(user=user_to_mark, date=today)
    
    action = request.POST.get('action')
    if action == 'check_in':
        attendance.check_in = timezone.localtime().time()
        attendance.status = 'PRESENT'
        attendance.save()
        messages.success(request, f"Marked {user_to_mark.username} as Present.")
    elif action == 'check_out':
        attendance.check_out = timezone.localtime().time()
        attendance.save()
        messages.success(request, f"Marked check-out for {user_to_mark.username}.")
        
    return redirect('manager_dashboard')

@login_required
@role_required(['MANAGER', 'ADMIN'])
def manager_tasks(request):
    tasks = Task.objects.filter(assigned_by=request.user).order_by('-created_at')
    return render(request, 'employees/manager_tasks.html', {'tasks': tasks})

@login_required
@role_required(['MANAGER', 'ADMIN'])
def task_create(request):
    user_role = request.user.profile.role
    dept = request.user.profile.department
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
    else:
        form = TaskForm()

    # Filter the assigned_to queryset based on role
    if user_role == 'ADMIN':
        # Admin can assign to any employee
        form.fields['assigned_to'].queryset = User.objects.all().exclude(id=request.user.id)
    elif dept:
        # Manager can assign to their department
        form.fields['assigned_to'].queryset = User.objects.filter(profile__department=dept).exclude(id=request.user.id)
    
    if request.method == 'POST' and form.is_valid():
        task = form.save(commit=False)
        task.assigned_by = request.user
        task.save()
        messages.success(request, "Task assigned successfully.")
        return redirect('dashboard')
        
    return render(request, 'employees/task_form.html', {'form': form})

@login_required
@role_required(['MANAGER', 'ADMIN'])
def manager_leaves(request):
    dept = request.user.profile.department
    leaves = Leave.objects.filter(user__profile__department=dept).order_by('-start_date')
    return render(request, 'employees/manager_leaves.html', {'leaves': leaves})

@login_required
@role_required(['MANAGER', 'ADMIN'])
def leave_approve(request, pk, status):
    leave = get_object_or_404(Leave, pk=pk)
    if leave.user.profile.department != request.user.profile.department and request.user.profile.role != 'ADMIN':
        messages.error(request, "You do not have permission to manage this leave.")
        return redirect('dashboard')
    
    if status in ['APPROVED', 'REJECTED']:
        leave.status = status
        leave.save()
        messages.success(request, f"Leave {status.lower()} successfully.")
    return redirect('manager_leaves')

# Employee Views
@login_required
def employee_dashboard(request):
    user = request.user
    tasks = Task.objects.filter(assigned_to=user, status__in=['PENDING', 'IN_PROGRESS'])
    leaves = Leave.objects.filter(user=user).order_by('-start_date')[:5]
    attendance = Attendance.objects.filter(user=user, date=timezone.localdate()).first()
    payrolls = Payroll.objects.filter(user=user).order_by('-payment_date')[:3]
    context = {
        'tasks': tasks,
        'leaves': leaves,
        'attendance': attendance,
        'payrolls': payrolls,
    }
    return render(request, 'employees/employee_dashboard.html', context)

@login_required
def my_payrolls(request):
    payrolls = Payroll.objects.filter(user=request.user).order_by('-payment_date')
    return render(request, 'employees/my_payrolls.html', {'payrolls': payrolls})

@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user).order_by('status', 'due_date')
    return render(request, 'employees/my_tasks.html', {'tasks': tasks})

@login_required
def task_status_update(request, pk, status):
    task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
    if status in ['PENDING', 'IN_PROGRESS', 'COMPLETED']:
        task.status = status
        task.save()
        messages.success(request, f"Task updated to {status.replace('_', ' ').title()}")
    return redirect('my_tasks')

from django.db import IntegrityError

@login_required
def attendance_check(request):
    user = request.user
    today = timezone.localdate()
    
    try:
        attendance, created = Attendance.objects.get_or_create(user=user, date=today)
    except IntegrityError:
        attendance = Attendance.objects.get(user=user, date=today)
    
    if 'check_in' in request.POST:
        attendance.check_in = timezone.localtime().time()
        attendance.status = 'PRESENT'
        attendance.save()
        messages.success(request, f"Checked in successfully at {attendance.check_in.strftime('%H:%M')}")
    elif 'check_out' in request.POST:
        attendance.check_out = timezone.localtime().time()
        attendance.save()
        messages.success(request, f"Checked out successfully at {attendance.check_out.strftime('%H:%M')}")
        
    return redirect('employee_dashboard')

@login_required
def leave_apply(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            messages.success(request, "Leave application submitted.")
            return redirect('employee_dashboard')
    else:
        form = LeaveForm()
    return render(request, 'employees/leave_form.html', {'form': form})
