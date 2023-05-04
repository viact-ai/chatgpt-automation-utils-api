from typing import List

from db import db_helper
from fastapi import APIRouter
from pydantic import BaseModel
from utils import llm_utils

router = APIRouter()

client = db_helper.get_client()


class IndexDocumentsBody(BaseModel):
    documents: List[str]
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
