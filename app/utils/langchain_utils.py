from pathlib import Path
from typing import Any

from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from utils.config_utils import get_config
from utils.logger_utils import get_logger

config = get_config()

logger = get_logger()


def txts2docs(txts: list[str]) -> list[Document]:
    return [Document(page_content=txt) for txt in txts]


def create_vectorstore_index(
    docs: list[Document],
    path: str | None = None,
) -> Chroma:
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()

    if path:
        persist_dir = Path(config.llm.langchain.persist_dir)
        path = persist_dir / path
        path.parent.mkdir(parents=True, exist_ok=True)

    db = Chroma.from_documents(
        texts,
        embeddings,
        persist_directory=str(path),
    )
    if path:
        db.persist()

    logger.info("Vectorstore created with %d documents" % len(docs))
    return db


# still not working
# def persist_vectorstore(db: Chroma, path: Path):
#     persist_dir = Path(config.llm.langchain.persist_dir)
#     path = persist_dir / path
#     path.parent.mkdir(parents=True, exist_ok=True)

#     db._persist_directory = str(path)

#     db._client_settings = chromadb.config.Settings(
#         chroma_db_impl="duckdb+parquet",
#         persist_directory=str(path),
#     )
#     db._client = chromadb.Client(db._client_settings)

#     db.persist()
#     logger.info("Vectorstore persisted at %s" % str(path))


def load_vectorstore(
    path: str | Path,
) -> Chroma:
    persist_dir = Path(config.llm.langchain.persist_dir)
    if path:
        path = persist_dir / path

    embedding = OpenAIEmbeddings()
    db = Chroma(persist_directory=str(path), embedding_function=embedding)

    logger.info("Vectorstore loaded from %s" % str(path))

    return db


def list_vectorstore() -> list[str]:
    persist_dir = Path(config.llm.langchain.persist_dir)
    return [str(path.name) for path in persist_dir.glob("*") if path.is_dir()]


def delete_vectorstore(
    path: str | Path,
) -> bool:
    """Delete vectorstore

    Args:
        path (str | Path): path to the vectorstore

    Returns:
        bool: ok. Return True if successful else False
    """
    persist_dir = Path(config.llm.langchain.persist_dir)
    path = persist_dir / path
    if not path.exists():
        return False

    for file in path.glob("*"):
        file.unlink(missing_ok=True)
    path.rmdir()
    return True


def check_vectorstore_exists(path: Path | str) -> bool:
    persist_dir = Path(config.llm.langchain.persist_dir)
    path = persist_dir / path
    return path.exists()


def add_docs_to_vectorstore(
    docs: list[Document],
    db: Chroma,
) -> Chroma:
    added_indexes = db.add_documents(docs)
    logger.info("Added %d documents to vectorstore" % len(added_indexes))
    return db


def get_retrieval_qa_chain(db: Chroma) -> RetrievalQA:
    llm = ChatOpenAI(
        temperature=config.llm.temperature,
        model_name=config.llm.model_name,
    )

    combine_docs_chain = load_qa_chain(
        llm,
        chain_type=config.llm.langchain.qa_chain_type,
    )
    qa = RetrievalQA(
        combine_documents_chain=combine_docs_chain,
        retriever=db.as_retriever(),
    )
    return qa


def query_vectorstore(
    db: Chroma,
    query: str,
) -> dict[str, Any]:
    # Search for similarity documents
    # docs = db.similarity_search(query)
    # print(docs)

    qa = get_retrieval_qa_chain(db)
    result = qa.run(query)
    return result
