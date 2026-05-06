from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manager-dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    
    # User Management (Admin)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    
    # Department Management (Admin)
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Payroll Management (Admin)
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/create/', views.payroll_create, name='payroll_create'),
    path('payroll/<int:pk>/payslip/', views.payroll_payslip, name='payroll_payslip'),
    
    # Reports (Admin)
    path('reports/', views.reports_overview, name='reports_overview'),
    path('reports/attendance/', views.attendance_report, name='attendance_report'),
    path('reports/payroll/', views.payroll_report, name='payroll_report'),
    path('reports/performance/', views.performance_report, name='performance_report'),
    
    # Manager URLs
    path('manager/tasks/', views.manager_tasks, name='manager_tasks'),
    path('manager/tasks/create/', views.task_create, name='task_create'),
    path('manager/leaves/', views.manager_leaves, name='manager_leaves'),
    path('manager/leaves/<int:pk>/<str:status>/', views.leave_approve, name='leave_approve'),
    path('manager/attendance/mark/<int:user_id>/', views.manager_mark_attendance, name='manager_mark_attendance'),
    path('profile/<int:pk>/', views.user_profile, name='user_profile'),
    
    # Features
    path('attendance/check/', views.attendance_check, name='attendance_check'),
    path('leave/apply/', views.leave_apply, name='leave_apply'),
    path('my-payrolls/', views.my_payrolls, name='my_payrolls'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('tasks/<int:pk>/status/<str:status>/', views.task_status_update, name='task_status_update'),
]
