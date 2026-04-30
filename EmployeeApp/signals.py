from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage

from .models import ApplicationDB


@receiver(post_save, sender=ApplicationDB)
def notify_employer_on_application(sender, instance, created, **kwargs):
    if not created:
        return  # Only for new applications

    job = instance.job
    employer = job.employer

    # ✅ Get employer email (priority: business_email → user.email)
    employer_email = None
    if employer.business_email:
        employer_email = employer.business_email
    elif employer.user and employer.user.email:
        employer_email = employer.user.email

    if not employer_email:
        return  # No email available

    # ✅ Applicant details
    applicant = instance.user

    applicant_name = applicant.get_full_name() or applicant.username
    applicant_email = applicant.email

    # Get phone from EmployeeDB
    employee_profile = getattr(applicant, 'employeedb', None)
    phone = employee_profile.contact_number if employee_profile else "Not provided"

    # Cover letter
    cover_letter = instance.cover_letter or "Not provided"

    # ✅ Email content
    subject = f"New Application for {job.job_title}"

    message = f"""
Hello,

You have received a new application for your job.

Job Title: {job.job_title}

Applicant Details:
Name: {applicant_name}
Email: {applicant_email}
Phone: {phone}

Cover Letter:
{cover_letter}

Please login to your dashboard to review the application.

- YConnect Team
"""

    # ✅ Create Email
    email = EmailMessage(
        subject,
        message,
        to=[employer_email]
    )

    # ✅ Attach resume if exists
    if instance.resume:
        email.attach_file(instance.resume.path)

    # ✅ Send email
    email.send(fail_silently=False)