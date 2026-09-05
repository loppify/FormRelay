# ⚡ FormRelay

> **Turn any HTML form into a Telegram-powered backend in seconds.**

FormRelay is a lightweight **headless form backend** for static websites, landing pages, portfolios, and small projects.

* No custom backend.
* No SMTP configuration.
* No user accounts.
* No JavaScript framework.

Just create a form endpoint, point your HTML `<form>` at it, and receive submissions directly in **Telegram**.

---

## ✨ Why FormRelay?

Building a simple contact form shouldn't require building an entire backend.

With FormRelay, your frontend can stay completely static:

```html
<form action="https://your-formrelay-instance.com/f/YOUR_FORM_ID" method="POST">
    <input name="name" placeholder="Your name" required>
    <input name="email" type="email" placeholder="Email" required>
    <textarea name="message" placeholder="Message" required></textarea>

    <button type="submit">Send</button>
</form>
```

That's it.

FormRelay receives the submission, stores it, and sends a formatted notification to your Telegram chat.

---

## 🚀 Features

* 🪶 **Headless** - works with any frontend that can submit an HTTP request
* ⚡ **Zero-config frontend** - just add a form `action`
* 🆔 **UUID-based form endpoints** - no accounts required
* 📦 **JSON & `multipart/form-data`** support
* 🧩 **Arbitrary form fields** - no predefined schema required
* 💬 **Telegram notifications** via Bot API
* 💾 **Persistent submissions** stored in PostgreSQL
* 🔄 **Automatic browser redirects** to a default thank-you page
* 🐳 **Docker-ready**
* ☁️ **Cloud deployment ready**
* 🖥️ **Tiny server-rendered UI** - no SPA or build pipeline

---

## 🎯 The idea

FormRelay is built around one simple workflow:

```text
Your Website
     │
     │ POST
     ▼
┌─────────────┐
│  FormRelay  │
└──────┬──────┘
       │
       ├──────────────► PostgreSQL
       │
       └──────────────► Telegram
```

Your website doesn't need to know anything about servers, databases, or Telegram.

It only needs an HTML form.

---

## 🏁 Quick Start

### 1. Create a FormRelay endpoint

Open the FormRelay web interface and provide:

* a name for your form
* your Telegram `chat_id`

FormRelay generates a unique endpoint for you.

### 2. Add the endpoint to your website

```html
<form action="https://your-formrelay-instance.com/f/YOUR_FORM_ID" method="POST">
    <input type="text" name="name" placeholder="Name">
    <input type="email" name="email" placeholder="Email">
    <textarea name="message" placeholder="Message"></textarea>

    <button type="submit">Send</button>
</form>
```

### 3. Submit the form

FormRelay will:

1. Parse the submitted fields
2. Store the submission
3. Send a notification to Telegram
4. Redirect the browser to the default thank-you page

Your backend is done.

---

## 📡 API

### Submit a form

```http
POST /f/{form_id}
```

The endpoint accepts both JSON and `multipart/form-data`.

### JSON

```bash
curl -X POST \
  https://your-formrelay-instance.com/f/YOUR_FORM_ID \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello from my website!"
  }'
```

### Multipart form data

```bash
curl -X POST \
  https://your-formrelay-instance.com/f/YOUR_FORM_ID \
  -F "name=John Doe" \
  -F "email=john@example.com" \
  -F "message=Hello from my website!"
```

Form fields are intentionally **schema-free**. You can send whatever fields your frontend needs.

For example:

```json
{
    "name": "Alice",
    "company": "Acme Inc.",
    "email": "alice@example.com",
    "subject": "Project inquiry",
    "message": "I'd like to discuss a project."
}
```

---

## 💬 Telegram Notifications

Every successful submission is formatted into a readable Telegram message and delivered through the Telegram Bot API.

Example:

```text
Нова заявка: Portfolio Contact

name: Alice

email: alice@example.com

company: Acme Inc.

message: I'd like to discuss a project.

```

No SMTP server required.

---

## 🛠️ Tech Stack

FormRelay intentionally uses a small stack:

| Component        | Technology             |
| ---------------- | ---------------------- |
| Language         | Python 3.12+           |
| API              | FastAPI                |
| Database         | PostgreSQL             |
| ORM              | SQLAlchemy 2.x (Async) |
| Migrations       | Alembic                |
| HTTP Client      | HTTPX                  |
| Templates        | Jinja2                 |
| Server           | Uvicorn                |
| Containerization | Docker                 |

The project uses asynchronous I/O throughout the request and Telegram delivery pipeline.

---

## 🐳 Self-hosting

Clone the repository:

```bash
git clone https://github.com/loppify/FormRelay.git
cd FormRelay
```

Install dependencies:

```bash
uv sync
```

Or run the application using Docker:

```bash
docker compose up --build
```

The exact environment variables and deployment configuration are intentionally kept simple and will evolve together with the MVP.

---

## ⚙️ Configuration

FormRelay uses environment variables for runtime configuration.

Typical configuration includes:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/formrelay

TELEGRAM_BOT_TOKEN=your_bot_token
```

> **Never commit your Telegram bot token or database credentials to Git.**

---

## 🧪 Development

Install dependencies:

```bash
uv sync
```

Run the development server:

```bash
uv run uvicorn formrelay.main:app --reload
```

Run tests:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

---

## 📂 Project Structure

```text
FormRelay/
├── app/
├── src/
│   └── formrelay/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```

The project follows a small, modular architecture so the MVP can evolve without turning into a monolith.

---

## 🔒 MVP Scope

FormRelay is intentionally small.

### Included

* Anonymous form creation
* UUID-based endpoints
* JSON submissions
* `multipart/form-data` submissions
* Dynamic form fields
* PostgreSQL persistence
* Telegram notifications
* Default thank-you redirect
* Docker deployment

### Not included yet

* User accounts
* Authentication / JWT
* Custom redirect URLs
* File uploads
* CAPTCHA / Turnstile
* Spam protection
* CSV / Excel / Google Sheets exports
* Billing and subscriptions
* Usage limits

These features may come later. The MVP focuses on one thing:

> **Make a static HTML form send a message to Telegram with as little friction as possible.**

---

## 🗺️ Roadmap

### `v0.1 - MVP`

* [x] Core FastAPI application
* [x] Form endpoints
* [x] PostgreSQL persistence
* [x] Telegram integration
* [x] JSON input
* [x] Multipart input
* [x] Docker setup
* [x] Public MVP release
* [ ] End-to-end production testing

### `v0.2 - Reliability`

* [ ] Better error handling
* [ ] Submission delivery status
* [ ] Basic request validation
* [ ] Improved Telegram formatting
* [ ] Health checks
* [ ] Observability

### `v0.3 - Protection`

* [ ] Rate limiting
* [ ] Spam protection
* [ ] Origin/domain restrictions
* [ ] Abuse prevention

### `v1.0 - Micro-SaaS`

* [ ] User accounts
* [ ] Form management dashboard
* [ ] Multiple forms per user
* [ ] Usage limits
* [ ] Custom redirects
* [ ] Subscription plans

---

## 🤝 Contributing

FormRelay is currently an early-stage project.

Issues, ideas, bug reports, and pull requests are welcome.

If you find something broken, open an issue with:

* what you expected
* what actually happened
* steps to reproduce
* relevant logs or request payloads

---

## 📄 License

See the repository for the current license information.

---

## 💡 Philosophy

FormRelay follows a simple principle:

**Your landing page shouldn't need a backend just to have a contact form.**

Keep the frontend static.
Keep the backend tiny.
Send the leads where you actually read them.

**Create - Copy - Deploy - Receive.**

---

<p align="center">
  Built with Python, FastAPI and a slightly unhealthy love for simple backends.
</p>
