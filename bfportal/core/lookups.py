from ajax_select import LookupChannel, register
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest


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
        if social_account := obj.socialaccount_set.first():
            extra_data = social_account.extra_data
            return (
                "<span class='tag'>%s</span>"
                % f"{extra_data['username']}#{extra_data['discriminator']} : {extra_data['id']}"
            )

    def check_auth(self, request: HttpRequest):
        """Allow anyone that is logged in to submit exp"""
        if not request.user.is_authenticated:
            raise PermissionDenied
