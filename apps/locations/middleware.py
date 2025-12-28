"""
Middleware for handling Cloudflare proxy headers.
"""

import json


class CloudflareProxyMiddleware:
    """
    Middleware to parse Cloudflare's CF-Visitor header and set the correct scheme.

    Cloudflare sends CF-Visitor: {"scheme":"https"} header to indicate the original
    scheme when the connection between Cloudflare and the origin is HTTP.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Parse CF-Visitor header
        cf_visitor = request.META.get('HTTP_CF_VISITOR')
        if cf_visitor:
            try:
                visitor_data = json.loads(cf_visitor)
                scheme = visitor_data.get('scheme')
                if scheme:
                    # Override X-Forwarded-Proto with the scheme from CF-Visitor
                    request.META['HTTP_X_FORWARDED_PROTO'] = scheme
            except (json.JSONDecodeError, KeyError):
                pass

        response = self.get_response(request)
        return response
