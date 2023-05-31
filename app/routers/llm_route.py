from db import db_helper
from fastapi import APIRouter
from pydantic import BaseModel
from utils import langchain_utils

router = APIRouter()

client = db_helper.get_client()


@router.get("/index_collection/{collection_id}")
def query_email_thread(
    collection_id: str,
    q: str,
):
    if not langchain_utils.check_vectorstore_exists(collection_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    index = langchain_utils.load_vectorstore(path=collection_id)

    result = langchain_utils.query_vectorstore(index, q)
    return {
        "status": "success",
        "result": result,
    }


class IndexDocumentsBody(BaseModel):
    documents: list[str]
    query: str


@router.post("/query_documents")
def index_documents(
    body: IndexDocumentsBody,
):
    docs = langchain_utils.txts2docs(body.documents)
    index = langchain_utils.create_vectorstore_index(docs)

    result = langchain_utils.query_vectorstore(index, body.query)
    return {
        "status": "success",
        "result": result,
    }


class IndexCollectionBody(BaseModel):
    collection_id: str
    documents: list[str]


@router.post("/index_collection")
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
        "status": "success",
    }


@router.post("/index_collection/documents")
def add_document_to_collection(
    body: IndexCollectionBody,
):
    if not langchain_utils.check_vectorstore_exists(body.collection_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    docs = langchain_utils.txts2docs(body.documents)
    index = langchain_utils.load_vectorstore(path=body.collection_id)
    index = langchain_utils.add_docs_to_vectorstore(docs=docs, db=index)

    return {
        "status": "success",
    }


@router.delete("/index_collection/{collection_id}")
def delete_index_email_thread(
    collection_id: str,
):
    if not langchain_utils.check_vectorstore_exists(collection_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    ok = langchain_utils.delete_vectorstore(path=collection_id)
    if not ok:
        return {
            "status": "failed",
            "message": "error when delete index",
        }

    return {
        "status": "success",
    }
