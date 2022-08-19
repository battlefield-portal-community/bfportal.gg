def get_dashboard_url(request, page):
    """Returns url to edit in admin panel for a given page"""
    return f"{request.scheme}://{request.get_host()}/admin/pages/{page.id}/edit"


def get_page_url(request, page):
    """Returns url to the page"""
    return f"{request.scheme}://{request.get_host()}{page.get_url()}"
