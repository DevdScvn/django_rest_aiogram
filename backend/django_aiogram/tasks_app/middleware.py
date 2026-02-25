"""CSRF exemption for API requests (REST API used by bot)."""
from django.utils.deprecation import MiddlewareMixin


class CsrfExemptApiMiddleware(MiddlewareMixin):
    """Exempt all /api/ requests from CSRF (stateless REST API)."""
    def process_request(self, request):
        if request.path.startswith("/api/"):
            setattr(request, "_dont_enforce_csrf_checks", True)
