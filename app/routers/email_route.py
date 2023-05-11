from datetime import datetime
from typing import List

from db import db_helper
from fastapi import APIRouter
from pydantic import BaseModel
from utils import email_utils, llm_utils
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
    if not llm_utils.check_index_exists(thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    index = llm_utils.load_index(path=thread_id)

    result = llm_utils.query_index(
        index,
        q,
    )
    return {
        "status": "success",
        "result": result,
    }


@router.get("/index_thread")
def list_thread_index():
    index_list = llm_utils.list_index()
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
    recipients: List[str]
    subject: str
    content: str
    scheduled_time: datetime


@router.post("/schedule")
def schedule_email(
    body: ScheduleEmailBody,
):
    email_utils.schedule_email(
        recipients=body.recipients,
        subject=body.subject,
        content=body.content,
        scheduled_time=body.scheduled_time,
    )
    return {
        "status": "success",
    }


class IndexThreadBody(BaseModel):
    thread_id: str
    messages: List[str]


@router.post("/index_thread")
def index_email_thread(
    body: IndexThreadBody,
):
    if llm_utils.check_index_exists(body.thread_id):
        return {
            "status": "failed",
            "message": "index already exists",
        }

    docs = llm_utils.txts2docs(body.messages)
    nodes = llm_utils.docs2nodes(docs)
    index = llm_utils.nodes2index(nodes)

    llm_utils.save_index(index=index, path=body.thread_id)
    return {
        "status": "success",
    }


@router.post("/index_thread/messages")
def add_messages_to_thread(
    body: IndexThreadBody,
):
    if not llm_utils.check_index_exists(body.thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    docs = llm_utils.txts2docs(body.messages)
    nodes = llm_utils.docs2nodes(docs)

    index = llm_utils.load_index(path=body.thread_id)
    index.insert_nodes(nodes)
    llm_utils.save_index(index=index, path=body.thread_id)

    return {
        "status": "success",
    }


@router.put("/index_thread")
def update_index_email_thread(
    body: IndexThreadBody,
):
    if not llm_utils.check_index_exists(body.thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    docs = llm_utils.txts2docs(body.messages)
    nodes = llm_utils.docs2nodes(docs)
    index = llm_utils.nodes2index(nodes)

    llm_utils.save_index(index=index, path=body.thread_id)
    return {
        "status": "success",
    }


@router.delete("/index_thread/{thread_id}")
def delete_index_email_thread(
    thread_id: str,
):
    if not llm_utils.check_index_exists(thread_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    ok = llm_utils.delete_index(path=thread_id)
    if not ok:
        return {
            "status": "failed",
            "message": "error when delete index",
        }

    return {
        "status": "success",
    }


class FollowUpEmailBody(BaseModel):
    history: List[HistoryMessage]
    user_input: str


@router.post("/follow_up")
def follow_up_email(
    body: FollowUpEmailBody,
):
    result = email_utils.write_follow_up_email(
        history=body.history,
        user_input=body.user_input,
    )
    return {
        "status": "success",
        "result": result,
    }
