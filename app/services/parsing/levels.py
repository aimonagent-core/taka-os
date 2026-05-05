# File: app/services/parsing/levels.py
# Purpose: PDF parsing levels (text, OCR, structured, LLM)
# Dependencies: pypdf, pdfplumber, pytesseract, pdf2image, Pillow, numpy

import json
import re
from typing import Any, Tuple

import logging

logger = logging.getLogger(__name__)


class Level1TextExtractor:
    async def extract(self, file_path: str) -> Tuple[str, float]:
        import pypdf

        text_parts: list[str] = []
        try:
            with open(file_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as exc:
            logger.error("level1_extraction_error: %s", exc)
            raise
        full_text = "\n".join(text_parts)
        score = min(len(full_text) / 1000.0, 1.0)
        return full_text, score


class Level2OCRExtractor:
    DEFAULT_DPI: int = 200
    DEFAULT_LANG: str = "fra+eng"

    async def extract(
        self, file_path: str, dpi: int = DEFAULT_DPI, lang: str = DEFAULT_LANG
    ) -> Tuple[str, float]:
        from pdf2image import convert_from_path
        import pytesseract
        import numpy as np

        text_parts: list[str] = []
        confidences: list[float] = []
        images = convert_from_path(file_path, dpi=dpi)
        for image in images:
            data = pytesseract.image_to_data(
                image, lang=lang, output_type=pytesseract.Output.DICT
            )
            page_text = " ".join(word for word in data["text"] if word.strip())
            text_parts.append(page_text)
            confs = [
                int(c)
                for c, t in zip(data["conf"], data["text"])
                if t.strip() and int(c) >= 0
            ]
            avg_conf = np.mean(confs) / 100.0 if confs else 0.0
            confidences.append(avg_conf)
        full_text = "\n".join(text_parts)
        overall_confidence = float(np.mean(confidences)) if confidences else 0.0
        return full_text, overall_confidence


class Level3StructuredExtractor:
    async def extract(self, file_path: str) -> Tuple[dict, float]:
        import pdfplumber

        result: dict = {"tables": [], "text_blocks": [], "words": []}
        total_cells = 0
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        result["tables"].append({"page": page_num, "data": table})
                        total_cells += sum(len(row) for row in table if row)
                words = page.extract_words()
                result["words"].extend(
                    [{"text": w["text"], "page": page_num} for w in words]
                )
                text = page.extract_text()
                if text:
                    result["text_blocks"].append({"page": page_num, "text": text})
        score = min(total_cells / max(len(pdf.pages), 1), 1.0)
        return result, score


class Level4LLMExtractor:
    SYSTEM_PROMPT: str = (
        "Tu es un analyste specialise dans les marches publics. "
        "Analyse le document et retourne UNIQUEMENT un JSON valide avec cette structure :\n"
        '{"summary": "Resume en 3 phrases", "sections": [{"title": "...", "content": "..."}], '
        '"themes": ["theme1", "theme2"], "language": "fr|en|other", '
        '"document_type": "appel_d_offres|avis_periodique|autre", "confidence": 0.0}\n'
        "Ne retourne aucun texte en dehors du JSON."
    )

    def __init__(self, client: "MistralAIClient") -> None:
        self._client = client

    async def extract(
        self, text: str, structured_hint: Any = None
    ) -> Tuple[dict, float]:
        truncated = text[:12000] if len(text) > 12000 else text
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": truncated},
        ]
        try:
            response = await self._client.chat_completion(
                messages=messages, temperature=0.1, max_tokens=2000
            )
            content = response["choices"][0]["message"]["content"]
            parsed = self._extract_json(content)
            confidence = parsed.get("confidence", 0.0)
            if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
                confidence = 0.5
            if parsed.get("document_type") in ("appel_d_offres", "avis_periodique"):
                confidence = min(confidence + 0.1, 1.0)
            if parsed.get("summary") and len(parsed["summary"]) > 20:
                confidence = min(confidence + 0.05, 1.0)
            return parsed, confidence
        except Exception as exc:
            logger.error("level4_llm_error: %s", exc)
            return {"error": str(exc), "document_type": "unknown", "confidence": 0.0}, 0.0

    def _extract_json(self, content: str) -> dict:
        match = re.search(
            r"```json\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE
        )
        if match:
            json_str = match.group(1)
        else:
            start = content.find("{")
            end = content.rfind("}")
            json_str = content[start : end + 1] if start != -1 and end != -1 else content
        return json.loads(json_str)
