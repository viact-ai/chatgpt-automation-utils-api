from pathlib import Path
from typing import List, Union

from langchain import OpenAI
from llama_index import (
    Document,
    GPTListIndex,
    GPTVectorStoreIndex,
    LLMPredictor,
    PromptHelper,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.data_structs import Node
from llama_index.node_parser import SimpleNodeParser
from llama_index.response.schema import RESPONSE_TYPE
from utils.config_utils import get_config

config = get_config()


GPT_INDEX_TYPE = Union[GPTListIndex, GPTVectorStoreIndex]


def txts2docs(txts: List[str]) -> List[Document]:
    return [Document(txt) for txt in txts]


def docs2nodes(docs: List[Document]) -> List[Node]:
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(docs)
    return nodes


def nodes2index(
    nodes: List[Node],
) -> GPTListIndex:
    # define LLM
    llm_predictor = LLMPredictor(
        llm=OpenAI(
            temperature=config.llm.temperature,
            model_name=config.llm.model_name,
        ),
    )

    # define prompt helper
    # set maximum input size
    max_input_size = config.llm.max_input_size
    # set number of output tokens
    num_output = config.llm.num_output
    # set maximum chunk overlap
    max_chunk_overlap = config.llm.max_chunk_overlap
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )
    index = GPTListIndex(nodes, service_context=service_context)
    # index = GPTVectorStoreIndex(nodes, service_context=service_context)
    return index


def load_index(
    path: Union[str, Path] = None,
) -> GPT_INDEX_TYPE:
    persist_dir = Path(config.llm.index_dir)
    if path:
        path = persist_dir / path

    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir=str(path))
    # load index
    index = load_index_from_storage(
        storage_context,
    )
    return index


def save_index(
    index: GPT_INDEX_TYPE,
    path: Union[str, Path] = None,
) -> None:
    persist_dir = Path(config.llm.index_dir)
    if path:
        path = persist_dir / path
    path.parent.mkdir(parents=True, exist_ok=True)

    index.storage_context.persist(
        persist_dir=str(path),
    )


def delete_index(
    path: Union[str, Path],
) -> bool:
    """Delete index

    Args:
        path (Union[str, Path]): path to the index

    Returns:
        bool: ok. Return True if successful else False
    """
    persist_dir = Path(config.llm.index_dir)
    path = persist_dir / path
    if not path.exists():
        return False

    for file in path.glob("*"):
        file.unlink(missing_ok=True)
    path.rmdir()


def query_index(
    index: GPT_INDEX_TYPE,
    query: str,
) -> RESPONSE_TYPE:
    query_engine = index.as_query_engine()
    return query_engine.query(query)


def check_index_exists(path: Union[Path, str]) -> bool:
    persist_dir = Path(config.llm.index_dir)
    path = persist_dir / path
    return path.exists()
