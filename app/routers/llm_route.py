from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel
from utils import index_utils

router = APIRouter()


class IndexDocumentsBody(BaseModel):
    documents: List[str]
    query: str
    mode: Literal["default", "tree_summarize"] = "default"


@router.post("/index_documents")
def index_documents(
    body: IndexDocumentsBody,
):
    docs = index_utils.txts2docs(body.documents)
    nodes = index_utils.docs2nodes(docs)
    index = index_utils.nodes2index(nodes)

    response = index_utils.query_index(index, body.query, mode=body.mode)
    return response
