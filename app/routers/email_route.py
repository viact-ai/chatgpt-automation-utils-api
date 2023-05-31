from datetime import datetime
from typing import Optional

from db import db_helper
from fastapi import APIRouter
from pydantic import BaseModel
from utils import email_utils, langchain_utils
from utils.config_utils import get_config
from utils.email_utils import HistoryMessage

router = APIRouter()

client = db_helper.get_client()

config = get_config()


class EmailPromptRevisionBody(BaseModel):
    email_id: str
    prompt: str
    email_body: str
    gpt_result: str


@router.get("/gpt_revision")
def get_gpt_revision(
    email_id: str,
):
    db = client["chatgpt"]
    collection = db["email_revisions"]
    documents = collection.find({"email_id": email_id})
    documents = [db_helper.jsonify_doc(doc) for doc in documents]
    return {
        "status": "success",
        "revisions": documents,
    }


@router.get("/query_thread/{thread_id}")
def query_email_thread(
    thread_id: str,
    q: str,
):
    if not langchain_utils.check_vectorstore_exists(thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    index = langchain_utils.load_vectorstore(path=thread_id)

    result = langchain_utils.query_vectorstore(index, q)
    return {
        "status": "success",
        "result": result,
    }


@router.get("/index_thread")
def list_thread_index():
    index_list = langchain_utils.list_vectorstore()
    return {
        "status": "success",
        "index_list": index_list,
    }


@router.post("/gpt_revision")
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
                "status": "failed",
                "message": "revision already exists",
            }

    inserted = collection.insert_one(body.dict())
    return {
        "status": "success",
        "inserted_id": str(inserted.inserted_id),
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


@router.post("/schedule")
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
        "status": "success",
    }


class IndexThreadBody(BaseModel):
    thread_id: str
    messages: list[str]


@router.post("/index_thread")
def index_email_thread(
    body: IndexThreadBody,
):
    if langchain_utils.check_vectorstore_exists(body.thread_id):
        return {
            "status": "failed",
            "message": "index already exists",
        }

    docs = langchain_utils.txts2docs(body.messages)
    langchain_utils.create_vectorstore_index(docs, path=body.thread_id)

    return {
        "status": "success",
    }


@router.post("/index_thread/messages")
def add_messages_to_thread(
    body: IndexThreadBody,
):
    if not langchain_utils.check_vectorstore_exists(body.thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    docs = langchain_utils.txts2docs(body.messages)
    index = langchain_utils.load_vectorstore(path=body.thread_id)
    langchain_utils.add_docs_to_vectorstore(docs, index)

    return {
        "status": "success",
    }


@router.put("/index_thread")
def update_index_email_thread(
    body: IndexThreadBody,
):
    if not langchain_utils.check_vectorstore_exists(body.thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    docs = langchain_utils.txts2docs(body.messages)
    langchain_utils.create_vectorstore_index(docs, path=body.thread_id)

    return {
        "status": "success",
    }


@router.delete("/index_thread/{thread_id}")
def delete_index_email_thread(
    thread_id: str,
):
    if not langchain_utils.check_vectorstore_exists(thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    ok = langchain_utils.delete_vectorstore(path=thread_id)
    if not ok:
        return {
            "status": "failed",
            "message": "error when delete index",
        }

    return {
        "status": "success",
    }


class FollowUpEmailBody(BaseModel):
    history: list[HistoryMessage]
    user_input: str
    instruction: Optional[str] = None


@router.post("/follow_up")
def follow_up_email(
    body: FollowUpEmailBody,
):
    result = email_utils.write_follow_up_email(
        history=body.history,
        user_input=body.user_input,
        instruction=body.instruction,
    )
    return {
        "status": "success",
        "result": result,
    }
