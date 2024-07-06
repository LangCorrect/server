# ruff: noqa: C901,PLR0915,PLR0912
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as translate
from django.views.generic import ListView

from langcorrect.constants import NotificationTypes
from langcorrect.corrections.constants import FileFormat
from langcorrect.corrections.helpers import check_can_make_corrections
from langcorrect.corrections.helpers import create_or_update_correction
from langcorrect.corrections.helpers import delete_correction
from langcorrect.corrections.helpers import delete_overall_feedback
from langcorrect.corrections.helpers import get_corrected_sentence
from langcorrect.corrections.helpers import get_or_create_post_user_correction
from langcorrect.corrections.helpers import get_overall_feedback
from langcorrect.corrections.helpers import get_post_rows
from langcorrect.corrections.models import PostCorrection
from langcorrect.corrections.models import PostUserCorrection
from langcorrect.corrections.utils import ExportCorrections
from langcorrect.decorators import premium_required
from langcorrect.helpers import create_notification
from langcorrect.posts.helpers import update_post_correction_status
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostRow
from langcorrect.users.models import User
from langcorrect.utils.mailing import email_new_correction


def _process_corrections(
    corrections: any,
    post_user_correction: PostUserCorrection,
    user: User,
) -> bool:
    is_corrections_made = False

    for correction in corrections:
        post_row_id = correction["sentence_id"]
        corrected_text = correction["corrected_text"]
        feedback = correction["feedback"]
        action = correction["action"]

        post_row = PostRow.available_objects.get(id=post_row_id)

        if action == PostCorrection.FeedbackType.PERFECT:
            create_or_update_correction(
                post_user_correction,
                post_row,
                PostCorrection.FeedbackType.PERFECT,
            )
            is_corrections_made |= True
        elif action == PostCorrection.FeedbackType.CORRECTED:
            create_or_update_correction(
                post_user_correction,
                post_row,
                PostCorrection.FeedbackType.CORRECTED,
                corrected_text,
                feedback,
            )
            is_corrections_made |= True
        elif action == "delete":
            delete_correction(post_user_correction, post_row)

    return is_corrections_made


def _remove_post_user_correction_if_empty(user_correction: PostUserCorrection):
    user_correction.refresh_from_db()

    if (
        not user_correction.overall_feedback
        and not user_correction.postcorrection_set.exists()
    ):
        user_correction.delete()


@login_required
def make_corrections(request, slug):
    post = get_object_or_404(Post, slug=slug)
    current_user = request.user

    if not check_can_make_corrections(current_user, post):
        raise PermissionDenied

    if request.method == "POST":
        corrections_data = request.POST.get("corrections_data")
        overall_feedback = request.POST.get("overall_feedback", None)
        should_delete_overall_feedback = request.POST.get(
            "delete_overall_feedback",
            None,
        )

        new_correction_made = False
        new_feedback_given = False

        if corrections_data or overall_feedback or should_delete_overall_feedback:
            post_user_correction = get_or_create_post_user_correction(
                post,
                current_user,
            )

            if overall_feedback:
                post_user_correction.overall_feedback = overall_feedback
                post_user_correction.save()
                new_feedback_given |= True

            if should_delete_overall_feedback == "true":
                delete_overall_feedback(post, current_user)

            if corrections_data:
                corrections = json.loads(corrections_data)
                has_new_corrections = _process_corrections(
                    corrections,
                    post_user_correction,
                    current_user,
                )
                new_correction_made |= has_new_corrections

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

        update_post_correction_status(post, status=new_correction_made)
        _remove_post_user_correction_if_empty(post_user_correction)
        return redirect(reverse("posts:detail", kwargs={"slug": post.slug}))
    else:  # noqa: RET505
        post_rows = get_post_rows(post).order_by("order")
        overall_feedback = get_overall_feedback(post, current_user)

        is_edit = False

        for post_row in post_rows:
            post_row.correction = post_row.sentence
            post_row.note = ""
            post_row.show_form = False
            post_row.is_action_taken = False
            post_row.action = "none"
            post_row.is_title = post_row.order == 0

            prev_correction = get_corrected_sentence(post_row, current_user)
            if prev_correction:
                is_edit |= True
                post_row.is_action_taken = True

                if (
                    prev_correction.feedback_type
                    == PostCorrection.FeedbackType.CORRECTED
                ):
                    post_row.show_form = True
                    post_row.action = PostCorrection.FeedbackType.CORRECTED
                    post_row.correction = prev_correction.correction
                    post_row.note = prev_correction.note
                else:
                    post_row.action = PostCorrection.FeedbackType.PERFECT

        context = {}
        context["post_rows"] = post_rows
        context["post"] = post
        context["overall_feedback"] = overall_feedback if overall_feedback else ""
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
    model = PostUserCorrection
    template_name = "corrections/user_corrections.html"
    paginate_by = 20

    def get_queryset(self):
        current_user = self.request.user

        return PostUserCorrection.objects.filter(user=current_user)


user_corrections_view = UserCorrectionsView.as_view()
