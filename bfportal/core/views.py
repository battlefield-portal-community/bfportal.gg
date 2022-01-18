from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.views.generic import TemplateView


from wagtail.core.models import Page
from loguru import logger

from core.forms import ExperiencePageForm
from core.models import ExperiencePage, HomePage


@login_required
def sumbit_experience(request: HttpRequest, home_page: HomePage):
    if request.method == 'POST':
        form = ExperiencePageForm(request.POST)
        if form.is_valid():
            logger.debug(f"Saving new exp {form.cleaned_data}")
            new_exp_page : ExperiencePage = form.save(commit=False)
            new_exp_page.slug = slugify(new_exp_page.title)
            new_exp_page.tags.add(*form.cleaned_data['tags'])
            new_exp_page.owner = request.user
            new_exp: ExperiencePage = home_page.get_first_child().add_child(instance=new_exp_page)
            if new_exp:
                new_exp.unpublish()
                new_exp.save_revision(submitted_for_moderation=True, user=request.user)
            return render(request, 'core/after_submit.html', {'exp_name': new_exp.title})

    else:
        form = ExperiencePageForm()

    return render(request, 'core/submit_experience_page.html', {
        'form': form,
    })

@login_required
def edit_experience(request: HttpRequest, experience_page: ExperiencePage):
    if request.method == 'POST':
        form = ExperiencePageForm(request.POST, instance=experience_page)
        if form.is_valid():
            experience_page.save_revision(submitted_for_moderation=True, user=request.user, changed=True)            
            return render(request, 'core/after_submit.html', {'exp_name': experience_page.title})
    else:
        return render(
            request,
            "core/submit_experience_page.html",
            {'form': ExperiencePageForm(instance=experience_page)}
        )


