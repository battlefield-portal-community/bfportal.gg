from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.views.generic import TemplateView
from wagtail.core.models import Page

from loguru import logger

from core.forms import ExperiencePageForm
from core.models import ExperiencePage


@login_required
def sumbit_experience(request, index_page: Page):
    if request.method == 'POST':
        form = ExperiencePageForm(request.POST)
        if form.is_valid():
            logger.debug(f"Saving new exp {form.cleaned_data}")
            new_exp_page : ExperiencePage = form.save(commit=False)
            new_exp_page.slug = slugify(new_exp_page.name)
            new_exp_page.title = new_exp_page.name
            new_exp: ExperiencePage = index_page.add_child(instance=new_exp_page)
            if new_exp:
                new_exp.unpublish()
                new_exp.save_revision(submitted_for_moderation=True, user=request.user)
            return render(request, 'core/after_submit.html', {'exp_name': new_exp.name})

    else:
        form = ExperiencePageForm()

    return render(request, 'core/submit_experience_page.html', {
        'form': form,
    })

