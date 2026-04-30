from django.db import models
from django.contrib.auth.models import User


class EmployeeDB(models.Model):
    # CHOICE

    GenderChoices = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
        ("Prefer Not To Say", "Prefer Not To Say"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)

    full_name = models.CharField(max_length=100,null=True,blank=True)
    contact_number = models.IntegerField(null=True,blank=True)
    current_location = models.CharField(max_length=150,null=True,blank=True)
    personal_email = models.EmailField(null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=20, choices=GenderChoices)
    profile_picture = models.ImageField(upload_to="Profile Picture")

class ApplicationDB(models.Model):
    job = models.ForeignKey("EmployerApp.JobDB", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    age = models.IntegerField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', null=True,blank=True)
    cover_letter = models.TextField(blank=True, null=True)
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'user')

class SavedJobDB(models.Model):
    job = models.ForeignKey("EmployerApp.JobDB", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'user')