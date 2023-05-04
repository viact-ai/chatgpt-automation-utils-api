import asyncio
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import List

from db import db_helper
from utils.config_utils import get_config
from utils.logger_utils import get_logger

logger = get_logger()

config = get_config()


client = db_helper.get_client()


def send_email(
    recipients: List[str],
    subject: str,
    content: str,
):
    try:
        sender = config.smtp.mail_from
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg.set_content(content)

        _smtp = None
        if config.smtp.ssl:
            _smtp = smtplib.SMTP_SSL
        else:
            _smtp = smtplib.SMTP

        with _smtp(config.smtp.server, config.smtp.port) as s:
            s.ehlo()
            if config.smtp.starttls:
                s.starttls()
                s.ehlo()
            s.login(
                config.smtp.user,
                config.smtp.password,
            )
            # s.sendmail(sender, recipients, msg.as_string())
            s.send_message(msg)

        return True

    except Exception as err:
        logger.exception(err)
        return False


def schedule_email(
    recipients: List[str],
    subject: str,
    content: str,
    scheduled_time: datetime,
):
    try:
        db = client["chatgpt"]
        collection = db["scheduled_emails"]
        collection.insert_one(
            {
                "recipients": recipients,
                "subject": subject,
                "content": content,
                "scheduled_time": scheduled_time,
                "is_sent": False,
            }
        )
    except Exception as err:
        logger.exception(err)


def send_scheduled_emails():
    db = client["chatgpt"]
    collection = db["scheduled_emails"]
    for email in collection.find({"scheduled_time": {"$lt": datetime.now()}}):
        if email["is_sent"]:
            continue

        logger.info(f"Sending email {email['_id']}")
        ok = send_email(
            recipients=email["recipients"],
            subject=email["subject"],
            content=email["content"],
        )
        if ok:
            logger.info(f"Email {email['_id']} sent")

            collection.update_one(
                {"_id": email["_id"]},
                {"$set": {"is_sent": True}},
            )
            logger.info(f"Email {email['_id']} marked as sent")
        else:
            logger.error(
                f"Email {email['_id']} failed to send. Retrying later"
            )


async def send_scheduled_emails_loop():
    while True:
        # Check for scheduled emails
        send_scheduled_emails()
        # Sleep for a specified interval before checking again
        await asyncio.sleep(10)  # Sleep for 10 seconds before checking again
