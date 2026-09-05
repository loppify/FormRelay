import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import SUPPORTED_LANGUAGES, get_locale
from app.database.models import Form
from app.database.session import get_db

router = APIRouter(prefix="/api/forms", tags=["forms"])


class FormCreate(BaseModel):
    title: str
    telegram_chat_id: int
    language: str = "en"


class FormRead(BaseModel):
    title: str
    telegram_chat_id: int
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=FormRead, status_code=status.HTTP_201_CREATED)
async def create_form_endpoint(
        data: FormCreate,
        locale: tuple[str, dict[str, str]] = Depends(get_locale),
        db: AsyncSession = Depends(get_db),
):
    current_lang, _ = locale
    lang = data.language if data.language in SUPPORTED_LANGUAGES else current_lang

    new_form = Form(
        title=data.title,
        telegram_chat_id=data.telegram_chat_id,
        language=lang,
    )
    db.add(new_form)
    await db.commit()
    await db.refresh(new_form)
    return new_form
