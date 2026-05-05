# File: app/services/parsing/pipeline.py
# Purpose: PDF parsing pipeline with 4 levels
# Dependencies: asyncio, time, structlog, app.services.parsing.levels

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

import logging

logger = logging.getLogger(__name__)


@dataclass
class PageResult:
    page_number: int
    text: str = ""
    ocr_used: bool = False
    confidence: float = 0.0
    tables: list[list[list[str]]] = field(default_factory=list)
    images: list[dict[str, Any]] = field(default_factory=list)
    word_count: int = 0


@dataclass
class ParseResult:
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
    pages: list[PageResult] = field(default_factory=list)
    entities: dict[str, list[dict]] = field(default_factory=dict)
    confidence_scores: dict[str, float] = field(default_factory=dict)
    level_reached: int = 0
    degraded: bool = False
    processing_time_ms: int = 0
    llm_analysis: dict[str, Any] | None = None


class ParsingPipeline:
    MIN_TEXT_LENGTH: int = 200
    MIN_CONFIDENCE: float = 0.5
    TIMEOUT_LEVEL_1: float = 10.0
    TIMEOUT_LEVEL_2: float = 60.0
    TIMEOUT_LEVEL_3: float = 30.0
    TIMEOUT_LEVEL_4: float = 45.0

    def __init__(
        self,
        level1: "Level1TextExtractor",
        level2: "Level2OCRExtractor",
        level3: "Level3StructuredExtractor",
        level4: "Level4LLMExtractor",
    ) -> None:
        self._level1 = level1
        self._level2 = level2
        self._level3 = level3
        self._level4 = level4

    async def parse(
        self,
        file_path: str,
        target_level: int = 4,
        metadata: dict[str, Any] | None = None,
    ) -> ParseResult:
        start_time = time.time()
        result = ParseResult(
            metadata=metadata or {},
            confidence_scores={
                "level_1_text": 0.0,
                "level_2_ocr": 0.0,
                "level_3_structured": 0.0,
                "level_4_llm": 0.0,
                "overall": 0.0,
            },
        )

        # Level 1
        try:
            text, score = await asyncio.wait_for(
                self._level1.extract(file_path), timeout=self.TIMEOUT_LEVEL_1
            )
            result.pages = [PageResult(page_number=1, text=text, word_count=len(text.split()))]
            result.confidence_scores["level_1_text"] = score
            result.level_reached = 1
            if score >= self.MIN_CONFIDENCE and len(text) >= self.MIN_TEXT_LENGTH:
                result.confidence_scores["overall"] = score
                if target_level == 1:
                    result.processing_time_ms = int((time.time() - start_time) * 1000)
                    return result
            else:
                result.degraded = True
        except asyncio.TimeoutError:
            result.degraded = True
        except Exception as exc:
            logger.error("parsing_level_1_error", error=str(exc))
            result.degraded = True

        # Level 2
        if target_level >= 2:
            try:
                text, score = await asyncio.wait_for(
                    self._level2.extract(file_path), timeout=self.TIMEOUT_LEVEL_2
                )
                result.pages = [PageResult(page_number=1, text=text, ocr_used=True, word_count=len(text.split()))]
                result.confidence_scores["level_2_ocr"] = score
                result.level_reached = 2
                if score >= self.MIN_CONFIDENCE:
                    result.confidence_scores["overall"] = max(result.confidence_scores["overall"], score)
                    if target_level == 2:
                        result.processing_time_ms = int((time.time() - start_time) * 1000)
                        return result
                else:
                    result.degraded = True
            except asyncio.TimeoutError:
                result.degraded = True
            except Exception as exc:
                logger.error("parsing_level_2_error", error=str(exc))
                result.degraded = True

        # Level 3
        if target_level >= 3:
            try:
                structured, score = await asyncio.wait_for(
                    self._level3.extract(file_path), timeout=self.TIMEOUT_LEVEL_3
                )
                result.confidence_scores["level_3_structured"] = score
                result.level_reached = 3
                if score >= self.MIN_CONFIDENCE:
                    result.confidence_scores["overall"] = max(result.confidence_scores["overall"], score)
                    if target_level == 3:
                        result.processing_time_ms = int((time.time() - start_time) * 1000)
                        return result
                else:
                    result.degraded = True
            except asyncio.TimeoutError:
                result.degraded = True
            except Exception as exc:
                logger.error("parsing_level_3_error", error=str(exc))
                result.degraded = True

        # Level 4
        if target_level >= 4:
            try:
                full_text = "\n".join(p.text for p in result.pages if p.text)
                llm_result, score = await asyncio.wait_for(
                    self._level4.extract(full_text, result.pages),
                    timeout=self.TIMEOUT_LEVEL_4,
                )
                result.llm_analysis = llm_result
                result.confidence_scores["level_4_llm"] = score
                result.level_reached = 4
                result.confidence_scores["overall"] = max(result.confidence_scores["overall"], score)
            except asyncio.TimeoutError:
                result.degraded = True
            except Exception as exc:
                logger.error("parsing_level_4_error", error=str(exc))
                result.degraded = True

        result.processing_time_ms = int((time.time() - start_time) * 1000)
        return result
