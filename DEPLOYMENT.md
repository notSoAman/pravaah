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
curl -i https://<your-render-url>.onrender.com/health/
```
Expected Response (`HTTP 200 OK`):
```json
{
  "status": "ok"
}
```

---

## 4. Keeping the Site Live 24/7 (Preventing Inactivity Sleep)

Render Web Services on the free tier automatically **spin down (sleep) after 15 minutes of inactivity** (zero incoming HTTP traffic). The next visitor experiences a 40–60 second "cold start" delay while the container boots back up.

To keep the site **instantly responsive 24/7**, use external HTTP pings to keep the container awake.

### A. Important: Verifying Your Exact Render URL
Render subdomain names (`*.onrender.com`) are **globally unique across all users**.
- If `https://pravaah.onrender.com` returns a Vite 403 error (`Blocked request... vite.config.js`), that subdomain belongs to a different project or user.
- To check your exact URL: Open your [Render Dashboard](https://dashboard.render.com/) -> Select your PRAVAAH Web Service -> The actual public URL is displayed directly beneath the service name at top-left (e.g., `https://pravaah-xxxx.onrender.com`).

### B. Recommended Primary Monitor: UptimeRobot (Free & 100% Reliable)
External uptime services like [UptimeRobot](https://uptimerobot.com) run on dedicated infrastructure and **never suffer from GitHub queue delays**:

1. Sign up for free at [uptimerobot.com](https://uptimerobot.com) (free plan includes 50 monitors).
2. Click **+ Add New Monitor**.
3. Configure the monitor:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `PRAVAAH Live`
   - **URL (or IP):** `https://<your-actual-render-url>.onrender.com/health/`
   - **Monitoring Interval:** `Every 5 minutes`
4. Click **Create Monitor**.
5. *Result:* UptimeRobot will ping your `/health/` endpoint every 5 minutes around the clock, guaranteeing the Render container never sleeps.

*(Alternative: You can also use [cron-job.org](https://cron-job.org/) to trigger a GET request to `/health/` every 5–8 minutes).*

### C. Secondary Backup: GitHub Actions (`.github/workflows/uptime.yml`)
This repository includes an automated keep-awake workflow configured to ping every 5 minutes (`*/5 * * * *`).

To connect it to your live service:
1. In your GitHub repository, navigate to **Settings -> Secrets and variables -> Actions**.
2. Click **New repository secret**.
3. Set:
   - **Name:** `SITE_URL`
   - **Secret:** `https://<your-actual-render-url>.onrender.com`
4. Click **Add secret**.
5. You can manually test the workflow anytime from the **Actions** tab -> **Render Keep Awake** -> **Run workflow**.

