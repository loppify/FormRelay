import uuid
from unittest.mock import AsyncMock, patch
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database.models import Base
from app.database.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_form_creation_and_submission():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        create_res = await ac.post(
            "/api/forms",
            json={"title": "Landing Test", "telegram_chat_id": 987654321},
        )
        assert create_res.status_code == 201
        form_id = create_res.json()["id"]

        with patch("app.api.ingest.send_telegram_alert", new_callable=AsyncMock) as mock_tg:
            mock_tg.return_value = True

            submit_res = await ac.post(
                f"/f/{form_id}",
                json={"client_name": "Ivan", "phone": "+380501112233"},
                headers={"Accept": "application/json"},
            )

            assert submit_res.status_code == 200
            assert submit_res.json()["status"] == "success"
            assert mock_tg.called
            assert mock_tg.call_args[0][0] == 987654321
            assert "Ivan" in mock_tg.call_args[0][1]


@pytest.mark.asyncio
async def test_invalid_form_uuid():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        random_id = uuid.uuid4()
        res = await ac.post(
            f"/f/{random_id}",
            json={"dummy": "data"},
            headers={"Accept": "application/json"},
        )
        assert res.status_code == 404