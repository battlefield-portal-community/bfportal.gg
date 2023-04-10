import enum
import os

import requests
from allauth.socialaccount.models import SocialAccount
from core import get_dashboard_url, get_page_url
from core.forms import ExperiencePageForm
from core.models import ExperiencePage, ExperiencesCategory, ExperiencesPage, HomePage
from core.utils.helper import unique_slug_generator
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from loguru import logger
from taggit.models import Tag


class EnumMeta(enum.EnumMeta):
    """Meta Class that enables `in` operator for Enums"""

    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True


class ReportTypes(enum.Enum, metaclass=EnumMeta):
    """All types of report that can be done for an exp"""

    BUGGED = 0
    BROKEN = 1
    XP_FARM = 2
    OK = 4


def send_approve_request(
    page: ExperiencePage, type: str = "new", request: HttpRequest = None
):
    """Tries to send an approval request embed to the

    discord channel specified by APPROVAL_CHANNEL_WEBHOOK_ID env
    """
    if (token := os.getenv("APPROVAL_CHANNEL_WEBHOOK_TOKEN", None)) is not None:
        webhook_id = os.getenv("APPROVAL_CHANNEL_WEBHOOK_ID", None)
        if webhook_id:
            webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{token}"
            admin_add = False
            uid = -1
            try:
                uid = SocialAccount.objects.get(user_id=page.owner.id).uid
            except SocialAccount.DoesNotExist:
                admin_add = True

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
                                {
                                    "name": "Author",
                                    "value": f"<@{uid}>"
                                    if not admin_add
                                    else "**admin**",
                                    "inline": True,
                                },
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
                            "fields": [
                                {
                                    "name": "By",
                                    "value": f"<@{uid}>"
                                    if not admin_add
                                    else "**admin**",
                                }
                            ],
                        }
                    ],
                }
            else:
                data = {
                    "content": "There is Something Wrong with the server pls check 🤐"
                }

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

            headers = {"Content-Type": "application/json"}
            result = requests.post(webhook_url, json=data, headers=headers)
            try:
                result.raise_for_status()
            except requests.exceptions.HTTPError as err:
                logger.debug(
                    f"Error {err} while sending approve request for {page.title}"
                )
                print(result.content)
            else:
                logger.debug(
                    f"{type.capitalize()} Experience request for {page.title} sent successfully "
                )
        else:
            logger.warning(
                "Unable to send Approval request to discord as APPROVAL_CHANNEL_WEBHOOK_ID is not set"
            )
    else:
        logger.warning(
            "Unable to send Approval request to discord as APPROVAL_CHANNEL_WEBHOOK_TOKEN is not set"
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
            new_exp_page.owner = request.user
            new_exp: ExperiencePage = ExperiencesPage.objects.all()[0].add_child(
                instance=new_exp_page
            )
            user_model = get_user_model()
            for pk in form.cleaned_data["creators"]:
                new_exp.creators.add(user_model.objects.get(pk=pk))

            for pk in form.cleaned_data["tags"]:
                new_exp.tags.add(Tag.objects.get(pk=pk))

            for sub_cat in form.cleaned_data["sub_categories"]:
                new_exp.sub_categories.add(sub_cat)

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

    return render(
        request,
        "core/submit_experience_page.html",
        {
            "form": form,
            "page": {
                "title": "Submit Experience",
                "description": "Submit your Experience on https://bfportal.gg/",
            },
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

            logger.debug(form.cleaned_data)
            experience_page.creators.clear()
            experience_page.tags.clear()

            user_model = get_user_model()
            for pk in form.cleaned_data["creators"]:
                experience_page.creators.add(user_model.objects.get(pk=pk))
            for pk in form.cleaned_data["tags"]:
                experience_page.tags.add(Tag.objects.get(pk=pk))

            # logger.debug(form.cleaned_data['tags'])

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
                {
                    "form": form,
                    "is_edit": True,
                    "disable_preview_embed": True,
                },
            )
    else:
        form = ExperiencePageForm(
            initial={
                "sub_categories": [
                    cat.pk for cat in experience_page.sub_categories.all()
                ],
                "description": experience_page.description,
            },
            instance=experience_page,
        )
        return render(
            request,
            "core/submit_experience_page.html",
            {
                "form": form,
                "is_edit": True,
                "disable_preview_embed": True,
            },
        )


# to sort tags based on how many times its used
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
            user.profile.add_liked_page(page)
        else:
            user.profile.remove_liked_page(page)
        user.save()
        page.save()
        return HttpResponse(f"{page.liked_by.all().count()}", status=201)
    except ExperiencePage.DoesNotExist:
        return HttpResponse("experience does not exits", status=404)


@login_required
def report_experience(request: HttpRequest, report_type: int):
    """View that handles reporting of EXP"""
    if request.method == "POST":
        try:
            report_type = ReportTypes(int(report_type))
            if report_type in ReportTypes:
                if page_id := request.GET.get("id", None):
                    try:
                        exp_page = ExperiencePage.objects.get(id=int(page_id))
                    except ExperiencePage.DoesNotExist:
                        logger.debug(f"Wrong page id {page_id}")
                        return HttpResponse(status=400)
                    save_page = True
                    response_text = "Reported Successfully"
                    match report_type:
                        case ReportTypes.OK:
                            if exp_page.owner == request.user:
                                exp_page.bugged = False
                                exp_page.broken = False
                                exp_page.save_revision(
                                    user=request.user,
                                    submitted_for_moderation=True,
                                    changed=True,
                                )
                                return HttpResponse("Awaiting approval", status=200)
                            else:
                                return HttpResponse(
                                    "Nice try... reported :)", status=404
                                )

                        case ReportTypes.BUGGED:
                            if exp_page.owner == request.user:
                                exp_page.bugged = True
                                response_text = "State Change Successful"
                            else:
                                exp_page.bugged_report.add(request.user)

                        case ReportTypes.BROKEN:
                            if exp_page.owner == request.user:
                                exp_page.broken = True
                                response_text = "State Change Successful"
                            else:
                                exp_page.broken_report.add(request.user)

                        case ReportTypes.XP_FARM:
                            exp_page.xp_farm_report.add(request.user)

                    if save_page:
                        exp_page.save()
                    return HttpResponse(response_text, status=200)
                else:
                    logger.debug(f"Wrong page id {page_id}")
                    return HttpResponse(status=400)
            else:
                raise ValueError()
        except ValueError:
            logger.debug(f"{report_type} not valid report type")
            return HttpResponse(status=404)
    else:
        return HttpResponse(404)


def events_view(request: HttpRequest):
    """Handles /events page"""
    return render(
        request,
        "502.html",
    )
