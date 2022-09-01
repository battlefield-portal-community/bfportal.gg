import operator
from datetime import datetime
from functools import reduce

from allauth.socialaccount.models import SocialAccount
from core.utils.helper import safe_cast
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.timezone import timezone
from embed_video.fields import EmbedVideoField
from loguru import logger
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.models import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, StreamFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet
from wagtailautocomplete.edit_handlers import AutocompletePanel
from wagtailsvg.edit_handlers import SvgChooserPanel
from wagtailsvg.models import Svg

from bfportal.settings.base import LOGIN_URL


def apply_filters(request: HttpRequest, posts: models.query.QuerySet):
    """Applies get param filters to database and returns posts"""
    all_posts = posts
    if experience := request.GET.get("experience", None):
        logger.debug(f"Experience Name :- {experience}")
        all_posts = all_posts.filter(title__icontains=experience)

    from_date = request.GET.get("From", None)
    if from_date is None or from_date == "":
        from_date = datetime.utcfromtimestamp(0)  # use date provided else use epoch
    else:
        from_date = datetime.fromisoformat(from_date)

    to_date = request.GET.get("To")
    if to_date is None or to_date == "":
        to_date = datetime.utcnow()  # use date provided else use current time
    else:
        to_date = datetime.fromisoformat(to_date)

    from_date = from_date.replace(tzinfo=timezone.utc)
    to_date = to_date.replace(tzinfo=timezone.utc)

    logger.debug(f"From {from_date} to {to_date}")
    all_posts = all_posts.filter(first_published_at__range=(from_date, to_date))
    if username := request.GET.get("user", ""):
        if username != "":
            all_posts = all_posts.annotate(
                discord_username=Concat("owner__first_name", V(" "), "owner__last_name")
            )
            logger.debug(f"username is {username}")
            all_posts = all_posts.filter(discord_username__icontains=username)

    if tags := request.GET.getlist("tag", None):
        logger.debug(tags)
        all_posts = all_posts.filter(tags__name__in=tags).distinct()

    if category := request.GET.getlist("category", None):
        category = list(map(str.lower, category))
        post: ExperiencePage
        all_posts = all_posts.filter(
            reduce(operator.or_, (Q(category__name__iexact=cat) for cat in category))
        )
    if sub_cats := request.GET.getlist("sub_cat", None):
        sub_cats: [SubCategory, ...]
        sub_cats = list(map(str.lower, sub_cats))
        post: ExperiencePage
        all_posts = all_posts.filter(
            reduce(
                operator.or_, (Q(sub_categories__name__iexact=cat) for cat in sub_cats)
            )
        )
    if tags or category or sub_cats:
        logger.debug(
            f"filtered {len(all_posts)} experiences for tags {tags}, cat [{category}, sub cat {sub_cats}]"
        )
    return all_posts


def pagination_wrapper(request: HttpRequest, posts: models.query.QuerySet) -> Paginator:
    """Returns paginated result for a query"""
    paginator = Paginator(apply_filters(request, posts), request.GET.get("n", 10))
    curr_page = safe_cast(request.GET.get("page", None), int, 1)
    try:
        # If the page exists and the ?page=x is an int
        posts = paginator.page(curr_page)
    except PageNotAnInteger:
        # If the ?page=x is not an int; show the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If the ?page=x is out of range (too high most likely)
        # Then return the last page
        posts = paginator.page(paginator.num_pages)

    return posts


class ExtraContent(blocks.StreamBlock):
    """Class defining extra fields available to all pages"""

    heading = blocks.CharBlock(form_classname="full title")
    cover_image = ImageChooserBlock()
    text = blocks.RichTextBlock()

    class Meta:
        template = "core/blocks/extra_content.html"
        icon = "user"
        required = False
        help_text = "Custom Content for a page"


class CustomBasePage(Page):
    """Base class for all pages in the app

    Require to expose ExtraContent to all child pages
    """

    extra_content = StreamField(ExtraContent(), blank=True)
    content_panels = Page.content_panels + [
        StreamFieldPanel(
            "extra_content",
            classname="collapsible",
        )
    ]

    class Meta:
        abstract = True


class HomePage(RoutablePageMixin, CustomBasePage):
    """Class defining the 'index' page of the website"""

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["core.ExperiencesPage", "core.ProfilePage", "core.BlogPage"]

    @route(r"^$")
    def base(self, request):  # noqa: D102
        logger.debug("base")
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request, filter_trending=True),
        )

    @route(r"^submit/$")
    def submit_exp(self, request):  # noqa: D102
        from core.views import submit_experience

        return submit_experience(request, self)

    def get_context(self, request, *args, **kwargs):  # noqa: D102
        filter_trending = kwargs.pop("filter_trending", False)
        context = super().get_context(request, *args, **kwargs)
        posts = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )

        context["categories"] = list(ExperiencesCategory.objects.all()) + list(
            SubCategory.objects.all()
        )
        context["posts"] = posts
        if filter_trending:
            context["trending_posts"] = (
                ExperiencePage.objects.filter(trending=True)
                .live()
                .public()
                .order_by("-first_published_at")
            )
        return context

    @route(r"^category/(.+)/$")
    def serve_category_page(self, request, cat):
        """Returns template with post of a category if cat present in db"""
        logger.debug("in")
        main_cat, sub_cat = None, None

        if cat_object := ExperiencesCategory.objects.filter(name__iexact=cat).first():
            main_cat = cat_object
        elif cat_object := SubCategory.objects.filter(name__iexact=cat).first():
            sub_cat = cat_object
        else:
            return self.render(request=request, template="404.html")

        request.GET = request.GET.copy()
        if main_cat:
            request.GET["category"] = main_cat.name
        if sub_cat:
            request.GET["sub_cat"] = sub_cat.name
        context = super().get_context(request)
        posts = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )
        context["posts"] = posts
        context["no_extra_content"] = True
        return TemplateResponse(request, self.get_template(request), context)


class ExperiencesCategory(models.Model):
    """Class defining properties of experience category tag"""

    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        Svg,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    visible = models.BooleanField(
        help_text="Show Category on home page?", default=True, null=False
    )
    panels = [FieldPanel("name"), SvgChooserPanel("icon"), FieldPanel("visible")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Main Categories"


class SubCategory(models.Model):
    """Class defining properties of experience sub categories"""

    name = models.CharField(max_length=255)
    icon = models.ForeignKey(
        Svg,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    visible = models.BooleanField(
        help_text="Show Category on home page?", default=True, null=False
    )
    panels = [FieldPanel("name"), SvgChooserPanel("icon"), FieldPanel("visible")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sub Categories"


register_snippet(ExperiencesCategory)
register_snippet(SubCategory)


class ExperiencePageTag(TaggedItemBase):
    """Class to link a tag to an Experience page"""

    content_object = ParentalKey(
        "ExperiencePage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class ExperiencesPage(RoutablePageMixin, CustomBasePage):
    """Class defining page that lists all experiences"""

    max_count = 1
    parent_page_types = ["core.HomePage"]
    subpage_types = ["core.ExperiencePage", "core.BlogPage"]

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        context["posts"] = pagination_wrapper(
            request,
            ExperiencePage.objects.live().public().order_by("-first_published_at"),
        )
        return context

    @route(r"^featured/$")
    def featured_experiences(self, request: HttpRequest):  # noqa: D102
        return TemplateResponse(
            request,
            self.get_template(request),
            {
                "posts": ExperiencePage.objects.live()
                .filter(featured__exact=True)
                .order_by("-first_published_at"),
            },
        )


class BlogPage(CustomBasePage):
    """Class for future usage"""

    pass


class ExperiencePage(RoutablePageMixin, CustomBasePage):
    """Class defining properties of an experience page

    This is equivalent to a post in a blog
    """

    featured = models.BooleanField(
        default=False,
        help_text="Is this experience a featured experience",
        verbose_name="Set Featured",
    )
    trending = models.BooleanField(
        default=False,
        null=False,
        help_text="Is this experience trending?",
        verbose_name="Set Trending",
    )
    description = models.TextField(
        default="",
        help_text="Description of Your experience",
        verbose_name="Description",
    )

    code = models.CharField(
        blank=True,
        max_length=6,
        default="",
        help_text="Six letter alpha-numeric code of you experience",
        verbose_name="Experience Code",
    )
    exp_url = models.URLField(
        blank=True,
        default="",
        help_text="Url of your experience",
        verbose_name="Experience Url",
    )

    tags = ClusterTaggableManager(
        blank=True,
        help_text="Some tags",
        through=ExperiencePageTag,
        verbose_name="Tags",
    )
    vid_url = EmbedVideoField(
        blank=True,
        default="",
        help_text="Link to vid showcasing your experience",
        verbose_name="Video Url",
    )
    cover_img_url = models.URLField(
        blank=True,
        default="",
        help_text="Link for your cover Image",
        verbose_name="Cover Image Url",
    )

    no_players = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="Max Number of Human Players in your experience",
        verbose_name="Number of Human Players",
    )
    no_bots = models.PositiveIntegerField(
        blank=True,
        default=0,
        help_text="Max Number of Bots in your experience",
        verbose_name="Number Of Bots",
    )
    # todo: migrate this to main-cats, sub-cats usage
    category = models.ForeignKey(
        ExperiencesCategory,
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Choose Main Category",
        related_name="+",
    )
    sub_categories = ParentalManyToManyField(
        "core.SubCategory", blank=True, help_text="Choose Sub Category Category"
    )

    bugged = models.BooleanField(
        default=False,
        null=False,
        help_text="Is the experience bugged",
        verbose_name="Bugged ?",
    )
    first_publish = models.BooleanField(default=True, null=False)

    likes = models.IntegerField(default=0, null=False, help_text="Number of likes")

    content_panels = (
        Page.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel(
                        "featured",
                        classname="full",
                    ),
                    FieldPanel(
                        "trending",
                        classname="full",
                    ),
                    AutocompletePanel("owner", target_model="core.Profile"),
                    FieldPanel("bugged", classname="full"),
                    FieldPanel("description", classname="full"),
                    FieldPanel("likes", classname="full"),
                    FieldPanel("category", widget=forms.RadioSelect),
                    FieldPanel("sub_categories", widget=forms.CheckboxSelectMultiple),
                ],
                heading="Basic Info",
                classname="collapsible",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("code", classname="full"),
                    FieldPanel("exp_url", classname="full"),
                ],
                heading="Sharing Info",
                classname="collapsible",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("tags"),
                    FieldPanel("cover_img_url", classname="full"),
                    FieldPanel("vid_url", classname="full"),
                ],
                heading="Extra Info",
                classname="collapsible",
            ),
            MultiFieldPanel(
                [
                    FieldPanel("no_players", classname="full"),
                    FieldPanel("no_bots", classname="full"),
                ],
                heading="Settings info",
                classname="collapsible",
            ),
        ]
        + [CustomBasePage.content_panels[-1]]
    )

    parent_page_types = ["core.ExperiencesPage"]
    subpage_types = []

    @route(r"^edit/$")
    def edit_page(self, request: HttpRequest):  # noqa: D102
        if request.user.is_authenticated:
            if self.owner == request.user:
                from .views import edit_experience

                return edit_experience(request, self)
            else:
                logger.debug(
                    f"{request.user} tried to edit a experience they dont own exp: {request.path}"
                )
                return HttpResponse("Unauthorized", status=401)
        else:
            return redirect(LOGIN_URL)

    @route(r"^delete/$")
    def delete_experience(self, request: HttpRequest):  # noqa: D102
        if request.user.is_authenticated:
            if self.owner == request.user:
                # todo actually delete it
                print("Delete experience")
                return redirect(request.META["HTTP_REFERER"])
            else:
                logger.debug(
                    f"{request.user} tried to delete a experience they dont own exp: {request.path}"
                )
                return HttpResponse("Unauthorized", status=401)
        else:
            return redirect(LOGIN_URL)

    @staticmethod
    def is_experience_page():  # noqa: D102
        return True


def social_user(discord_id: int):
    """Returns a User object for a discord id"""
    try:
        usr = get_user_model().objects.get(
            id=SocialAccount.objects.get(uid=discord_id).user_id
        )
        return usr
    except ObjectDoesNotExist:
        return False


class Profile(models.Model):
    """Class that tracks extra data about user"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked = models.ManyToManyField(ExperiencePage)
    autocomplete_search_field = "user__username"

    def autocomplete_label(self):
        """Called by Wagtail auto complete to get label for an account"""
        if not self.user.is_superuser:
            discord_data = self.user.socialaccount_set.extra().first().extra_data
            if len(discord_data.get("username", "")):
                return f"{discord_data['username']}#{discord_data['discriminator']} : {discord_data['id']}"
            else:
                return str(self.user)
        else:
            return str(self.user)

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        """Called when a new user is created"""
        if created:
            Profile.objects.create(user=instance)

    @staticmethod
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        """Called when a user data is updated"""
        instance.profile.save()


class ProfilePage(RoutablePageMixin, CustomBasePage):
    """Class representing the details of a user profile page"""

    max_count = 1
    parent_page_types = ["core.HomePage"]
    subpage_types = ["core.BlogPage"]

    def serve(self, request, view=None, args=None, kwargs=None):
        """Checks if a user is authenticated before serving the profile page"""
        if request.user.is_authenticated:
            return super().serve(request, view, args, kwargs)
        else:
            return redirect(LOGIN_URL)

    def get_context(self, request, *args, **kwargs):  # noqa: D102
        list_experiences = kwargs.pop("list_experiences", None)
        user_acc = kwargs.pop("user", None)
        context = super().get_context(request, *args, **kwargs)
        all_posts = (
            ExperiencePage.objects.live()
            .public()
            .filter(owner=user_acc)
            .order_by("-first_published_at")
        )

        if not user_acc:
            user_acc = request.user
        if list_experiences:
            context["posts"] = pagination_wrapper(
                request,
                all_posts,
            )

            logger.debug(f"filtred {len(all_posts)} for {user_acc}")
        context["user"] = request.user
        context["requested_user"] = user_acc
        context["latest_post"] = all_posts.first()
        context["total_num_posts"] = len(all_posts)
        return context

    @route(r"^$")
    def root_profile_page(self, request):  # noqa: D102
        return redirect("/")

    @route(r"^(\d{18})/$", name="discord_id")
    def profile_page_view(self, request: HttpRequest, discord_id):
        """Serves a profile page for a user ID"""
        user = social_user(discord_id)
        if user:
            logger.debug(f"fetch profile for {user}")
            return TemplateResponse(
                request,
                self.get_template(request),
                self.get_context(request, list_experiences=True, user=user),
            )
        else:
            return HttpResponse("Nope", status=404)

    @route(r"(\d{18})/experiences/$", name="discord_id")
    def user_experiences(self, request, discord_id):
        """Servers a list of experiences by a user"""
        user = social_user(discord_id=discord_id)
        if user:
            logger.debug(f"fetch experiences for {user}")
            return TemplateResponse(
                request,
                "core/experiences_page.html",
                self.get_context(request=request, list_experiences=True, user=user),
            )
        else:
            return HttpResponse("User not Found", status=404)


class AvailableTags(models.Model):  # noqa: D101
    tags = models.TextField(
        blank=True, verbose_name="All available tags in BF 2042 Portal Rules editor"
    )
