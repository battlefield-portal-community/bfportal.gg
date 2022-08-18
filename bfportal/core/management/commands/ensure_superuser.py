from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to make a super-user from commandline

    Super-user is only created when there is none present
    """

    help = "Creates an admin user non-interactively if it doesn't exist"

    def add_arguments(self, parser):
        """Adds agrs for command"""
        parser.add_argument("--username", help="Admin's username")
        parser.add_argument("--email", help="Admin's email")
        parser.add_argument("--password", help="Admin's password")

    def handle(self, *args, **options):
        """Handler for Command"""
        user = get_user_model()
        if not user.objects.filter(username=options["username"]).exists():
            user.objects.create_superuser(
                username=options["username"],
                email=options["email"],
                password=options["password"],
            )
