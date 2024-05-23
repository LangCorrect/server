# ruff: noqa: DJ001,RUF005
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop
from model_utils.models import SoftDeletableModel
from model_utils.models import TimeStampedModel
from notifications.signals import notify
from taggit.managers import TaggableManager

from langcorrect.languages.models import LevelChoices
from langcorrect.posts.utils import SentenceSplitter
from langcorrect.users.models import GenderChoices
from langcorrect.users.models import User

sentence_splitter = SentenceSplitter()


class PostVisibility(models.TextChoices):
    PUBLIC = "public", _("Viewable by everyone")
    MEMBER = "member", _("Viewable only by registered members")


class Post(TimeStampedModel, SoftDeletableModel):
    class Meta:
        ordering = ["-created"]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=60)
    text = models.TextField()
    native_text = models.TextField()
    language = models.ForeignKey(
        "languages.Language",
        on_delete=models.CASCADE,
    )
    gender_of_narration = models.CharField(
        choices=GenderChoices.choices,
        default=GenderChoices.UNKNOWN,
        max_length=1,
    )
    permission = models.CharField(
        choices=PostVisibility.choices,
        default=PostVisibility.PUBLIC,
        max_length=6,
    )
    is_draft = models.BooleanField(default=False)
    prompt = models.ForeignKey(
        "prompts.Prompt",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    slug = models.SlugField(max_length=255, null=True)
    tags = TaggableManager(blank=True)
    language_level = models.CharField(
        choices=LevelChoices.choices,
        default=LevelChoices.A1,
        max_length=2,
    )
    is_corrected = models.BooleanField(default=False)

    def get_absolute_url(self) -> str:
        return reverse("posts:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug and not self.is_draft:
            new_slug = generated_slug = slugify(self.title, allow_unicode=True)

            if not new_slug:
                count = 1
                generated_slug = f"-{count}"

            if Post.all_objects.filter(slug=new_slug).exists() or not new_slug:
                count = 1
                while (
                    Post.all_objects.exclude(id=self.pk)
                    .filter(slug=generated_slug)
                    .exists()
                ):
                    generated_slug = f"{new_slug}-{count}"
                    count += 1
            self.slug = generated_slug

        super().save(*args, **kwargs)

    @property
    def get_correctors(self):
        user_ids = self.postrowfeedback_set.values_list("user_id", flat=True)
        return User.objects.filter(id__in=user_ids)

    @property
    def corrected_by_count(self):
        return self.get_correctors.count()


class PostImage(TimeStampedModel, SoftDeletableModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file_key = models.CharField(max_length=255)

    @property
    def get_image_url(self):
        return f"{settings.MEDIA_URL}{self.file_key}"


class PostRow(TimeStampedModel, SoftDeletableModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    sentence = models.TextField()
    is_actual = models.BooleanField(default=True)
    order = models.IntegerField(default=None, null=True)


class PostReply(TimeStampedModel, SoftDeletableModel):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user",
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    recipient = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="which_user",
        null=True,
    )
    text = models.TextField()
    corrected_row = models.ForeignKey(
        "corrections.CorrectedRow",
        on_delete=models.SET_NULL,
        null=True,
    )
    perfect_row = models.ForeignKey(
        "corrections.PerfectRow",
        on_delete=models.SET_NULL,
        null=True,
    )
    reply = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reply_to_comment",
    )
    dislike = models.BooleanField(default=False)

    class Meta:
        ordering = ["created"]


@receiver(post_save, sender=Post)
def send_follower_notifications(sender, instance, created, **kwargs):
    post = instance
    user = post.user

    if created:
        recipients = [
            follower.user
            for follower in user.follow_to.all()
            if post.language in follower.user.native_languages
        ]

        notify.send(
            sender=user,
            recipient=recipients,
            verb=gettext_noop("submitted a new entry"),
            action_object=post,
            notification_type="new_post",
        )


@receiver(post_save, sender=Post)
def send_prompt_author_notifications(sender, instance, created, **kwargs):
    post = instance
    user = post.user

    if created and post.prompt:
        recipient = post.prompt.user

        notify.send(
            sender=user,
            recipient=recipient,
            verb=gettext_noop("responded to your prompt"),
            action_object=post,
            notification_type="new_prompt_response",
        )


@receiver(post_save, sender=Post)
def split_post_into_sentences(sender, instance, created, **kwargs):
    post = instance
    user = post.user
    post_sentences = sentence_splitter.split_sentences(post.text, post.language.code)
    title_and_sentences = [post.title] + post_sentences

    if created:
        create_post_rows(user, post, title_and_sentences)
    else:
        update_post_rows(user, post, title_and_sentences)


def create_post_rows(user, post, sentences):
    for idx, sentence in enumerate(sentences):
        PostRow.objects.create(user=user, post=post, sentence=sentence, order=idx)


def update_post_rows(user, post, sentences):
    all_rows = PostRow.available_objects.filter(post=post)
    old_rows = {row.sentence: row for row in all_rows}

    for idx, sentence in enumerate(sentences):
        if sentence in old_rows:
            show_sentence(old_rows[sentence], idx)
        else:
            PostRow.objects.create(user=user, post=post, sentence=sentence, order=idx)

    hide_removed_sentences(old_rows, sentences)


def show_sentence(post_row, order):
    post_row.is_actual = True
    post_row.order = order
    post_row.save()


def hide_removed_sentences(old_rows, sentences):
    for sentence, row in old_rows.items():
        if sentence not in sentences:
            row.is_actual = False
            row.save()
