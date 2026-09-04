from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.forms import router as forms_router
from app.api.ingest import router as ingest_router
from app.database.session import init_db
from app.services.telegram import http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await http_client.aclose()


app = FastAPI(title="FormRelay", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(forms_router)
app.include_router(ingest_router)


@app.get("/", response_class=HTMLResponse)
async def render_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/success", response_class=HTMLResponse)
async def render_success(request: Request):
    return templates.TemplateResponse(request=request, name="success.html")
