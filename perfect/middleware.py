class CTFCleanupMiddleware:
    """Deletes stale CTF cookies from every response so old cookies
    don't leak across challenges. The browser auto-expires them."""
    STALE_COOKIES = ['ctf_xss_stored', 'ctf_xss_reflected']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        for name in self.STALE_COOKIES:
            response.delete_cookie(name)
        return response
