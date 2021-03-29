from django.core.mail import send_mail
from django.template import loader

from web_crawler import settings


def send_email(email, params):
    email_template_name = params.pop("html")

    subject = params.pop("subject")
    message = ""
    template = loader.get_template(email_template_name)
    html_message = template.render(params)
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        html_message=html_message,
    )
