from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

if not settings.DEBUG:
    from sentry_sdk import capture_exception


class EmailSender:
    """
    Utility class to send emails using Django's EmailMultiAlternatives.
    """

    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.site_base_url = settings.SITE_BASE_URL

    def _render_template(self, template_name, context):
        """
        Renders a Django template with the given context.

        :param template_name: Path to the template
        :param context: Dictionary with template variables
        :return: Rendered template as string
        """
        return render_to_string(template_name, context)

    def send_email(self, subject, template_name, context, recipient_list):
        """
        Send an email with content rendered from a Django template.

        :param subject: Email subject
        :param template_name: Path to the email template
        :param context: Dictionary with template variables
        :param recipient_list: List of recipients
        """
        html_content = self._render_template(template_name, context)

        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=html_content,
                from_email=self.from_email,
                to=recipient_list,
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            capture_exception(e)


def email_new_correction(post):
    """
    Send a new correction received email.

    :param post: Post object
    """

    user = post.user
    email = user.email
    subject = "[LangCorrect] New Correction!"

    context = {"username": user.username, "post_link": f"{settings.SITE_BASE_URL}{post.get_absolute_url()}"}

    msg = EmailSender()
    msg.send_email(
        subject=subject, template_name="emails/new_correction.html", context=context, recipient_list=[email]
    )
