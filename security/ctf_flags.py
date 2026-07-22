"""
CTF Flag definitions for the Helmaand Security Lab.

All flags follow the format: HLMD{...}

Each flag is short, memorable, and themed to its vulnerability category.

XSS   → exfil/cookie themes   (flags delivered via a flag cookie)
SQLi  → DB-extraction themes  (flags stored in a dedicated table or hidden rows)
CSRF  → trust/impersonation    (flags revealed in success messages)
"""

# ─────────────── XSS (5) ───────────────
XSS_STORED      = "HLMD{st0r3d_c00k13_m0nst3r}"
XSS_REFLECTED   = "HLMD{r3fl3ct3d_gl4ss_sh4tt3r}"
XSS_DOM         = "HLMD{d0m_s1nk_b0w_bre4ch}"
XSS_ATTRIBUTE   = "HLMD{4ttr_m0us3_0v3r_l34k}"
XSS_SELF        = "HLMD{s3lf_1nfl1ct3d_1nj3ct}"

# ─────────────── SQLi (5) ───────────────
SQLI_UNION      = "HLMD{un10n_s3l3ct_d4t4_dr41n}"
SQLI_ERROR      = "HLMD{3rr0r_l34k_sch3m4_expl0s10n}"
SQLI_BLIND      = "HLMD{bl1nd_b00l3an_0r4cl3}"
SQLI_TIME       = "HLMD{t1m3_w41ts_f0r_n0_0n3}"
SQLI_AUTH       = "HLMD{4uth_byp4ss_m4st3r_k3y}"

# ─────────────── CSRF (5) ───────────────
CSRF_POST       = "HLMD{f0rg3d_p0st_3m41l_h1j4ck}"
CSRF_GET        = "HLMD{g3t_r3qu3st_s1l3nt_w1p3}"
CSRF_LOGIN      = "HLMD{l0g1n_sw4p_1mp3rs0n4t10n}"
CSRF_LOGOUT     = "HLMD{l0g0ut_f0rc3d_3v1ct10n}"
CSRF_PASSWORD   = "HLMD{p4ssw0rd_r3s3t_p0wn3d}"

ALL_FLAGS = {
    'xss_stored':     (XSS_STORED,    'XSS',    'Easy'),
    'xss_reflected':  (XSS_REFLECTED, 'XSS',    'Easy'),
    'xss_dom':        (XSS_DOM,       'XSS',    'Intermediate'),
    'xss_attribute':  (XSS_ATTRIBUTE, 'XSS',    'Intermediate'),
    'xss_self':       (XSS_SELF,      'XSS',    'Easy'),
    'sqli_union':     (SQLI_UNION,    'SQLi',   'Intermediate'),
    'sqli_error':     (SQLI_ERROR,    'SQLi',   'Intermediate'),
    'sqli_blind':     (SQLI_BLIND,    'SQLi',   'Intermediate'),
    'sqli_time':      (SQLI_TIME,     'SQLi',   'Intermediate'),
    'sqli_auth':      (SQLI_AUTH,     'SQLi',   'Easy'),
    'csrf_post':      (CSRF_POST,     'CSRF',   'Intermediate'),
    'csrf_get':       (CSRF_GET,      'CSRF',   'Easy'),
    'csrf_login':     (CSRF_LOGIN,    'CSRF',   'Intermediate'),
    'csrf_logout':    (CSRF_LOGOUT,   'CSRF',   'Easy'),
    'csrf_password':  (CSRF_PASSWORD, 'CSRF',   'Intermediate'),
}
