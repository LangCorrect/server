import json
import os

import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from taggit.models import Tag  # noqa: E402

from langcorrect.challenges.models import Challenge  # noqa: E402
from langcorrect.corrections.models import CorrectedRow, CorrectionType, OverallFeedback, PerfectRow  # noqa: E402
from langcorrect.languages.models import Language, LanguageLevel  # noqa: E402
from langcorrect.posts.models import Post, PostReply, PostRow  # noqa: E402
from langcorrect.prompts.models import Prompt  # noqa: E402

User = get_user_model()

CORRECTION_TYPES_MAPPING = {
    "Grammar": "Grammar",
    "Spelling": "Spelling",
    "Stylistic": "Style and Tone",
    "Usage": "Word Choice",
}


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


def migrate_posts():
    print("migrating posts...")

    with open("./temp_data/post_data.json") as file:
        data = json.load(file)

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        is_removed = entry["fields"]["is_removed"]
        user_pk = entry["fields"]["user"]
        title = entry["fields"]["title"]
        text = entry["fields"]["text"]
        native_text = entry["fields"]["native_text"]
        language_pk = entry["fields"]["language"]
        gender_of_narration = entry["fields"]["gender_of_narration"]
        permission = entry["fields"]["permission"]
        is_draft = entry["fields"]["is_draft"]
        prompt_pk = entry["fields"]["prompt"]
        slug = entry["fields"]["slug"]
        language_level = entry["fields"]["language_level"]
        is_corrected = entry["fields"]["is_corrected"]
        tag_ids = entry["fields"]["tag_ids"]

        post = Post.objects.create(
            pk=pk,
            created=created,
            modified=modified,
            is_removed=is_removed,
            user=User.objects.get(pk=user_pk),
            title=title,
            text=text,
            native_text=native_text,
            language=Language.objects.get(pk=language_pk),
            gender_of_narration=gender_of_narration,
            permission=permission,
            is_draft=is_draft,
            prompt=Prompt.objects.get(pk=prompt_pk) if prompt_pk else None,
            slug=slug,
            language_level=language_level,
            is_corrected=is_corrected,
        )

        for tag_id in tag_ids:
            tag = Tag.objects.get(id=tag_id)
            post.tags.add(tag)

        post.save()


def migrate_post_rows():
    print("migrating post rows...")

    with open("./temp_data/postrows_data.json") as file:
        data = json.load(file)

    total_count = len(data)
    curr_count = 0

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        is_removed = entry["fields"]["is_removed"]
        user_pk = entry["fields"]["user"]
        post_pk = entry["fields"]["post"]
        sentence = entry["fields"]["sentence"]
        is_actual = entry["fields"]["is_actual"]
        order = entry["fields"]["order"]

        try:
            post = Post.all_objects.get(pk=post_pk) if post_pk else None
        except Post.DoesNotExist:
            post = None

        PostRow.objects.create(
            pk=pk,
            created=created,
            modified=modified,
            is_removed=is_removed,
            user=User.objects.get(pk=user_pk),
            post=post,
            sentence=sentence,
            is_actual=is_actual,
            order=order,
        )

        curr_count += 1
        print(f"Finished importing postrow {curr_count}/{total_count}")


def migrate_corrected_rows():
    print("Migrating CorrectedRows...")

    with open("./temp_data/correctedrow_data.json") as file:
        data = json.load(file)

    total_count = len(data)
    curr_count = 0

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        is_removed = entry["fields"]["is_removed"]
        user_pk = entry["fields"]["user"]
        post_pk = entry["fields"]["post"]
        post_row_pk = entry["fields"]["post_row"]
        correction = entry["fields"]["correction"]
        note = entry["fields"]["note"]
        pretty_corrections = entry["fields"]["pretty_corrections"]

        try:
            post = Post.all_objects.get(pk=post_pk) if post_pk else None
        except Post.DoesNotExist:
            post = None

        try:
            post_row = PostRow.all_objects.get(pk=post_row_pk) if post_row_pk else None

            correction = CorrectedRow.objects.create(
                pk=pk,
                created=created,
                modified=modified,
                is_removed=is_removed,
                user=User.objects.get(pk=user_pk),
                post=post,
                post_row=post_row,
                correction=correction,
                note=note,
            )

            for correction_type in pretty_corrections:
                c_type = CORRECTION_TYPES_MAPPING.get(correction_type)
                ctype = CorrectionType.objects.get(name=c_type)
                correction.correction_types.add(ctype)

            correction.save()
        except PostRow.DoesNotExist:
            pass

        curr_count += 1
        print(f"Finished importing correctedrow {curr_count}/{total_count}")


def migrate_perfect_rows():
    print("Migrating perfect rows...")

    with open("./temp_data/perfects_data.json") as file:
        data = json.load(file)

    total_count = len(data)
    curr_count = 0

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        is_removed = entry["fields"]["is_removed"]
        user_pk = entry["fields"]["user"]
        post_pk = entry["fields"]["post"]
        post_row_pk = entry["fields"]["post_row"]

        try:
            post = Post.all_objects.get(pk=post_pk) if post_pk else None
        except Post.DoesNotExist:
            post = None

        try:
            post_row = PostRow.all_objects.get(pk=post_row_pk) if post_row_pk else None
            PerfectRow.objects.create(
                pk=pk,
                created=created,
                modified=modified,
                is_removed=is_removed,
                user=User.objects.get(pk=user_pk),
                post=post,
                post_row=post_row,
            )
        except PostRow.DoesNotExist:
            pass

        curr_count += 1
        print(f"Finished importing PerfectRow {curr_count}/{total_count}")


def migrate_overall_feedback():
    print("Migrating overall feedback...")

    with open("./temp_data/overall_feedback_data.json") as file:
        data = json.load(file)

    total_count = len(data)
    curr_count = 0

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        is_removed = entry["fields"]["is_removed"]
        user_pk = entry["fields"]["user"]
        post_pk = entry["fields"]["post"]
        comment = entry["fields"]["comment"]
        is_draft = entry["fields"]["is_draft"]

        try:
            post = Post.all_objects.get(pk=post_pk)

            OverallFeedback.objects.create(
                pk=pk,
                created=created,
                modified=modified,
                is_removed=is_removed,
                user=User.objects.get(pk=user_pk),
                post=post,
                comment=comment,
                is_draft=is_draft,
            )
        except Post.DoesNotExist:
            pass

        curr_count += 1
        print(f"Finished importing OverallFeedback {curr_count}/{total_count}")


def migrate_post_replies():
    print("Migrate post replies...")

    with open("./temp_data/replies_data.json") as file:
        data = json.load(file)

    total_count = len(data)
    curr_count = 0

    for entry in data:
        pk = entry["pk"]
        created = entry["fields"]["created"]
        modified = entry["fields"]["modified"]
        is_removed = entry["fields"]["is_removed"]
        user_pk = entry["fields"]["user"]
        post_pk = entry["fields"]["post"]
        recipient_pk = entry["fields"]["recipient"]
        text = entry["fields"]["text"]
        corrected_row_pk = entry["fields"]["corrected_row"]
        perfect_row_pk = entry["fields"]["perfect_row"]
        reply_pk = entry["fields"]["reply"]
        dislike = entry["fields"]["dislike"]

        try:
            corrected_row = CorrectedRow.all_objects.get(pk=corrected_row_pk) if corrected_row_pk else None
        except CorrectedRow.DoesNotExist:
            corrected_row = None

        try:
            perfect_row = PerfectRow.all_objects.get(pk=perfect_row_pk) if perfect_row_pk else None
        except PerfectRow.DoesNotExist:
            perfect_row = None

        try:
            reply = PostReply.all_objects.get(pk=reply_pk) if reply_pk else None
        except PostReply.DoesNotExist:
            reply = None

        try:
            post = Post.all_objects.get(pk=post_pk)

            PostReply.objects.create(
                pk=pk,
                created=created,
                modified=modified,
                is_removed=is_removed,
                post=post,
                user=User.objects.get(pk=user_pk),
                recipient=User.objects.get(pk=recipient_pk),
                text=text,
                reply=reply,
                corrected_row=corrected_row,
                perfect_row=perfect_row,
                dislike=dislike,
            )
        except Post.DoesNotExist:
            pass

        curr_count += 1
        print(f"Finished importing PostReply {curr_count}/{total_count}")


def main():
    # migrate_users()
    # migrate_languages()  # load fixture instead
    # migrate_language_levels()
    # migrate_challenges()
    # migrate_prompts()
    # migrate_posts()
    # migrate_post_rows()
    # migrate_corrected_rows()
    # migrate_perfect_rows()
    # migrate_overall_feedback()
    migrate_post_replies()


main()
