from dataclasses import dataclass

from souriva.agent import DocumentAgent
from souriva.config import Settings, get_settings
from souriva.model import create_model
from souriva.rag import FaissStore, HashEmbeddings
from souriva.tools import DocumentTools


@dataclass
class Runtime:
    settings: Settings
    store: FaissStore
    tools: DocumentTools
    agent: DocumentAgent


def create_runtime(settings: Settings | None = None) -> Runtime:
    settings = settings or get_settings()
    store = FaissStore(
        HashEmbeddings(settings.embedding_dimensions), settings.index_path, settings.metadata_path
    )
    store.load()
    tools = DocumentTools(store)
    model = create_model(
        settings.model_backend,
        settings.model_base_url,
        settings.model_name,
        settings.model_api_key,
    )
    agent = DocumentAgent(
        store,
        model,
        top_k=settings.retrieval_top_k,
        min_relevance=settings.min_relevance,
        calculator=tools.calculator,
    )
    return Runtime(settings, store, tools, agent)

