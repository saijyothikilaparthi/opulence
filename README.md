# Opulence

**Bespoke gift hampers, designed around them.**

Opulence provides a custom gift hamper consultation experience paired with a FastAPI + PostgreSQL backend and a unified Admin Console.

---

## 🚀 Quick Start (Running Locally)

### 1. Requirements
* Python 3.12+
* PostgreSQL 16+

### 2. Start the Backend Server
```bash
source .venv/bin/activate
uvicorn app.main:app --reload
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
  * **Home (`index.html`)**: Hero section, dynamic seasonal announcement banner, concept overview, work gallery, and 3 service categories.
  * **Individual (`individual.html`)**: Bespoke single hampers for personal occasions.
  * **Non-Corporate (`non-corporate.html`)**: Bespoke group hampers for weddings and family gatherings.
  * **Corporate (`corporate.html`)**: Branded bulk hampers for clients and employees.
* **Consultation Modal Form**: Shared pop-up modal across all pages with dynamic category selection (Individual, Corporate, Customized) that connects to `POST /api/enquiries`.

---

## 🛠️ Backend Architecture & Tech Stack

* **Framework:** FastAPI (ASGI Python)
* **Database:** PostgreSQL (`gift_management`) via `psycopg`
* **Data Validation:** Pydantic v2
* **Storage:** Local static uploads (`uploads/banners/`, `uploads/gallery/`)

### Database Tables:
* **`enquiries`**: Website consultation requests (Individual, Corporate, Customized) with instant WhatsApp Business notification triggers.
* **`orders`**: Offline/manual order tracking (WhatsApp, Instagram, Walk-in) with order status and payment status (`unpaid`, `partial`, `paid`).
* **`banners`**: Current active seasonal announcement banner (auto-deactivates previous banners on new upload).
* **`gallery_work`**: Showcase pictures of past gift hampers for the homepage work gallery.

---

## 🎛️ Admin Dashboard Console (`/demo/admin.html`)

A tabbed administration dashboard allowing the team to manage operations without code changes:

1. **📦 Orders Management:** Record offline orders, update order status, update payment status, and delete orders.
2. **🌐 Website Enquiries:** View consultation leads submitted from the website, manage lead status, and delete entries.
3. **🖼️ Active Banner:** Upload seasonal promotional banners with custom event titles and notes.
4. **🎨 Work Gallery Showcase:** Upload pictures of completed hampers to display live on the website gallery with delete controls.

---

## 📞 Contact

* Phone: +91 81064 89375
* Email: meenankrishnavarma13@gmail.com
