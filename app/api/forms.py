import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.database.models import Form
from app.database.session import get_db

router = APIRouter(prefix="/api/forms", tags=["forms"])


class FormCreate(BaseModel):
    title: str
    telegram_chat_id: int


class FormRead(BaseModel):
    title: str
    telegram_chat_id: int
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=FormRead, status_code=status.HTTP_201_CREATED)
async def create_form(data: FormCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    new_form = Form(title=data.title, telegram_chat_id=data.telegram_chat_id)
    db.add(new_form)
    await db.commit()
    await db.refresh(new_form)
    return new_form
