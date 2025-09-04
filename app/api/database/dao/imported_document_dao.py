from __future__ import annotations
from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.database.models.imported_document import ImportedDocument

class ImportedDocumentDAO:
    async def add_document(self, db: AsyncSession, doc: ImportedDocument) -> ImportedDocument:
        db.add(doc)
        await db.commit()
        return doc

    async def add_raw(self, db: AsyncSession, file_name: str, content: str) -> ImportedDocument:
        rec = ImportedDocument(file_name=file_name, content=content, is_process=False)
        db.add(rec)
        await db.commit()
        return rec

    async def list_unprocessed(self, db: AsyncSession, limit: Optional[int] = None) -> List[ImportedDocument]:
        stmt = (
            select(ImportedDocument)
            .where(ImportedDocument.is_process.is_(False))
            .order_by(ImportedDocument.created_at.asc())
        )
        if limit:
            stmt = stmt.limit(limit)
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def mark_processed(self, db: AsyncSession, doc_id: str) -> None:
        stmt = (
            update(ImportedDocument)
            .where(ImportedDocument.id == doc_id)
            .values(is_process=True)
            .execution_options(synchronize_session=False)
        )
        await db.execute(stmt)
        await db.commit()
