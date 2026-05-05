# File: app/api/v1/endpoints/documents.py
# Purpose: Document upload, parsing, and retrieval endpoints
# Dependencies: fastapi, sqlalchemy, app.services.parsing, app.services.memory, app.services.validation

import tempfile
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.ao import Document, DocumentStatus, MemoryType, User
from app.schemas.document import DocumentCreate, DocumentOut, DocumentParseResult, DocumentUpdate
from app.services.llm.mistral_client import MistralAIClient
from app.services.memory.memory_service import MemoryService
from app.services.parsing.entity_extractors import AmountExtractor, CPVExtractor, DeadlineExtractor
from app.services.parsing.levels import (
    Level1TextExtractor,
    Level2OCRExtractor,
    Level3StructuredExtractor,
    Level4LLMExtractor,
)
from app.services.parsing.pipeline import ParsingPipeline
from app.services.validation.gates import ValidationPipeline

router = APIRouter()


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported",
        )
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    doc = Document(
        id=uuid4(),
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        filename=file.filename or "untitled.pdf",
        original_filename=file.filename or "untitled.pdf",
        file_path=tmp_path,
        status=DocumentStatus.PENDING,
        file_size=len(contents),
        mime_type="application/pdf",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.post("/{doc_id}/parse", response_model=DocumentParseResult)
async def parse_document(
    doc_id: UUID,
    target_level: int = Query(4, ge=1, le=4),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    doc = await db.get(Document, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    pipeline = ParsingPipeline(
        level1=Level1TextExtractor(),
        level2=Level2OCRExtractor(),
        level3=Level3StructuredExtractor(),
        level4=Level4LLMExtractor(client=MistralAIClient(api_key=settings.mistral_api_key)),
    )
    result = await pipeline.parse(doc.file_path, target_level=target_level)

    doc.status = DocumentStatus.EXTRACTING
    doc.parse_level_reached = result.level_reached
    doc.parse_result = {
        "version": result.version,
        "pages": [
            {
                "page_number": p.page_number,
                "text": p.text,
                "ocr_used": p.ocr_used,
                "confidence": p.confidence,
                "tables": p.tables,
            }
            for p in result.pages
        ],
        "confidence_scores": result.confidence_scores,
        "level_reached": result.level_reached,
        "degraded": result.degraded,
        "processing_time_ms": result.processing_time_ms,
        "llm_analysis": result.llm_analysis,
    }
    doc.processing_time_ms = result.processing_time_ms
    await db.commit()

    full_text = "\n".join(p.text for p in result.pages if p.text)
    cpv = CPVExtractor().extract(full_text)
    amounts = AmountExtractor().extract(full_text)
    deadlines = DeadlineExtractor().extract(full_text)

    doc.extracted_entities = {
        "cpv": [
            {"code": c.code, "confidence": c.confidence, "context": c.context}
            for c in cpv[:5]
        ],
        "amounts": [
            {
                "value": str(a.value),
                "currency": a.currency,
                "type": a.type_label,
                "confidence": a.confidence,
            }
            for a in amounts[:5]
        ],
        "deadlines": [
            {"date": d.date.isoformat(), "type": d.type_label, "confidence": d.confidence}
            for d in deadlines[:5]
        ],
    }
    await db.commit()

    memory = MemoryService(db, MistralAIClient(api_key=settings.mistral_api_key))
    await memory.ingest(
        content=full_text[:4000],
        memory_type=MemoryType.SEMANTIC,
        user_id=current_user.id,
        source_type="document",
        source_id=doc.id,
        metadata={
            "filename": doc.filename,
            "level_reached": result.level_reached,
            "degraded": result.degraded,
        },
        priority=3,
    )

    return {
        "document_id": str(doc.id),
        "status": doc.status.value,
        "level_reached": result.level_reached,
        "degraded": result.degraded,
        "confidence_scores": result.confidence_scores,
        "processing_time_ms": result.processing_time_ms,
        "entities": doc.extracted_entities,
    }


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:
    doc = await db.get(Document, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.get("", response_model=list[DocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> list[Document]:
    from sqlalchemy import select

    stmt = (
        select(Document)
        .where(Document.tenant_id == current_user.tenant_id)
        .offset(skip)
        .limit(limit)
        .order_by(Document.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/{doc_id}/validate")
async def validate_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    doc = await db.get(Document, doc_id)
    if not doc or doc.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    parsed = doc.parse_result or {}
    entities = doc.extracted_entities or {}
    amounts = entities.get("amounts", [])
    deadlines = entities.get("deadlines", [])

    document_data = {
        "title": (parsed.get("llm_analysis", {}) or {}).get("summary", "")[:100],
        "description": (parsed.get("llm_analysis", {}) or {}).get("summary", ""),
        "amount": float(amounts[0]["value"]) if amounts else None,
        "deadline": deadlines[0]["date"] if deadlines else None,
        "raw_text": "\n".join(p.get("text", "") for p in parsed.get("pages", [])),
    }

    validator = ValidationPipeline(db)
    result = await validator.validate(document_data, doc_id)

    doc.validation_result = {
        "overall_passed": result.overall_passed,
        "overall_score": result.overall_score,
        "status": result.status.value if hasattr(result.status, "value") else str(result.status),
        "retryable": result.retryable,
        "gates": [
            {
                "gate": g.gate.value,
                "passed": g.passed,
                "score": g.score,
                "threshold": g.threshold,
                "details": g.details,
            }
            for g in result.gate_results
        ],
    }
    doc.status = DocumentStatus.APPROVED if result.overall_passed else DocumentStatus.REVIEW
    await db.commit()

    return {
        "document_id": str(doc_id),
        "overall_passed": result.overall_passed,
        "overall_score": result.overall_score,
        "status": doc.status.value,
        "retryable": result.retryable,
        "gates": [
            {
                "gate": g.gate.value,
                "passed": g.passed,
                "score": g.score,
                "threshold": g.threshold,
                "details": g.details,
            }
            for g in result.gate_results
        ],
    }
