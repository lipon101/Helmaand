from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import connection
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Category, Review, Promo
from security.ctf_flags import (
    XSS_STORED, XSS_REFLECTED, XSS_DOM,
    SQLI_UNION, SQLI_ERROR, SQLI_BLIND, SQLI_TIME, SQLI_AUTH,
)


def home(request):
    featured_products = Product.objects.filter(is_active=True)[:6]
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })


def shop_catalog(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/catalog.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        comment = request.POST.get('comment', '')
        rating = request.POST.get('rating', 5)
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 5
        if comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment,
            )
            messages.success(request, "Your review has been posted!")
            return redirect('shop:product_detail', slug=product.slug)

    response = render(request, 'shop/detail.html', {
        'product': product,
        'reviews': reviews,
        'ctf_flag': XSS_STORED,
    })
    # Force-delete stale cookies from old CTF versions
    response.delete_cookie('ctf_xss_stored')
    return response


def product_search(request):
    """
    VULNERABLE (SQLi - UNION-based): Builds a raw SQL query via f-string
    concatenation of user-supplied `q`, so a UNION-based payload can
    exfiltrate arbitrary data.
    Example payload:
        q = "x' UNION SELECT id,name,slug,brand,description,price,
               discount_price,stock,size,color,is_active,created_at,
               updated_at,category_id FROM shop_product
               WHERE is_active=0 -- "
    """
    query = request.GET.get('q', '')
    results = []
    error_message = None
    if query:
        # NOTE: intentionally vulnerable — f-string interpolation into SQL
        sql = (
            f"SELECT * FROM shop_product "
            f"WHERE is_active = 1 AND name LIKE '%{query}%' "
            f"ORDER BY created_at DESC"
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [c[0] for c in cursor.description]
                rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            error_message = str(e)

    return render(request, 'shop/search.html', {
        'query': query,
        'results': results,
        'error_message': error_message,
    })


def track_order(request):
    """
    VULNERABLE (XSS - Reflected): The `order_id` GET parameter is reflected
    directly into the page via {{ tracking_id|safe }} without sanitization.
    A crafted URL like /track/?id=<script>alert(1)</script> executes JS in
    the victim's browser when visited.
    """
    tracking_id = request.GET.get('id', '')
    order_status = None
    if tracking_id and tracking_id.isdigit():
        # Simulated lookup — only real digits trigger the "found" path
        order_status = "In Transit"

    response = render(request, 'shop/track_order.html', {
        'tracking_id': tracking_id,
        'order_status': order_status,
        'ctf_flag': XSS_REFLECTED,
    })
    # Force-delete stale cookies from old CTF versions
    response.delete_cookie('ctf_xss_reflected')
    return response


def product_gallery(request):
    """
    VULNERABLE (XSS - DOM): The page contains JavaScript that reads
    location.hash and writes it into innerHTML without sanitization.
    Visiting /gallery/#<img src=x onerror=alert(1)> executes the payload
    entirely client-side. The server never sees the payload — this is pure
    DOM-based XSS.
    """
    featured_products = Product.objects.filter(is_active=True)[:8]
    response = render(request, 'shop/gallery.html', {
        'featured_products': featured_products,
    })
    # CTF: flag cookie — exfiltrate via DOM XSS (document.cookie)
    response.set_cookie('ctf_xss_dom', XSS_DOM)
    return response


def category_filter(request):
    """
    VULNERABLE (SQLi - Error-based): The `sort` GET parameter is concatenated
    into a raw ORDER BY clause. Invalid SQL causes the database error (with
    table/column names) to be reflected back to the user, leaking schema info.
    Example payload:  ?sort=(CASE WHEN (SELECT 1)=1 THEN name ELSE price END)
    Error payload:    ?sort=extractvalue(1,concat(0x7e,(SELECT version())))
    """
    sort_param = request.GET.get('sort', 'name')
    # Whitelist would prevent this; intentionally absent
    allowed = {'name', 'price', 'created_at'}
    use_raw = sort_param not in allowed  # any non-whitelisted value → raw SQL

    products = []
    error_message = None
    if use_raw and sort_param:
        # NOTE: intentionally vulnerable — raw concatenation into ORDER BY
        sql = (
            f"SELECT id, name, slug, brand, description, price, "
            f"discount_price, stock, size, color, is_active, created_at, "
            f"updated_at, category_id FROM shop_product "
            f"WHERE is_active = 1 ORDER BY {sort_param} DESC"
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [c[0] for c in cursor.description]
                rows = cursor.fetchall()
            products = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            # NOTE: intentionally exposing the raw DB error to the user
            error_message = str(e)
    else:
        products = list(
            Product.objects.filter(is_active=True)
            .order_by('-' + sort_param)
            .values('id', 'name', 'slug', 'brand', 'description', 'price',
                    'discount_price', 'stock', 'size', 'color', 'is_active')
        )

    return render(request, 'shop/category_filter.html', {
        'sort': sort_param,
        'products': products,
        'error_message': error_message,
    })


def check_stock(request):
    """
    VULNERABLE (SQLi - Blind boolean-based & time-based): The `product_id`
    parameter is concatenated into a raw SQL query. The page only returns
    "In Stock" or "Out of Stock" (boolean), so an attacker can extract data
    bit by bit using boolean conditions. SLEEP() can also be injected for
    time-based blind extraction.

    Boolean example:
        ?id=1 AND (SELECT substr(password,1,1)='a' FROM auth_user WHERE is_superuser=1) --
    Time-based example:
        ?id=1 AND SLEEP(3) --

    Note: SQLite doesn't have SLEEP(); the boolean path still works on SQLite.
    On MySQL/Postgres deployments, time-based payloads function as expected.
    """
    product_id = request.GET.get('id', '')
    stock_info = None
    error_message = None

    if product_id:
        # NOTE: intentionally vulnerable — raw concatenation
        sql = (
            f"SELECT stock FROM shop_product "
            f"WHERE id = {product_id} AND is_active = 1"
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
            if row and row[0] > 0:
                stock_info = f"In Stock ({row[0]} units available)"
            elif row:
                stock_info = "Out of Stock"
            else:
                stock_info = "Product not found"
        except Exception as e:
            error_message = str(e)

    return render(request, 'shop/check_stock.html', {
        'product_id': product_id,
        'stock_info': stock_info,
        'error_message': error_message,
    })


def newsletter_signup(request):
    """
    VULNERABLE (XSS - Attribute-based): The ?name= GET parameter is reflected
    directly into an HTML attribute value without escaping quotes. An attacker
    can break out of the attribute and inject an event handler.

    Example payload:
        /newsletter/?name=" onmouseover="alert(document.cookie)
    """
    name = request.GET.get('name', '')
    subscribed = False
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            subscribed = True
            messages.success(request, "You've been subscribed to the newsletter!")
    elif name:
        subscribed = True

    return render(request, 'shop/newsletter.html', {
        'name': name,
        'subscribed': subscribed,
    })


def promo_validator(request):
    """
    VULNERABLE (SQLi - Time-based blind): The ?code= parameter is concatenated
    into a raw SQL query against the promo table. The page only returns "Valid"
    or "Invalid" — no data is reflected. An attacker can inject a time-delay
    payload (SLEEP on MySQL, randomblob on SQLite) and measure response time to
    extract data character by character.

    Boolean example (works on SQLite):
        ?code=SUMMER25' OR (SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_time') --
    Time-based example (MySQL):
        ?code=SUMMER25' OR IF((SELECT substr(flag,1,1)='H' FROM security_ctfflag WHERE challenge_id='sqli_time'),SLEEP(3),0) --
    """
    code = request.GET.get('code', '')
    result = None

    if code:
        # NOTE: intentionally vulnerable — raw concatenation into SQL
        sql = f"SELECT 1 FROM shop_promo WHERE code = '{code}' AND is_active = 1 LIMIT 1"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()
            result = "Valid promo code! Discount applied." if row else "Invalid promo code."
        except Exception:
            result = "Invalid promo code."

    return render(request, 'shop/promo.html', {
        'code': code,
        'result': result,
    })


@csrf_exempt
def staff_login_view(request):
    """
    VULNERABLE (SQLi - Auth bypass): The staff login form builds a raw SQL query
    by concatenating the username and password fields. A classic injection in the
    username field bypasses authentication entirely.

    The WAF blocks SQLi patterns in URL query strings AND POST bodies.
    To bypass the WAF, the payload is delivered via a browser cookie.
    WAFs never inspect cookie values, so the payload passes through invisible.

    WAF-safe flow:
        1. Visit /staff-login/encode/ — sets _ctf_payload cookie and redirects here
        2. This view reads the cookie, decodes base64, injects into raw SQL
    """
    username = ''
    password = ''

    # Method 1: Read base64-encoded payload from cookie (WAF-invisible)
    cookie_token = request.COOKIES.get('_ctf_payload', '')
    if cookie_token:
        try:
            import base64
            decoded = base64.b64decode(cookie_token).decode('utf-8')
            if '|' in decoded:
                username, password = decoded.split('|', 1)
            else:
                username = decoded
                password = ''
        except Exception:
            pass

    # Method 2: Read base64-encoded payload via _token GET param
    if not username:
        token = request.GET.get('_token', '')
        if token:
            try:
                import base64
                decoded = base64.b64decode(token).decode('utf-8')
                if '|' in decoded:
                    username, password = decoded.split('|', 1)
                else:
                    username = decoded
                    password = ''
            except Exception:
                pass

    # Method 3: Direct params (works locally, blocked by WAF on Render)
    if not username and request.GET.get('username'):
        username = request.GET.get('username', '')
        password = request.GET.get('password', '')

    error_message = None
    if username:
        # NOTE: intentionally vulnerable — raw concatenation into SQL
        sql = (
            f"SELECT * FROM auth_user "
            f"WHERE username = '{username}' AND password = '{password}' "
            f"AND is_staff = 1 LIMIT 1"
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [c[0] for c in cursor.description]
                row = cursor.fetchone()
            if row:
                user_dict = dict(zip(columns, row))
                from django.contrib.auth.models import User
                user = User.objects.get(id=user_dict['id'])
                login(request, user)
                messages.success(request, f"Welcome to the staff area, {user.username}!")
                messages.info(request, f"Flag: {SQLI_AUTH}")
                return redirect('shop:home')
            else:
                error_message = "Invalid staff credentials."
        except Exception as e:
            error_message = str(e)

    return render(request, 'shop/staff_login.html', {
        'error_message': error_message,
    })


def staff_login_encode(request):
    """
    WAF bypass helper: sets a cookie with the base64-encoded SQLi payload,
    then redirects to /staff-login/. The WAF inspects URLs and POST bodies
    but NEVER inspects cookie values — the payload is invisible to it.
    """
    import base64
    username = request.GET.get('username', "admin' OR '1'='1")
    password = request.GET.get('password', 'anything')
    raw = f"{username}|{password}"
    token = base64.b64encode(raw.encode()).decode()
    response = redirect('shop:staff_login')
    # Set cookie with the payload — WAF cannot see this
    response.set_cookie('_ctf_payload', token, max_age=300)
    return response
