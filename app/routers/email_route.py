from datetime import datetime
from typing import Optional

from db import db_helper
from depends.auth_dep import verify_credentials
from fastapi import APIRouter, Depends
from google.oauth2.credentials import Credentials
from pydantic import BaseModel
from schemas.response import APIResponse
from utils import email_utils, langchain_utils
from utils.config_utils import get_config
from utils.email_utils import HistoryMessage
from utils.googleapi_utils import fetch_gmail_messages

router = APIRouter()

client = db_helper.get_client()

config = get_config()


class EmailPromptRevisionBody(BaseModel):
    email_id: str
    prompt: str
    email_body: str
    gpt_result: str


@router.get("/gpt_revision", response_model=APIResponse)
def get_gpt_revision(
    email_id: str,
):
    db = client["chatgpt"]
    collection = db["email_revisions"]
    documents = collection.find({"email_id": email_id})
    documents = [db_helper.jsonify_doc(doc) for doc in documents]
    return {
        "data": documents,
    }


@router.get("/query_thread/{thread_id}", response_model=APIResponse)
def query_email_thread(
    thread_id: str,
    q: str,
):
    if not langchain_utils.check_vectorstore_exists(thread_id):
        return {
            "error": True,
            "message": "index does not exists",
        }

    index = langchain_utils.load_vectorstore(path=thread_id)

    result = langchain_utils.query_vectorstore(index, q)
    return {
        "data": result,
    }


@router.get("/index_thread", response_model=APIResponse)
def list_thread_index():
    index_list = langchain_utils.list_vectorstore()
    return {
        "data": index_list,
    }


@router.post("/gpt_revision", response_model=APIResponse)
def add_revision(
    body: EmailPromptRevisionBody,
):
    db = client["chatgpt"]
    collection = db["email_revisions"]

    existing_item = collection.find_one(
        {
            "email_id": body.email_id,
            "prompt": body.prompt,
        }
    )
    if existing_item:
        if existing_item["gpt_result"] == body.gpt_result:
            return {
                "error": True,
                "message": "revision already exists",
            }

    inserted = collection.insert_one(body.dict())
    return {
        "data": str(inserted.inserted_id),
    }


class ScheduleEmailBody(BaseModel):
    recipients: list[str]
    subject: str
    content: str
    scheduled_time: datetime
    reply_to: str = None
    references: str = None
    cc: str = None
    bcc: str = None


@router.post("/schedule", response_model=APIResponse)
def schedule_email(
    body: ScheduleEmailBody,
):
    email_utils.schedule_email(
        recipients=body.recipients,
        subject=body.subject,
        content=body.content,
        scheduled_time=body.scheduled_time,
        reply_to=body.reply_to,
        references=body.references,
        cc=body.cc,
        bcc=body.bcc,
    )
    return {
        "error": False,
    }


class IndexThreadBody(BaseModel):
    thread_id: str
    messages: list[str]


@router.post("/index_thread", response_model=APIResponse)
def index_email_thread(
    body: IndexThreadBody,
):
    if langchain_utils.check_vectorstore_exists(body.thread_id):
        return {
            "error": True,
            "message": "index already exists",
        }

    docs = langchain_utils.txts2docs(body.messages)
    langchain_utils.create_vectorstore_index(docs, path=body.thread_id)

    return {
        "error": False,
    }


@router.post("/index_thread/messages", response_model=APIResponse)
def add_messages_to_thread(
    body: IndexThreadBody,
):
    if not langchain_utils.check_vectorstore_exists(body.thread_id):
        return {
            "error": False,
            "message": "index does not exists",
        }

    docs = langchain_utils.txts2docs(body.messages)
    index = langchain_utils.load_vectorstore(path=body.thread_id)
    langchain_utils.add_docs_to_vectorstore(docs, index)

    return {
        "error": False,
    }


@router.put("/index_thread", response_model=APIResponse)
def update_index_email_thread(
    body: IndexThreadBody,
):
    if not langchain_utils.check_vectorstore_exists(body.thread_id):
        return {
            "error": True,
            "message": "index does not exists",
        }

    docs = langchain_utils.txts2docs(body.messages)
    langchain_utils.create_vectorstore_index(docs, path=body.thread_id)

    return {
        "error": False,
    }


@router.delete("/index_thread/{thread_id}", response_model=APIResponse)
def delete_index_email_thread(
    thread_id: str,
):
    if not langchain_utils.check_vectorstore_exists(thread_id):
        return {
            "error": True,
            "message": "index does not exists",
        }

    ok = langchain_utils.delete_vectorstore(path=thread_id)
    if not ok:
        return {
            "error": True,
            "message": "error when delete index",
        }

    return {
        "error": False,
    }


class FollowUpEmailBody(BaseModel):
    history: list[HistoryMessage]
    user_input: str
    instruction: Optional[str] = None


@router.post("/follow_up", response_model=APIResponse)
def follow_up_email(
    body: FollowUpEmailBody,
):
    result = email_utils.write_follow_up_email(
        history=body.history,
        user_input=body.user_input,
        instruction=body.instruction,
    )
    return {
        "data": result,
    }


@router.get("/fetch_gmail_messages", response_model=APIResponse)
async def fetch_gmail_messages_route(
    q: str = None,
    offset: int = 0,
    limit: int = 10,
    plain_text: bool = False,
    include_spam_trash: bool = False,
    creds: Credentials = Depends(verify_credentials),
):
    messages = await fetch_gmail_messages(
        creds,
        query=q,
        offset=offset,
        limit=limit,
        plain_text=plain_text,
        include_spam_trash=include_spam_trash,
    )

    if messages is None:
        return {
            "error": True,
            "message": "Error when fetching messages",
        }

    return {
        "data": messages,
    }
