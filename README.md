# PRAVAAH — Mass-Communication & Media Club Web Application

**CS50’s Web Programming with Python and JavaScript — Final Capstone Project**

---

## Overview

**PRAVAAH** is the official web platform and content publishing system for a collegiate mass-communication, film, and media collective. Designed with a cinematic, editorial aesthetic inspired by studio platforms such as A24 Films, the application serves as a central digital archive and dynamic publication hub. It showcases student-produced films, curated events with rich photographic galleries, a club roster organized by organizational hierarchy, and an editorial journal powered by an automated Notion export ingestion pipeline.

The application is built on a backend powered by **Django (Python)** and a reactive frontend using **JavaScript (Alpine.js)** and **Tailwind CSS**. It is fully responsive across mobile, tablet, and desktop viewports, and features automated media optimization, resilient file lifecycle management, and production-grade cloud storage integrations.

---

## Distinctiveness and Complexity

This project was conceived and built from the ground up to satisfy the rigorous distinctiveness and complexity requirements set forth by Harvard University's CS50W curriculum.

### 1. Distinctiveness from Prior CS50W Projects

PRAVAAH is distinct in purpose, architecture, and user experience from all previous course assignments:

- **Not an E-Commerce / Auction Site (Project 2 — Commerce):** PRAVAAH contains no auctions, bids, shopping carts, or payment systems. It is not a commercial platform, but an editorial cultural archive and media publication engine.
- **Not a Social Network (Project 4 — Network):** There are no user profiles, follower/following relationships, public status feeds, or social "like" interactions. General visitors consume curated cultural content, while authorized editors and administrators manage publications through a protected, authenticated pipeline.
- **Not an Email Client (Project 3 — Mail):** It is not a single-page inbox/sent/archive interface; rather, it is a multi-view editorial publishing platform with specialized media renderers, relational data models, and an automated ingestion pipeline.
- **Not an Encyclopedia / Wiki (Project 1 — Wiki):** While it includes articles, PRAVAAH does not rely on simple in-browser Markdown entry forms. Instead, it implements an automated, multi-step archive ingestion pipeline capable of unpacking Notion ZIP export archives, processing nested folders, stripping proprietary metadata, extracting local binary media, sanitizing markup, dynamically rewriting embedded third-party video iframes, and storing assets in remote or local storage.
- **Not the Pizza Project:** There are no food menus, orders, cart configurations, or topping selections.

In aesthetic and functional direction, PRAVAAH eschews generic Bootstrap templates, dashboard cards, and SaaS interfaces in favor of a typography-first, monochrome, image-dominant editorial design system inspired by contemporary cinematic distribution platforms.

### 2. Architectural and Data Model Complexity

The backend is structured around **seven specialized Django models** in [`pravaah/models.py`](file:///home/aman/Projects/pravaah/pravaah/models.py) with relational integrity and data constraints:

1. `Member`: Represents creative crew members, handling bio descriptions, slug generation, and uploaded portrait photography.
2. `Event`: Stores club activities, dates, narrative descriptions, automated slug resolution, and cover imagery.
3. `EventImage`: A relational child model connected via `models.CASCADE` and `related_name="gallery"` to `Event`, supporting multi-image photo essays with per-image captions and integer ordering.
4. `Movie`: Archives cinematic productions, storing release dates, synopses, poster art, and source video URLs. It features an automated Python property (`youtube_embed_url`) utilizing regular expressions to normalize diverse YouTube URL variants (`youtu.be`, `shorts`, `/watch?v=`, `/embed/`) into privacy-enhanced, embeddable `youtube-nocookie.com` URLs with minimal branding parameters.
5. `Journal`: Models published essays and editorial commentary, linked to `Member` via `models.PROTECT` to enforce referential integrity. It includes scheduled publication logic via timezone-aware queries (`is_published`), automated slug generation, and storage for sanitized HTML content.
6. `JournalImport`: A dedicated ingestion staging model tracking file uploads of raw Notion ZIP exports, processing state machines (`pending`, `processing`, `success`, `failed`), detailed error reporting, and a one-to-one relationship with the generated `Journal` object.
7. `HeroSlide`: Manages homepage cinematic slides, controlling slide order, active toggles, and image backgrounds.

### 3. Automated Notion Ingestion & Sanitization Engine

A technical centerpiece of PRAVAAH is its automated Notion archive ingestion service implemented in [`pravaah/services/importer.py`](file:///home/aman/Projects/pravaah/pravaah/services/importer.py). This service allows writers to draft articles entirely in Notion—including images, headings, lists, tables, and video embeds—and export them as a standard ZIP file. The system processes the upload automatically:

- **Recursive ZIP Archive Extraction:** Notion exports often produce multi-part or nested ZIP files (e.g., `ExportBlock-...-Part-1.zip`). The service recursively unpacks these archives in memory using `zipfile` and `io.BytesIO`, handling deep virtual directory structures without polluting the server filesystem.
- **HTML DOM Parsing & Cleansing:** Using `BeautifulSoup4`, the service locates the primary HTML document, isolates the `.page-body` or `<article>` element, and purges Notion-specific artifact elements (such as proprietary page header banners and metadata property tables).
- **Asset Extraction & Storage Re-Mapping:** Embedded local images referenced by relative URLs inside the Notion export are extracted from the archive bytes, matched through exact path resolution or fuzzy basename fallbacks, and uploaded directly to Django's active storage backend (local disk or Supabase Cloud Storage) with unique, collision-free paths. The HTML `src` attributes are dynamically rewritten to the corresponding media URLs.
- **Dynamic Video Embed Rewriting:** Notion outputs video references as standard anchors or iframes. The service detects YouTube and Vimeo URLs via regular expressions and reconstructs them into responsive, aspect-ratio-constrained 16:9 embed containers using `youtube-nocookie.com` and Vimeo player protocols with strict security headers.
- **HTML Sanitization:** To protect against Cross-Site Scripting (XSS), the extracted markup is passed through Python's `bleach` library, enforcing a strict whitelist of permissible HTML tags (`p`, `h1`-`h6`, `blockquote`, `ul`, `ol`, `li`, `table`, `img`, `iframe`, etc.), safe attributes (whitelisting only `href`, `src`, `alt`, `allowfullscreen`, etc.), and approved URI protocols (`http`, `https`, `mailto`).
- **Transactional State Management:** Upon successful conversion, the system creates or updates the target `Journal` record, purges the temporary uploaded ZIP file, and automatically deletes the staging `JournalImport` record to keep the administrative database clean.

### 4. Automated Image Optimization & Storage Lifecycle Pipeline

To guarantee rapid loading times for photography-heavy layouts, PRAVAAH incorporates an automated image processing pipeline in [`pravaah/utils/image_processing.py`](file:///home/aman/Projects/pravaah/pravaah/utils/image_processing.py) and [`pravaah/signals.py`](file:///home/aman/Projects/pravaah/pravaah/signals.py):

- **Pillow Image Processing:** Uploaded images undergo automated EXIF orientation transposition (`ImageOps.exif_transpose`), mode conversion (converting RGBA and palette modes to RGB for clean JPEG encoding), Lanczos high-quality resampling down to pre-configured maximum dimensions (1600px for covers, 1920px for galleries, 800px for team portraits), and progressive compression.
- **Lifecycle Cleanup Signals:** When models are updated with new image files, or when records are deleted, custom Django signal receivers (`pre_save` and `post_delete`) intercept the operations. They check whether a file is referenced by any other database records and automatically delete the stale file from the storage backend (local media or cloud bucket), preventing storage bloat and orphaned files.

### 5. Frontend Interactivity & UI Engineering

Rather than relying on monolithic frontend frameworks or generic UI libraries, PRAVAAH combines **Alpine.js** for lightweight reactive interactions with a custom-compiled **Tailwind CSS** design system:

- **Cinematic Homepage Slider:** The homepage features a 4-slide Ken Burns carousel. Slide transitions blend opacity and slow zoom transforms (`scale-100` to `scale-110` over 6000ms), synchronized with timed text entrance animations. Slide markers display the club's identity across four scripts (English, Devanagari, Gurmukhi, and Assamese/Bengali) reflecting linguistic diversity. Users can let the slides cycle automatically or jump directly to any slide via reactive indicators.
- **Universal Image Lightbox Component:** Defined in [`templates/components/image_lightbox.html`](file:///home/aman/Projects/pravaah/templates/components/image_lightbox.html), a global Alpine.js component intercepts clicks on images across the site, smoothly presenting them in a high-resolution, backdrop-blurred fullscreen modal with escape key listeners and non-intrusive metadata captions.
- **Fullscreen Navigation Overlay:** A distraction-free overlay ([`templates/components/menu_overlay.html`](file:///home/aman/Projects/pravaah/templates/components/menu_overlay.html)) with oversized serif navigation links and micro-animations, responding to click triggers and keyboard shortcuts (`Escape`).
- **Database Query Optimization:** In [`pravaah/views.py`](file:///home/aman/Projects/pravaah/pravaah/views.py), queries utilize `select_related` (for single-query foreign key retrieval on authors) and `prefetch_related` (for efficient multi-image gallery fetching), completely eliminating $N+1$ query issues. The `team_list` view implements SQL-level ordering using Django's `Case`, `When`, and `Value` annotations to arrange executive leadership in precise organizational hierarchy.

### 6. Mobile Responsiveness

Every view is designed mobile-first and tested across breakpoints (320px mobile, 768px tablet, 1024px desktop, 1440px+ widescreen). Navigation transitions from a compact mobile top bar to a fullscreen overlay; multi-column film entries collapse cleanly from alternating two-column layouts into unified vertical stories; and event galleries automatically adapt from single-column mobile viewports to balanced three-column desktop grids.

---

## File Manifest: What’s Contained in Each File

Below is a comprehensive catalogue of the files created and configured across the PRAVAAH codebase:

```
pravaah/
├── manage.py                                 # Django CLI entrypoint
├── requirements.txt                          # Python dependencies specification
├── package.json                              # Node.js package manifest for Tailwind compilation
├── tailwind.config.js                        # Tailwind CSS design system configuration
├── build.sh                                  # Production deployment automation script
├── Procfile                                  # Gunicorn process definition for cloud hosts
├── render.yaml                               # Render Infrastructure-as-Code blueprint
├── runtime.txt                               # Explicit Python runtime version definition
├── .env.example                              # Template documenting required environment variables
├── AGENTS.md                                 # Architecture rules & A24 design specifications
├── CLOUDFLARE_R2_SETUP.md                    # Cloudflare R2 object storage documentation
├── DEPLOYMENT.md                             # Production deployment runbook
├── STYLING_IMPROVEMENTS.md                   # Visual audit & design system specifications
│
├── config/                                   # Project-level Django configuration
│   ├── __init__.py                           # Python package marker
│   ├── settings.py                           # Core settings (DB, storage, middleware, auth)
│   ├── urls.py                               # Global URL routing table & media endpoints
│   ├── wsgi.py                               # WSGI application callable for web servers
│   ├── asgi.py                               # ASGI application callable for async servers
│   └── storages.py                           # Custom storage class declarations
│
├── pravaah/                                  # Primary core Django application
│   ├── __init__.py                           # App initialization
│   ├── apps.py                               # PravaahConfig with automatic signal registration
│   ├── models.py                             # 7 database models (Member, Event, Movie, etc.)
│   ├── views.py                              # View functions with optimized ORM queries
│   ├── admin.py                              # Django Admin customization & image previews
│   ├── signals.py                            # Pre-save & post-delete cleanup & optimization hooks
│   ├── storages.py                           # Supabase S3/REST storage backend implementation
│   │
│   ├── services/                             # Business logic & background processing
│   │   ├── __init__.py                       # Package marker
│   │   └── importer.py                       # Notion ZIP ingestion, BS4 parsing, Bleach sanitizing
│   │
│   ├── utils/                                # Helper utilities
│   │   └── image_processing.py               # Pillow-based EXIF & resize optimization engine
│   │
│   ├── management/commands/                  # Custom Django manage.py commands
│   │   ├── process_journal_imports.py        # CLI command to process queued Notion imports
│   │   ├── sync_media_to_supabase.py         # Batch migration tool for media assets
│   │   ├── verify_storage.py                 # Diagnostic script verifying storage bucket access
│   │   └── ping_self.py                      # Health-check pinger for hosted environments
│   │
│   └── migrations/                           # Database schema migration files
│       ├── 0001_initial.py                   # Initial table creations
│       └── 0002_alter_member_photo.py        # Schema refinement for member photos
│
├── templates/                                # Django HTML templates
│   ├── base.html                             # Master HTML shell (fonts, CSS, Alpine, lightbox)
│   ├── index.html                            # Cinematic 4-slide hero landing page
│   │
│   ├── components/                           # Modular, reusable UI components
│   │   ├── navbar.html                       # Minimalist sticky header with hamburger toggle
│   │   ├── menu_overlay.html                 # Fullscreen typography navigation overlay
│   │   ├── image_lightbox.html               # Zero-dependency reactive image zoom modal
│   │   └── footer.html                       # Editorial monochrome footer
│   │
│   ├── events/                               # Event catalog & detail templates
│   │   ├── list.html                         # Ruled timeline of events with 16:9 thumbnails
│   │   └── detail.html                       # Fullscreen cover, narrative body, 3-column gallery
│   │
│   ├── films/                                # Film catalogue templates
│   │   └── list.html                         # Alternating poster/player layout with YouTube embeds
│   │
│   ├── journal/                              # Editorial publication templates
│   │   ├── list.html                         # 2-column essay archive with author bylines
│   │   └── detail.html                       # Reading view for sanitized Notion articles
│   │
│   └── team/                                 # Roster templates
│       └── list.html                         # Hierarchical leadership & crew presentation
│
├── static/                                   # Frontend static assets
│   ├── src/input.css                         # Tailwind source with typography & custom utilities
│   ├── css/styles.css                        # Compiled production CSS stylesheet
│   └── images/                               # Static imagery (hero slides, logo, favicons)
│
├── fixtures/                                 # Seed data for immediate evaluation
│   └── initial_data.json                     # Complete database dump with members, events, films
│
└── docs/                                     # Project reference documentation
    ├── DESIGN.md                             # Color palettes, typography, and layout rules
    └── WRITER_GUIDE.md                       # Editorial guidelines for Notion authoring
```

---

## How to Run the Application

Follow these steps to set up and run PRAVAAH locally in your development environment.

### Prerequisites

- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Git**
- *(Optional)* **Node.js 18+ & npm** (only required if you wish to recompile Tailwind CSS; precompiled CSS is already included in `static/css/styles.css`)

---

### Step 1: Clone the Repository and Navigate to the Directory

```bash
git clone https://github.com/notSoAman/pravaah.git
cd pravaah
```

---

### Step 2: Create and Activate a Virtual Environment

On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

### Step 3: Install Required Python Packages

Install all project dependencies from `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables

The project includes sensible defaults that fall back to a local **SQLite** database and local disk media storage when no `.env` file is present. If you wish to configure custom settings or test cloud storage, copy the example environment file:

```bash
cp .env.example .env
```

Default local behavior:
- `DEBUG=True`
- Database: local `db.sqlite3`
- Media files: served locally via `/media/` from the `media/` directory

---

### Step 5: Apply Database Migrations

Run Django's migration tool to initialize database tables:

```bash
python manage.py migrate
```

---

### Step 6: Load Initial Sample Data (Fixtures)

To immediately populate the application with sample team members, films, events, galleries, and journal essays for grading and evaluation, load the provided fixture:

```bash
python manage.py loaddata fixtures/initial_data.json
```

*(Note: The database now contains sample records ready to browse immediately).*

---

### Step 7: Create a Superuser Account (for Django Admin)

Create an administrative account to access the Django Admin dashboard:

```bash
python manage.py createsuperuser
```

Follow the interactive prompts to set your username, email, and password.

---

### Step 8: (Optional) Compile Static Styles

A complete, precompiled Tailwind stylesheet is already included at [`static/css/styles.css`](file:///home/aman/Projects/pravaah/static/css/styles.css). If you make edits to templates or [`static/src/input.css`](file:///home/aman/Projects/pravaah/static/src/input.css) and wish to rebuild the stylesheet:

```bash
npm install
npm run build
```

---

### Step 9: Launch the Development Server

Start Django's built-in development server:

```bash
python manage.py runserver
```

The application will be live at:
```
http://127.0.0.1:8000/
```

---

### Step 10: Accessing the Application and Admin

- **Main Website:** Open your browser and navigate to `http://127.0.0.1:8000/`
  - Home: `http://127.0.0.1:8000/`
  - Films Catalogue: `http://127.0.0.1:8000/films/`
  - Events & Galleries: `http://127.0.0.1:8000/events/`
  - Journal & Articles: `http://127.0.0.1:8000/journal/`
  - Team Roster: `http://127.0.0.1:8000/team/`
- **Django Admin Portal:** Navigate to `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

---

## Additional Information for Course Staff

### 1. Testing the Automated Notion Ingestion Pipeline

To test the Notion export ingestion pipeline:
1. Log in to the Django Admin at `/admin/`.
2. Under **Pravaah**, click **Journal imports** -> **Add Journal Import**.
3. Select an Author (create one in Members if none exists) and specify a Title.
4. Upload any standard Notion HTML export `.zip` file into the **Source zip** field.
5. Click **Save**.
6. The admin's `save_model` hook immediately executes `process_journal_import()`. It recursively unpacks the archive, extracts images, rewrites URLs, cleans the HTML via Bleach, generates a published `Journal` entry, cleans up the uploaded ZIP from disk, and removes the staging import record with a success notification.
7. Navigate to `/journal/` on the main site to view your published article.

Alternatively, pending imports can be batch-processed via the custom management command:
```bash
python manage.py process_journal_imports
```

### 2. Automated Image Processing & Cleanup Verification

When uploading images through the admin (e.g., adding an Event cover or Member portrait):
- Pillow automatically checks EXIF orientation, converts the color profile, resizes the file to standard dimensions, and compresses it.
- If you edit an existing record and upload a new image, or delete a record, the custom signals in [`pravaah/signals.py`](file:///home/aman/Projects/pravaah/pravaah/signals.py) verify that no other record references the previous file, and purge the old asset from storage automatically.

### 3. Production Deployment Architecture

While PRAVAAH runs smoothly locally on SQLite, it is configured for enterprise production deployment:
- **Web Server:** Gunicorn WSGI server configured in [`Procfile`](file:///home/aman/Projects/pravaah/Procfile).
- **Static Assets:** Handled by **WhiteNoise** with gzip/Brotli compression and persistent cache headers.
- **Database:** Auto-detects `DATABASE_URL` via `dj-database-url` (e.g., Neon PostgreSQL).
- **Media Storage:** Optional switch to **Supabase Cloud Storage** or S3 via the custom storage backend in [`pravaah/storages.py`](file:///home/aman/Projects/pravaah/pravaah/storages.py).
- **Health Check Endpoint:** Available at `/health/` for automated uptime monitors.

---

## Harvard CS50W Submission Checklist

1. **Course Authorization:** Ensure you have authorized CS50 via [submit.cs50.io](https://submit.cs50.io/invites/89679428401548238ceb022f141b9947).
2. **Git Repository Branch:** Push this codebase to branch `web50/projects/2020/x/capstone` on `https://github.com/me50/<YOUR_GITHUB_USERNAME>.git`.
3. **Screencast Video:** Record a demonstration video (under 5 minutes in length), uploaded to YouTube (Unlisted or Public). Ensure the video opens with a slide or overlay clearly displaying both your **edX username** and **GitHub username**, and shows the web application live in action.
4. **Submission Form:** Complete and submit the official form at [forms.cs50.io/5393b988-f6b5-42cf-9d60-4ebab244449c](https://forms.cs50.io/5393b988-f6b5-42cf-9d60-4ebab244449c).
