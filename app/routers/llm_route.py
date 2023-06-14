from typing import Optional

from db import db_helper
from fastapi import APIRouter
from pydantic import BaseModel
from schemas.response import APIResponse
from utils import langchain_utils
from utils.llama_utils import run_chatgpt

router = APIRouter()

client = db_helper.get_client()


class RunChatGPTBody(BaseModel):
    prompt: str
    instruction: Optional[str] = None


@router.post("/chatgpt", response_model=APIResponse)
def run_chatgpt_route(
    body: RunChatGPTBody,
):
    res = run_chatgpt(body.prompt, body.instruction)
    return {
        "data": res,
    }


@router.get("/index_collection/{collection_id}", response_model=APIResponse)
def query_email_thread(
    collection_id: str,
    q: str,
):
    if not langchain_utils.check_vectorstore_exists(collection_id):
        return {
            "error": True,
            "message": "index does not exists",
        }

    index = langchain_utils.load_vectorstore(path=collection_id)

    result = langchain_utils.query_vectorstore(index, q)
    return {
        "data": result,
    }


class IndexDocumentsBody(BaseModel):
    documents: list[str]
    query: str


@router.post("/query_documents", response_model=APIResponse)
def index_documents(
    body: IndexDocumentsBody,
):
    docs = langchain_utils.txts2docs(body.documents)
    index = langchain_utils.create_vectorstore_index(docs)

    result = langchain_utils.query_vectorstore(index, body.query)
    return {
        "data": result,
    }


class IndexCollectionBody(BaseModel):
    collection_id: str
    documents: list[str]


@router.post("/index_collection", response_model=APIResponse)
def index_collection(
    body: IndexCollectionBody,
):
    if langchain_utils.check_vectorstore_exists(body.collection_id):
        return {
            "status": "failed",
            "message": "index already exists",
        }

    docs = langchain_utils.txts2docs(body.documents)
    langchain_utils.create_vectorstore_index(docs, path=body.collection_id)

    return {
        "error": False,
    }


@router.post("/index_collection/documents", response_model=APIResponse)
def add_document_to_collection(
    body: IndexCollectionBody,
):
    if not langchain_utils.check_vectorstore_exists(body.collection_id):
        return {
            "error": True,
            "message": "index does not exists",
        }

    docs = langchain_utils.txts2docs(body.documents)
    index = langchain_utils.load_vectorstore(path=body.collection_id)
    index = langchain_utils.add_docs_to_vectorstore(docs=docs, db=index)

    return {
        "error": False,
    }


@router.delete("/index_collection/{collection_id}", response_model=APIResponse)
def delete_index_email_thread(
    collection_id: str,
):
    if not langchain_utils.check_vectorstore_exists(collection_id):
        return {
            "error": True,
            "message": "index does not exists",
        }

    ok = langchain_utils.delete_vectorstore(path=collection_id)
    if not ok:
        return {
            "error": True,
            "message": "error when delete index",
        }

    return {
        "error": False,
    }
