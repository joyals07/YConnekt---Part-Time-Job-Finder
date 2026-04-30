from django.urls import path
from . import views

urlpatterns = [
    path('RegisterEmployer/',views.registerEmployer,name="regEmp"),
    path('SaveEmployer/',views.saveEmployer,name="saveEmp"),

    path('EmployerDashboard/',views.employerDashboard,name="EmpDash"),

    path('OurJobs/',views.showJobs,name="OurJobs"),
    path('ShowJob/<int:job_id>/',views.showActiveJob,name="showJob"),
    path('EditJob/<int:job_id>/',views.editJob,name="EditJob"),
    path('delete-job/<int:id>/', views.deleteJob, name='deleteJob'),
    path('toggle-job/<int:id>/', views.toggleJobStatus, name='toggleJob'),

    path('JobPost/',views.postJob,name="PostJob"),
    path('SavePost/',views.saveJob,name="SaveJob"),

    path('Profile/',views.profilePage,name="ProfilePage"),
    path('EditEmployerProfile/',views.editProfile,name="EditProfilePage"),


    path('Applications/', views.viewApplications, name="ViewApplications"),
    path('ApplicantProfile/<int:application_id>/',views.applicantProfile,name="ApplicantProfile"),
    path('ToggleSaveApplicant/<int:application_id>/',views.toggleSaveApplicant,name='ToggleSaveApplicant'),
    path('SavedApplicants/', views.savedApplicants, name='SavedApplicants'),


    ]

