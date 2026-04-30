from django.db import models
from django.contrib.auth.models import User


class EmployerDB(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True,blank=True)

    store_name = models.CharField(max_length=100,null=True,blank=True)
    store_location = models.CharField(max_length=150,null=True,blank=True)
    store_description = models.CharField(max_length=500,null=True,blank=True)
    website = models.CharField(max_length=100,null=True,blank=True)
    business_email = models.EmailField(null=True,blank=True)
    store_logo = models.ImageField(upload_to="Store Logo",null=True,blank=True)
    contact_number = models.IntegerField(null=True,blank=True)

class JobDB(models.Model):
    # CHOICE
    JobTypeChoices = [
        ("Part Time", "Part Time"),
        ("Full Time", "Full Time"),
        ("Flexible", "Flexible")
    ]

    # FIELDS
    job_title = models.CharField(max_length=100,null=True,blank=True)
    job_location = models.CharField(max_length=150,null=True,blank=True)
    job_type = models.CharField(max_length=20,choices=JobTypeChoices)
    job_description = models.CharField(max_length=500,null=True,blank=True)
    job_requirement = models.CharField(max_length=500,null=True,blank=True)
    posted_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    is_paused = models.BooleanField(default=False)

    employer = models.ForeignKey(EmployerDB,on_delete=models.CASCADE,related_name="jobs")

class SavedApplicantDB(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey("EmployeeApp.ApplicationDB", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employer', 'application')

class ApplicantRating(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey("EmployeeApp.ApplicationDB",on_delete=models.CASCADE)

    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employer', 'application')

    def __str__(self):
        return f"{self.employer.username} - {self.application.id} ({self.rating})"