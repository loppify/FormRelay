# FormRelay

Receive submissions from a static HTML form in Telegram.

FormRelay is a small form backend for landing pages, portfolios, and other static websites. It creates a form endpoint, stores incoming submissions in PostgreSQL, and attempts to send each submission to a configured Telegram chat.

This is a personal MVP by [Rostyslav Tarasov](https://github.com/loppify). The initial version focuses on one workflow: create an endpoint, add it to a website, and receive enquiries in Telegram.

[Hosted MVP](https://formrelay-5ysr.onrender.com/) · [Issues](https://github.com/loppify/FormRelay/issues)

## What it does

- Creates UUID-based form endpoints without requiring an account.
- Accepts JSON objects and ordinary HTML form fields, including text fields submitted as multipart form data.
- Stores submissions and their timestamps in PostgreSQL.
- Formats Telegram notifications with HTML-escaped field names and values.
- Returns a JSON response or redirects the browser to a thank-you page.
- Provides English, Ukrainian, and German interface translations.
- Includes Docker configuration, automated flow tests, and a GitHub Actions workflow for linting, formatting, testing, and triggering deployment.

## Connect a website

1. Open the hosted MVP.
2. Start [the FormRelay bot](https://t.me/formrelay1_bot) so it can message your account.
3. Enter a form title and the Telegram chat ID for the destination you control.
4. Copy the generated endpoint into your form's `action` attribute.
5. Send a test submission and check that the notification arrives.

```html
<form action="https://formrelay-5ysr.onrender.com/f/YOUR_FORM_ID" method="post">
  <label>
    Name
    <input name="name" required>
  </label>
  <label>
    Email
    <input name="email" type="email" required>
  </label>
  <label>
    Message
    <textarea name="message" required></textarea>
  </label>
  <button type="submit">Send</button>
</form>
```

Replace `YOUR_FORM_ID` with the generated UUID. Field names are flexible; a predefined contact-form schema is not required. Browser-side validation such as `required` does not replace server-side validation.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/forms` | Create a form endpoint |
| `POST` | `/f/{form_id}` | Submit fields to an existing form |
| `GET` | `/` | Open the setup interface |
| `GET` | `/success` | Open the thank-you page |

Create an endpoint on a local instance:

```bash
curl -X POST http://127.0.0.1:8000/api/forms \
  -H 'Content-Type: application/json' \
  -d '{"title":"Portfolio","telegram_chat_id":123456789,"language":"en"}'
```

Replace the example chat ID with your own. The response includes the form's UUID in `id`.

Submit JSON:

```bash
curl -X POST http://127.0.0.1:8000/f/YOUR_FORM_ID \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -d '{"name":"Alex","email":"alex@example.com","message":"Project enquiry"}'
```

The response is `200` with a status and submission ID when the handler completes. Without `Accept: application/json`, the handler returns a `303` redirect to `/success`.

**Delivery behavior:** the database commit happens before the Telegram request. A successful HTTP response currently does not confirm Telegram delivery. Failed sends are logged, but delivery status and automatic recovery are not yet implemented.

## Run locally

Requirements: Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), Docker with Compose, and a Telegram bot token.

```bash
git clone https://github.com/loppify/FormRelay.git
cd FormRelay
uv sync
```

Create `.env` in the repository root:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/formrelay
TELEGRAM_BOT_TOKEN=replace_with_your_bot_token
BASE_URL=http://127.0.0.1:8000
```

The database credentials above match the included local Compose database. Start PostgreSQL and the application:

```bash
docker compose up -d db
uv run uvicorn app.main:app --reload
```

Open [the application](http://127.0.0.1:8000/) or [API documentation](http://127.0.0.1:8000/docs). The current startup code creates missing tables with SQLAlchemy `create_all`; it does not migrate an existing schema.

For a self-hosted instance, start your own bot before testing notifications. The landing page currently links to the hosted FormRelay bot; update that link when using a different bot.

### Running both services in Docker

Set the database host in `.env` to `db`:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/formrelay
```

Before using the complete Compose setup, align the Dockerfile's Python base image with the project's Python 3.12+ requirement and correct `poastgres` to `postgres` in the database health-check command.

```bash
docker compose up --build
```

These configuration adjustments are needed in the current repository. The local Python workflow above avoids building the application image.

## Development

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

The flow tests use an in-memory SQLite database and mock Telegram delivery. They cover form creation with a JSON submission, an HTML-form redirect, and an unknown form ID. They do not establish production PostgreSQL behavior or delivery reliability during Telegram failures.

| Location | Responsibility |
| --- | --- |
| `app/api/` | Form creation and submission routes |
| `app/database/` | SQLAlchemy models and async sessions |
| `app/services/telegram.py` | Notification formatting and delivery |
| `app/core/` | Configuration and localization |
| `app/templates/`, `app/static/` | Server-rendered interface |
| `app/translations/` | Interface and notification translations |
| `tests/` | Automated flow tests |

## Current boundaries

- File uploads are not supported. Send text fields or JSON objects.
- Payload validation and application-level limits are basic.
- Destination ownership verification, rate limiting, and spam protection are not implemented.
- There is no account dashboard, submission-management API, billing, or custom redirect configuration.
- Alembic is a dependency, but a migration history has not been added.

The next development priorities are reliable delivery, verified destinations, input boundaries, and reproducible database changes. Further features will depend on feedback from people using the product.

## Feedback

For a bug report, include the expected result, the observed behavior, and a reproducible example with personal data and credentials removed. For a feature request, describe the form workflow you are trying to support.

## License

[GNU Affero General Public License v3.0](LICENSE).
