import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from langcorrect.corrections.helpers import check_can_make_corrections
from langcorrect.corrections.models import CorrectedRow, OverallFeedback, PerfectRow
from langcorrect.posts.models import Post, PostRow


@login_required
def make_corrections(request, slug):
    post = get_object_or_404(Post, slug=slug)
    current_user = request.user

    if not check_can_make_corrections(current_user, post):
        raise PermissionDenied()

    if request.method == "POST":
        corrections_data = request.POST.get("corrections_data")
        overall_feedback = request.POST.get("overall_feedback", None)

        if corrections_data:
            corrections = json.loads(corrections_data)

            for correction in corrections:
                sentence_id = correction["sentence_id"]
                corrected_text = correction["corrected_text"]
                feedback = correction["feedback"]
                action = correction["action"]

                post_row_instance = PostRow.objects.get(id=sentence_id)

                if action == "perfect":
                    PerfectRow.available_objects.get_or_create(
                        post=post, post_row=post_row_instance, user=current_user
                    )

                if action == "corrected":
                    corrected_row, _ = CorrectedRow.available_objects.get_or_create(
                        post=post, post_row=post_row_instance, user=current_user
                    )
                    corrected_row.correction = corrected_text
                    corrected_row.note = feedback
                    corrected_row.save()

                if action == "delete":
                    # Note: a sentence cannot be both marked as perfect or corrected
                    PerfectRow.available_objects.filter(
                        post=post, post_row=post_row_instance, user=current_user
                    ).delete()
                    CorrectedRow.available_objects.filter(
                        post=post, post_row=post_row_instance, user=current_user
                    ).delete()

        if overall_feedback:
            feedback_row, _ = OverallFeedback.available_objects.get_or_create(
                post=post,
                user=current_user,
            )
            feedback_row.comment = overall_feedback
            feedback_row.save()

        return redirect(reverse("posts:detail", kwargs={"slug": post.slug}))
    else:
        all_post_rows = PostRow.available_objects.filter(post=post, is_actual=True).order_by("order")

        overall_feedback = OverallFeedback.available_objects.filter(post=post, user=current_user).first()

        for post_row in all_post_rows:
            previous_correction = CorrectedRow.available_objects.filter(
                post_row_id=post_row.id, user=current_user
            ).first()

            previous_perfect = PerfectRow.available_objects.filter(post_row_id=post_row.id, user=current_user).first()

            post_row.correction = post_row.sentence
            post_row.note = ""
            post_row.show_form = False
            post_row.is_action_taken = False
            post_row.action = "none"

            if previous_correction:
                post_row.correction = previous_correction.correction
                post_row.note = previous_correction.note
                post_row.show_form = True
                post_row.is_action_taken = True
                post_row.action = "corrected"
            elif previous_perfect:
                post_row.is_action_taken = True
                post_row.action = "perfect"

    context = {}
    context["post_rows"] = all_post_rows
    context["post"] = (post,)
    context["overall_feedback"] = overall_feedback.comment if overall_feedback else ""

    return render(request, "corrections/make_corrections.html", context)
