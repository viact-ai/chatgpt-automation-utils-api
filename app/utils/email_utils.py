import asyncio
import smtplib
from datetime import datetime
from email.message import EmailMessage
from typing import Literal, TypedDict

from db import db_helper
from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from utils.config_utils import get_config
from utils.logger_utils import get_logger

logger = get_logger()

config = get_config()


client = db_helper.get_client()


def send_email(
    recipients: list[str],
    subject: str,
    content: str,
    cc: str = None,
    bcc: str = None,
    reply_to: str = None,
    references: str = None,
) -> bool:
    """Send email to recipients

    Args:
        recipients (list[str]): list of email addresses
        subject (str): subject of the email
        content (str): body/content of the email
        cc (str): cc email address. Default to None
        bcc (str): bcc email address. Default to None
        reply_to (str): message id to reply to. Default to None
        references (str): message ids to reference. Default to None

    Returns:
        bool: return True if ok, False otherwise
    """
    try:
        sender = config.smtp.mail_from
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)

        if cc:
            msg["Cc"] = cc
        if bcc:
            msg["Bcc"] = bcc

        if reply_to:
            msg["In-Reply-To"] = reply_to
            msg["References"] = references or "" + " " + reply_to

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
    recipients: list[str],
    subject: str,
    content: str,
    scheduled_time: datetime,
    cc: str = None,
    bcc: str = None,
    reply_to: str = None,
    references: str = None,
):
    try:
        db = client["chatgpt"]
        collection = db["scheduled_emails"]
        collection.insert_one(
            {
                "recipients": recipients,
                "subject": subject,
                "content": content,
                "reply_to": reply_to,
                "cc": cc,
                "bcc": bcc,
                "references": references,
                "scheduled_time": scheduled_time,
                "is_sent": False,
            }
        )
    except Exception as err:
        logger.exception(err)


def send_scheduled_emails():
    db = client["chatgpt"]
    collection = db["scheduled_emails"]
    for email in collection.find(
        {"scheduled_time": {"$lt": datetime.utcnow()}}
    ):
        if email["is_sent"]:
            continue

        logger.info(f"Sending email {email['_id']}")
        ok = send_email(
            recipients=email["recipients"],
            subject=email["subject"],
            content=email["content"],
            reply_to=email["reply_to"] if "reply_to" in email else None,
            references=email["references"] if "references" in email else None,
            cc=email["cc"] if "cc" in email else None,
            bcc=email["bcc"] if "bcc" in email else None,
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


class HistoryMessage(TypedDict):
    role: Literal["human", "assistant"]
    message: str


def write_follow_up_email(
    user_input: str,
    history: list[HistoryMessage],
    instruction: str = None,
) -> str:
    if not instruction:
        instruction = """Assitant is working at an AI company that mainly focus on computer vision.
        Asisstant's job is to write a follow-up email to a potential customer who is interested in our product.
        You have to make sure to answer all the questions that the customer has asked.
        You also have to make sure to get all of the following information from the customer:
        - Brife description of the customer's company
        - Problem that the customer is facing or want to apply AI to
        - Budget to spend
        - Time to spend
        You have to ask for all the information above until you get all.
        If the information is mentioned in the email, don't ask for it again.
        Once you have enough information, summarize the information and write a follow-up email to the customer.
        Then ask for the time to schedule a meeting with the customer."""  # noqa: E501

    template = """

    {history}
    Human: {human_input}
    Assistant: """

    template = instruction + template

    prompt = PromptTemplate(
        template=template,
        input_variables=["history", "human_input"],
    )

    memory = ConversationBufferWindowMemory(k=5)

    for msg in history:
        r = msg["role"]
        m = msg["message"]
        if r == "human":
            memory.chat_memory.add_user_message(m)
        else:
            memory.chat_memory.add_ai_message(m)

    chatgpt_chain = LLMChain(
        llm=OpenAI(temperature=0.1),
        prompt=prompt,
        verbose=True,
        memory=memory,
    )

    output = chatgpt_chain.predict(
        human_input=user_input,
    )
    return output
