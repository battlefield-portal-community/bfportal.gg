from ajax_select import urls as ajax_select_urls
from core.api import api_router
from core.views import (
    CategoriesAutocomplete,
    TagsAutocomplete,
    events_view,
    handle_like_request,
    report_experience,
)
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView, TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls
from wagtailautocomplete.urls.admin import urlpatterns as autocomplete_admin_urls

from .robots import serve_robots_txt
from .sitemaps import sitemaps

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/autocomplete/", include(autocomplete_admin_urls)),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # allow only social login :)
    *[
        path("password/change/", RedirectView.as_view(url="/")),
        path("password/set/", RedirectView.as_view(url="/")),
        path("password/reset/", RedirectView.as_view(url="/")),
        path("password/reset/done/", RedirectView.as_view(url="/")),
        re_path(
            "^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
            RedirectView.as_view(url="/"),
        ),
        path("password/reset/key/done/", RedirectView.as_view(url="/")),
        path("email/", RedirectView.as_view(url="/")),
        path("confirm-email/", RedirectView.as_view(url="/")),
        re_path("^confirm-email/(?P<key>[-:\\w]+)/$", RedirectView.as_view(url="/")),
        path("signup/", RedirectView.as_view(url="/")),
    ],
    # go straight to discord login
    *[
        path("login/", RedirectView.as_view(url="/discord/login/?process=login")),
        path("", include("allauth.urls")),
    ],
    # api urls
    *[
        path(
            "api/categories/",
            CategoriesAutocomplete.as_view(),
            name="category-autocomplete",
        ),
        path("api/tags/", TagsAutocomplete.as_view(), name="tags-autocomplete"),
        re_path(r"^api/report/(\d+)/$", report_experience, name="report-experience"),
        re_path(
            r"^api/like/(\d+)/$",
            handle_like_request,
            name="add_like_to_experience_page",
        ),
        path("api/", api_router.urls),
        re_path(
            "^api/$", TemplateView.as_view(template_name="coming_soon.html")
        ),  # todo: add correct api docs
    ],
    re_path(r"^ajax_select/", include(ajax_select_urls)),
    path("markdownx/", include("markdownx.urls")),
    path("events/", events_view, name="events-view"),
]

# sitemap urls
urlpatterns += [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
    )
]
# robots.txt
urlpatterns += [
    path(
        "robots.txt",
        serve_robots_txt,
    )
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # auto reload on static or template edit
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    # A temp url to serve templates directly
    urlpatterns.append(path("test/", TemplateView.as_view(template_name="502.html")))
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
