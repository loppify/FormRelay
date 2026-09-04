import html
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(10.0, connect=5.0),
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
)


def format_submission_message(from_title: str, payload: dict) -> str:
    lines = [f"<b>Нова заявка. {html.escape(from_title)}</b>\n"]
    for key, val in payload.items():
        if key.startswith("_"):
            continue
        clean_key = html.escape(str(key))
        clean_val = html.escape(str(val))
        lines.append(f"<b>{clean_key}:</b> {clean_val}\n")
    return "\n".join(lines)


async def send_telegram_alert(chat_id: int, message: str) -> bool:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    print(settings.TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = await http_client.post(url, json=payload)

        if response.status_code == 400 and "can't parse entities" in response.text:
            logger.warning("HTML parse error. Retrying without formatting.")
            payload.pop("parse_mode")
            response = await http_client.post(url, json=payload)

        if response.status_code == 200:
            return True

        logger.error(
            f"Failed to send Telegram message to {chat_id}: "
            f"Status {response.status_code}, Body: {response.text}"
        )
        return False
    except httpx.RequestError as exc:
        logger.error(f"Network error while sending Telegram message to {chat_id}: {exc}")
        return False
