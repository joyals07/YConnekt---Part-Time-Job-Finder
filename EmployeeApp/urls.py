from django.urls import path
from . import views

urlpatterns = [
    path('RegisterEmployee/',views.regEmployee,name="regEmployee"),
    path('SaveEmployee/',views.saveEmployee,name="SaveEmployee"),

    path('EmployeeDashboard/',views.employeeDashboard,name="EmployeeDash"),

    path('JobList/',views.jobList,name="JobList"),
    path('ViewJob/<int:job_id>/',views.viewJob,name="ViewJob"),
    path('ToggleSaveJob/<int:job_id>/', views.toggleSaveJob, name="ToggleSaveJob"),

    path('ApplicationForm/<int:job_id>/',views.applicationForm,name='Application'),
    path('SendApplicationForm/<int:job_id>/',views.sendApplication,name="SendApplication"),

    path('About/',views.aboutPage,name="About"),
    path('EditProfile/', views.editProfile, name='EditProfile'),

    path('AppliedJobs/',views.appliedJobs,name="AppliedJobs"),

    path('SavedJobs/', views.savedJobs, name="SavedJobs"),
]