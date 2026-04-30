from django.shortcuts import render, redirect, get_object_or_404
from datetime import date, datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from django.contrib import messages
from EmployerApp.models import EmployerDB, JobDB, SavedApplicantDB, ApplicantRating
from EmployeeApp.models import ApplicationDB, EmployeeDB
from django.utils.timezone import now
from django.db.models import Avg, Count
import re


def registerEmployer(request):
    return render(request,"Register_Employer.html")

def saveEmployer(request):
    if request.method == 'POST':

        name = request.POST.get("compname")
        loc = request.POST.get("comploc")
        desc = request.POST.get("compdesc")
        web = request.POST.get("compweb")
        logo = request.FILES.get("storelogo")
        num = request.POST.get("compnum")

        username = request.POST.get("username")
        email = request.POST.get("compemail")
        password = request.POST.get("password")

        if not name or not loc or not desc or not num or not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("regEmp")

        if not num.isdigit() or len(num) != 10:
            messages.error(request, "Enter a valid 10 digit contact number.")
            return redirect("regEmp")

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect("regEmp")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("regEmp")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("regEmp")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        EmployerDB.objects.create(
            user=user,
            store_name=name,
            store_location=loc,
            store_description=desc,
            website=web,
            business_email=email,
            store_logo=logo,
            contact_number=num
        )

        login(request, user)

        return redirect("EmpDash")

    return redirect("regEmp")


def employerDashboard(request):
    employer = EmployerDB.objects.get(user=request.user)

    total_jobs = JobDB.objects.filter(employer=employer,is_active=True).count()
    total_applications = ApplicationDB.objects.filter(job__employer=employer).count()

    return render(request,"Employer_Dash.html",
                  {'emp':employer,
                   "total_jobs": total_jobs,
                   "total_applications": total_applications})



def showJobs(request):
    employer = EmployerDB.objects.get(user=request.user)

    jobs = JobDB.objects.filter(
        employer=employer,
        closing_date__gte=now().date()).select_related("employer")

    expired_jobs = JobDB.objects.filter(
        employer=employer,
        closing_date__lt=now().date()).select_related("employer")


    return render(request,"Show_Jobs.html",
                  {'jobs':jobs,'emp':employer,'expired_jobs': expired_jobs})


def showActiveJob(request, job_id):
    employer = EmployerDB.objects.get(user=request.user)

    job = JobDB.objects.select_related("employer").get(
        id=job_id, employer=employer
    )

    total_applications = ApplicationDB.objects.filter(job=job).count()

    requirements = []
    if job.job_requirement:
        requirements = job.job_requirement.strip().splitlines()

    return render(request, "Show_Active_Job.html", {
        'job': job,
        'emp': employer,
        'requirements': requirements,
        "total_applications": total_applications
    })



def postJob(request):
    employer = EmployerDB.objects.get(user=request.user)
    return render(request, "Add_Job.html",
          {'jobtype':JobDB.JobTypeChoices,
                   'today': date.today().isoformat(),
                   'emp': employer
                   })

def saveJob(request):

    if request.method == 'POST':

        title = request.POST.get("JobTitle")
        loc = request.POST.get("JobLocation")
        jtype = request.POST.get("JobType")
        clsdate = request.POST.get("JobClosingDate")
        desc = request.POST.get("JobDesc")
        req = request.POST.get("JobReq")

        # Validation
        if not title or not loc or not jtype or not clsdate:
            messages.error(request, "All fields are required.")
            return redirect("PostJob")

        if len(title) < 3:
            messages.error(request, "Job title must be at least 3 characters.")
            return redirect("PostJob")

        if clsdate < str(now().date()):
            messages.error(request, "Closing date cannot be in the past.")
            return redirect("PostJob")

        employer = EmployerDB.objects.get(user=request.user)

        JobDB.objects.create(
            job_title=title,
            job_location=loc,
            job_type=jtype,
            job_description=desc,
            job_requirement=req,
            closing_date=clsdate,
            employer=employer
        )

        messages.success(request, "Job posted successfully!")

        return redirect("OurJobs")


def editJob(request, job_id):

    employer = EmployerDB.objects.get(user=request.user)
    job = get_object_or_404(JobDB, id=job_id, employer=employer)

    jobtypes = JobDB._meta.get_field('job_type').choices

    if request.method == "POST":

        title = request.POST.get("JobTitle")
        loc = request.POST.get("JobLocation")
        jtype = request.POST.get("JobType")
        desc = request.POST.get("JobDesc")
        req = request.POST.get("JobReq")
        clsdate = request.POST.get("JobClosingDate")

        # 🔍 Validation
        if not title or not loc or not jtype or not clsdate:
            messages.error(request, "All fields are required.")
            return redirect("EditJob", job_id=job.id)

        if len(title) < 3:
            messages.error(request, "Job title must be at least 3 characters.")
            return redirect("EditJob", job_id=job.id)

        # Convert to date
        try:
            clsdate_obj = datetime.strptime(clsdate, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("EditJob", job_id=job.id)

        if clsdate_obj < now().date():
            messages.error(request, "Closing date cannot be in the past.")
            return redirect("EditJob", job_id=job.id)

        # ✅ Save fields
        job.job_title = title
        job.job_location = loc
        job.job_type = jtype
        job.job_description = desc
        job.job_requirement = req
        job.closing_date = clsdate_obj

        # 🔥 SMART LOGIC (not forced)
        if clsdate_obj >= now().date():
            job.is_active = True

        job.save()

        messages.success(request, "Job updated successfully.")

        return redirect("showJob", job_id=job.id)

    return render(request, "Edit_Job.html", {
        "job": job,
        "jobtypes": jobtypes
    })

def deleteJob(request,id):
    employer = EmployerDB.objects.get(user=request.user)
    job = get_object_or_404(JobDB, id=id, employer=employer)
    job.delete()

    return redirect('OurJobs')

def toggleJobStatus(request,id):
    employer = EmployerDB.objects.get(user=request.user)
    job = get_object_or_404(JobDB, id=id, employer=employer)

    job.is_paused = not job.is_paused
    job.save()

    return redirect(request.META.get('HTTP_REFERER'))



def profilePage(request):
    employer = EmployerDB.objects.get(user=request.user)
    return render(request,"Profile.html",
                  {'emp':employer})

def editProfile(request):
    emp = get_object_or_404(EmployerDB, user=request.user)
    if request.method == "POST":
        name = request.POST.get("store_name")
        location = request.POST.get("store_location")
        phone = request.POST.get("contact_number")
        email = request.POST.get("business_email")
        website = request.POST.get("website")
        desc = request.POST.get("store_description")

        # Validation
        if not name or not location or not phone or not email:
            messages.error(request, "Required fields cannot be empty.")
            return redirect("EditProfilePage")

        if not phone.isdigit() or len(phone) != 10:
            messages.error(request, "Enter a valid 10 digit phone number.")
            return redirect("EditProfilePage")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, "Enter a valid email address.")
            return redirect("EditProfilePage")

        emp.store_name = name
        emp.store_location = location
        emp.contact_number = phone
        emp.business_email = email
        emp.website = website
        emp.store_description = desc

        if request.FILES.get("store_logo"):
            emp.store_logo = request.FILES.get("store_logo")
        emp.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("ProfilePage")

    return render(request, "Edit_Employer.html", {"emp": emp})



def viewApplications(request):
    employer = EmployerDB.objects.get(user=request.user)

    applications = ApplicationDB.objects.filter(
        job__employer=employer
    ).select_related('job', 'user').order_by('-applied_on')

    return render(request, "View_Applications.html", {
                    "applications": applications,
                    'emp': employer
            })

def applicantProfile(request, application_id):
    employer = EmployerDB.objects.get(user=request.user)
    application = get_object_or_404(ApplicationDB, id=application_id, job__employer=employer)
    employee = get_object_or_404(EmployeeDB, user=application.user)

    is_saved = SavedApplicantDB.objects.filter(employer=request.user,application=application).exists()
    rating_obj = ApplicantRating.objects.filter(employer=request.user,application=application).first()

    if request.method == "POST":
        rating_value = request.POST.get("rating")

        ApplicantRating.objects.update_or_create(
            employer=request.user,
            application=application,
            defaults={"rating": rating_value}
        )
        return redirect("ApplicantProfile", application_id=application.id)

    ratings = ApplicantRating.objects.filter(application__user=employee.user)

    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    total_ratings = ratings.count()

    return render(request, "Applicant_Profile.html", {
        "application": application,
        "employee": employee,
        'emp': employer,
        "is_saved": is_saved,
        "rating_obj": rating_obj,
        "avg_rating": round(avg_rating),
        "total_ratings": total_ratings
    })

def toggleSaveApplicant(request, application_id):

    application = get_object_or_404(ApplicationDB, id=application_id)

    saved = SavedApplicantDB.objects.filter(
        employer=request.user,
        application=application
    )

    if saved.exists():
        saved.delete()
    else:
        SavedApplicantDB.objects.create(
            employer=request.user,
            application=application
        )

    return redirect('ApplicantProfile', application_id=application.id)

def savedApplicants(request):
    employer = EmployerDB.objects.get(user=request.user)
    saved_applicants = SavedApplicantDB.objects.filter(employer=request.user).select_related(
         'application__job',
                'application__user').order_by('-created_at')

    return render(request, "Saved_Applicants.html", {
        'emp': employer,
        "saved_applicants": saved_applicants
    })