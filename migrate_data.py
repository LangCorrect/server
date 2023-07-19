import json
import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from taggit.models import Tag  # noqa: E402

from langcorrect.challenges.models import Challenge  # noqa: E402
from langcorrect.languages.models import Language, LanguageLevel  # noqa: E402
from langcorrect.prompts.models import Prompt  # noqa: E402

User = get_user_model()


def migrate_users():
    print("Migrating users...")

    with open("./temp_data/profile_data.json") as file:
        data = json.load(file)

    user_objects = []

    for entry in data:
        pk = entry["pk"]
        password = entry["fields"]["password"]
        last_login = entry["fields"]["last_login"]
        is_superuser = entry["fields"]["is_superuser"]
        username = entry["fields"]["username"]
        first_name = entry["fields"]["first_name"]
        last_name = entry["fields"]["last_name"]
        email = entry["fields"]["email"]
        is_staff = entry["fields"]["is_staff"]
        is_active = entry["fields"]["is_active"]
        date_joined = entry["fields"]["date_joined"]
        gender = entry["fields"]["gender"]
        nick_name = entry["fields"]["nick_name"]
        bio = entry["fields"]["bio"]
        staff_notes = entry["fields"]["staff_notes"]
        is_volunteer = entry["fields"]["is_volunteer"]
        is_premium = entry["fields"]["is_premium"]
        is_moderator = entry["fields"]["is_moderator"]
        is_lifetime_vip = entry["fields"]["is_lifetime_vip"]
        is_max_studying = entry["fields"]["is_max_studying"]

        user_objects.append(
            User(
                pk=pk,
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                bio=bio,
                date_joined=date_joined,
                last_login=last_login,
                is_superuser=is_superuser,
                is_staff=is_staff,
                is_active=is_active,
                nick_name=nick_name,
                staff_notes=staff_notes,
                is_volunteer=is_volunteer,
                is_premium=is_premium,
                is_moderator=is_moderator,
                is_lifetime_vip=is_lifetime_vip,
                is_max_studying=is_max_studying,
            )
        )

    User.objects.bulk_create(user_objects)


def migrate_languages():
    print("migrating languages...")

    with open("./temp_data/language_data.json") as file:
        data = json.load(file)

    lang_objects = []

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        en_name = entry["fields"]["en_name"]
        code = entry["fields"]["code"]
        family_code = entry["fields"]["family_code"]
        lang_objects.append(
            Language(pk=pk, created=created, modified=modified, en_name=en_name, code=code, family_code=family_code)
        )

    Language.objects.bulk_create(lang_objects)


def migrate_language_levels():
    print("migrating language levels...")

    with open("./temp_data/language_levels_data.json") as file:
        data = json.load(file)

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        user_pk = entry["fields"]["user"]
        language_pk = entry["fields"]["language"]
        level = entry["fields"]["level"]

        LanguageLevel.objects.create(
            pk=pk,
            created=created,
            modified=modified,
            user=User.objects.get(pk=user_pk),
            language=Language.objects.get(pk=language_pk),
            level=level,
        )


def migrate_challenges():
    print("migrating challenges...")

    with open("./temp_data/challenge_data.json") as file:
        data = json.load(file)

    chal_objects = []

    for entry in data:
        pk = entry["pk"]
        start_date = entry["fields"]["start_date"]
        end_date = entry["fields"]["end_date"]
        title = entry["fields"]["title"]
        description = entry["fields"]["description"]
        url = entry["fields"]["url"]
        slug = entry["fields"]["slug"]
        is_active = entry["fields"]["is_active"]

        chal_objects.append(
            Challenge(
                pk=pk,
                start_date=start_date,
                end_date=end_date,
                title=title,
                description=description,
                url=url,
                slug=slug,
                is_active=is_active,
            )
        )

    Challenge.objects.bulk_create(chal_objects)


def migrate_prompts():
    print("migrating prompts...")

    with open("./temp_data/prompt_data.json") as file:
        data = json.load(file)

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["updated"]
        user_pk = entry["fields"]["user"]
        content = entry["fields"]["content"]
        difficulty_level = entry["fields"]["difficulty_level"]
        language_pk = entry["fields"]["language"]
        slug = entry["fields"]["slug"]
        chal_pk = entry["fields"]["challenge"]
        tag_ids = entry["fields"]["tag_ids"]

        prompt = Prompt.objects.create(
            pk=pk,
            created=created,
            modified=modified,
            user=User.objects.get(pk=user_pk),
            content=content,
            difficulty_level=difficulty_level,
            language=Language.objects.get(pk=language_pk),
            slug=slug,
            challenge=Challenge.objects.get(pk=chal_pk) if chal_pk else None,
        )

        for tag_id in tag_ids:
            tag = Tag.objects.get(id=tag_id)
            prompt.tags.add(tag)

        prompt.save()


def main():
    # migrate_users()
    # migrate_languages()  # load fixture instead
    # migrate_language_levels()
    # migrate_challenges()
    migrate_prompts()


main()
