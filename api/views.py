from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from EmployeeApp.models import ApplicationDB, EmployeeDB, SavedJobDB
from EmployerApp.models import ApplicantRating, EmployerDB, JobDB, SavedApplicantDB

from .serializers import CustomTokenSerializer


PAGE_SIZE = 10


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


def error_response(message, response_status=status.HTTP_400_BAD_REQUEST):
    return Response({"error": message}, status=response_status)


def validate_required(data, fields):
    missing = [field for field in fields if not data.get(field)]
    if missing:
        return f"{missing[0]} required"
    return None


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return bool(value)


def get_employee(user):
    return EmployeeDB.objects.filter(user=user).first()


def get_employer(user):
    return EmployerDB.objects.filter(user=user).first()


def active_jobs():
    return JobDB.objects.filter(
        is_active=True,
        is_paused=False,
        closing_date__gte=now().date(),
    )


def serialize_job(job, include_detail=False, is_applied=False):
    data = {
        "id": job.id,
        "title": job.job_title,
        "company": job.employer.store_name,
        "location": job.job_location,
        "job_type": job.job_type,
        "closing_date": job.closing_date,
    }

    if include_detail:
        data.update(
            {
                "description": job.job_description,
                "requirements": job.job_requirement,
                "posted_date": job.posted_date,
                "is_applied": is_applied,
            }
        )

    return data


def file_url(file_field):
    return file_field.url if file_field else None


def serialize_employee(employee):
    user = employee.user
    return {
        "id": employee.id,
        "user_id": user.id if user else None,
        "username": user.username if user else None,
        "email": user.email if user else employee.personal_email,
        "name": employee.full_name,
        "phone": employee.contact_number,
        "location": employee.current_location,
        "dob": employee.date_of_birth,
        "gender": employee.gender,
        "profile_picture": file_url(employee.profile_picture),
    }


def serialize_employer(employer):
    user = employer.user
    return {
        "id": employer.id,
        "user_id": user.id if user else None,
        "username": user.username if user else None,
        "email": user.email if user else employer.business_email,
        "name": employer.store_name,
        "location": employer.store_location,
        "description": employer.store_description,
        "website": employer.website,
        "phone": employer.contact_number,
        "logo": file_url(employer.store_logo),
    }


def serialize_application(application, include_profile=False):
    data = {
        "id": application.id,
        "job_id": application.job.id,
        "job": application.job.job_title,
        "company": application.job.employer.store_name,
        "applicant": application.user.username,
        "resume": file_url(application.resume),
        "cover_letter": application.cover_letter,
        "age": application.age,
        "applied_on": application.applied_on,
    }

    if include_profile:
        employee = EmployeeDB.objects.filter(user=application.user).first()
        data["profile"] = serialize_employee(employee) if employee else None

    return data


@api_view(["POST"])
def register_employee(request):
    data = request.data
    required = ["name", "phone", "location", "dob", "gender", "username", "email", "password"]

    missing_error = validate_required(data, required)
    if missing_error:
        return error_response(missing_error)

    if User.objects.filter(username=data["username"]).exists():
        return error_response("Username exists")

    if User.objects.filter(email=data["email"]).exists():
        return error_response("Email exists")

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
            )

            EmployeeDB.objects.create(
                user=user,
                full_name=data["name"],
                contact_number=data["phone"],
                current_location=data["location"],
                personal_email=data["email"],
                date_of_birth=data["dob"],
                gender=data["gender"],
                profile_picture=request.FILES.get("profile_picture"),
            )
    except IntegrityError:
        return error_response("Unable to register employee")

    return Response({"message": "Employee registered"}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def register_employer(request):
    data = request.data
    required = ["name", "location", "email", "username", "password"]

    missing_error = validate_required(data, required)
    if missing_error:
        return error_response(missing_error)

    if User.objects.filter(username=data["username"]).exists():
        return error_response("Username exists")

    if User.objects.filter(email=data["email"]).exists():
        return error_response("Email exists")

    try:
        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
            )

            EmployerDB.objects.create(
                user=user,
                store_name=data["name"],
                store_location=data["location"],
                business_email=data["email"],
                contact_number=data.get("phone"),
                store_logo=request.FILES.get("logo"),
            )
    except IntegrityError:
        return error_response("Unable to register employer")

    return Response({"message": "Employer registered"}, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def employee_profile(request):
    employee = get_employee(request.user)
    if not employee:
        return error_response("Only employees", status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(serialize_employee(employee))

    data = request.data
    field_map = {
        "name": "full_name",
        "phone": "contact_number",
        "location": "current_location",
        "dob": "date_of_birth",
        "gender": "gender",
        "email": "personal_email",
    }

    for request_field, model_field in field_map.items():
        if request_field in data:
            setattr(employee, model_field, data.get(request_field))

    if request.FILES.get("profile_picture"):
        employee.profile_picture = request.FILES.get("profile_picture")

    if data.get("email"):
        request.user.email = data.get("email")
        request.user.save(update_fields=["email"])

    employee.save()
    return Response({"message": "Employee profile updated", "data": serialize_employee(employee)})


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def employer_profile(request):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    if request.method == "GET":
        return Response(serialize_employer(employer))

    data = request.data
    field_map = {
        "name": "store_name",
        "location": "store_location",
        "description": "store_description",
        "website": "website",
        "email": "business_email",
        "phone": "contact_number",
    }

    for request_field, model_field in field_map.items():
        if request_field in data:
            setattr(employer, model_field, data.get(request_field))

    if request.FILES.get("logo"):
        employer.store_logo = request.FILES.get("logo")

    if data.get("email"):
        request.user.email = data.get("email")
        request.user.save(update_fields=["email"])

    employer.save()
    return Response({"message": "Employer profile updated", "data": serialize_employer(employer)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employee_dashboard(request):
    if not get_employee(request.user):
        return error_response("Only employees", status.HTTP_403_FORBIDDEN)

    return Response(
        {
            "available_jobs": active_jobs().count(),
            "applied_jobs": ApplicationDB.objects.filter(user=request.user).count(),
            "saved_jobs": SavedJobDB.objects.filter(user=request.user).count(),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employer_dashboard(request):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    jobs = JobDB.objects.filter(employer=employer)
    today = now().date()

    return Response(
        {
            "total_jobs": jobs.count(),
            "active_jobs": jobs.filter(is_active=True, is_paused=False, closing_date__gte=today).count(),
            "paused_jobs": jobs.filter(is_paused=True).count(),
            "expired_jobs": jobs.filter(closing_date__lt=today).count(),
            "total_applications": ApplicationDB.objects.filter(job__employer=employer).count(),
        }
    )


@api_view(["GET"])
def job_list(request):
    jobs = active_jobs().select_related("employer")

    search = request.GET.get("search")
    if search:
        jobs = jobs.filter(
            Q(job_title__icontains=search)
            | Q(job_location__icontains=search)
            | Q(employer__store_name__icontains=search)
        )

    sort_options = {
        "new": "-posted_date",
        "old": "posted_date",
        "deadline": "closing_date",
    }
    jobs = jobs.order_by(sort_options.get(request.GET.get("sort"), "-posted_date"))

    try:
        page = max(int(request.GET.get("page", 1)), 1)
    except (TypeError, ValueError):
        page = 1

    total = jobs.count()
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_jobs = jobs[start:end]

    return Response(
        {
            "success": True,
            "total": total,
            "page": page,
            "count": len(page_jobs),
            "data": [serialize_job(job) for job in page_jobs],
        }
    )


@api_view(["GET"])
def job_detail(request, job_id):
    job = get_object_or_404(JobDB.objects.select_related("employer"), id=job_id)

    if not active_jobs().filter(id=job.id).exists():
        return Response(
            {
                "success": False,
                "message": "Job not available",
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    is_applied = False
    if request.user.is_authenticated:
        is_applied = ApplicationDB.objects.filter(user=request.user, job=job).exists()

    return Response(
        {
            "success": True,
            "data": serialize_job(job, include_detail=True, is_applied=is_applied),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_job(request):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    data = request.data
    required = ["title", "location", "job_type", "closing_date"]

    missing_error = validate_required(data, required)
    if missing_error:
        return error_response(missing_error)

    job = JobDB.objects.create(
        job_title=data.get("title"),
        job_location=data.get("location"),
        job_type=data.get("job_type"),
        job_description=data.get("description"),
        job_requirement=data.get("requirements"),
        closing_date=data.get("closing_date"),
        employer=employer,
    )

    return Response({"message": "Job created", "job_id": job.id})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def employer_jobs(request):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    jobs = JobDB.objects.filter(employer=employer).order_by("-posted_date")
    data = []

    for job in jobs:
        item = serialize_job(job)
        item.update(
            {
                "is_active": job.is_active,
                "is_paused": job.is_paused,
                "applications": ApplicationDB.objects.filter(job=job).count(),
            }
        )
        data.append(item)

    return Response(data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def edit_job(request, job_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    job = get_object_or_404(JobDB, id=job_id, employer=employer)
    data = request.data

    field_map = {
        "title": "job_title",
        "location": "job_location",
        "job_type": "job_type",
        "description": "job_description",
        "requirements": "job_requirement",
        "closing_date": "closing_date",
    }

    for request_field, model_field in field_map.items():
        if request_field in data:
            setattr(job, model_field, data.get(request_field))

    job.save()
    return Response({"message": "Job updated"})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_job_status(request, job_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    job = get_object_or_404(JobDB, id=job_id, employer=employer)

    if "is_active" in request.data:
        job.is_active = parse_bool(request.data.get("is_active"))

    if "is_paused" in request.data:
        job.is_paused = parse_bool(request.data.get("is_paused"))

    if "is_active" not in request.data and "is_paused" not in request.data:
        job.is_paused = not job.is_paused

    job.save(update_fields=["is_active", "is_paused"])
    return Response(
        {
            "message": "Job status updated",
            "is_active": job.is_active,
            "is_paused": job.is_paused,
        }
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_job(request, job_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    job = get_object_or_404(JobDB, id=job_id, employer=employer)
    job.delete()
    return Response({"message": "Job deleted"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request, job_id):
    if not get_employee(request.user):
        return error_response("Only employees", status.HTTP_403_FORBIDDEN)

    job = get_object_or_404(active_jobs(), id=job_id)

    if ApplicationDB.objects.filter(user=request.user, job=job).exists():
        return error_response("Already applied")

    ApplicationDB.objects.create(
        user=request.user,
        job=job,
        resume=request.FILES.get("resume"),
        cover_letter=request.data.get("cover_letter"),
        age=request.data.get("age"),
    )

    return Response({"message": "Applied successfully"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_applications(request):
    applications = (
        ApplicationDB.objects.filter(user=request.user)
        .select_related("job", "job__employer")
        .order_by("-applied_on")
    )

    data = [
        {
            "job": application.job.job_title,
            "company": application.job.employer.store_name,
            "applied_on": application.applied_on,
        }
        for application in applications
    ]

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def job_applicants(request, job_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    job = get_object_or_404(JobDB, id=job_id, employer=employer)
    applications = (
        ApplicationDB.objects.filter(job=job)
        .select_related("user", "job", "job__employer")
        .order_by("-applied_on")
    )

    data = [
        serialize_application(application, include_profile=True)
        for application in applications
    ]

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def application_detail(request, application_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    application = get_object_or_404(
        ApplicationDB.objects.select_related("user", "job", "job__employer"),
        id=application_id,
        job__employer=employer,
    )

    data = serialize_application(application, include_profile=True)
    data["is_saved"] = SavedApplicantDB.objects.filter(
        employer=request.user,
        application=application,
    ).exists()
    data["rating"] = ApplicantRating.objects.filter(
        employer=request.user,
        application=application,
    ).values_list("rating", flat=True).first()

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_save_job(request, job_id):
    if not get_employee(request.user):
        return error_response("Only employees", status.HTTP_403_FORBIDDEN)

    job = get_object_or_404(active_jobs(), id=job_id)
    saved = SavedJobDB.objects.filter(user=request.user, job=job)

    if saved.exists():
        saved.delete()
        return Response({"message": "Removed from saved"})

    SavedJobDB.objects.create(user=request.user, job=job)
    return Response({"message": "Saved job"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saved_jobs(request):
    saved = (
        SavedJobDB.objects.filter(user=request.user)
        .select_related("job", "job__employer")
        .order_by("-created_at")
    )

    data = [
        {
            "job": saved_job.job.job_title,
            "company": saved_job.job.employer.store_name,
        }
        for saved_job in saved
    ]

    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_save_applicant(request, application_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    application = get_object_or_404(ApplicationDB, id=application_id, job__employer=employer)
    saved = SavedApplicantDB.objects.filter(employer=request.user, application=application)

    if saved.exists():
        saved.delete()
        return Response({"message": "Removed from saved applicants"})

    SavedApplicantDB.objects.create(employer=request.user, application=application)
    return Response({"message": "Applicant saved"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def saved_applicants(request):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    saved = (
        SavedApplicantDB.objects.filter(employer=request.user)
        .select_related("application__user", "application__job", "application__job__employer")
        .order_by("-created_at")
    )

    data = [
        {
            "saved_id": saved_applicant.id,
            "saved_on": saved_applicant.created_at,
            "application": serialize_application(
                saved_applicant.application,
                include_profile=True,
            ),
        }
        for saved_applicant in saved
    ]

    return Response(data)


@api_view(["POST", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def rate_applicant(request, application_id):
    employer = get_employer(request.user)
    if not employer:
        return error_response("Only employers", status.HTTP_403_FORBIDDEN)

    application = get_object_or_404(ApplicationDB, id=application_id, job__employer=employer)

    try:
        rating = int(request.data.get("rating"))
    except (TypeError, ValueError):
        return error_response("Valid rating required")

    if rating < 1 or rating > 5:
        return error_response("Rating must be between 1 and 5")

    rating_obj, created = ApplicantRating.objects.update_or_create(
        employer=request.user,
        application=application,
        defaults={"rating": rating},
    )

    ratings = ApplicantRating.objects.filter(application__user=application.user).aggregate(
        average=Avg("rating"),
        total=Count("id"),
    )

    return Response(
        {
            "message": "Applicant rated" if created else "Applicant rating updated",
            "rating": rating_obj.rating,
            "average_rating": round(ratings["average"] or 0, 2),
            "total_ratings": ratings["total"],
        }
    )
