from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from langcorrect.corrections.tests.factories import PerfectRowFactory
from langcorrect.posts.tests.factories import PostFactory
from langcorrect.prompts.tests.factories import PromptFactory
from langcorrect.users.tests.factories import UserFactory

User = get_user_model()


class Command(BaseCommand):
    help = "Sets up mock data for the project"

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=100, help="Number of users to create")
        parser.add_argument("--posts", type=int, default=400, help="Number of posts to create")
        parser.add_argument("--prompts", type=int, default=10, help="Number of prompts to create")

    def handle(self, *args, **options):
        try:
            user_count = options.get("users")
            post_count = options.get("posts")
            prompt_count = options.get("prompts")

            self.run_migrations()
            self.install_fixtures()
            self.create_admin_users()
            self.create_premium_users()
            self.create_normal_users()

            self.generate_users(user_count)
            self.generate_posts(post_count)
            self.generate_prompts(prompt_count)
            self.generate_corrections()

            self.stdout.write(
                self.style.SUCCESS(
                    f"""Successfully set up mock data:
                        - {user_count} users
                        - {post_count} posts
                        - {prompt_count} prompts created.
                    """
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
            raise CommandError("Failed to set up mock data.") from e

    def run_migrations(self):
        self.stdout.write(self.style.SUCCESS("Running migrations..."))
        call_command("migrate")
        self.stdout.write(self.style.SUCCESS("Migrations completed."))

    def install_fixtures(self):
        self.stdout.write(self.style.SUCCESS("Installing fixtures..."))
        call_command("loaddata", "fixtures/tests/languages.json")
        self.stdout.write(self.style.SUCCESS("Finished installing fixtures."))

    def create_admin_users(self):
        self.stdout.write(self.style.SUCCESS("Creating admin user..."))
        UserFactory.create(
            username="admin",
            password="password",
            email="admin@dundermifflin.com",
            is_superuser=True,
            is_staff=True,
            verify_email_address=True,
        )
        self.stdout.write(self.style.SUCCESS("Finished creating admin user."))

    def create_premium_users(self):
        self.stdout.write(self.style.WARNING("Skipping create_premium_users as it is not implemented."))
        pass

    def create_normal_users(self):
        self.stdout.write(self.style.SUCCESS("Creating normal user..."))
        UserFactory.create(username="jim", password="password", email="jim@example.com", verify_email_address=True)
        UserFactory.create(username="pam", password="password", email="pam@example.com", verify_email_address=True)
        UserFactory.create(
            username="dwight", password="password", email="dwight@example.com", verify_email_address=True
        )
        self.stdout.write(self.style.SUCCESS("Finished creating normal user."))

    def generate_users(self, user_count):
        self.stdout.write(self.style.SUCCESS(f"Generating {user_count} users..."))
        UserFactory.create_batch(user_count, password="password", verify_email_address=True)
        self.stdout.write(self.style.SUCCESS("Finished creating users."))

    def generate_prompts(self, prompt_count):
        self.stdout.write(self.style.SUCCESS(f"Generating {prompt_count} prompts..."))
        PromptFactory.create_batch(prompt_count, max_posts=4)
        self.stdout.write(self.style.SUCCESS("Finished creating prompts."))

    def generate_posts(self, post_count):
        self.stdout.write(self.style.SUCCESS(f"Generating {post_count} posts..."))
        PostFactory.create_batch(post_count)
        self.stdout.write(self.style.SUCCESS("Finished creating posts."))

    def generate_corrections(self):
        self.stdout.write(self.style.SUCCESS("Generating perfect sentences..."))
        PerfectRowFactory.create_batch(50)
        self.stdout.write(self.style.SUCCESS("Finished generating perfect sentences."))
