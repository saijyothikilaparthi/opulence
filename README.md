# Opulence

**Bespoke gift hampers, designed around them.**

Opulence provides a custom gift hamper consultation experience paired with a FastAPI + PostgreSQL backend and a unified Admin Console.

---

## 🚀 Quick Start (Running Locally)

### 1. Requirements
* Python 3.12+
* PostgreSQL 16+

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Create the database (once)
Run as the `postgres` superuser (e.g. `psql -U postgres`):
```sql
CREATE ROLE gift_app LOGIN PASSWORD 'change_this_password';
CREATE DATABASE gift_management OWNER gift_app;
```
Tables are created automatically when the server starts.

Connection settings can be overridden with environment variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (always set a real password outside local development).

### 4. Start the Backend Server
Run from the project root:
```bash
python -m uvicorn app.main:app --reload
```

---

## 🌐 Application Portals

* **Website Frontend:** `http://127.0.0.1:8000/`
* **Admin Dashboard Console:** `http://127.0.0.1:8000/demo/admin.html`
* **Interactive API Documentation (Swagger):** `http://127.0.0.1:8000/docs`

---

## 🎨 Frontend Design & Features

* **Tech Stack:** Plain HTML5, CSS3 (CSS Custom Properties), Vanilla JavaScript (no external frameworks or build step).
* **Pages:**
  * **Home (`index.html`)**: Hero carousel of past commissions, festive collections, concept overview, work gallery (static items plus photos uploaded from the admin console), and 3 service categories.
  * **Individual (`individual.html`)**: Bespoke single hampers for personal occasions.
  * **Celebrations & Bulk (`celebrations.html`)**: Group hampers for weddings, family gatherings and festivals. `non-corporate.html` redirects here.
  * **Corporate (`corporate.html`)**: Branded bulk hampers for clients and employees.
* **Photography:** Real commission photos live in `frontend/assets/work/`.
* **Consultation Modal Form**: Shared pop-up modal across all pages with dynamic category selection (Individual, Corporate, Customized) that connects to `POST /api/enquiries`.

---

## 🛠️ Backend Architecture & Tech Stack

* **Framework:** FastAPI (ASGI Python)
* **Database:** PostgreSQL (`gift_management`) via `psycopg`
* **Data Validation:** Pydantic v2
* **Storage:** Local static uploads (`uploads/gallery/` for work photos, `uploads/references/` for customer reference files)

### Database Tables:
* **`enquiries`**: Website consultation requests (Individual, Corporate, Customized). A WhatsApp notification message is formatted and logged for each one (sending via the WhatsApp Business API is not wired up yet).
* **`orders`**: Offline/manual order tracking (WhatsApp, Instagram, Walk-in) with order status (`pending`, `in-progress`, `completed`, `cancelled`) and payment status (`unpaid`, `partial`, `paid`).
* **`gallery_work`**: Showcase pictures of past gift hampers for the homepage work gallery, categorised as Corporate Gifting, Celebrations & Bulk, or Individual Hampers.
* **`categories`, `products`, `hamper_sizes`, `hampers`, `hamper_items`**: Catalog API (not yet used by the website or admin console).

> ⚠️ The admin endpoints (`/api/*/admin`, `/api/orders`) have no authentication yet. Do not expose this server publicly until they are protected.

---

## 🎛️ Admin Dashboard Console (`/demo/admin.html`)

A tabbed administration dashboard allowing the team to manage operations without code changes:

1. **📦 Orders Management:** Record offline orders, update order status, update payment status, and delete orders.
2. **🌐 Website Enquiries:** View consultation leads submitted from the website, manage lead status, and delete entries.
3. **🎨 Work Gallery Showcase:** Upload pictures of completed hampers (JPG, PNG, WEBP or GIF) to display live on the website gallery with delete controls.

---

## 📞 Contact

* Phone: +91 81064 89375
* Email: meenankrishnavarma13@gmail.com
