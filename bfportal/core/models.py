from django.db import models
from django.template.response import TemplateResponse
from django.shortcuts import render

from wagtail.core.models import Page
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from taggit.models import TaggedItemBase

from modelcluster.models import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from allauth.socialaccount.models import SocialAccount

from loguru import logger


class HomePage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ['wagtailcore.Page']
    subpage_types = ['core.ExperiencesPage']

    @route(r'^$')
    def base(self, request):
        return TemplateResponse(
            request,
            self.get_template(request),
            self.get_context(request)
        )
    
    @route(r'^submit/$')
    def submit_exp(self, request):
        from core.views import sumbit_experience
        return sumbit_experience(request, self)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context['posts'] = ExperiencePage.objects.live().public().order_by('-first_published_at')
        if request.user.is_authenticated:
            context['social_user'] = SocialAccount.objects.get(user=request.user)
        return context


class ExperiencePageTag(TaggedItemBase):
    content_object  = ParentalKey(
        'ExperiencePage',
        related_name='tagged_items',
        on_delete=models.CASCADE,
    )


class ExperiencesPage(RoutablePageMixin, Page):
    max_count = 1
    parent_page_types = ['core.HomePage']
    subpage_types = ['core.ExperiencePage']

    def get_context(self, request, *args, **kwargs):
        """Adding custom stuff to our context."""
        context = super().get_context(request, *args, **kwargs)
        # Get all posts
        all_posts = ExperiencePage.objects.live().public().order_by('-first_published_at')

        if request.GET.get('tag', None):
            tags = request.GET.get('tag')
            all_posts = all_posts.filter(tags__slug__in=[tags])
            logger.debug(f"Filted {len(all_posts)} experiences by tags {tags}")

        context["posts"] = all_posts
        return context


class ExperiencePage(Page):
    description = models.TextField(default='', help_text="Description of Your experience")

    code = models.CharField(blank=True, max_length=6, default='', help_text="Six letter alpha-numeric code of you experience")
    exp_url = models.URLField(blank=True, default='', help_text="Url of your experience")
    
    tags = ClusterTaggableManager(blank=True, help_text="Some tags", through=ExperiencePageTag)
    vid_url = models.URLField(blank=True, default='', help_text="Link to vid showcasing your experience")
    cover_img_url = models.URLField(blank=True, default='', help_text="Link for your cover Image")
    
    no_players = models.IntegerField(blank=True, default=-1, help_text="Max Number of Human Players in your experience")
    no_bots = models.IntegerField(blank=True, default=-1, help_text="Max Number of Bots in your experience")

    
    content_panels = Page.content_panels + [
        FieldPanel('description', classname='full'),

        FieldPanel('code', classname='full'),
        FieldPanel('exp_url', classname='full'),

        FieldPanel('tags'),
        FieldPanel('cover_img_url', classname='full'),
        FieldPanel('vid_url', classname='full'),

        FieldPanel('no_players', classname='full'),
        FieldPanel('no_bots', classname='full'),
    ]

    parent_page_types =  ['core.ExperiencesPage']

    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             name="%(app_label)s_%(class)s_code_or_exp_url",
    #             check=(
    #                 models.Q(code__isnull=True, exp_url__isnull=False)
    #                 | models.Q(code__isnull=False, exp_url__isnull=True)
    #             ),
    #         )
    #     ]