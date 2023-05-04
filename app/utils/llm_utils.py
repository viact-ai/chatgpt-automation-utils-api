from pathlib import Path
from typing import List, Union

from langchain import OpenAI
from llama_index import (
    Document,
    GPTVectorStoreIndex,
    LLMPredictor,
    PromptHelper,
    ServiceContext,
    StorageContext,
    load_index_from_storage,
)
from llama_index.data_structs import Node
from llama_index.node_parser import SimpleNodeParser
from utils.config_utils import get_config

config = get_config()


def txts2docs(txts: List[str]) -> Document:
    return [Document(txt) for txt in txts]


def docs2nodes(docs: List[Document]) -> List[Node]:
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(docs)
    return nodes


def nodes2index(
    nodes: List[Node],
) -> GPTVectorStoreIndex:
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
    index = GPTVectorStoreIndex(nodes, service_context=service_context)
    return index


def load_index(
    path: Union[str, Path] = None,
) -> GPTVectorStoreIndex:
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
    index: GPTVectorStoreIndex,
    path: Union[str, Path] = None,
) -> None:
    persist_dir = Path(config.llm.index_dir)
    if path:
        path = persist_dir / path
    path.parent.mkdir(parents=True, exist_ok=True)

    index.storage_context.persist(
        persist_dir=str(path),
    )


def query_index(
    index: GPTVectorStoreIndex,
    query: str,
):
    query_engine = index.as_query_engine()
    return query_engine.query(query).response


def check_index_exists(path: Union[Path, str]) -> bool:
    persist_dir = Path(config.llm.index_dir)
    path = persist_dir / path
    return path.exists()