# Helmaand 🛍️

**CTF e-Commerce Platform** — a Django 6.0 clothing/apparel storefront with authentication, product catalog, cart, orders, and an admin dashboard.

Built with:
- 🐍 Python 3.12+
- 🌐 Django 6.0.7
- 🗄️ SQLite (default database)
- 🖼️ Pillow (image handling)
- 🎨 Django Templates + static CSS

---

## 📦 Project Structure

```
Helmaand/
├── manage.py              # Django CLI entry point
├── requirements.txt       # Python dependencies
├── perfect/               # Django project package (settings, urls, wsgi)
├── accounts/              # User auth: login, register, profile
├── shop/                  # Product catalog: home, shop, product detail
├── cart/                  # Shopping cart (model scaffolded)
├── orders/                # Orders (model scaffolded)
├── dashboard/             # Admin dashboard views
├── security/              # Security app (scaffolded)
├── templates/             # HTML templates (base, accounts, shop)
└── static/                # Static assets (CSS)
```

---

## 🚀 Run Locally — Step by Step

Follow these steps in order. Commands assume you are in the project root (the folder containing `manage.py`).

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

> `requirements.txt` contains:
> ```
> Django==6.0.7
> Pillow==12.3.0
> ```

### Step 4 — Apply database migrations

This creates the SQLite database (`db.sqlite3`) and all tables.

```bash
python manage.py migrate
```

### Step 5 — Create a superuser (for the admin panel)

```bash
python manage.py createsuperuser
```

You'll be prompted for a username, email, and password.

### Step 6 — (Optional) Collect static files

Only needed if `DEBUG=False` or for production. Safe to run anytime.

```bash
python manage.py collectstatic
```

### Step 7 — Run the development server

```bash
python manage.py runserver
```

Now open your browser:

| Page              | URL                                |
|-------------------|------------------------------------|
| 🏠 Home           | http://127.0.0.1:8000/             |
| 🛒 Shop Catalog   | http://127.0.0.1:8000/shop/       |
| 👤 Login          | http://127.0.0.1:8000/accounts/login/ |
| 📝 Register       | http://127.0.0.1:8000/accounts/register/ |
| 📊 Admin Dashboard| http://127.0.0.1:8000/dashboard/  |
| ⚙️ Django Admin   | http://127.0.0.1:8000/admin/      |

---

## 🧪 Useful Management Commands

```bash
# Check for issues in your project
python manage.py check

# Show all migration state
python manage.py showmigrations

# Make new migrations after model changes
python manage.py makemigrations

# Start an interactive Django shell
python manage.py shell

# Run the test suite (per app)
python manage.py test shop
python manage.py test accounts
```

---

## ⚙️ Configuration

Settings live in `perfect/settings.py`. Key environment variables you can set:

| Variable                | Default | Description                              |
|-------------------------|---------|------------------------------------------|
| `DJANGO_DEBUG`          | `True`  | Enable/disable debug mode                |
| `DJANGO_ALLOWED_HOSTS`  | *(empty)* | Comma-separated list of allowed hosts  |

Example:
```bash
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
python manage.py runserver
```

---

## 🌐 Free Deployment (Render)

This app works on **[Render](https://render.com/)** free tier:

1. Push your code to GitHub.
2. Create a new **Web Service** on Render and connect the repo.
3. Set the build command:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
4. Set the start command:
   ```bash
   gunicorn perfect.wsgi:application
   ```
   (add `gunicorn` to `requirements.txt` for production)
5. Set environment variables:
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=your-app.onrender.com`

---

## 📝 Notes

- This project is in **early development**. Cart operations, order checkout, and payment logic are scaffolded but not fully implemented.
- SQLite is used by default — fine for development and small-scale demos.
- Default `SECRET_KEY` is dev-only; **set a real secret** before deploying.

---

## 📄 License

This project is provided as-is for educational/CTF purposes.
