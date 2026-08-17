# PRAVAAH Deployment & Database Migration Guide

This guide covers migrating the PRAVAAH Django application from SQLite to Neon PostgreSQL for production hosting on Render, while preserving SQLite for local development.

---

## 1. Local Development

In local development, the application defaults to using SQLite (`db.sqlite3`) if `DATABASE_URL` is not defined in the environment.

### Setup Steps:
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/macOS
   # .venv\Scripts\activate   # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure local environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

4. Run database migrations for local SQLite:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## 2. Neon Setup (PostgreSQL)

1. **Create Account & Project**:
   Sign in to [Neon PostgreSQL](https://neon.tech) and create a new project (e.g., `pravaah-db`).

2. **Get Connection String**:
   - Navigate to the Neon Dashboard -> **Dashboard** / **Connection Details**.
   - Copy the PostgreSQL connection string URI. Ensure `?sslmode=require` is appended to the connection URL.
   - Example connection string:
     `postgresql://user:password@ep-xyz.us-east-2.aws.neon.tech/pravaah_db?sslmode=require`

3. **Verify Settings**:
   Django will parse `DATABASE_URL` using `dj-database-url` and `psycopg` whenever `DATABASE_URL` is present.

---

## 3. Render Deployment

1. **Create a Web Service on Render**:
   - Log in to [Render](https://render.com).
   - Click **New +** -> **Web Service**.
   - Connect your GitHub repository (`pravaah`).

2. **Service Configuration**:
   - **Environment**: Python 3.12
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application`

3. **Configure Environment Variables**:
   Add all required environment variables in the Render Dashboard (under **Environment** tab).

4. **Deploy**:
   Click **Create Web Service** to start the initial deployment.

---

## 4. Required Environment Variables

Configure the following environment variables on Render:

| Variable | Description | Example / Value |
| :--- | :--- | :--- |
| `SECRET_KEY` | Production Django secret key | `your-secure-random-secret-key` |
| `DEBUG` | Enable/disable Django debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated allowed domain names | `pravaah.onrender.com,.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins | `https://pravaah.onrender.com,https://*.onrender.com` |
| `DATABASE_URL` | Neon PostgreSQL connection URI | `postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/pravaah_db?sslmode=require` |
| `SITE_URL` | Public base URL of the site | `https://pravaah.onrender.com` |

---

## 5. Migration Steps

### Initial Production Database Migration
When deploying to Render with `DATABASE_URL` configured, database migrations are automatically applied during build execution via `./build.sh`:
```bash
python manage.py migrate
```

### Manual Database Migration
If you need to run migrations manually against your Neon database from your local machine:
```bash
DATABASE_URL="postgresql://user:pass@ep-xyz.us-east-2.aws.neon.tech/pravaah_db?sslmode=require" python manage.py migrate
```

### Health Check Verification
Verify that the database and web service are operational by querying the health check endpoint:
```bash
curl -i https://pravaah.onrender.com/health/
```
Expected Response (HTTP Status 200 OK):
```json
{
  "status": "ok"
}
```
