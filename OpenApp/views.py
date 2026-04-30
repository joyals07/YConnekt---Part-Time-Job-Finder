from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import ContactMessage
from EmployerApp.models import EmployerDB, JobDB
from EmployeeApp.models import EmployeeDB, ApplicationDB
from django.contrib import messages
import re

def indexPage(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not name:
            messages.error(request, "Name is required.")
            return redirect("IndexPage")


        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, email):
            messages.error(request, "Enter a valid email address.")
            return redirect("IndexPage")

        if not message:
            messages.error(request, "Message cannot be empty.")
            return redirect("IndexPage")


        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )

        return redirect("IndexPage")
    return render(request,"Landing_Page.html")

def signupPage(request):
    return render(request,"SignupPage.html")

def loginUser(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        passwd = request.POST.get("password")

        if not uname or not passwd:
            messages.error(request, "All fields are required.")
            return render(request, "SignupPage.html")

        try:
            user_obj = User.objects.get(email=uname)
            uname = user_obj.username
        except User.DoesNotExist:
            pass

        user = authenticate(request, username=uname, password=passwd)

        if user is not None:
            login(request, user)

            if user.is_superuser:
                return redirect("adminPage")
            elif EmployerDB.objects.filter(user=user).exists():
                return redirect("EmpDash")
            elif EmployeeDB.objects.filter(user=user).exists():
                return redirect("EmployeeDash")

            return redirect("Signup")

        messages.error(request, "Invalid Username/Email or Password")
        return render(request, "SignupPage.html")

    return render(request, "SignupPage.html")

def logoutUser(request):
    logout(request)
    return redirect("SignUp")




def adminPage(request):
    total_jobs = JobDB.objects.count()
    total_employees = EmployeeDB.objects.count()
    total_employers = EmployerDB.objects.count()
    total_applications = ApplicationDB.objects.count()

    context = {
        "total_jobs": total_jobs,
        "total_employees": total_employees,
        "total_employers": total_employers,
        "total_applications": total_applications
    }

    return render(request,"AdminPage.html",context)

def messageList(request):
    messages_list = ContactMessage.objects.all().order_by('-sent_at')

    return render(request, "Messages.html", {
        "messages_list": messages_list
    })

def employerList(request):
    employers = EmployerDB.objects.all().order_by('-id')

    return render(request, "Employer_List.html", {
        "employers": employers
    })

def employeeList(request):
    employees = EmployeeDB.objects.all().order_by('-id')

    return render(request, "Employee_List.html", {
        "employees": employees
    })

def jobListAdmin(request):
    jobs = JobDB.objects.select_related('employer').all().order_by('-posted_date')

    return render(request, "All_Jobs.html", {
        "jobs": jobs
    })

def applicationList(request):
    applications = ApplicationDB.objects.select_related(
        'user',
        'job',
        'job__employer'
    ).all().order_by('-id')

    return render(request, "Applications_List.html", {
        "applications": applications
    })