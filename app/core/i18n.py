# app/core/i18n.py
import json
from functools import lru_cache
from pathlib import Path

from fastapi import Request

SUPPORTED_LANGUAGES = {"en", "uk"}
DEFAULT_LANGUAGE = "en"

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"


@lru_cache
def load_translations(language: str) -> dict[str, str]:
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    with (TRANSLATIONS_DIR / f"{language}.json").open(encoding="utf-8") as file:
        return json.load(file)


def get_language(request: Request) -> str:
    lang: str = request.query_params.get("lang") or DEFAULT_LANGUAGE

    if lang in SUPPORTED_LANGUAGES:
        return lang

    lang = request.cookies.get("language") or DEFAULT_LANGUAGE

    if lang in SUPPORTED_LANGUAGES:
        return lang

    for lang in request.headers.get("accept-language", "").lower().split(","):
        lang = lang.split(";")[0].strip().split("-")[0]

        if lang in SUPPORTED_LANGUAGES:
            return lang

    return DEFAULT_LANGUAGE


def get_locale(request: Request) -> tuple[str, dict[str, str]]:
    language = get_language(request)

    return language, load_translations(language)
