from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail

from EmployerApp.models import JobDB
from EmployeeApp.models import EmployeeDB


@receiver(post_save, sender=JobDB)
def send_job_notification(sender, instance, created, **kwargs):
    if not created:
        return  # Only for new jobs

    # Step 1: Get all employees
    employees = EmployeeDB.objects.select_related('user').all()

    # Step 2: Collect emails (prefer personal_email, fallback to user.email)
    email_list = []
    for emp in employees:
        if emp.personal_email:
            email_list.append(emp.personal_email)
        elif emp.user and emp.user.email:
            email_list.append(emp.user.email)

    if not email_list:
        return

    # Step 3: Prepare email
    subject = f"New Job Posted: {instance.job_title}"

    message = f"""
Hello,

A new job has been posted on YConnect.

Title: {instance.job_title}
Location: {instance.job_location}
Type: {instance.job_type}

Requirements:
{instance.job_requirement}

Apply before: {instance.closing_date}

- YConnect Team
"""

    # Step 4: Send emails
    send_mass_mail(
        [(subject, message, None, [email]) for email in email_list],
        fail_silently=False
    )