import json
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.i18n import load_translations
from app.database.models import Delivery, DeliveryStatus, Form, Submission
from app.database.session import get_db
from app.services.telegram import format_submission_message, send_telegram_alert

router = APIRouter()


@router.post("/f/{form_id}")
async def handle_form_submission(
    form_id: uuid.UUID, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(
        select(Form).options(selectinload(Form.destinations)).where(Form.id == form_id)
    )
    form_obj = result.scalar_one_or_none()

    if not form_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Form endpoint not found"
        )

    translations = load_translations(form_obj.language)

    def t(key: str) -> str:
        return translations.get(key, key)

    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            data = await request.json()
        except json.decoder.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body"
            )
    else:
        form_data = await request.form()
        data = {k: v for k, v in form_data.items()}

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Form payload is empty"
        )

    submission = Submission(form_id=form_obj.id, payload=data)
    db.add(submission)
    await db.flush()

    deliveries = [
        Delivery(
            submission_id=submission.id,
            destination_id=destination.id,
            status=DeliveryStatus.PENDING,
        )
        for destination in form_obj.destinations
    ]
    db.add_all(deliveries)

    await db.commit()

    msg_text = format_submission_message(form_obj.title, data, t=t)

    for delivery in deliveries:
        destination = delivery.destination

        if destination.type == "telegram":
            succeeded = await send_telegram_alert(int(destination.reference), msg_text)
            delivery.status = (
                DeliveryStatus.SUCCEEDED if succeeded else DeliveryStatus.FAILED
            )
            await db.commit()

    await db.commit()
    accept = request.headers.get("accept", "")

    if "application/json" in accept:
        return JSONResponse(
            content={"status": "success", "id": submission.id},
            status_code=status.HTTP_200_OK,
        )
    return RedirectResponse(url="/success", status_code=status.HTTP_303_SEE_OTHER)
