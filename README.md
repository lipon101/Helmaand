# Helmaand 🛍️

**CTF e-Commerce Platform** — a Django 6.0 clothing/apparel storefront with **intentionally vulnerable** endpoints for security training and capture-the-flag exercises.

> ⚠️ **WARNING**: This application contains real, exploitable vulnerabilities (XSS, SQLi, CSRF). It is designed for **educational and authorized security testing only**. Never deploy on a public network without isolation.

Built with:
- 🐍 Python 3.12+
- 🌐 Django 6.0.7
- 🗄️ SQLite (default database)
- 🖼️ Pillow (image handling)
- 🎨 Django Templates + Bootstrap 5

---

## 📦 Project Structure

```
Helmaand/
├── manage.py              # Django CLI entry point
├── requirements.txt       # Python dependencies (Django, Pillow, gunicorn)
├── perfect/               # Django project package (settings, urls, wsgi)
├── accounts/              # User auth: login, register, profile, change-email (CSRF)
├── shop/                  # Product catalog: home, shop, search (SQLi), detail (XSS)
├── cart/                  # Shopping cart (model scaffolded)
├── orders/                # Orders (model scaffolded)
├── dashboard/             # Admin dashboard views
├── security/              # Security lab hub — challenge listing
├── templates/             # HTML templates (base, accounts, shop, security, dashboard)
└── static/                # Static assets (CSS)
```

---

## 🔓 CTF Challenges

**15 challenges** across three vulnerability categories, at easy-to-intermediate difficulty. Visit the **Security Lab** page (`/lab/`) for hints, objectives, and flag hints.

All flags use the format **`HLMD{...}`**.

### XSS Challenges (5)

| # | Challenge | Difficulty | Endpoint | Flag Cookie |
|---|-----------|------------|----------|-------------|
| 1 | Stored XSS | Easy | `/product/<slug>/` | `ctf_xss_stored` |
| 2 | Reflected XSS | Easy | `/track/?id=` | `ctf_xss_reflected` |
| 3 | DOM-based XSS | Intermediate | `/gallery/#` (hash) | `ctf_xss_dom` |
| 4 | Attribute XSS | Intermediate | `/newsletter/?name=` | `ctf_xss_attribute` |
| 5 | Self-XSS | Easy | `/accounts/profile/` | `ctf_xss_self` |

**How to test:**

1. **Stored XSS** — Post a review on any product page with `<img src=x onerror="alert(document.cookie)">`. The comment renders with `\|safe`. Reload to execute. Read the `ctf_xss_stored` cookie.
2. **Reflected XSS** — Visit `/track/?id=<script>alert(document.cookie)</script>`. The `?id=` value renders with `\|safe`. Read the `ctf_xss_reflected` cookie.
3. **DOM-based XSS** — Visit `/gallery/#<img src=x onerror="alert(document.cookie)">`. Client-side JS writes `location.hash` into `innerHTML`. Read the `ctf_xss_dom` cookie.
4. **Attribute XSS** — Visit `/newsletter/?name=" onmouseover="alert(document.cookie)`. Breaks out of the HTML attribute. Trigger the event handler. Read the `ctf_xss_attribute` cookie.
5. **Self-XSS** — Register with a username containing `<img src=x onerror="alert(document.cookie)">`, then visit your profile. The username renders with `\|safe`. Read the `ctf_xss_self` cookie.

---

### SQL Injection Challenges (5)

| # | Challenge | Difficulty | Endpoint | Flag Location |
|---|-----------|------------|----------|---------------|
| 6 | UNION-based SQLi | Intermediate | `/search/?q=` | Hidden product (`is_active=0`) |
| 7 | Error-based SQLi | Intermediate | `/filter/?sort=` | `security_ctfflag` table |
| 8 | Blind Boolean SQLi | Intermediate | `/stock/?id=` | `security_ctfflag` table |
| 9 | Time-based Blind SQLi | Intermediate | `/promo/?code=` | `security_ctfflag` table |
| 10 | Auth Bypass SQLi | Easy | `/staff-login/` | Success message |

**How to test:**

6. **UNION SQLi** — The search runs `SELECT * FROM shop_product WHERE is_active=1 AND name LIKE '%{q}%'`. Craft a UNION payload to exfiltrate the hidden product:
   ```
   x' UNION SELECT id,name,slug,brand,description,price,discount_price,stock,size,color,is_active,created_at,updated_at,category_id FROM shop_product WHERE is_active=0 --
   ```
7. **Error SQLi** — The filter passes `?sort=` directly into `ORDER BY`. Try `?sort=extractvalue` or any invalid column — the raw DB error is reflected back, leaking schema info for further extraction.
8. **Blind SQLi** — The stock checker runs `SELECT stock FROM shop_product WHERE id = {id} AND is_active = 1`. Only "In Stock"/"Out of Stock" is returned. Use boolean conditions:
   ```
   ?id=1 AND (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_blind') --
   ```
9. **Time-based SQLi** — The promo validator runs `SELECT 1 FROM shop_promo WHERE code='{code}'`. Only "Valid"/"Invalid" is returned. Use a time-delay payload (SQLite: `randomblob`; MySQL: `SLEEP`) and measure response time.
10. **Auth Bypass SQLi** — The staff login builds `SELECT * FROM auth_user WHERE username='{username}' AND password='{password}' AND is_staff=1`. Bypass with:
    ```
    username: admin' OR '1'='1      password: anything
    ```

---

### CSRF Challenges (5)

| # | Challenge | Difficulty | Endpoint | Method |
|---|-----------|------------|----------|--------|
| 11 | CSRF via POST | Intermediate | `/accounts/change-email/` | POST |
| 12 | CSRF via GET | Easy | `/accounts/reset-preferences/` | GET |
| 13 | Login CSRF | Intermediate | `/accounts/quick-login/` | POST |
| 14 | Logout CSRF | Easy | `/accounts/force-logout/` | GET |
| 15 | Password Change CSRF | Intermediate | `/accounts/change-password/` | POST |

**How to test:**

11. **CSRF POST** — The change-email view is `@csrf_exempt` with no CSRF token. Build an auto-submitting form on another origin:
    ```html
    <html><body onload="document.forms[0].submit()">
      <form action="http://127.0.0.1:8000/accounts/change-email/" method="POST">
        <input type="hidden" name="email" value="hacker@evil.com">
      </form>
    </body></html>
    ```
12. **CSRF GET** — The reset-preferences endpoint performs a state change via plain GET. Embed `<img src="http://127.0.0.1:8000/accounts/reset-preferences/">` on any page.
13. **Login CSRF** — The quick-login endpoint is `@csrf_exempt`. For a cross-site login, POST the attacker's credentials to `/accounts/quick-login/` from another origin.
14. **Logout CSRF** — The force-logout endpoint logs out via plain GET. Embed `<img src="http://127.0.0.1:8000/accounts/force-logout/">` on any page.
15. **Password Change CSRF** — The change-password view is `@csrf_exempt` and accepts the new password via POST. Forge a cross-site POST with `new_password=<known_value>`.

---

## 🚀 Run Locally — Step by Step

### Step 1 — Clone the repository

```bash
git clone https://github.com/lipon101/Helmaand.git
cd Helmaand
```

### Step 2 — Create and activate a virtual environment

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### Step 3 — Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4 — Apply database migrations

```bash
python manage.py migrate
```

### Step 5 — Seed demo data (products, hidden flags, CTF flags, promo codes, sample XSS review)

```bash
python manage.py seed_data
```

This creates:
- **Superuser:** `admin` / `admin123`
- **Test user:** `demo` / `demo123`
- 6 demo products + 1 hidden flag product (`is_active=0`)
- 3 promo codes (`SUMMER25`, `WELCOME10`, `VIP50`)
- 15 CTF flags seeded into the `security_ctfflag` table
- A sample stored-XSS review on the Luxury Leather Jacket

### Step 6 — (Optional) Collect static files

```bash
python manage.py collectstatic
```

### Step 7 — Run the development server

```bash
python manage.py runserver
```

Open your browser:

| Page              | URL                                |
|-------------------|------------------------------------|
| 🏠 Home           | http://127.0.0.1:8000/             |
| 🛒 Shop Catalog   | http://127.0.0.1:8000/shop/       |
| 🔍 Search (SQLi)  | http://127.0.0.1:8000/search/     |
| 🔬 Security Lab   | http://127.0.0.1:8000/lab/        |
| 👤 Login          | http://127.0.0.1:8000/accounts/login/ |
| 📝 Register       | http://127.0.0.1:8000/accounts/register/ |
| 📊 Dashboard      | http://127.0.0.1:8000/dashboard/  |
| ⚙️ Django Admin   | http://127.0.0.1:8000/admin/      |

---

## 🧪 Useful Management Commands

```bash
python manage.py check              # Check for issues
python manage.py showmigrations      # Show migration state
python manage.py makemigrations      # Make new migrations after model changes
python manage.py seed_data           # Populate demo data + CTF flag
python manage.py shell               # Interactive Django shell
```

---

## ⚙️ Configuration

Settings live in `perfect/settings.py`. Key environment variables:

| Variable                | Default | Description                              |
|-------------------------|---------|------------------------------------------|
| `DJANGO_DEBUG`          | `True`  | Enable/disable debug mode                |
| `DJANGO_ALLOWED_HOSTS`  | *(empty)* | Comma-separated list of allowed hosts  |

---

## 🌐 Deploy on Render (Free Tier)

1. Push your code to GitHub.
2. Create a new **Web Service** on [Render](https://render.com/) and connect the repo.
3. Set the build command:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py seed_data
   python manage.py collectstatic --noinput
   ```
4. Set the start command:
   ```bash
   gunicorn perfect.wsgi:application
   ```
5. Set environment variables:
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=your-app.onrender.com`

---

## 🔐 Test Credentials

After running `seed_data`:

| User    | Password   | Role       |
|---------|------------|------------|
| `admin` | `admin123` | Superuser  |
| `demo`  | `demo123`  | Regular user |

---

## 📝 Notes

- This project is an **intentionally vulnerable CTF platform** — do not use in production.
- SQLite is used by default — fine for development and CTF demos.
- Cart operations, order checkout, and payment logic are scaffolded but not fully implemented.

---

## 📄 License

This project is provided as-is for educational/CTF purposes.
