from ajax_select import LookupChannel, register
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from taggit.models import Tag


@register("DiscordUsers")
class DiscordUsersLookup(LookupChannel):
    """LookupChannel for selecting creators on submit exp page"""

    model: User = get_user_model()

    def get_query(self, q, request):
        """Returns all users that contains `q` in their username"""
        return self.model.objects.filter(username__icontains=q).order_by("username")[
            :10
        ]

    def format_item_display(self, obj: User):
        """Controls how a selected user looks on the submit exp page"""
        user_name = obj.username
        if social_account := obj.socialaccount_set.first():
            user_name = social_account.extra_data["username"]

        return f"<span class='text-white w-max text-sm font-medium'>@{user_name}</span>"

    def format_match(self, obj):
        """Controls how an item is displayed in the autocomplete menu"""
        if social_account := obj.socialaccount_set.first():
            extra_data = social_account.extra_data
            return (
                "<span>%s</span>"
                % f"{extra_data['username']}#{extra_data['discriminator']} : {extra_data['id']}"
            )
        return "<span>%s</span>" % obj.username

    def check_auth(self, request: HttpRequest):
        """Allow anyone that is logged in to submit exp"""
        if not request.user.is_authenticated:
            raise PermissionDenied


@register("tags")
class TagsLookup(LookupChannel):
    """LookupChannel for selecting tags on submit exp page"""

    model = Tag

    def get_query(self, q, request):
        """Returns all tags that contains `q` in their name"""
        return self.model.objects.filter(name__istartswith=q)[:5]

    def format_item_display(self, obj: Tag):
        """Controls how a selected tag looks on the submit exp page"""
        return f"<span class='text-white w-max text-sm font-medium'>{obj.name}</span>"

    def format_match(self, obj):
        """Controls how an item is displayed in the autocomplete menu"""
        return "<span>%s</span>" % obj.name

    def check_auth(self, request: HttpRequest):
        """Allow anyone that is logged in to submit exp"""
        if not request.user.is_authenticated:
            raise PermissionDenied
