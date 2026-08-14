import re
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader
import chromadb
from chromadb.utils import embedding_functions


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


def ingest_sops():
    sops_dir = get_sops_dir()
    if not sops_dir.exists():
        raise FileNotFoundError(f"SOP directory not found at {sops_dir}")

    pdf_files = sorted(list(sops_dir.glob("*.pdf")))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {sops_dir}")

    total_pages = 0
    all_chunks = []

    for pdf_path in pdf_files:
        pages = extract_pages_from_pdf(pdf_path)
        total_pages += len(pages)
        for p in pages:
            chunks = chunk_page_text(
                text=p["text"],
                sop_id=p["sop_id"],
                source=p["source"],
                page_num=p["page"]
            )
            all_chunks.extend(chunks)

    backend_dir = Path(__file__).resolve().parent
    chroma_db_dir = backend_dir / "chroma_db"
    chroma_db_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(chroma_db_dir))
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    try:
        client.delete_collection(name="mfgx_sops")
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name="mfgx_sops",
        embedding_function=sentence_transformer_ef
    )

    ids = [c["id"] for c in all_chunks]
    documents = [c["text"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print("MFGX AI SOP Ingestion")
    print("---------------------")
    print(f"SOP files found: {len(pdf_files)}")
    print(f"Pages processed: {total_pages}")
    print(f"Chunks created: {len(all_chunks)}")
    print(f"Chunks stored: {collection.count()}")
    print("Collection: mfgx_sops")
    print("Status: SUCCESS")

    return {
        "files_found": len(pdf_files),
        "pages_processed": total_pages,
        "chunks_created": len(all_chunks),
        "chunks_stored": collection.count(),
        "collection": "mfgx_sops"
    }


if __name__ == "__main__":
    ingest_sops()
