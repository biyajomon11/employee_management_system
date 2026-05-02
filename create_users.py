import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_project.settings')
django.setup()

from django.contrib.auth.models import User

def create_predefined_users():
    users = [
        {'username': 'admin', 'password': 'admin123', 'is_superuser': True, 'is_staff': True},
        {'username': 'manager', 'password': 'manager123', 'is_superuser': False, 'is_staff': True},
        {'username': 'employee', 'password': 'employee123', 'is_superuser': False, 'is_staff': False},
    ]

    for user_data in users:
        username = user_data['username']
        # Check if user already exists
        if not User.objects.filter(username=username).exists():
            print(f"Creating user: {username}...")
            user = User.objects.create_user(
                username=username,
                password=user_data['password'],
                is_superuser=user_data['is_superuser'],
                is_staff=user_data['is_staff']
            )
            user.save()
            print(f"SUCCESS: User '{username}' created successfully.")
        else:
            print(f"INFO: User '{username}' already exists.")

if __name__ == '__main__':
    print("Initializing predefined users...")
    create_predefined_users()
    print("Done.")
