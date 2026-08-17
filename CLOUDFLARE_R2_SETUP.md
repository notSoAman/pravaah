# Cloudflare R2 Media Storage Setup & Configuration Guide

This guide details the step-by-step procedure to set up **Cloudflare R2 Object Storage** for hosting media assets (event covers, gallery photos, member photos, film posters, hero slides, and Notion journal imports) for the **PRAVAAH** Django project on **Render**.

---

## 1. Cloudflare Account Setup

1. Sign up or log in to the [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. In the left-hand navigation sidebar, select **R2 Object Storage**.
3. If this is your first time using R2, click **Purchase R2 Subscription** or enable R2 (Cloudflare provides a generous free tier of 10 GB storage and 10 million read operations/month).

---

## 2. R2 Bucket Creation

1. Navigate to **R2** -> **Overview**.
2. Click **Create bucket**.
3. Set **Bucket Name** to `pravaah-media` (or your preferred unique bucket name).
4. Choose your desired location hint (e.g., `Automatic` or `APAC`).
5. Click **Create Bucket**.
6. *(Optional - Public Access)*:
   - Under your bucket's **Settings** tab, scroll to **Public Access**.
   - You can connect a custom domain (e.g., `media.pravaah.org`) under **Custom Domains**, or enable **R2.dev Subdomain** to allow direct browser image access.

---

## 3. API Token Creation

1. Under **R2** -> **Overview**, click **Manage R2 API Tokens** on the right side.
2. Click **Create API Token**.
3. Configure the token permissions:
   - **Token Name**: `pravaah-render-storage-token`
   - **Permissions**: Select **Admin Read & Write** (or Object Read & Write).
   - **Specify Bucket**: Select **Apply to specific buckets only** and pick `pravaah-media`.
4. Click **Create API Token**.
5. Save the generated credentials securely:
   - **Account ID** (found on the R2 Overview page right sidebar)
   - **Access Key ID**
   - **Secret Access Key**

---

## 4. Environment Variables

Configure the following environment variables on your deployment platform (e.g., Render Dashboard):

| Variable | Required | Description | Example |
| :--- | :--- | :--- | :--- |
| `USE_R2_STORAGE` | **Yes** | Enable Cloudflare R2 storage backend | `True` |
| `R2_ACCOUNT_ID` | **Yes** | Cloudflare Account ID | `0123456789abcdef0123456789abcdef` |
| `R2_ACCESS_KEY_ID` | **Yes** | R2 API Access Key ID | `a1b2c3d4e5f6g7h8i9j0` |
| `R2_SECRET_ACCESS_KEY` | **Yes** | R2 API Secret Access Key | `secretkey1234567890abcdef` |
| `R2_BUCKET_NAME` | **Yes** | Cloudflare R2 Bucket Name | `pravaah-media` |
| `R2_CUSTOM_DOMAIN` | *Optional* | Custom Domain or R2 public URL | `media.pravaah.org` |

---

## 5. Render Configuration

1. Log in to [Render](https://render.com) and navigate to your **PRAVAAH** Web Service.
2. Select **Environment** from the left-side menu.
3. Under **Environment Variables**, click **Add Environment Variable** for each of the following:
   - Set `USE_R2_STORAGE` = `True`
   - Set `R2_ACCOUNT_ID` = *(Your Cloudflare Account ID)*
   - Set `R2_ACCESS_KEY_ID` = *(Your Access Key ID)*
   - Set `R2_SECRET_ACCESS_KEY` = *(Your Secret Access Key)*
   - Set `R2_BUCKET_NAME` = `pravaah-media`
   - Set `R2_CUSTOM_DOMAIN` = *(Optional custom domain)*
4. Click **Save Changes**. Render will automatically trigger a new deployment.

---

## 6. Verification Steps

1. **Upload Test**:
   - Access the Django Admin interface at `https://<your-app>.onrender.com/admin/`.
   - Upload a new Team Member photo, Event cover image, or Film poster.
2. **CDN URL Check**:
   - Inspect the uploaded image URL in your browser developer tools.
   - Verify that the image URL begins with your R2 bucket endpoint or custom domain:
     `https://pravaah-media.<account_id>.r2.cloudflarestorage.com/media/...` or `https://media.pravaah.org/media/...`.
3. **Journal Import Verification**:
   - Upload a Notion HTML export ZIP file via `JournalImport` admin.
   - Verify that ZIP extraction processes correctly, images are stored in R2, and the imported article content displays inline images served from R2.
