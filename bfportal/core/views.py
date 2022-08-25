import os

import requests
from allauth.socialaccount.models import SocialAccount
from core import get_dashboard_url, get_page_url
from core.forms import ExperiencePageForm
from core.models import ExperiencePage, ExperiencesCategory, ExperiencesPage, HomePage
from core.utils.helper import unique_slug_generator
from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.utils import timezone
from loguru import logger
from taggit.models import Tag


def send_approve_request(
    page: ExperiencePage, type: str = "new", request: HttpRequest = None
):
    """Tries to send an approval request embed to the

    discord channel specified by APPROVAL_CHANNEL_WEBHOOK_ID env
    """
    if (token := os.getenv("APPROVAL_CHANNEL_WEBHOOK_TOKEN", None)) is not None:
        webhook_id = os.getenv("APPROVAL_CHANNEL_WEBHOOK_ID")
        webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{token}"
        uid = SocialAccount.objects.get(user_id=page.owner.id).uid
        logger.debug("Trying to send approve request")
        url = get_page_url(request, page)
        if type == "new":
            data = {
                "content": "New Experience approve request",
                "embeds": [
                    {
                        "url": url,
                        "title": page.title,
                        "description": page.description[0:200] + ".....",
                        "image": {
                            "url": page.cover_img_url
                            if page.cover_img_url
                            else "https://super-static-assets.s3.amazonaws.com/19d9fbc6-6292-4be8-ac70-5a186b556054%2Fimages%2Fb6495922-b4c7-4002-9c3d-56bfaa5b98b5.jpg"  # noqa: E501
                        },
                        "fields": [
                            {"name": "Author", "value": f"<@{uid}>", "inline": True},
                            {
                                "name": "Submitted on",
                                "value": f"<t:{int(page.first_published_at.timestamp())}>",
                                "inline": True,
                            },
                            {
                                "name": "Featured",
                                "value": ":white_check_mark:"
                                if page.featured
                                else ":x:",
                                "inline": True,
                            },
                            {
                                "name": "Category",
                                "value": ":white_small_square: "
                                + f"\u200B{page.category}",
                            },
                            {
                                "name": "Sub Categories",
                                "value": ":white_small_square: "
                                + "".join(
                                    [f"`{i}` " for i in page.sub_categories.all()]
                                ),
                            },
                            {
                                "name": "Tags",
                                "value": ":white_small_square: "
                                + "".join([f"`{i}` " for i in page.tags.all()]),
                            },
                        ],
                    }
                ],
            }
        elif type == "edit":
            data = {
                "content": "Request to make Changes to a Experience",
                "embeds": [
                    {
                        "url": url,
                        "title": page.title,
                        "fields": [{"name": "By", "value": f"<@{uid}>"}],
                    }
                ],
            }
        else:
            data = {"content": "There is Something Wrong with the server pls check 🤐"}

        data["token"] = token
        data["components"] = [
            {
                "type": 1,
                "components": [
                    {
                        "type": 2,
                        "style": 5,
                        "url": get_dashboard_url(request, page),
                        "label": "Go to Dashboard",
                    }
                ],
            }
        ]

        print(data)
        headers = {"Content-Type": "application/json"}
        result = requests.post(webhook_url, json=data, headers=headers)
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.debug(f"Error {err} while sending approve request for {page.title}")
            print(result.content)
        else:
            logger.debug(
                f"{type.capitalize()} Experience request for {page.title} sent successfully "
            )


@login_required
def submit_experience(request: HttpRequest, home_page: HomePage):
    """Called when a user submits an experience

    This function handles the routing on successful submission
    """
    if request.method == "POST":
        form = ExperiencePageForm(request.POST)
        if form.is_valid():
            logger.debug(f"Saving new exp {form.cleaned_data}")
            new_exp_page: ExperiencePage = form.save(commit=False)
            new_exp_page.slug = unique_slug_generator(new_exp_page)
            new_exp_page.tags.add(*form.cleaned_data["tags"])
            new_exp_page.category = form.cleaned_data["category"]
            new_exp_page.owner = request.user
            new_exp: ExperiencePage = ExperiencesPage.objects.all()[0].add_child(
                instance=new_exp_page
            )
            for cats in form.cleaned_data["sub_categories"]:
                new_exp_page.sub_categories.add(cats)
            if new_exp:
                new_exp.unpublish()
                new_exp.save_revision(submitted_for_moderation=True, user=request.user)
                new_exp.first_published_at = timezone.now()
                new_exp.save()
                send_approve_request(new_exp, "new", request)
            return render(
                request, "core/after_submit.html", {"exp_name": new_exp.title}
            )

    else:
        form = ExperiencePageForm()
        form.fields[
            "cover_img_url"
        ].initial = (
            f"{request.scheme}://{request.get_host()}{static('images/placeholder.png')}"
        )

    return render(
        request,
        "core/submit_experience_page.html",
        {
            "form": form,
        },
    )


@login_required
def edit_experience(request: HttpRequest, experience_page: ExperiencePage):
    """Called when a user tries to edit an experience

    handles the routing when a successful edit is done
    """
    if request.method == "POST":
        form = ExperiencePageForm(request.POST, instance=experience_page)
        if form.is_valid():
            experience_page.save_revision(
                submitted_for_moderation=True, user=request.user, changed=True
            )
            send_approve_request(experience_page, "edit", request)
            return render(
                request,
                "core/after_submit.html",
                {"exp_name": experience_page.title, "after_edit": True},
            )
        else:
            return render(
                request,
                "core/submit_experience_page.html",
                {"form": form, "is_edit": True},
            )
    else:
        return render(
            request,
            "core/submit_experience_page.html",
            {"form": ExperiencePageForm(instance=experience_page), "is_edit": True},
        )


# to sort tags based on how many time its used
# >>> a = ExperiencePageTag.objects.values_list('tag_id').annotate(tag_count=Count('tag_id')).order_by('-tag_count')
# >>> [Tag.objects.get(id=i[0]) for i in a]


def filter_startswith(
    model, starts_with_value: str = None, order_by: str = "id", max_count: int = None
) -> list:
    """Filters objects of a Model

    returns all in DB if no starts_with_value
    else returns the values whose name starts with starts_with_value
    """
    qs = model.objects.all().order_by(order_by)
    if starts_with_value:
        qs = qs.filter(name__istartswith=starts_with_value)
        return qs
    return qs[0:max_count]


class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    """Used by filter API to get all categories"""

    def get_queryset(self):
        """Returns all the Categories that match the condition"""
        return filter_startswith(ExperiencesCategory, self.q)


class TagsAutocomplete(autocomplete.Select2QuerySetView):
    """Used by filter API to get all tags starting with some value"""

    def get_queryset(self):
        """Returns all the tags that match the condition"""
        return filter_startswith(Tag, self.q, max_count=10)


@login_required
def handle_like_request(request: HttpRequest, page_id):
    """favorite/un-favorite"""
    try:
        page = ExperiencePage.objects.get(id=page_id)
        user = request.user
        user_fav = user.profile.liked
        if page not in user_fav.all():
            user_fav.add(page)
            page.likes += 1
        else:
            user_fav.remove(page)
            page.likes -= 1
        user.save()
        page.save()
        return HttpResponse(f"{page.likes}", status=201)
    except ExperiencePage.DoesNotExist:
        return HttpResponse("experience does not exits", status=404)
