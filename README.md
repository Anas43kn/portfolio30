# Portfolio V2 Operator Manual

This project is a Docker-ready FastAPI portfolio platform built from the original static V1 portfolio.

V1 is still preserved at:

```text
reference/portfolio_v1.html
```

V2 keeps the same general visual direction: white luxury tech, monochrome palette, subtle code labels, numbered sections, thin borders, sticky top navigation, dark-mode toggle, reveal animation, and an impact-first layout.

The big difference: V2 does not hardcode the main portfolio content into one HTML file. The public site reads content from SQLite, and the admin panel writes content into SQLite.

## Quick Start

From this folder:

```powershell
python -m pip install -r requirements.txt
python -m app.seed
python -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Admin:

```text
http://127.0.0.1:8000/admin/login
email: admin@example.com
password: change-me
```

With Docker:

```powershell
docker compose up --build
```

The Docker command runs `python -m app.seed` first, then starts Uvicorn.

## Project Map

```text
portfolio-v2/
+-- app/
|   +-- main.py                 FastAPI app setup
|   +-- config.py               Environment variables and defaults
|   +-- database.py             SQLAlchemy engine/session/init
|   +-- auth.py                 Password hashing and admin guard
|   +-- seed.py                 Initial admin + V1-inspired content
|   +-- schemas.py              Small Pydantic schemas
|   +-- database.db             SQLite database
|   +-- models/
|   |   +-- __init__.py         All database table models
|   +-- routes/
|   |   +-- public.py           Public website routes
|   |   +-- admin.py            Admin dashboard + CRUD routes
|   |   +-- auth.py             Admin login/logout routes
|   +-- templates/
|   |   +-- base.html           Public layout shell
|   |   +-- index.html          Public homepage structure
|   |   +-- case_study_detail.html
|   |   +-- blog_detail.html
|   |   +-- admin/              Admin templates
|   +-- static/
|       +-- css/style.css       All public/admin styling
|       +-- js/main.js          Theme, reveal animation, nav, slug helper
|       +-- uploads/            Images
+-- reference/
|   +-- portfolio_v1.html       Static V1 source of visual truth
+-- Dockerfile
+-- docker-compose.yml
+-- requirements.txt
+-- README.md
```

## How The App Starts

`app/main.py` creates the FastAPI app.

It does four important things:

1. Loads settings from `app/config.py`.
2. Adds `SessionMiddleware` so admin login can use secure browser cookies.
3. Mounts `/static` so CSS, JS, and images can load.
4. Includes the route files:

```python
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(public.router)
```

On startup, it calls:

```python
init_db()
```

That lives in `app/database.py` and creates missing database tables from the SQLAlchemy models.

Important quirk: `init_db()` creates tables, but it does not seed content. For content/admin user, run:

```powershell
python -m app.seed
```

Docker does this automatically.

## Environment Variables

Configured in `app/config.py`.

Defaults:

```env
APP_NAME=Portfolio V2
DATABASE_URL=sqlite:///./app/database.db
SECRET_KEY=change-me-in-production
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me
MAX_UPLOAD_MB=5
TRUSTED_PROXY_IPS=*
```

What they do:

- `DATABASE_URL`: tells SQLAlchemy where the database is.
- `SECRET_KEY`: signs admin session cookies. Change before deployment.
- `ADMIN_EMAIL`: first admin account email created by the seed script.
- `ADMIN_PASSWORD`: first admin account password created by the seed script.
- `MAX_UPLOAD_MB`: maximum allowed image upload size per file.
- `TRUSTED_PROXY_IPS`: proxy IPs trusted for `X-Forwarded-Proto`; `*` is practical on managed platforms such as Northflank.

For production, use a real secret:

```env
SECRET_KEY=a-long-random-string
ADMIN_EMAIL=your@email.com
ADMIN_PASSWORD=a-strong-password
```

## Database Layer

The database setup is in:

```text
app/database.py
```

Main parts:

- `Base`: SQLAlchemy declarative base.
- `engine`: database connection engine.
- `SessionLocal`: database session factory.
- `get_db()`: FastAPI dependency that opens/closes a DB session per request.
- `init_db()`: creates tables.

Current database:

```text
app/database.db
```

SQLite is intentionally used for the MVP. PostgreSQL later should mostly mean changing:

```env
DATABASE_URL=postgresql+psycopg://user:password@postgres:5432/portfolio
```

Then add a PostgreSQL driver and Alembic migrations.

## Database Tables

All models live in:

```text
app/models/__init__.py
```

### `users`

Admin/client identity table.

Fields:

- `email`
- `password_hash`
- `role`
- `created_at`
- `updated_at`

Current admin role check expects:

```text
role = admin
```

Future client portal can use:

```text
role = client
```

### `site_settings`

Key/value settings used mainly by the homepage and header.

Examples:

- `name`
- `role`
- `hero_title`
- `hero_subtitle`
- `hero_microline`
- `contact_email`
- `linkedin_url`
- `location`
- `cv_url`
- `profile_image`
- `profile_badges`

Edit these in:

```text
/admin/settings
```

### `impact_metrics`

Homepage impact numbers.

Generated into the `#impact` section.

Fields:

- `value`: big number, like `40%`.
- `label`: short explanation.
- `description`: optional smaller text.
- `display_order`: order on page.
- `is_active`: whether it shows publicly.

### `case_studies`

Main Work section and detail pages.

Generated into:

- Homepage `#work`
- `/case-studies`
- `/case-studies/{slug}`

Important fields:

- `title`: card/detail title.
- `slug`: URL piece.
- `subtitle`: detail page lede.
- `tag`: code-style pill label.
- `short_description`: card text.
- `context`, `constraint`: detail blocks.
- `architecture_summary`: newline-separated bullet list.
- `outcome_summary`: newline-separated bullet list.
- `code_line`: code-style block at bottom.
- `stack`: card footer left text.
- `impact`: card footer right text.
- `display_order`: ordering.
- `is_featured`: appears on homepage if true.
- `is_published`: public visibility.

Quirk: homepage only shows case studies where both are true:

```text
is_featured = true
is_published = true
```

### `case_study_sections`

Reserved for richer case study detail sections. The current public detail template mainly uses fields directly from `case_studies`.

### `projects`

Admin-managed projects table.

Generated into:

- Homepage `#projects`
- `/projects`
- `/projects/{slug}`

Project cards are image-forward. If `cover_image` is set, the image is rendered as a faded grayscale background on the card. Clicking the card opens the project detail page with the larger image and project details.

Important fields:

- `title`
- `slug`
- `description`
- `stack`
- `impact`
- `project_type`
- `cover_image`
- `display_order`
- `is_published`

### `services`

Generated into homepage `#services`.

Fields:

- `title`
- `description`
- `icon_label`: code-style tag, like `production.tooling`.
- `cover_image`: optional uploaded/linked image for the service card.
- `display_order`
- `is_active`

### `blog_posts`

Generated into:

- Homepage Engineering Notes preview
- `/blog`
- `/blog/{slug}`

Fields:

- `title`
- `slug`
- `excerpt`
- `content`
- `category`
- `tags`
- `cover_image`
- `content_format`
- `is_published`
- `published_at`

Quirk: blog content is escaped by default when `content_format` is `plain`. This is safer. If a trusted admin intentionally wants an HTML writing zone, set:

```text
content_format = html
```

Then `blog_detail.html` renders `content` as trusted HTML.

### `experience_entries`

Generated into homepage `#experience`.

Fields:

- `period`
- `title`
- `meta`
- `description`
- `display_order`
- `is_active`

### `system_layers`

Generated into homepage `#layers`.

Fields:

- `layer_key`: visible code-style label, like `automation.layer`.
- `title`: stored but not currently displayed on homepage.
- `description`
- `items_json`: list of bullet items.
- `display_order`
- `is_active`

Quirk: `items_json` can be valid JSON, for example:

```json
["PLC logic", "Industrial networking", "Safety debugging"]
```

The admin route also accepts line-based input if JSON parsing fails, then converts each line into JSON.

### `approach_items`

Generated into homepage `#approach`.

Fields:

- `text`
- `display_order`
- `is_active`

### `newsletter_subscribers`

Generated by the TLDR email signup form.

Fields:

- `email`
- `source`
- `created_at`
- `is_active`

Current behavior:

- Validates basic email format.
- Lowercases and trims email.
- Prevents duplicate records.
- Does not send emails yet.

### `clients` and `client_projects`

Reserved future client portal tables.

Current route:

```text
/client
```

It only shows a reserved placeholder page.

## What The Seed Script Generates

Seed file:

```text
app/seed.py
```

Run it:

```powershell
python -m app.seed
```

It creates:

1. Database tables, through `init_db()`.
2. First admin user from `ADMIN_EMAIL` and `ADMIN_PASSWORD`.
3. Homepage settings.
4. Impact metrics.
5. Services.
6. Three flagship case studies.
7. Experience entries.
8. System layers.
9. Approach items.
10. One starter blog post.

Important quirk: most seed inserts use `add_if_empty()`.

That means:

- If a table already has records, seed will not duplicate that table.
- If you edit content in admin and rerun seed, your existing table content should not be overwritten.
- `site_settings` only inserts missing keys; existing setting values are not overwritten.

Admin user quirk:

- If the admin email already exists, seed does not update the password.
- To change an existing admin password today, either add a password reset feature later or manually update the DB.

## Request Flow

### Homepage `/`

Route:

```text
app/routes/public.py -> home()
```

It queries:

- `SiteSetting`
- `ImpactMetric`
- `CaseStudy`
- `Service`
- `ExperienceEntry`
- `SystemLayer`
- `ApproachItem`
- `BlogPost`

Then renders:

```text
app/templates/index.html
```

The template decides layout. The database decides content.

### Case Study Detail

URL:

```text
/case-studies/{slug}
```

Route:

```text
app/routes/public.py -> case_study_detail()
```

Template:

```text
app/templates/case_study_detail.html
```

Only published case studies render publicly.

### Blog

URLs:

```text
/blog
/blog/{slug}
```

Routes:

```text
blog_index()
blog_detail()
```

Templates:

```text
app/templates/blog.html
app/templates/blog_detail.html
```

Only published blog posts render publicly.

### Newsletter Signup

Form in:

```text
app/templates/index.html
```

Posts to:

```text
/newsletter
```

Handled by:

```text
app/routes/public.py -> newsletter_signup()
```

Stores email in:

```text
newsletter_subscribers
```

Redirects back to:

```text
/?signup=ok#contact
```

or:

```text
/?signup=invalid#contact
```

## Admin Flow

Login routes:

```text
app/routes/auth.py
```

Admin content routes:

```text
app/routes/admin.py
```

Admin templates:

```text
app/templates/admin/
```

Admin protection:

```text
app/auth.py -> require_admin()
```

The admin login stores this in the signed browser session:

```python
request.session["user_id"] = user.id
request.session["role"] = user.role
```

Every admin route depends on `require_admin()`.

Password hashing:

```text
pbkdf2_sha256 via passlib
```

This was chosen because bcrypt had compatibility trouble in the local Python 3.13 environment.

## Admin CRUD: How It Is Generated

Most admin list/form pages are generated from `ENTITY_CONFIG` in:

```text
app/routes/admin.py
```

Example:

```python
"services": {
    "model": Service,
    "title": "Services",
    "fields": ["title", "description", "icon_label", "display_order", "is_active"],
    "long": {"description"},
    "bools": {"is_active"},
    "status": "is_active",
}
```

This config tells the admin system:

- Which SQLAlchemy model to edit.
- What title to show in admin.
- Which fields to put in the form.
- Which fields should be textarea fields.
- Which fields should be checkboxes.
- Which boolean field controls publish/active toggling.

Generated templates:

- `admin/list.html`: generic list table.
- `admin/form.html`: generic create/edit form.

So when you add a new model later, you can often add it to `ENTITY_CONFIG` and get a basic admin screen quickly.

Current admin routes:

```text
/admin
/admin/settings
/admin/case-studies
/admin/case-studies/new
/admin/case-studies/{id}/edit
/admin/projects
/admin/blogs
/admin/services
/admin/impact
/admin/experience
/admin/system-layers
/admin/approach
```

Quirk: the user-facing route says `/admin/blogs`, not `/admin/blog-posts`, because the entity key is `blogs`.

## Templates: What Controls Structure

Templates are responsible for layout structure, not main content.

### Public Base Layout

File:

```text
app/templates/base.html
```

Controls:

- HTML `<head>`
- CSS link
- sticky topbar
- brand/name
- nav links
- dark mode button
- global JS include

Change nav labels here:

```html
<a class="navlink" href="/#services">Services</a>
```

Change site `<title>` default here:

```html
{% block title %}Digital Industrial Systems Architect{% endblock %}
```

Brand text comes from database settings:

```html
{{ settings.name }}
{{ settings.role }}
```

If missing, it falls back to:

```text
YOUR NAME
digital.industrial.systems.architect
```

### Homepage Structure

File:

```text
app/templates/index.html
```

Controls section order:

1. Hero
2. Impact
3. Services
4. Work
5. Experience
6. System Layers
7. Approach
8. Engineering Notes
9. Contact / TLDR

Example:

```html
<section id="services" aria-label="Services">
```

Change section titles/numbers here:

```html
<div class="kicker"><span>02</span> / SERVICES</div>
```

Change the small right-side section note here:

```html
<div class="subnote">problems I help solve / systems I stabilize</div>
```

Main text inside cards usually comes from database rows.

### Case Study Detail

File:

```text
app/templates/case_study_detail.html
```

Controls:

- case study detail layout
- context/constraint/architecture/outcome blocks
- code box

The actual text comes from `case_studies`.

### Blog Detail

File:

```text
app/templates/blog_detail.html
```

Controls the blog detail page layout.

The blog content is escaped by default. That is safer for admin-entered content.

### Admin Templates

Files:

```text
app/templates/admin/base.html
app/templates/admin/login.html
app/templates/admin/dashboard.html
app/templates/admin/list.html
app/templates/admin/form.html
app/templates/admin/settings.html
```

Use these if you want to change admin layout, not public styling.

## Styling: Where It Lives

All styling lives in:

```text
app/static/css/style.css
```

There is not a separate CSS file for admin. Public and admin share this file.

The visual design is mostly controlled by CSS variables at the top:

```css
:root {
  --bg: #f7f7f7;
  --panel: #ffffff;
  --text: #111111;
  --muted: rgba(17, 17, 17, 0.66);
  --rule: rgba(17, 17, 17, 0.12);
  --shadow: 0 8px 24px rgba(17, 17, 17, 0.06);
  --radius: 16px;
  --max: 1100px;
}
```

Dark mode variables are here:

```css
[data-theme="dark"] {
  --bg: #0f0f10;
  --panel: #141416;
}
```

### Change Colors

Edit:

```css
--bg
--panel
--text
--muted
--rule
--grid
```

Examples:

- Page background: `--bg`
- Card background: `--panel`
- Main text: `--text`
- Soft paragraph text: `--muted`
- Borders: `--rule`
- Hero grid lines: `--grid`

### Change Page Width

Edit:

```css
--max: 1100px;
```

This controls the maximum width of the topbar and main wrapper.

### Change Main Page Padding

Edit:

```css
.wrap {
  padding: 28px 22px 80px;
}
```

Meaning:

- `28px`: top padding
- `22px`: left/right padding
- `80px`: bottom padding

### Change Section Spacing

Edit:

```css
section {
  padding: 70px 0 10px;
}
```

Meaning:

- `70px`: top space before each section content
- `0`: left/right space, because `.wrap` handles page side padding
- `10px`: bottom space

If sections feel too tall, reduce `70px`.

### Change Hero Spacing

Edit:

```css
.hero {
  padding-top: 44px;
}

.hero-inner {
  padding: 56px 0 28px;
  gap: 28px;
}
```

Use these for hero breathing room.

### Change Hero Title Size

Edit:

```css
.headline {
  font-size: clamp(34px, 5.2vw, 62px);
}
```

Meaning:

- Minimum: `34px`
- Fluid middle size: `5.2vw`
- Maximum: `62px`

To make it smaller:

```css
font-size: clamp(32px, 4.6vw, 54px);
```

### Change Card Padding

Edit:

```css
.metric, .service, .card, .layer, .approach, .box, .mblock {
  padding: 16px;
}
```

This affects many card-like blocks.

For only work cards:

```css
.card {
  padding: 20px;
}
```

Add that after the shared rule.

### Change Grid Columns

Current desktop grids:

```css
.metrics { grid-template-columns: repeat(4, 1fr); }
.services, .layers { grid-template-columns: repeat(3, 1fr); }
.cards { grid-template-columns: repeat(3, 1fr); }
```

Examples:

Make services two columns:

```css
.services { grid-template-columns: repeat(2, 1fr); }
```

Make cards wider:

```css
.cards { grid-template-columns: repeat(2, 1fr); }
```

Mobile behavior is controlled here:

```css
@media (max-width: 900px) {
  .hero-inner, .metrics, .cards, .services, .layers, .contact, .modal-grid {
    grid-template-columns: 1fr;
  }
}
```

### Change Topbar

Topbar styles:

```css
.topbar
.topbar-inner
.brand
.navlink
.actions
```

Topbar padding:

```css
.topbar-inner {
  padding: 14px 22px;
}
```

Nav item padding:

```css
.navlink {
  padding: 8px;
}
```

### Change Buttons

Button styles:

```css
.btn, .toggle
.btn.primary
```

Button padding:

```css
padding: 9px 12px;
```

Button pill shape:

```css
border-radius: 999px;
```

### Change Portrait

The portrait is now dynamic.

Admin:

```text
/admin/settings -> profile_image
```

You can upload a new image with the file picker, paste a local static path, or paste an external URL.

Uploaded image files are stored in:

```text
app/static/uploads/
```

Template usage:

```text
app/templates/index.html
```

The template reads:

```html
{{ settings.profile_image }}
```

If `profile_image` is empty, it falls back to:

```text
uploads/unnamed.jpg
```

CSS:

```css
.portrait {
  clip-path: polygon(...);
  max-width: 330px;
}
```

To use a normal rectangle, remove or comment:

```css
clip-path: polygon(...);
```

### Change Reveal Animation

CSS:

```css
.reveal
.reveal.is-visible
```

JS:

```text
app/static/js/main.js
```

If you do not want reveal animation, remove `reveal` classes from templates or make this:

```css
.reveal {
  opacity: 1;
  transform: none;
}
```

## JavaScript: What It Does

File:

```text
app/static/js/main.js
```

It handles:

1. Dark mode toggle.
2. Saving theme to `localStorage`.
3. Reveal-on-scroll animation.
4. Active nav link detection.
5. Admin slug auto-generation from title.

Slug quirk:

- If a slug field already has a value, JS does not overwrite it.
- If you type into the slug manually, JS marks it as touched.
- Server-side fallback also creates a slug if blank.

## How To Change Content

Use admin first.

### Change Hero Title

Go to:

```text
/admin/settings
```

Edit:

```text
hero_title
```

This appears in:

```text
app/templates/index.html
```

as:

```html
{{ settings.hero_title }}
```

### Change Hero Subtitle

Admin:

```text
/admin/settings -> hero_subtitle
```

### Change Microline

Admin:

```text
/admin/settings -> hero_microline
```

Example:

```text
// PLC -> Interface -> Data -> Manufacturing
```

### Change Name In Top Left

Admin:

```text
/admin/settings -> name
```

### Change Role In Top Left

Admin:

```text
/admin/settings -> role
```

### Change Homepage/Profile Picture

Admin:

```text
/admin/settings -> profile_image
```

This uses the same upload system as project, service, blog, and case study images.

### Change Profile Badges Under The Picture

Admin:

```text
/admin/settings -> profile_badges
```

Use one badge per line:

```text
Hands-on Architect
Automation + Data
Platform Scale
```

### Change Contact Email

Admin:

```text
/admin/settings -> contact_email
```

### Change Impact Numbers

Admin:

```text
/admin/impact
```

### Change Services

Admin:

```text
/admin/services
```

### Change Work Cards

Admin:

```text
/admin/case-studies
```

For homepage visibility, make sure:

```text
is_featured = checked
is_published = checked
```

### Change Experience

Admin:

```text
/admin/experience
```

### Change System Layers

Admin:

```text
/admin/system-layers
```

For bullet items, use JSON:

```json
["Item one", "Item two", "Item three"]
```

or type one item per line. The backend will convert lines to JSON.

### Change Approach Bullets

Admin:

```text
/admin/approach
```

### Add A Blog Post

Admin:

```text
/admin/blogs/new
```

Check:

```text
is_published
```

Published posts appear on:

```text
/blog
```

The latest three appear on the homepage.

### Add Images To Services, Projects, Case Studies, Or Blog Posts

Admin forms now show image controls for `cover_image` fields.

You can either:

1. Upload an image with the file picker.
2. Paste an existing path like `uploads/example.jpg`.
3. Paste an external image URL.

Uploaded files are stored in:

```text
app/static/uploads/
```

The database stores the relative path:

```text
uploads/generated-file-name.webp
```

Allowed upload extensions:

```text
.jpg
.jpeg
.png
.webp
.gif
```

Where images show:

- Services: inline image at the top of the service card.
- Case studies: faded homepage card background and large detail image.
- Projects: faded grayscale card background and large detail image after click.
- Blogs: faded preview card background and large detail image on the post.

### Use The Blog HTML Zone

Admin:

```text
/admin/blogs/new
```

For normal writing:

```text
content_format = plain
```

For controlled HTML:

```text
content_format = html
```

Then you can write HTML in the `content` textarea, for example:

```html
<p>This is a technical note with an inline image.</p>
<img src="/static/uploads/example.webp" alt="PLC interface screenshot">
<pre><code>// commissioning.flow -> browser.interface</code></pre>
```

Use HTML mode only for trusted admin-written content.

## How To Change Layout Titles

These are not in the database yet. They live in the templates.

Homepage section labels:

```text
app/templates/index.html
```

Examples:

```html
<div class="kicker"><span>01</span> / IMPACT</div>
<div class="kicker"><span>02</span> / SERVICES</div>
<div class="kicker"><span>03</span> / WORK</div>
```

Right-side notes:

```html
<div class="subnote">measured outcomes / platform constraints</div>
```

Top navigation labels:

```text
app/templates/base.html
```

Admin sidebar labels:

```text
app/templates/admin/base.html
```

Admin page titles:

```text
app/routes/admin.py -> ENTITY_CONFIG
```

Example:

```python
"services": {
    "title": "Services",
}
```

## What Is Hardcoded vs Dynamic

### Dynamic From Database

- Header name
- Header role
- Profile/hero image
- Hero title
- Hero subtitle
- Hero microline
- Contact email
- LinkedIn URL
- Location
- CV URL
- Impact metrics
- Services
- Case study cards
- Case study detail content
- Experience entries
- System layers
- Approach bullets
- Blog preview
- Blog pages
- Newsletter subscriber emails

### Hardcoded In Templates

- Section order
- Section numbers
- Section labels like `IMPACT`, `SERVICES`, `WORK`
- Top nav link labels
- Button labels like `View Work`, `Contact`, `Register`
- Footer text
- Admin page layout

### Hardcoded In CSS

- Colors
- Padding
- Font sizes
- Grid column counts
- Borders
- Card radius
- Shadows
- Reveal animation timing
- Responsive breakpoint

### Generated By Seed

The initial content in `app/database.db` is generated by:

```text
app/seed.py
```

After that, normal edits happen through the admin panel.

## TLDR Newsletter: Current State

The TLDR form only registers email addresses.

It does not send newsletters yet.

Stored table:

```text
newsletter_subscribers
```

To view subscribers:

```powershell
python -c "import sqlite3; con=sqlite3.connect('app/database.db'); print(con.execute('select email, source, created_at, is_active from newsletter_subscribers').fetchall())"
```

Future sending should be added as a separate admin feature, not inside the signup form.

Recommended future tables:

```text
newsletter_campaigns
newsletter_sends
```

Recommended future admin routes:

```text
/admin/newsletter
/admin/newsletter/new
/admin/newsletter/{id}/send
```

Recommended environment variables:

```env
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
MAIL_FROM=
```

## Common Changes Cheat Sheet

Change homepage headline:

```text
/admin/settings -> hero_title
```

Change headline size:

```text
app/static/css/style.css -> .headline
```

Change section spacing:

```text
app/static/css/style.css -> section { padding: ... }
```

Change whole page width:

```text
app/static/css/style.css -> --max
```

Change side padding:

```text
app/static/css/style.css -> .wrap { padding: ... }
```

Change nav labels:

```text
app/templates/base.html
```

Change section labels/numbers:

```text
app/templates/index.html
```

Change card spacing:

```text
app/static/css/style.css -> .metric, .service, .card...
```

Change card columns:

```text
app/static/css/style.css -> .cards / .services / .metrics
```

Change public content:

```text
/admin
```

Change seed defaults:

```text
app/seed.py
```

Change database fields:

```text
app/models/__init__.py
```

Change public queries:

```text
app/routes/public.py
```

Change admin forms:

```text
app/routes/admin.py -> ENTITY_CONFIG
app/templates/admin/form.html
```

## Quirks And Gotchas

### Seed Does Not Overwrite Existing Content

Most seed data only inserts if a table is empty. This protects admin edits.

If you want a totally fresh seed:

1. Stop the server.
2. Delete `app/database.db`.
3. Run `python -m app.seed`.

### Main Content Should Not Be Edited In HTML

If it is portfolio content, edit it through admin.

Use templates only for layout and section structure.

### Published vs Active

Different tables use slightly different visibility names:

- Case studies/blog/projects: `is_published`
- Services/impact/experience/layers/approach: `is_active`

The admin toggle uses whichever field is configured as `status` in `ENTITY_CONFIG`.

### Featured Case Studies

A case study can be published but not featured.

Published means it can appear at:

```text
/case-studies/{slug}
```

Featured means it appears on the homepage Work section.

### Blog HTML Is Escaped

Blog content is displayed safely as text.

If you later want Markdown, add a Markdown renderer instead of marking raw HTML safe.

### No Real Analytics Yet

There are no analytics tables or event tracking routes right now.

Add those later without disturbing public/admin content.

### No Image Upload Processing Yet

The upload workflow exists, but it is still intentionally simple.

It currently:

- validates the file extension
- accepts `.jpg`, `.jpeg`, `.png`, `.webp`, and `.gif`
- streams the upload in chunks
- enforces `MAX_UPLOAD_MB`
- writes the file to `app/static/uploads/`
- stores the path in the database

It does not yet:

- resize images
- compress images
- strip EXIF metadata
- virus-scan files
- move files to object storage

For production, add image processing or use an external media service.

### Uploaded Images Are Stored, Not Processed

The upload system validates extensions, enforces `MAX_UPLOAD_MB`, streams file chunks, and writes images to `app/static/uploads/`.

It does not resize, crop, compress, strip metadata, or virus-scan yet. For production, add an image-processing step and stronger validation.

Important storage note:

```text
app/static/uploads/
```

is local disk storage. In Docker or production, mount this folder as a persistent volume or move uploaded media to object storage.

For a small single-owner portfolio, local disk is fine.

For multiple users, client uploads, frequent project screenshots, or many blog images, move uploads to S3, Cloudflare R2, Azure Blob Storage, or similar.

Recommended future image path:

```text
Browser upload
      v
FastAPI validation
      v
Object storage
      v
Database stores object key or URL
      v
CDN serves image
```

This keeps app RAM, container disk, backups, and deploy size under control.

### RAM And Storage For Multiple Users

The app is lightweight, but multi-user deployment changes the pressure points.

Sessions:

- Admin login uses signed browser cookies.
- There is no large server-side session store right now.
- Memory use per logged-in user is low.

Database:

- SQLite is fine for an MVP and one/few admins.
- SQLite becomes a bottleneck when many users write at the same time.
- Move to PostgreSQL before a real client portal or multi-admin deployment.

Uploads:

- Uploads stream in chunks instead of loading the whole file into memory.
- `MAX_UPLOAD_MB` defaults to `5`.
- Keep uploads small, preferably 2-5 MB.
- Convert screenshots/photos to `.webp` before upload when possible.
- Store media outside the container for production.

Static files:

- FastAPI static serving is acceptable for development and small deployments.
- For production, put a reverse proxy/CDN in front or move uploads to object storage.

Before many users can sign in safely, add:

- user management in admin
- invite/password reset flow
- role permissions beyond only `admin`
- audit logs for content changes
- login rate limiting
- upload rate limiting
- PostgreSQL
- persistent object storage

### Admin Is Practical, Not Fancy

The admin panel is intentionally plain: tables, edit buttons, forms, checkboxes, number fields.

That is by design. It should be fast to edit content, not a second portfolio.

## Development Workflow

After changing Python:

```powershell
python -m compileall app
```

After changing templates/CSS:

Refresh the browser.

If using Uvicorn reload:

```powershell
python -m uvicorn app.main:app --reload
```

If database model fields change:

For now, this MVP has no migrations. During early development, easiest reset:

```powershell
Remove-Item app/database.db
python -m app.seed
```

Later, add Alembic before real production data matters.

## Deployment Notes

Before deploying:

1. Change `SECRET_KEY`.
2. Change `ADMIN_EMAIL`.
3. Change `ADMIN_PASSWORD`.
4. Run behind HTTPS.
5. Use a persistent database volume.
6. Use a persistent upload volume or object storage.
7. Add Alembic migrations.
8. Add backup strategy for SQLite or move to PostgreSQL.
9. Add proper email sending for TLDR newsletters.
10. Add image resizing/compression for uploaded media.
11. Add rate limiting before multiple users sign in.

### HTTPS Proxy / Northflank Mixed Content

Managed hosts such as Northflank usually terminate HTTPS before traffic reaches Uvicorn. Without proxy header support, FastAPI may think the request scheme is `http` and generate insecure asset URLs.

This project handles that in two ways:

- Uvicorn starts with `--proxy-headers --forwarded-allow-ips '*'`.
- Static asset links in templates use root-relative paths such as `/static/css/style.css`.

If you still see mixed-content warnings, check that the deployed command includes:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips '*'
```

And keep this environment variable:

```env
TRUSTED_PROXY_IPS=*
```

## Mental Model

Think of the system like this:

```text
Database content
      v
public.py queries
      v
Jinja templates structure the page
      v
style.css gives the V1 luxury-tech look
      v
main.js adds polish: theme, reveal, active nav
```

Admin is the reverse:

```text
Admin form
      v
admin.py generic CRUD
      v
SQLAlchemy model
      v
SQLite table
      v
Public site updates automatically
```

That is the whole machine room.
#   p o r t f o l i o 3 0  
 
