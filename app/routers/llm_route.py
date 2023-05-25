from db import db_helper
from fastapi import APIRouter
from pydantic import BaseModel
from utils import llm_utils

router = APIRouter()

client = db_helper.get_client()


@router.get("/index_collection/{collection_id}")
def query_email_thread(
    collection_id: str,
    q: str,
):
    if not llm_utils.check_index_exists(collection_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    index = llm_utils.load_index(path=collection_id)

    result = llm_utils.query_index(
        index,
        q,
    )
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
    docs = llm_utils.txts2docs(body.documents)
    nodes = llm_utils.docs2nodes(docs)
    index = llm_utils.nodes2index(nodes)

    result = llm_utils.query_index(
        index,
        body.query,
    )
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
    if llm_utils.check_index_exists(body.collection_id):
        return {
            "status": "failed",
            "message": "index already exists",
        }

    docs = llm_utils.txts2docs(body.documents)
    nodes = llm_utils.docs2nodes(docs)
    index = llm_utils.nodes2index(nodes)

    llm_utils.save_index(index=index, path=body.collection_id)
    return {
        "status": "success",
    }


@router.post("/index_collection/documents")
def add_document_to_collection(
    body: IndexCollectionBody,
):
    if not llm_utils.check_index_exists(body.collection_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    docs = llm_utils.txts2docs(body.documents)
    nodes = llm_utils.docs2nodes(docs)

    index = llm_utils.load_index(path=body.collection_id)
    index.insert_nodes(nodes)
    llm_utils.save_index(index=index, path=body.collection_id)

    return {
        "status": "success",
    }


@router.delete("/index_collection/{collection_id}")
def delete_index_email_thread(
    collection_id: str,
):
    if not llm_utils.check_index_exists(collection_id):
        return {
            "status": "failed",
            "message": "index does not exists",
        }

    ok = llm_utils.delete_index(path=collection_id)
    if not ok:
        return {
            "status": "failed",
            "message": "error when delete index",
        }

    return {
        "status": "success",
    }
