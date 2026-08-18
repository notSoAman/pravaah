# PRAVAAH Deployment & Management Guide

This guide covers deploying the **PRAVAAH** Django application to **Render**, backed by **Supabase PostgreSQL** for data and **Supabase Storage** for media assets.

---

## 1. Environment Variables on Render

In your Render Dashboard (**Web Service -> Environment**), configure the following environment variables:

| Variable Name | Required Value | Description |
| :--- | :--- | :--- |
| `SECRET_KEY` | *(Your secure Django secret key)* | Production Django secret key |
| `DEBUG` | `False` | Disable debug mode in production |
| `ALLOWED_HOSTS` | `pravaah.onrender.com,.onrender.com,localhost,127.0.0.1` | Allowed host headers |
| `CSRF_TRUSTED_ORIGINS` | `https://pravaah.onrender.com,https://*.onrender.com` | Trusted origins for CSRF protection |
| `DATABASE_URL` | `postgresql://postgres.rgarjpnbfgcyygnrqvuz:partly-winnings-fax@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres?sslmode=require` | Supabase PostgreSQL Connection String |
| `USE_SUPABASE_STORAGE` | `True` | Enables Supabase Storage backend |
| `SUPABASE_PROJECT_URL` | `https://rgarjpnbfgcyygnrqvuz.supabase.co` | Supabase project URL |
| `SUPABASE_SECRET_KEY` | `<your_supabase_secret_key>` | Supabase service API key |
| `SUPABASE_BUCKET` | `media-pravaah` | Supabase storage bucket name |
| `SITE_URL` | `https://pravaah.onrender.com` | Public base URL of the site |

---

## 2. Django Admin Capabilities (/admin)

Once deployed to Render (e.g. `https://pravaah.onrender.com/admin/`), you can log into Django Admin and perform full CRUD operations directly on Supabase:

### A. Adding Records & Uploading Media
- Creating a new **Member**, **Event**, **Movie**, **HeroSlide**, or **Journal**:
  - Database row is inserted directly into **Supabase PostgreSQL**.
  - Attached images are automatically optimized and saved to your **Supabase Storage** bucket (`media-pravaah`).

### B. Updating & Replacing Images
- Replacing an existing photo/cover image:
  - The new image is uploaded to **Supabase Storage**.
  - The old image is **automatically deleted** from Supabase Storage so no orphan files accumulate.

### C. Deleting Records & Bulk Deletion
- Deleting an individual record or performing **bulk deletion** (`Delete selected...`):
  - Database rows are deleted from **Supabase PostgreSQL**.
  - Associated media files are **automatically deleted** from **Supabase Storage**.

---

## 3. Helper Management Commands

Run these from your terminal when needed:

### Verify Storage Audit
Audits all database records against Supabase Storage and reports missing or orphaned files:
```bash
python manage.py verify_storage
```

### Sync Local Media to Supabase
Uploads all local media files into your Supabase Storage bucket:
```bash
python manage.py sync_media_to_supabase --overwrite
```

### Health Check
Verify web service & database status:
```bash
curl -i https://pravaah.onrender.com/health/
```
Expected Response (`HTTP 200 OK`):
```json
{
  "status": "ok"
}
```
