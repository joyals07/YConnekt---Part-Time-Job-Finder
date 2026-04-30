from django.shortcuts import render,redirect,get_object_or_404
from datetime import date
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from .models import *
from EmployerApp.models import *
from django.db.models import Avg,Count
from django.utils.timezone import now
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.core.paginator import Paginator

def regEmployee(request):
    gender_choices = EmployeeDB._meta.get_field('gender').choices
    return render(request,"Register_Employee.html",
                  {"today": date.today(),
                   "gender_choices": gender_choices}
                  )

def saveEmployee(request):

    if request.method == "POST":

        name = request.POST.get("yname")
        num = request.POST.get("ynum")
        loc = request.POST.get("yloc")
        dob = request.POST.get("ydob")
        gen = request.POST.get("gender")
        ppic = request.FILES.get("profpic")

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not name or not num or not loc or not dob or not gen or not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("regEmployee")

        if not num.isdigit() or len(num) != 10:
            messages.error(request, "Enter a valid 10 digit phone number.")
            return redirect("regEmployee")


        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect("regEmployee")


        email_regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}\b'
        if not re.match(email_regex, email):
            messages.error(request, "Invalid email format.")
            return redirect("regEmployee")


        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already registered.")
            return redirect("regEmployee")


        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("regEmployee")


        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )


        EmployeeDB.objects.create(
            user=user,
            full_name=name,
            contact_number=num,
            current_location=loc,
            personal_email=email,
            date_of_birth=dob,
            gender=gen,
            profile_picture=ppic
        )

        login(request, user)

        return redirect("EmployeeDash")

    return redirect("regEmployee")


def employeeDashboard(request):
    employee = EmployeeDB.objects.get(user=request.user)

    today = now().date()
    JobDB.objects.filter(closing_date__lt=today).update(is_active=False)

    total_jobs = JobDB.objects.filter(is_active=True).count()

    applied_count = ApplicationDB.objects.filter(user=request.user).count()

    saved_count = SavedJobDB.objects.filter(user=request.user).count()

    return render(request,"Employee_Dashboard.html",
                  {'emp':employee,
                   'total_jobs': total_jobs,
                   'applied_count': applied_count,
                   'saved_count': saved_count})



def jobList(request):

    employee = EmployeeDB.objects.get(user=request.user)

    jobs = JobDB.objects.filter(
        is_paused=False,
        closing_date__gte=now().date()).select_related("employer")

    # 🔍 SEARCH
    query = request.GET.get("q")
    if query:
        jobs = jobs.filter(job_title__icontains=query
        ) | jobs.filter(
            job_location__icontains=query
        ) | jobs.filter(
            employer__store_name__icontains=query
        )

    # 🎯 SORT
    sort = request.GET.get("sort")

    if sort == "new":
        jobs = jobs.order_by("-posted_date")
    elif sort == "old":
        jobs = jobs.order_by("posted_date")
    elif sort == "deadline":
        jobs = jobs.order_by("closing_date")
    else:
        jobs = jobs.order_by("-posted_date")  # default

    # 📄 PAGINATION
    paginator = Paginator(jobs, 10)  # 10 jobs per page
    page_number = request.GET.get("page")
    jobs = paginator.get_page(page_number)

    return render(request, "Job_List.html", {
        'jobs': jobs,
        'emp': employee,
        'query': query,
        'sort': sort
    })

def viewJob(request,job_id):
    employee = EmployeeDB.objects.get(user=request.user)
    job = JobDB.objects.get(id=job_id)

    already_applied = ApplicationDB.objects.filter(
        job=job,
        user=request.user
    ).exists()

    saved = SavedJobDB.objects.filter(
        job=job,
        user=request.user
    ).exists()

    requirements = []
    if job.job_requirement:
        requirements = job.job_requirement.splitlines()

    return render(request,"View_Job.html",
                  {'job':job,
                   'job_id': job.id,
                   "requirements": requirements,
                   'already_applied': already_applied,
                   'saved': saved,
                   'emp': employee
                   })

def toggleSaveJob(request, job_id):
    job = get_object_or_404(JobDB, id=job_id)
    saved = SavedJobDB.objects.filter(
        job=job,
        user=request.user
    )
    if saved.exists():
        saved.delete()   # Unsave
    else:
        SavedJobDB.objects.create(
            job=job,
            user=request.user
        )
    return redirect('ViewJob', job_id=job.id)

def applicationForm(request, job_id):
    job = get_object_or_404(JobDB, id=job_id)
    yemp = EmployeeDB.objects.get(user=request.user)
    dob = yemp.date_of_birth

    today = date.today()
    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return render(request, "Application_Form.html", {
        'job': job,
        'job_id': job.id,
        'emp' : yemp,
        'age': age
    })

def sendApplication(request, job_id):
    job = get_object_or_404(JobDB, id=job_id)
    yemp = EmployeeDB.objects.get(user=request.user)

    if request.method == 'POST':
        resume = request.FILES.get("resume")
        cover = request.POST.get("cover_letter")
        age = request.POST.get("age")

        # Validation
        contact = request.POST.get("contact")
        email = request.POST.get("email")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return redirect("Application", job_id=job.id)

        if not contact.isdigit() or len(contact) != 10:
            messages.error(request, "Enter a valid 10 digit phone number.")
            return redirect("Application", job_id=job.id)

        ApplicationDB.objects.create(
            job=job,
            user=request.user,
            resume=resume,
            cover_letter=cover,
            age=age
        )

        messages.success(request, "Application submitted successfully.")

        return redirect("ViewJob", job_id=job.id)

    return render(request, "Application_Form.html", {
        'job': job,
        'job_id': job.id,
        'emp': yemp
    })



def appliedJobs(request):
    employee = EmployeeDB.objects.get(user=request.user)
    applications = ApplicationDB.objects.filter(user=request.user).select_related('job').order_by('-id')
    return render(request, "Applied_Jobs.html",
                  {'applications': applications,'emp':employee})


def savedJobs(request):
    employee = EmployeeDB.objects.get(user=request.user)

    SavedJobDB.objects.filter(job__closing_date__lt=now().date()).delete()

    saved_jobs = SavedJobDB.objects.filter(
        user=request.user
    ).select_related('job').order_by('-created_at')

    return render(request, "Saved_Jobs.html", {
        'saved_jobs': saved_jobs,'emp':employee
    })



def aboutPage(request):
    employee = EmployeeDB.objects.get(user=request.user)
    applications = ApplicationDB.objects.filter(user=request.user)

    rating_data = ApplicantRating.objects.filter(
        application__in=applications).aggregate(
            average=Avg('rating'),
            total=Count('id')
        )

    average_rating = rating_data['average']
    total_ratings = rating_data['total']

    return render(request,"About.html",
                  {'emp':employee,
                   "average_rating": average_rating,
                   "total_ratings": total_ratings
                   })

def editProfile(request):
    emp = get_object_or_404(EmployeeDB, user=request.user)
    gender_choices = EmployeeDB._meta.get_field('gender').choices

    if request.method == "POST":

        name = request.POST.get("full_name")
        location = request.POST.get("current_location")
        phone = request.POST.get("contact_number")
        email = request.POST.get("personal_email")
        dob = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")

        if not name or not location or not phone or not email or not dob or not gender:
            messages.error(request, "All fields are required.")
            return redirect("EditProfile")

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Enter a valid 10 digit phone number.")
            return redirect("EditProfile")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return redirect("EditProfile")

        emp.full_name = name
        emp.current_location = location
        emp.contact_number = phone
        emp.personal_email = email
        emp.date_of_birth = dob
        emp.gender = gender

        if request.FILES.get("profile_picture"):
            emp.profile_picture = request.FILES.get("profile_picture")
        emp.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("About")

    return render(request, "Edit_About.html", {
        "emp": emp,
        "gender_choices": gender_choices
    })



