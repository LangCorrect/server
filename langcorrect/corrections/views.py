# ruff: noqa: C901,PLR0915,PLR0912
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.db.models import Max
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as translate
from django.views.generic import ListView

from langcorrect.corrections.constants import FileFormat
from langcorrect.corrections.constants import NotificationTypes
from langcorrect.corrections.helpers import add_or_update_correction
from langcorrect.corrections.helpers import check_can_make_corrections
from langcorrect.corrections.helpers import check_if_overall_feedback_exists
from langcorrect.corrections.helpers import create_notification
from langcorrect.corrections.helpers import delete_correction
from langcorrect.corrections.helpers import delete_overall_feedback
from langcorrect.corrections.helpers import update_overall_feedback
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PostRowFeedback
from langcorrect.corrections.utils import ExportCorrections
from langcorrect.decorators import premium_required
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostRow
from langcorrect.utils.mailing import email_new_correction


def _handle_correction_data(user, post, correction):
    sentence_id = correction["sentence_id"]
    corrected_text = correction["corrected_text"]
    feedback = correction["feedback"]
    action = correction["action"]
    correction_types = None  # noqa: F841

    correction_created = False

    post_row = PostRow.objects.get(id=sentence_id)

    if action == "perfect":
        correction_created |= add_or_update_correction(
            user,
            post,
            post_row,
            PostRowFeedback.FeedbackType.PERFECT,
        )
    elif action == "corrected":
        correction_created |= add_or_update_correction(
            user,
            post,
            post_row,
            PostRowFeedback.FeedbackType.CORRECTED,
            corrected_text,
            feedback,
        )
    elif action == "delete":
        delete_correction(user, post, post_row)

    return correction_created


def _handle_overall_feedback(user, post, feedback, delete=False):  # noqa:FBT002
    if delete:
        delete_overall_feedback(user, post)
    elif check_if_overall_feedback_exists(user, post):
        update_overall_feedback(user, post, feedback)
    else:
        OverallFeedback.objects.create(
            user=user,
            post=post,
            comment=feedback,
        )
        create_notification(
            user,
            post.user,
            post,
            NotificationTypes.NEW_COMMENT,
        )


@login_required
def make_corrections(request, slug):
    post = get_object_or_404(Post, slug=slug)
    current_user = request.user

    if not check_can_make_corrections(current_user, post):
        raise PermissionDenied

    if request.method == "POST":
        corrections_data = request.POST.get("corrections_data")
        overall_feedback = request.POST.get("overall_feedback", None)
        delete_overall_feedback = request.POST.get("delete_overall_feedback", None)

        previous_correctors = list(post.get_correctors)
        new_correction_made = False
        new_feedback_given = False

        if corrections_data:
            corrections = json.loads(corrections_data)
            for correction in corrections:
                new_correction_made |= _handle_correction_data(
                    current_user,
                    post,
                    correction,
                )

        if overall_feedback:
            _handle_overall_feedback(
                current_user,
                post,
                overall_feedback,
                delete_overall_feedback == "true",
            )

        if new_correction_made:
            post.is_corrected = True
            post.save()
        elif post.get_correctors.count() == 0:
            post.is_corrected = False
            post.save()

        if current_user not in previous_correctors:
            if new_correction_made:
                create_notification(
                    current_user,
                    post.user,
                    post,
                    NotificationTypes.NEW_CORRECTION,
                )

                if post.user.is_premium_user:
                    email_new_correction(post)
            elif new_feedback_given:
                create_notification(
                    current_user,
                    post.user,
                    post,
                    NotificationTypes.NEW_COMMENT,
                )
        else:
            create_notification(
                current_user,
                post.user,
                post,
                NotificationTypes.UPDATE_CORRECTION,
            )

        return redirect(reverse("posts:detail", kwargs={"slug": post.slug}))
    else:  # noqa: RET505
        all_post_rows = PostRow.available_objects.filter(
            post=post,
            is_actual=True,
        ).order_by("order")

        overall_feedback = OverallFeedback.available_objects.filter(
            post=post,
            user=current_user,
        ).first()

        is_edit = False

        for post_row in all_post_rows:
            post_row.correction = post_row.sentence
            post_row.note = ""
            post_row.show_form = False
            post_row.is_action_taken = False
            post_row.action = "none"
            post_row.is_title = post_row.order == 0

            previous_correction = PostRowFeedback.available_objects.filter(
                user=current_user,
                post=post,
                post_row=post_row,
            ).first()

            if previous_correction:
                post_row.is_action_taken = True
                is_edit |= True

                if (
                    previous_correction.feedback_type
                    == PostRowFeedback.FeedbackType.PERFECT
                ):
                    post_row.action = "perfect"
                else:
                    post_row.action = "corrected"
                    post_row.show_form = True
                    post_row.correction = previous_correction.correction
                    post_row.note = previous_correction.note

    context = {}
    context["post_rows"] = all_post_rows
    context["post"] = post
    context["overall_feedback"] = overall_feedback.comment if overall_feedback else ""
    context["is_edit"] = is_edit
    context["disable_page_container"] = True

    return render(request, "corrections/make_corrections.html", context)


@login_required
@premium_required
def export_corrections(request, slug):
    post = get_object_or_404(Post, slug=slug)
    export_format = request.GET.get("format", "").upper()

    match export_format:
        case FileFormat.CSV:
            return ExportCorrections(post).export_csv()
        case FileFormat.PDF:
            return ExportCorrections(post).export_pdf()
        case FileFormat.JSON:
            return ExportCorrections(post).export_json()
        case _:
            messages.warning(request, translate("Invalid export format specified."))
            return redirect(reverse("posts:detail", kwargs={"slug": post.slug}))


class UserCorrectionsView(LoginRequiredMixin, ListView):
    model = PostRowFeedback
    template_name = "corrections/user_corrections.html"
    paginate_by = 50

    def get_queryset(self):
        current_user = self.request.user

        feedback_qs = PostRowFeedback.available_objects.filter(user=current_user)

        posts_with_corrections = feedback_qs.values("post").annotate(
            corrections_count=Count("id"),
            latest_correction_date=Max("created"),
        )

        post_ids = posts_with_corrections.values_list("post", flat=True)
        return (
            Post.available_objects.filter(id__in=post_ids)
            .annotate(
                num_corrections=Count(
                    "postrowfeedback",
                    filter=Q(postrowfeedback__user=current_user),
                ),
                date_corrected=Max(
                    "postrowfeedback__created",
                    filter=Q(postrowfeedback__user=current_user),
                ),
            )
            .order_by("-date_corrected")
        )


user_corrections_view = UserCorrectionsView.as_view()
