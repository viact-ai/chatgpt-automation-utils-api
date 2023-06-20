import base64
import datetime
import email

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from schemas.email import Email
from utils.logger_utils import get_logger

logger = get_logger()


def convert_to_datetime(date_string: str) -> datetime.datetime:
    # Parse the date string to a tuple
    parsed_date = email.utils.parsedate_tz(date_string)

    # Convert the tuple to a datetime object
    datetime_obj = datetime.datetime.fromtimestamp(
        email.utils.mktime_tz(parsed_date)
    )

    return datetime_obj


async def fetch_gmail_messages(
    creds: Credentials,
    query: str = "",
    offset: int = 0,
    limit: int = 10,
    plain_text: bool = False,
    include_spam_trash: bool = False,
) -> list[Email] | None:
    # Build the Gmail service
    service = build("gmail", "v1", credentials=creds)

    try:
        # Build the Gmail API service
        service = build("gmail", "v1", credentials=creds)

        # Call Gmail API to fetch messages in INBOX
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                labelIds=["INBOX"],
                maxResults=offset + limit,
                includeSpamTrash=include_spam_trash,
            )
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            return []

        # Do pagination
        if len(messages) < offset:
            return []

        messages = messages[offset : offset + limit]

        _messages = []

        def on_message_fetched(request_id, response, exception):
            if exception is not None:
                logger.error("Error when fetching with req_id %s", request_id)
                return

            _messages.append(response)

        # Create batch of http request to fetch message
        batch = service.new_batch_http_request()
        for message in messages:
            batch.add(
                service.users()
                .messages()
                .get(userId="me", id=message["id"], format="raw"),
                callback=on_message_fetched,
            )
        batch.execute()

        messages = _messages

        emails = []
        for message in messages:
            # # Parse the raw message.
            mime_msg = email.message_from_bytes(
                base64.urlsafe_b64decode(message["raw"])
            )

            # Parse the message body
            body = ""
            message_main_type = mime_msg.get_content_maintype()
            if message_main_type == "multipart":
                for part in mime_msg.get_payload():
                    if plain_text:
                        if part.get_content_type() == "text/plain":
                            charset = part.get_content_charset()
                            body += (
                                part.get_payload(decode=True)
                                .decode(charset)
                                .strip()
                            )
                    else:
                        if part.get_content_maintype() == "text":
                            charset = part.get_content_charset()
                            body += (
                                part.get_payload(decode=True)
                                .decode(charset)
                                .strip()
                            )
            elif message_main_type == "text":
                charset = mime_msg.get_content_charset()
                body = (
                    mime_msg.get_payload(decode=True).decode(charset).strip()
                )

            # Decode subject header
            subject = email.header.decode_header(mime_msg["subject"])[0][0]

            thread_id = message["threadId"]
            label_ids = message["labelIds"]
            _date = convert_to_datetime(mime_msg["date"])

            e = Email(
                threadId=thread_id,
                labelIds=label_ids,
                messageId=mime_msg["message-id"],
                subject=subject,
                sendFrom=mime_msg["from"],
                sendTo=mime_msg["to"],
                body=body,
                sendDate=_date.isoformat(),
            )
            emails.append(e)

        return emails

    except Exception as err:
        logger.exception(err)
        return None
