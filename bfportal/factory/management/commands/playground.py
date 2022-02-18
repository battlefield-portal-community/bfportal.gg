from django.core.management import BaseCommand

from allauth.socialaccount.models import SocialAccount
from core.models import ExperiencePage
import requests
from loguru import logger


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("pass")
