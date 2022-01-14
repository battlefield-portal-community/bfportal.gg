from django.shortcuts import render
from wagtail.core.models import Page

from core.forms import ExperiencePageForm
from core.models import ExperiencePage, IndexPage



def sumbit_experience(request):
    if request.method == 'POST':
        form = ExperiencePageForm(request.POST)
        if form.is_valid():
            new_exp = ExperiencePage(
                title = form.cleaned_data['name'],
                name = form.cleaned_data['name'],
                code = form.cleaned_data['code'],
                exp_url = form.cleaned_data['exp_url'],
                vid_url = form.cleaned_data['vid_url'],
                cover_img_url = form.cleaned_data['cover_img_url'],
                description = form.cleaned_data['description'],
                no_players = form.cleaned_data['no_players'],
                no_bots = form.cleaned_data['no_bots'],
            )
            IndexPage.objects.first().add_child(instance=new_exp)
            

    else:
        form = ExperiencePageForm()

    return render(request, 'core/submit_experience_page.html', {
        'form': form,
    })
