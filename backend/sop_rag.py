import os
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions

# PyTorch CPU thread & memory optimization for low-RAM (512MB) cloud instances
try:
    import torch
    torch.set_num_threads(1)
    torch.set_grad_enabled(False)
except ImportError:
    pass


class SOPRAG:
    _instance: Optional['SOPRAG'] = None

    def __new__(cls, chroma_dir: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super(SOPRAG, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, chroma_dir: Optional[Path] = None):
        if getattr(self, "_initialized", False):
            return

        if chroma_dir is None:
            backend_dir = Path(__file__).resolve().parent
            self.chroma_dir = backend_dir / "chroma_db"
        else:
            self.chroma_dir = Path(chroma_dir)

        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="mfgx_sops",
            embedding_function=self.embedding_fn
        )
        self._initialized = True

    def search_sops(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic search over the SOP ChromaDB collection.
        Returns top_k most relevant chunks with metadata and distance.
        """
        if not query or not query.strip():
            return []

        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        formatted_results = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            formatted_results.append({
                "text": doc,
                "sop_id": meta.get("sop_id", ""),
                "source": meta.get("source", ""),
                "page": meta.get("page", 1),
                "distance": round(float(dist), 4) if dist is not None else 0.0
            })

        return formatted_results


# Helper functions reusing singleton instance
def get_sop_rag() -> SOPRAG:
    return SOPRAG()

def search_sops(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    rag = get_sop_rag()
    return rag.search_sops(query=query, top_k=top_k)
