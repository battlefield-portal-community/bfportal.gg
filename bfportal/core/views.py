import datetime
import os

import requests
from allauth.socialaccount.models import SocialAccount
from core.forms import ExperiencePageForm
from core.models import ExperiencePage, ExperiencesCategory, ExperiencesPage, HomePage
from core.utils.helper import unique_slug_generator
from dal import autocomplete
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils import timezone
from loguru import logger
from taggit.models import Tag


def send_approve_request(page: ExperiencePage, type: str = "new"):
    logger.debug("send_approve_request called")
    if (token := os.getenv("APPROVAL_CHANNEL_WEBHOOK_TOKEN", None)) is not None:
        webhook_id = os.getenv("APPROVAL_CHANNEL_WEBHOOK_ID")
        webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{token}"
        uid = SocialAccount.objects.get(user_id=page.owner.id).uid
        data = dict()
        if type == "new":
            data = {
                "content": "New Experience approve request",
                "embeds": [
                    {
                        "url": page.full_url,
                        "title": page.title,
                        "description": page.description[0:200] + ".....",
                        "image": {
                            "url": page.cover_img_url
                            if page.cover_img_url
                            else "https://super-static-assets.s3.amazonaws.com/19d9fbc6-6292-4be8-ac70-5a186b556054%2Fimages%2Fb6495922-b4c7-4002-9c3d-56bfaa5b98b5.jpg"
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
                                + "\u200B".join(
                                    [str(i) for i in page.categories.all()]
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
                        "url": page.full_url,
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
                        "url": page.full_url,
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
    if request.method == "POST":
        form = ExperiencePageForm(request.POST)
        if form.is_valid():
            logger.debug(f"Saving new exp {form.cleaned_data}")
            new_exp_page: ExperiencePage = form.save(commit=False)
            new_exp_page.slug = unique_slug_generator(new_exp_page)
            new_exp_page.tags.add(*form.cleaned_data["tags"])
            selected = form.cleaned_data["categories"]
            if selected:
                new_exp_page.categories.clear()
                for cat in selected:
                    new_exp_page.categories.add(cat)
            new_exp_page.owner = request.user
            new_exp: ExperiencePage = ExperiencesPage.objects.all()[0].add_child(
                instance=new_exp_page
            )
            if new_exp:
                new_exp.unpublish()
                new_exp.save_revision(submitted_for_moderation=True, user=request.user)
                new_exp.first_published_at = timezone.now()
                new_exp.save()
                send_approve_request(new_exp, "new")
            return render(
                request, "core/after_submit.html", {"exp_name": new_exp.title}
            )

    else:
        form = ExperiencePageForm()

    return render(
        request,
        "core/submit_experience_page.html",
        {
            "form": form,
        },
    )


@login_required
def edit_experience(request: HttpRequest, experience_page: ExperiencePage):
    if request.method == "POST":
        form = ExperiencePageForm(request.POST, instance=experience_page)
        if form.is_valid():
            selected = form.cleaned_data["categories"]
            if selected:
                experience_page.categories.clear()
                for cat in selected:
                    experience_page.categories.add(cat)
            experience_page.save_revision(
                submitted_for_moderation=True, user=request.user, changed=True
            )
            send_approve_request(experience_page, "edit")
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


class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = ExperiencesCategory.objects.all().order_by("id")
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs


class TagsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tag.objects.all().order_by("id")
        if self.q:
            qs = qs.filter(name__istartswith=self.q)
            return qs
        return qs[0:10]
