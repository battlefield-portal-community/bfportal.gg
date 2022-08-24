from core.models import (
    ExperiencesCategory,
    ExperiencesPage,
    HomePage,
    Profile,
    ProfilePage,
)
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from loguru import logger
from wagtail.core.models import Page, Site


class Command(BaseCommand):
    """A command to initialize and ensure defaults for the whole app"""

    help = "Makes sure that the database is initialized and base pages and user groups are made"

    def handle(self, *args, **options):
        """Handler for Command"""
        if len(HomePage.objects.all()) == 0:
            logger.info("Init New Website")
            logger.info("Adding and setting new root page")
            site = Site.objects.last()
            root = Page.objects.get(id=1).specific
            new_home_page = HomePage(title="BF Portal Library", slug="bfportal-library")
            root.add_child(instance=new_home_page)
            site.root_page = new_home_page
            site.save()
            logger.info("setting new root page Successful")
            logger.info("Adding Sub-Page types")
            profile_page = ProfilePage(title="Profile page", slug="users")
            experiences_listing_page = ExperiencesPage(
                title="Experiences", slug="experiences"
            )
            new_home_page.add_child(instance=experiences_listing_page)
            new_home_page.add_child(instance=profile_page)
            new_home_page.save()
            logger.info("Adding Sub-Page types Successful")
        if len(ExperiencesCategory.objects.all()) == 0:
            logger.info("Adding Experience Categories")
            cat_names = ["Prefab", "Jam", "Multiplayer", "Solo"]
            for cat in cat_names:
                cat_obj = ExperiencesCategory(name=cat)
                cat_obj.save()
            logger.info("Adding Experience Categories Successful")

        for user in User.objects.all():
            if not hasattr(user, "profile"):
                user.profile = Profile()
                user.save()
