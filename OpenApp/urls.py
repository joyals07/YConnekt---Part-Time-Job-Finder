from django.urls import path
from . import views

urlpatterns = [
    path('Index/',views.indexPage,name="IndexPage"),
    path('SignUp/',views.signupPage,name="SignUp"),
    path('Login/',views.loginUser,name="Login"),
    path('Logout/',views.logoutUser,name="Logout"),

    path('Admin/',views.adminPage,name="adminPage"),
    path('Messages/', views.messageList, name="MessageList"),
    path('Employers/', views.employerList, name="EmployerList"),
    path('Employees/', views.employeeList, name="EmployeeList"),
    path('AllJobs/', views.jobListAdmin, name="AllJobs"),
    path('Applications/', views.applicationList, name="ApplicationList")
]