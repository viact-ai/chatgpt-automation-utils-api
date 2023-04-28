from pathlib import Path
from typing import List, Literal, Union

from langchain import OpenAI
from llama_index import (
    Document,
    GPTSimpleVectorIndex,
    LLMPredictor,
    PromptHelper,
    ServiceContext,
)
from llama_index.data_structs.node_v2 import Node
from llama_index.node_parser import SimpleNodeParser
from utils.config_utils import get_config

config = get_config()


def txts2docs(txts: List[str]) -> Document:
    return [Document(txt) for txt in txts]


def docs2nodes(docs: List[Document]) -> List[Node]:
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(docs)
    return nodes


def nodes2index(nodes: List[Node]) -> GPTSimpleVectorIndex:
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
    index = GPTSimpleVectorIndex(nodes, service_context=service_context)
    return index


def load_index(path: Union[Path, str]) -> GPTSimpleVectorIndex:
    index = GPTSimpleVectorIndex.load_from_disk(str(path))
    return index


def save_index(index: GPTSimpleVectorIndex, path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    index.save_to_disk(str(path))


def query_index(
    index: GPTSimpleVectorIndex,
    query: str,
    mode: Literal["default", "tree_summarize"] = "default",
):
    return index.query(query, mode=mode)
