# Employee Management System Setup Guide

You have successfully generated the Django project. Since you are using MySQL, please follow these steps to connect your database and start the application.

## 1. Configure MySQL Database
1. Open **MySQL Workbench**.
2. Connect to your local MySQL server.
3. Open a new SQL tab and run the following command to create the database:
   ```sql
   CREATE DATABASE employee_db;
   ```
   *(Note: The database name `employee_db` is configured in `employee_project/settings.py`. If you used a different name, username, or password, please update the `DATABASES` dictionary in `settings.py` to match)*.

## 2. Install Project Dependencies
Open your Command Prompt or PowerShell, navigate to the project directory, activate the virtual environment, and ensure the dependencies are installed:
```powershell
cd c:\Users\User\OneDrive\Desktop\Employee_project
.\venv\Scripts\activate
pip install Django pymysql
```

## 3. Apply Database Migrations
With the virtual environment activated, navigate into the project root and create the tables in your newly created MySQL database:
```powershell
cd employee_project
python manage.py makemigrations employees
python manage.py migrate
```

## 4. Create Predefined Users
We have created a helper script to automatically generate the 3 required users: Admin, Manager, and Employee.
Run the following command:
```powershell
python create_users.py
```
**Credentials Created:**
- Admin: `admin` / `admin123` (Full CRUD + User Management)
- Manager: `manager` / `manager123` (Add/Edit Employees)
- Employee: `employee` / `employee123` (View Only)

## 5. Run the Development Server
Start the Django application:
```powershell
python manage.py runserver
```

You can now open a web browser and navigate to `http://127.0.0.1:8000/login/` to use the Employee Management System!
