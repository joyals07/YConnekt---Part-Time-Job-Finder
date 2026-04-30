from django.urls import path
from .views import (

    # AUTH
    CustomLoginView,
    register_employee,
    register_employer,
    employee_dashboard,
    employee_profile,
    employer_dashboard,
    employer_profile,

    # JOBS
    job_list,
    job_detail,
    create_job,
    employer_jobs,
    edit_job,
    delete_job,
    update_job_status,

    # APPLICATIONS
    apply_job,
    application_detail,
    my_applications,
    job_applicants,
    rate_applicant,

    # SAVED JOBS
    toggle_save_job,
    saved_jobs,
    toggle_save_applicant,
    saved_applicants,
)

urlpatterns = [

    # =========================
    # AUTH
    # =========================
    path('login/', CustomLoginView.as_view()),
    path('register/employee/', register_employee),
    path('register/employer/', register_employer),
    path('employee/profile/', employee_profile),
    path('employee/dashboard/', employee_dashboard),
    path('employer/profile/', employer_profile),
    path('employer/dashboard/', employer_dashboard),

    # =========================
    # JOBS
    # =========================
    path('jobs/', job_list),
    path('jobs/<int:job_id>/', job_detail),
    path('jobs/create/', create_job),
    path('employer/jobs/', employer_jobs),
    path('jobs/<int:job_id>/edit/', edit_job),
    path('jobs/<int:job_id>/status/', update_job_status),
    path('jobs/<int:job_id>/delete/', delete_job),

    # =========================
    # APPLICATIONS
    # =========================
    path('apply/<int:job_id>/', apply_job),
    path('my-applications/', my_applications),
    path('jobs/<int:job_id>/applicants/', job_applicants),
    path('applications/<int:application_id>/', application_detail),
    path('applications/<int:application_id>/rate/', rate_applicant),

    # =========================
    # SAVED JOBS
    # =========================
    path('save-job/<int:job_id>/', toggle_save_job),
    path('saved-jobs/', saved_jobs),
    path('save-applicant/<int:application_id>/', toggle_save_applicant),
    path('saved-applicants/', saved_applicants),
]
