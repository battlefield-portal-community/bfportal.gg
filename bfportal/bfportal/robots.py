from django.http import HttpRequest, HttpResponse


def serve_robots_txt(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Returns robots.txt"""
    robots_txt = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: http://{request.get_host()}/sitemap.xml",
        ]
    )
    return HttpResponse(robots_txt, content_type="text/plain")
