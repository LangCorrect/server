# ruff: noqa: C901,PLR0915,PLR0912
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Case
from django.db.models import Count
from django.db.models import Max
from django.db.models import Q
from django.db.models import When
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as translate
from django.utils.translation import gettext_noop
from django.views.generic import ListView
from notifications.signals import notify

from langcorrect.corrections.constants import FileFormat
from langcorrect.corrections.helpers import check_can_make_corrections
from langcorrect.corrections.models import CorrectedRow
from langcorrect.corrections.models import OverallFeedback
from langcorrect.corrections.models import PerfectRow
from langcorrect.corrections.utils import ExportCorrections
from langcorrect.decorators import premium_required
from langcorrect.posts.models import Post
from langcorrect.posts.models import PostRow
from langcorrect.utils.mailing import email_new_correction


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

        previous_correctors = post.get_correctors
        new_correction_made = False
        new_feedback_given = False

        if corrections_data:
            corrections = json.loads(corrections_data)

            for correction in corrections:
                sentence_id = correction["sentence_id"]
                corrected_text = correction["corrected_text"]
                feedback = correction["feedback"]
                action = correction["action"]

                post_row_instance = PostRow.objects.get(id=sentence_id)

                if action == "perfect":
                    _, perfect_created = PerfectRow.available_objects.get_or_create(
                        post=post,
                        post_row=post_row_instance,
                        user=current_user,
                    )
                    new_correction_made |= perfect_created

                if action == "corrected":
                    (
                        corrected_row,
                        correctedrow_created,
                    ) = CorrectedRow.available_objects.get_or_create(
                        post=post,
                        post_row=post_row_instance,
                        user=current_user,
                    )
                    corrected_row.correction = corrected_text
                    corrected_row.note = feedback
                    corrected_row.save()

                    new_correction_made |= correctedrow_created

                if action == "delete":
                    # Note: a sentence cannot be both marked as perfect or corrected
                    PerfectRow.available_objects.filter(
                        post=post,
                        post_row=post_row_instance,
                        user=current_user,
                    ).delete()
                    CorrectedRow.available_objects.filter(
                        post=post,
                        post_row=post_row_instance,
                        user=current_user,
                    ).delete()

        if overall_feedback:
            (
                feedback_row,
                feedback_created,
            ) = OverallFeedback.available_objects.get_or_create(
                post=post,
                user=current_user,
            )
            feedback_row.comment = overall_feedback
            feedback_row.save()

            new_feedback_given |= feedback_created

            if delete_overall_feedback == "true":
                feedback_row.delete()

        if current_user not in previous_correctors:
            if new_correction_made:
                notify.send(
                    sender=current_user,
                    recipient=post.user,
                    verb=gettext_noop("corrected"),
                    action_object=post,
                    notification_type="new_correction",
                )
            elif new_feedback_given:
                notify.send(
                    sender=current_user,
                    recipient=post.user,
                    verb=gettext_noop("commented on"),
                    action_object=post,
                    notification_type="new_comment",
                )

        if new_correction_made:
            post.is_corrected = True
            post.save()

        elif post.get_correctors.count() == 0:
            post.is_corrected = False
            post.save()

        if (
            new_correction_made
            and current_user not in previous_correctors
            and post.user.is_premium_user
        ):
            email_new_correction(post)

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
            previous_correction = CorrectedRow.available_objects.filter(
                post_row_id=post_row.id,
                user=current_user,
            ).first()

            previous_perfect = PerfectRow.available_objects.filter(
                post_row_id=post_row.id,
                user=current_user,
            ).first()

            post_row.correction = post_row.sentence
            post_row.note = ""
            post_row.show_form = False
            post_row.is_action_taken = False
            post_row.action = "none"
            post_row.is_title = post_row.order == 0

            if previous_correction:
                post_row.correction = previous_correction.correction
                post_row.note = previous_correction.note
                post_row.show_form = True
                post_row.is_action_taken = True
                post_row.action = "corrected"
                is_edit |= True
            elif previous_perfect:
                post_row.is_action_taken = True
                post_row.action = "perfect"
                is_edit |= True

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
        case _:
            messages.warning(request, translate("Invalid export format specified."))
            return redirect(reverse("posts:detail", kwargs={"slug": post.slug}))


class UserCorrectionsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "corrections/user_corrections.html"
    paginate_by = 20

    def get_queryset(self):
        current_user = self.request.user

        correctedrow_condition = Q(
            correctedrow__user=current_user,
            correctedrow__is_removed=False,
        )
        perfectrow_condition = Q(
            perfectrow__user=current_user,
            perfectrow__is_removed=False,
        )

        qs = Post.available_objects.filter(
            correctedrow_condition | perfectrow_condition,
        ).distinct()

        return qs.annotate(
            num_corrections=Count(
                "correctedrow__id",
                distinct=True,
                filter=correctedrow_condition,
            )
            + Count("perfectrow__id", distinct=True, filter=perfectrow_condition),
            date_corrected=Max(
                Case(
                    When(correctedrow__user=current_user, then="correctedrow__created"),
                    When(perfectrow__user=current_user, then="perfectrow__created"),
                ),
            ),
        ).order_by("-date_corrected")


user_corrections_view = UserCorrectionsView.as_view()
