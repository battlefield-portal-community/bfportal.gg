import os

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import Count, Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from loguru import logger
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

from bfportal.settings.base import LOGIN_URL

from .experience import ExperiencePage
from .helper import pagination_wrapper
from .pages import CustomBasePage


def social_user(discord_id: int) -> User | bool:
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
    liked = models.ManyToManyField(ExperiencePage, blank=True)
    is_mock_user = models.BooleanField(
        default=False,
        null=False,
        help_text="If set to true, this user was created by the mock command, and is a fake user",
    )
    hide_username = models.BooleanField(
        default=False,
        null=False,
        help_text="If set to true hides the username on the website",
    )
    autocomplete_search_field = "user__username"

    panels = [FieldPanel("hide_username")]

    def __str__(self):
        return self.user.username

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

    def add_liked_page(self, experience_page: ExperiencePage):
        """Adds a ExperiencePage to `self.liked`, and adds self to `ExperiencePage.liked_by`

        Does not call the `save` function.
        """
        self.liked.add(experience_page)
        experience_page.liked_by.add(self)

    def remove_liked_page(self, experience_page: ExperiencePage):
        """Removes a `ExperiencePage` from `self.liked`, and removes self from page's `liked_by`

        Does not call the `save` function.
        """
        self.liked.remove(experience_page)
        experience_page.liked_by.remove(self)

    @staticmethod
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance: User, created, **kwargs):
        """Called when a new user is created"""
        if created:
            if (group := Group.objects.filter(name="self edit")).exists():
                instance.groups.add(group[0])
            Profile.objects.create(user=instance)

    @staticmethod
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        """Called when a user data is updated"""
        if (
            profile := getattr(instance, "profile", None)
        ) is None:  # is case a user with no profile tries to log in.
            profile = Profile.objects.create(user=instance)
        profile.save()


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
            .filter(Q(owner=user_acc) | Q(creators=user_acc))
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
        context["earned_likes"] = sum(all_posts.aggregate(Count("liked_by")).values())
        context["owners"] = os.getenv("OWNERS", "").split(",")
        return context

    @route(r"^$")
    def root_profile_page(self, request):  # noqa: D102
        return redirect("/")

    @route(r"^(\d{18,})/$", name="discord_id")
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

    @route(r"(\d{18,})/experiences/$", name="discord_id")
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
            return TemplateResponse(request, "404.html", status=404)

    @route(r"(\d{18,})/liked/$", name="discord_id")
    def user_liked_experiences(self, request, discord_id):
        """Servers a list of experiences by a user"""
        user = social_user(discord_id=discord_id)
        if user:
            return TemplateResponse(
                request,
                "core/experiences_page.html",
                {"posts": user.profile.liked.all()},
            )
        else:
            return TemplateResponse(request, "404.html", status=404)

    @route(r"^(\w+)/$", name="username")
    def named_profile_page_view(self, request: HttpRequest, username):
        """Handles the requests for users that have a named profile"""
        if username == "admin":
            return TemplateResponse(
                request,
                self.get_template(request),
                self.get_context(
                    request,
                    list_experiences=True,
                    user=User.objects.filter(is_superuser=True).first(),
                ),
            )
        else:
            return TemplateResponse(request, "404.html", status=404)
