from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

import fitz
from docx import Document
from fastapi import UploadFile

from app.core.security import sanitize_text, validate_upload


@dataclass
class ParsedUpload:
    filename: str
    content: bytes
    text: str


async def parse_upload(file: UploadFile) -> ParsedUpload:
    content = await file.read()
    validate_upload(file, len(content))
    text = extract_text(file.filename or "upload", content)
    return ParsedUpload(file.filename or "upload", content, sanitize_text(text))


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _pdf_text(content)
    if suffix == ".docx":
        return "\n".join(p.text for p in Document(BytesIO(content)).paragraphs)
    if suffix == ".doc":
        return _doc_text(content)
    return ""


def _pdf_text(content: bytes) -> str:
    with fitz.open(stream=content, filetype="pdf") as document:
        return "\n".join(page.get_text() for page in document)


def _doc_text(content: bytes) -> str:
    with NamedTemporaryFile(suffix=".doc", delete=False) as temp:
        temp.write(content)
        temp.flush()
        path = Path(temp.name)
        try:
            result = run(["antiword", temp.name], capture_output=True, text=True, check=False)
            if result.stdout:
                return result.stdout
        except FileNotFoundError:
            pass
        try:
            import textract

            return textract.process(temp.name).decode("utf-8", errors="ignore")
        except Exception:
            return ""
        finally:
            path.unlink(missing_ok=True)
