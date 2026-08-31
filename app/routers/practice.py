"""Authenticated access to practice journal media."""

from fastapi import APIRouter
from fastapi.responses import Response
from sqlalchemy import select

from app.deps import CurrentPlayer, DbDep
from app.errors import NotFoundError
from app.models import PracticeAttachment, PracticeEntry

router = APIRouter(prefix="/practice-attachments", tags=["skills"])


@router.get("/{attachment_id}", summary="Download a practice attachment")
def download(attachment_id: int, player: CurrentPlayer, db: DbDep) -> Response:
    attachment = db.scalar(
        select(PracticeAttachment)
        .join(PracticeEntry)
        .where(
            PracticeAttachment.id == attachment_id,
            PracticeEntry.player_id == player.id,
        )
    )
    if attachment is None:
        raise NotFoundError(f"No practice attachment with id {attachment_id}.")
    return Response(
        content=attachment.data,
        media_type=attachment.content_type,
        headers={"Content-Disposition": f'inline; filename="{attachment.filename}"'},
    )
