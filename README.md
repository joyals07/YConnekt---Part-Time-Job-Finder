# YConnekt---Part-Time-Job-Finder

YConneckt is a Django job portal connecting employees and employers. It supports registration, login, job posting/search, applications, saved jobs, applicant management, dashboards, profiles, ratings, and REST APIs, making it a practical end-to-end web application.

## Features

\- Employee and employer registration/login

\- Role-based dashboards

\- Job posting, editing, deleting, pause/resume

\- Job search, sorting, and pagination

\- Job application with resume upload

\- Saved jobs for employees

\- Saved applicants for employers

\- Applicant rating system

\- Admin-side listing pages

\- REST API with JWT authentication





## Tech Stack



\- Python

\- Django

\- Django REST Framework

\- Simple JWT Authentication

\- SQLite database

\- HTML, CSS, Bootstrap/Material Dashboard

\- Pillow for image uploads

\- Gunicorn for production server support




## Main Packages Used



Django

djangorestframework

djangorestframework\_simplejwt

Pillow

gunicorn

PyJWT

sqlparse

asgiref







## Project Workflow



* Users can register as employee or employer.
* Employers can create and manage job posts.
* Employees can browse jobs, view details, save jobs, and apply.
* Employers can view applications, open applicant profiles, save applicants, and rate them.
* Dashboard pages show key counts like active jobs, saved jobs, applications, and posted jobs.
* REST APIs are available under /api/ for authentication, jobs, profiles, dashboards, applications, and saved items.




## Important URLs



* /YConnekt/Index/             Landing page
* /YConnekt/Login/             Login
* /YConnekt/SignUp/            Signup
* /Employee/EmployeeDashboard/ Employee dashboard
* /Employer/EmployerDashboard/ Employer dashboard
* /api/login/                  API JWT login
* /api/jobs/                   API job list





## Local Setup



* git clone <your-repo-url>
* cd YConneckt
* python -m venv .venv
* .venv\\Scripts\\activate
* pip install -r requirements.txt
* python manage.py migrate
* python manage.py runserver







## Email Configuration



This project uses email notifications for:



* New job posts
* New job applications



In settings.py, use environment variables:



&#x09;**EMAIL\_HOST\_USER = os.environ.get("EMAIL\_HOST\_USER")**

&#x09;**EMAIL\_HOST\_PASSWORD = os.environ.get("EMAIL\_HOST\_PASSWORD")**

&#x09;**DEFAULT\_FROM\_EMAIL = EMAIL\_HOST\_USER**



Use a Gmail App Password, not your real Gmail password.









## Deployment Notes



Before deploying, update settings.py to use production-safe values:



&#x09;**SECRET\_KEY = os.environ.get("SECRET\_KEY")**



&#x09;**DEBUG = os.environ.get("DEBUG", "False") == "True"**



&#x09;**ALLOWED\_HOSTS = os.environ.get(**

&#x20;   		**"ALLOWED\_HOSTS",**

&#x20;   		**"127.0.0.1,localhost"**

&#x09;**).split(",")**



For Render or similar hosting, set environment variables like:





&#x09;**SECRET\_KEY=your-production-secret-key**

&#x09;**DEBUG=False**

&#x09;**ALLOWED\_HOSTS=your-app-name.onrender.com**

&#x09;**EMAIL\_HOST\_USER=your-email@gmail.com**

&#x09;**EMAIL\_HOST\_PASSWORD=your-gmail-app-password**





* **Production start command:**



&#x09;gunicorn YConneckt.wsgi:application



* **Build command example:**



&#x09;pip install -r requirements.txt \&\& python manage.py collectstatic --noinput \&\& python manage.py migrate











