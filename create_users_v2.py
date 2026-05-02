import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_project.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Profile, Department

def create_users():
    # Create Departments
    it_dept, _ = Department.objects.get_or_create(name='IT', description='Information Technology')
    hr_dept, _ = Department.objects.get_or_create(name='HR', description='Human Resources')
    
    # Create Admin
    admin_user, created = User.objects.get_or_create(username='admin', email='admin@example.com')
    if created:
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        profile = admin_user.profile
        profile.role = 'ADMIN'
        profile.save()
        print("Admin created: admin / admin123")
    
    # Create Manager
    manager_user, created = User.objects.get_or_create(username='manager', email='manager@example.com')
    if created:
        manager_user.set_password('manager123')
        manager_user.save()
        profile = manager_user.profile
        profile.role = 'MANAGER'
        profile.department = it_dept
        profile.save()
        print("Manager created: manager / manager123")
        
    # Create Employee
    employee_user, created = User.objects.get_or_create(username='employee', email='employee@example.com')
    if created:
        employee_user.set_password('employee123')
        employee_user.save()
        profile = employee_user.profile
        profile.role = 'EMPLOYEE'
        profile.department = it_dept
        profile.save()
        print("Employee created: employee / employee123")

if __name__ == '__main__':
    create_users()
