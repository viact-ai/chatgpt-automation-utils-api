from pathlib import Path

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
from utils.logger_utils import get_logger

config = get_config()

logger = get_logger()

GPT_INDEX_TYPE = GPTListIndex | GPTVectorStoreIndex


def txts2docs(txts: list[str]) -> list[Document]:
    return [Document(txt) for txt in txts]


def docs2nodes(docs: list[Document]) -> list[Node]:
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(docs)
    return nodes


def nodes2index(
    nodes: list[Node],
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
    path: str | Path = None,
) -> GPT_INDEX_TYPE:
    persist_dir = Path(config.llm.llama_index.persist_dir)
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
    path: str | Path = None,
) -> None:
    persist_dir = Path(config.llm.llama_index.persist_dir)
    if path:
        path = persist_dir / path
    path.parent.mkdir(parents=True, exist_ok=True)

    index.storage_context.persist(
        persist_dir=str(path),
    )


def delete_index(
    path: str | Path,
) -> bool:
    """Delete index

    Args:
        path (str | Path): path to the index

    Returns:
        bool: ok. Return True if successful else False
    """
    persist_dir = Path(config.llm.llama_index.persist_dir)
    path = persist_dir / path
    if not path.exists():
        return False

    for file in path.glob("*"):
        file.unlink(missing_ok=True)
    path.rmdir()
    return True


def list_index() -> list[str]:
    persist_dir = Path(config.llm.llama_index.persist_dir)
    return [str(path.name) for path in persist_dir.glob("*") if path.is_dir()]


def query_index(
    index: GPT_INDEX_TYPE,
    query: str,
) -> RESPONSE_TYPE:
    query_engine = index.as_query_engine()
    return query_engine.query(query).response


def check_index_exists(path: Path | str) -> bool:
    persist_dir = Path(config.llm.llama_index.persist_dir)
    path = persist_dir / path
    return path.exists()
