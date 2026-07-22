from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def lab_index(request):
    """Security Lab hub — lists all 15 CTF challenges grouped by category."""
    challenges = [
        # ───────────────────── XSS (5) ─────────────────────
        {
            'id': 'xss_stored',
            'name': 'Stored XSS',
            'difficulty': 'Easy',
            'category': 'XSS',
            'endpoint': '/product/luxury-leather-jacket/',
            'description': 'A customer review form stores and displays user comments without sanitization. Inject JavaScript that executes when another user views the product page.',
            'hint': 'Visit any product detail page and post a review. The comment field is rendered with the |safe filter. Try <code>&lt;script&gt;alert(document.cookie)&lt;/script&gt;</code>.',
            'objective': 'Exfiltrate the flag cookie from a victim\'s browser via a stored XSS payload.',
            'flag_hint': 'A flag cookie is set on the product page. Read document.cookie to find it.',
        },
        {
            'id': 'xss_reflected',
            'name': 'Reflected XSS',
            'difficulty': 'Easy',
            'category': 'XSS',
            'endpoint': '/track/',
            'description': 'The order-tracking page reflects the ?id= GET parameter directly into the HTML without escaping. Craft a URL that executes JavaScript when a victim clicks it.',
            'hint': 'The tracking_id value is rendered with {{ tracking_id|safe }}. Visit /track/?id=&lt;script&gt;alert(document.cookie)&lt;/script&gt;.',
            'objective': 'Craft a malicious URL that steals the flag cookie from the victim\'s browser.',
            'flag_hint': 'A flag cookie is set on the track-order page. Use document.cookie to read it.',
        },
        {
            'id': 'xss_dom',
            'name': 'DOM-based XSS',
            'difficulty': 'Intermediate',
            'category': 'XSS',
            'endpoint': '/gallery/',
            'description': 'The product gallery page reads location.hash and writes it into innerHTML via JavaScript. The payload never reaches the server — this is pure client-side DOM XSS.',
            'hint': 'Append a hash to the URL: /gallery/#&lt;img src=x onerror="alert(document.cookie)"&gt;. The page JS does el.innerHTML = hash with no sanitization.',
            'objective': 'Execute JavaScript via the URL hash fragment and read the flag cookie.',
            'flag_hint': 'A flag cookie is set on the gallery page. The DOM XSS sink lets you run JS to read it.',
        },
        # ──────────────────── SQLi (5) ────────────────────
        {
            'id': 'sqli_union',
            'name': 'UNION-based SQLi',
            'difficulty': 'Intermediate',
            'category': 'SQLi',
            'endpoint': '/search/',
            'description': 'The product search uses raw SQL with string concatenation. Craft a UNION SELECT payload to exfiltrate data from a hidden product row.',
            'hint': 'The q parameter is interpolated into SELECT * FROM shop_product WHERE name LIKE \'%q%\'. There is a hidden product (is_active=0) containing a flag. Use UNION SELECT to pull all columns.',
            'objective': 'Find the hidden inactive product whose description contains the flag.',
            'flag_hint': 'The flag is in the description field of shop_product where is_active=0. UNION SELECT all columns.',
        },
        {
            'id': 'sqli_error',
            'name': 'Error-based SQLi',
            'difficulty': 'Intermediate',
            'category': 'SQLi',
            'endpoint': '/filter/',
            'description': 'The product filter passes the ?sort= parameter directly into an ORDER BY clause. Invalid SQL triggers a raw database error that is reflected back, leaking schema information.',
            'hint': 'Try ?sort=extractvalue(1,concat(0x7e,(SELECT version()))) or any invalid column name. The raw DB error is shown to the user.',
            'objective': 'Use error-based injection to extract the flag from the security_ctfflag table.',
            'flag_hint': 'Target table: security_ctfflag. Extract the flag column where challenge_id=\'sqli_error\'.',
        },
        {
            'id': 'sqli_blind',
            'name': 'Blind Boolean SQLi',
            'difficulty': 'Intermediate',
            'category': 'SQLi',
            'endpoint': '/stock/',
            'description': 'The stock checker takes ?id= and concatenates it into a raw SQL query. Only "In Stock" or "Out of Stock" is returned — no product data. Extract data bit by bit using boolean conditions.',
            'hint': 'The query is SELECT stock FROM shop_product WHERE id = {id} AND is_active = 1. Try ?id=1 AND (SELECT 1=1) -- vs ?id=1 AND (SELECT 1=2) --. The response differs, enabling boolean-based extraction.',
            'objective': 'Extract the blind SQLi flag from the security_ctfflag table using boolean-based blind injection.',
            'flag_hint': 'Target table: security_ctfflag. Extract the flag column where challenge_id=\'sqli_blind\', one character at a time.',
        },
        {
            'id': 'sqli_time',
            'name': 'Time-based Blind SQLi',
            'difficulty': 'Intermediate',
            'category': 'SQLi',
            'endpoint': '/promo/',
            'description': 'The promo code validator concatenates the ?code= parameter into a raw SQL query that checks a promotions table. No data is returned — only "Valid" or "Invalid". A time-delay payload reveals whether a condition is true.',
            'hint': 'The query is SELECT 1 FROM shop_promo WHERE code=\'CODE\'. On SQLite use randomblob(300000000) to cause a delay; on MySQL use SLEEP(5). Inject a subquery condition and measure response time.',
            'objective': 'Extract the time-based SQLi flag from the security_ctfflag table using time-based blind injection.',
            'flag_hint': 'Target table: security_ctfflag. Extract the flag column where challenge_id=\'sqli_time\' by measuring response delays.',
        },
        {
            'id': 'sqli_auth',
            'name': 'Authentication Bypass',
            'difficulty': 'Easy',
            'category': 'SQLi',
            'endpoint': '/staff-login/',
            'description': 'The staff login form builds a raw SQL query by concatenating the username and password. A classic SQL injection in the username field can bypass authentication and log in without a valid password.',
            'hint': 'The query is SELECT * FROM auth_user WHERE username=\'USER\' AND password=\'PASS\'. Try username <code>admin\' OR \'1\'=\'1</code> with any password, or <code>admin\'--</code> to comment out the password check.',
            'objective': 'Log in to the staff area without knowing any password.',
            'flag_hint': 'After bypassing auth, the staff dashboard shows the flag in a success message.',
        },
        # ──────────────────── CSRF (5) ────────────────────
        {
            'id': 'csrf_post',
            'name': 'CSRF via POST',
            'difficulty': 'Intermediate',
            'category': 'CSRF',
            'endpoint': '/accounts/change-email/',
            'description': 'The email-change endpoint disables CSRF protection via @csrf_exempt. Craft a malicious HTML page that auto-submits a POST to change a logged-in user\'s email.',
            'hint': 'The change-email form has no CSRF token and the view is @csrf_exempt. Build an external HTML page with a hidden auto-submitting form that POSTs email=attacker@evil.com to /accounts/change-email/.',
            'objective': 'Successfully change a victim user\'s email via a cross-site POST request.',
            'flag_hint': 'After the POST succeeds, the redirect page shows the flag in a flash message.',
        },
        {
            'id': 'csrf_get',
            'name': 'CSRF via GET',
            'difficulty': 'Easy',
            'category': 'CSRF',
            'endpoint': '/accounts/reset-preferences/',
            'description': 'The reset-preferences endpoint performs a state-changing operation (clearing shipping info) via a plain GET request. No CSRF token, no POST required.',
            'hint': 'Simply embedding <code>&lt;img src="https://helmaand.local/accounts/reset-preferences/"&gt;</code> on any page will trigger the reset when a logged-in victim visits.',
            'objective': 'Reset a victim user\'s shipping profile data via a cross-site GET request.',
            'flag_hint': 'After the GET succeeds, the redirect page shows the flag in a flash message.',
        },
        {
            'id': 'csrf_password',
            'name': 'Password Change CSRF',
            'difficulty': 'Intermediate',
            'category': 'CSRF',
            'endpoint': '/accounts/change-password/',
            'description': 'The password-change endpoint is @csrf_exempt and accepts the new password via POST. An attacker can forge a cross-site request to change a victim\'s password to a known value.',
            'hint': 'Build an auto-submitting form that POSTs new_password=attacker123 to /accounts/change-password/. The victim\'s password is changed without their knowledge.',
            'objective': 'Change a victim user\'s password to a known value via a forged cross-site POST.',
            'flag_hint': 'After the password change succeeds, the profile page shows the flag in a flash message.',
        },
    ]
    return render(request, 'security/lab.html', {'challenges': challenges})


@login_required
def vault_view(request):
    """
    Hidden vault page — only reachable by users who know the URL.
    This is the single, soft placement of the author credit.
    """
    if not request.user.is_staff:
        return render(request, 'security/vault_denied.html', status=403)
    return render(request, 'security/vault.html')
