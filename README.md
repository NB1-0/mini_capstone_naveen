# Online Bookstore Backend

FastAPI backend for an online bookstore with MongoDB, JWT authentication, RBAC, book management, ordering, and admin reporting.

## Features

- JWT authentication with register, login, token, and profile endpoints
- Role-based access control for `admin` and `customer`
- Book catalog with admin-only create, update, and delete operations
- Customer order placement with stock validation and stock deduction
- Admin order listing, status updates, and sales reporting
- Structured controller, service, repository, and MongoDB layers
- Request logging, rate limiting, and centralized exception handling

## Project Structure

```text
backend/
  app/
    api/
    controllers/
    core/
    db/
    exceptions/
    middleware/
    models/
    repositories/
    schemas/
    services/
    utils/
  scripts/
  tests/
  requirements.txt
  Dockerfile
  docker-compose.yml
  .env
frontend/
```

## Environment

The project reads configuration from `backend/.env` when you run the backend from the `backend/` directory.

Important variables:

- `BOOKSTORE_MONGODB_URL`
- `BOOKSTORE_MONGODB_DB_NAME`
- `BOOKSTORE_SECRET_KEY`
- `BOOKSTORE_ADMIN_EMAIL`
- `BOOKSTORE_ADMIN_PASSWORD`

## Local Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/create_admin.py
python scripts/seed_books.py
uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000/api/v1`

Frontend URL: `http://127.0.0.1:8000/`

Swagger UI: `http://127.0.0.1:8000/docs`

Swagger authorization uses HTTP bearer auth. Log in with `/api/v1/auth/login` or `/api/v1/auth/token`, copy the returned JWT access token, and paste it into the `Authorize` dialog.
If `/docs` shows a blank loading page, reinstall dependencies so the local Swagger UI assets are available: `pip install -r requirements.txt`.

## Docker

```bash
cd backend
docker compose up --build
```

## Frontend Overview

The project now includes a lightweight same-origin frontend served by FastAPI from `frontend/`.

- Public catalog browsing from `GET /api/v1/books`
- Customer login and registration with JWT session storage
- Cart and checkout flow backed by `POST /api/v1/orders`
- Customer order history from `GET /api/v1/orders`
- Admin inventory tools for book create, update, and delete
- Admin sales report and order status updates

## API Overview

### Auth

- `POST /api/v1/auth/register` with `email`, `password`, and optional `role`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `GET /api/v1/auth/me`

### Users

- `GET /api/v1/users/me`
- `GET /api/v1/users` admin only

### Books

- `GET /api/v1/books`
- `GET /api/v1/books/{book_id}`
- `POST /api/v1/books` admin only
- `PUT /api/v1/books/{book_id}` admin only
- `DELETE /api/v1/books/{book_id}` admin only

### Orders

- `POST /api/v1/orders` customer only
- `GET /api/v1/orders` customer only
- `GET /api/v1/orders/{order_id}` customer only

### Admin

- `GET /api/v1/admin/orders`
- `GET /api/v1/admin/salesreport`
- `PATCH /api/v1/admin/orders/{order_id}/status`

## Tests

```bash
cd backend
pytest
```
