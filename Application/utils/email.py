from celery.utils.log import get_task_logger
from Application import mail, app, celery
from Application.flask_imports import render_template, url_for
from flask_mail import Message

logger = get_task_logger(__name__)

@celery.task(name="send_email", ignore_result=True)
def send_email(title, recipients, template, context):
    try:
        with app.app_context():
            message = Message(
                subject=title,
                recipients=recipients,
                html=render_template(template, **context)
            )
            mail.send(message)
    
    except Exception as e:
        logger.warning(f"Sending email error: {e}")

@celery.task(name="send_email_text", ignore_result=True)
def send_email_text(title, recipients, text):
    try:
        with app.app_context():
            message = Message(
                subject=title,
                recipients=recipients,
                html=text
            )
            mail.send(message)
    except Exception as e:
        logger.warning(f"sending email error: {e}")


class SendEmails:
    def __init__(self, title, recipients, template=None, context=None, text=None):
        self.title = title
        self.recipients = recipients
        self.template = template
        self.context = context
        self.text = text


    def send(self):
        if self.template:
            send_email.apply_async(
                args=[self.title, self.recipients, self.template, self.context]
            )

        else:
            send_email_text.apply_async(
                args=[self.title, self.recipients, self.text]
            )

reset_email = SendEmails(
    title="Reset Password",
    recipients=None,
    template=None,
    context=None
)

order_cancelled_email = SendEmails (
    title="ClickEat Orders", 
    recipients = None,
    template=None,
    context=None
)

# template = "emails/orders/order_invoice.html"
# template = "emails/orders/customer_care_email.html"
# template= "emails/orders/order_receipt.html"

order_placed_email = SendEmails(
    title = "ClickEat Customer Placed Order",
    recipients = None,
    template = None,
    context = None
)

customer_care_email = SendEmails(
    title = "ClickEat Orders",
    recipients = None,
    template = None,
    context = None
)

order_receipt_email = SendEmails(
    title="ClickEat Orders",
    recipients=None,
    template= None,
    context=None
)