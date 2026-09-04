import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


from app.database.models import Form, Submission
from app.database.session import get_db
from app.services.telegram import send_telegram_alert, format_submission_message

router = APIRouter()


@router.post("/f/{form_id}")
async def handle_form_submission(
    form_id: uuid.UUID, request: Request, db: Annotated[AsyncSession, Depends(get_db)]
):
    query = select(Form).where(Form.id == form_id)
    result = await db.execute(query)
    form_obj = result.scalar_one_or_none()

    if not form_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Form endpoint not found"
        )

    content_type = request.headers.get("content-type", "")
    data: dict = {}

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
    await db.commit()

    msg_text = format_submission_message(form_obj.title, data)
    await send_telegram_alert(form_obj.telegram_chat_id, msg_text)

    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return JSONResponse(
            content={"status": "success", "id": submission.id},
            status_code=status.HTTP_200_OK,
        )
    return RedirectResponse(url="/success", status_code=status.HTTP_303_SEE_OTHER)
