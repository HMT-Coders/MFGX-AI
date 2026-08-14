import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("MFGX_SOPRAG")


def get_sops_dir() -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    sops_dir = base_dir / "sops"
    if not sops_dir.exists():
        sops_dir = base_dir / "spos"
    return sops_dir


def clean_extracted_text(text: str) -> str:
    if not text:
        return ""
    lines = text.split("\n")
    cleaned_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in lines]
    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def extract_pages_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    reader = PdfReader(pdf_path)
    sop_id = pdf_path.stem
    pages = []
    for i, page in enumerate(reader.pages):
        try:
            raw_text = page.extract_text(extraction_mode="layout")
        except Exception:
            raw_text = page.extract_text()

        text = clean_extracted_text(raw_text)
        if text:
            pages.append({
                "sop_id": sop_id,
                "source": pdf_path.name,
                "page": i + 1,
                "text": text
            })
    return pages


def chunk_page_text(
    text: str,
    sop_id: str,
    source: str,
    page_num: int,
    chunk_size: int = 600,
    overlap: int = 100
) -> List[Dict[str, Any]]:
    text = text.strip()
    if not text:
        return []

    if len(text) <= chunk_size:
        return [{
            "id": f"{sop_id}-page-{page_num}-chunk-0",
            "text": text,
            "metadata": {
                "sop_id": sop_id,
                "source": source,
                "page": page_num
            }
        }]

    chunks = []
    start = 0
    chunk_index = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        if end < text_len:
            space_idx = text.rfind(' ', max(start, end - 100), end + 50)
            if space_idx != -1 and space_idx > start:
                end = space_idx

        chunk_str = text[start:end].strip()
        if chunk_str:
            chunks.append({
                "id": f"{sop_id}-page-{page_num}-chunk-{chunk_index}",
                "text": chunk_str,
                "metadata": {
                    "sop_id": sop_id,
                    "source": source,
                    "page": page_num
                }
            })
            chunk_index += 1

        start = end - overlap
        if start >= text_len - overlap or end >= text_len:
            break

    return chunks


class SOPRAG:
    """
    Hybrid Lightweight Vector RAG Engine.
    Uses zero PyTorch, zero ChromaDB, zero SentenceTransformers.
    Steady-state RAM: ~55 MB (well under 512 MB limit).
    """
    _instance: Optional['SOPRAG'] = None

    def __new__(cls, backend_dir: Optional[Path] = None):
        if cls._instance is None:
            cls._instance = super(SOPRAG, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, backend_dir: Optional[Path] = None):
        if getattr(self, "_initialized", False):
            return

        if backend_dir is None:
            self.backend_dir = Path(__file__).resolve().parent
        else:
            self.backend_dir = Path(backend_dir)

        self.chunks_cache_file = self.backend_dir / "sop_chunks_cache.json"
        self.embeddings_cache_file = self.backend_dir / "sop_embeddings_cache.json"

        self.chunks: List[Dict[str, Any]] = []
        self._load_or_build_chunks()

        # Initialize Mode B: Local TF-IDF Vectorizer
        self.corpus = [c["text"] for c in self.chunks]
        self.tfidf_vectorizer = TfidfVectorizer(ngram_range=(1, 3), sublinear_tf=True)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.corpus)

        # Mode A Cloud Embeddings Cache
        self.cloud_embeddings: Optional[np.ndarray] = None
        self._load_or_build_cloud_embeddings()

        self._initialized = True

    def _load_or_build_chunks(self):
        if self.chunks_cache_file.exists():
            try:
                with open(self.chunks_cache_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
                if self.chunks:
                    return
            except Exception as e:
                logger.warning(f"Failed to load cached SOP chunks: {e}")

        # Parse SOP PDFs
        sops_dir = get_sops_dir()
        if not sops_dir.exists():
            logger.warning(f"SOP directory not found: {sops_dir}")
            return

        pdf_files = sorted(list(sops_dir.glob("*.pdf")))
        all_chunks = []
        for pdf_path in pdf_files:
            pages = extract_pages_from_pdf(pdf_path)
            for p in pages:
                chk_list = chunk_page_text(
                    text=p["text"],
                    sop_id=p["sop_id"],
                    source=p["source"],
                    page_num=p["page"]
                )
                all_chunks.extend(chk_list)

        self.chunks = all_chunks

        # Cache on disk
        try:
            with open(self.chunks_cache_file, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save SOP chunks cache: {e}")

    def _load_or_build_cloud_embeddings(self):
        if self.embeddings_cache_file.exists():
            try:
                with open(self.embeddings_cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data and len(data) == len(self.chunks):
                        self.cloud_embeddings = np.array(data, dtype=np.float32)
                        return
            except Exception as e:
                logger.warning(f"Could not load cloud embeddings cache: {e}")

        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key or not self.chunks:
            return

        try:
            import google.genai as genai
            client = genai.Client(api_key=api_key)
            embed_matrix = []
            for c in self.chunks:
                res = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=c["text"]
                )
                if res and res.embeddings:
                    embed_matrix.append(res.embeddings[0].values)

            if len(embed_matrix) == len(self.chunks):
                self.cloud_embeddings = np.array(embed_matrix, dtype=np.float32)
                with open(self.embeddings_cache_file, "w", encoding="utf-8") as f:
                    json.dump(embed_matrix, f)
        except Exception as e:
            logger.info(f"Cloud embedding precomputation skipped: {e}")

    def search_sops(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform semantic retrieval over SOP chunks.
        Mode A: Cloud Embeddings (if available)
        Mode B: Local TF-IDF Vectorizer (Fallback)
        """
        if not query or not query.strip() or not self.chunks:
            return []

        # Try Mode A: Cloud Embeddings
        results = self._search_cloud(query, top_k=top_k)
        if results:
            return results

        # Fallback Mode B: Local TF-IDF Vectorizer
        return self._search_tfidf(query, top_k=top_k)

    def _search_cloud(self, query: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
        if self.cloud_embeddings is None:
            return None

        api_key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return None

        try:
            import google.genai as genai
            client = genai.Client(api_key=api_key)
            res = client.models.embed_content(
                model="gemini-embedding-001",
                contents=query
            )
            if not res or not res.embeddings:
                return None

            q_vec = np.array(res.embeddings[0].values, dtype=np.float32)
            
            # Cosine similarity
            norms = np.linalg.norm(self.cloud_embeddings, axis=1) * np.linalg.norm(q_vec)
            norms[norms == 0] = 1e-9
            sims = np.dot(self.cloud_embeddings, q_vec) / norms

            top_indices = np.argsort(sims)[::-1][:top_k]
            formatted_results = []
            for idx in top_indices:
                score = float(sims[idx])
                if score <= 0:
                    continue
                c = self.chunks[idx]
                meta = c.get("metadata", {})
                formatted_results.append({
                    "text": c.get("text", ""),
                    "sop_id": meta.get("sop_id", ""),
                    "source": meta.get("source", ""),
                    "page": meta.get("page", 1),
                    "distance": round(1.0 - score, 4)  # Distance representation
                })

            return formatted_results if formatted_results else None
        except Exception as e:
            logger.warning(f"Cloud embedding search error, falling back to TF-IDF: {e}")
            return None

    def _search_tfidf(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        q_vec = self.tfidf_vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(sims)[::-1][:top_k]
        formatted_results = []
        for idx in top_indices:
            score = float(sims[idx])
            c = self.chunks[idx]
            meta = c.get("metadata", {})
            formatted_results.append({
                "text": c.get("text", ""),
                "sop_id": meta.get("sop_id", ""),
                "source": meta.get("source", ""),
                "page": meta.get("page", 1),
                "distance": round(1.0 - score, 4)  # Distance representation
            })

        return formatted_results


# Helper functions
def get_sop_rag() -> SOPRAG:
    return SOPRAG()

def search_sops(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    rag = get_sop_rag()
    return rag.search_sops(query=query, top_k=top_k)
