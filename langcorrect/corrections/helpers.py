def _sort_key(correction_dict):
    return correction_dict["ordering"]


def order_user_corrections_by_post_row(user_corrections):
    for user, _ in user_corrections.items():
        user_corrections[user]["corrections"].sort(key=_sort_key)
    return user_corrections


def populate_user_corrections(perfect_rows, corrected_rows, feedback_rows):
    user_corrections = {}

    for row in perfect_rows:
        data = row.serialize
        user = row.user

        if user not in user_corrections:
            user_corrections[user] = {"corrections": [], "overall_feedback": ""}

        user_corrections[user]["corrections"].append(data)

    for row in corrected_rows:
        data = row.serialize
        user = row.user

        if user not in user_corrections:
            user_corrections[user] = {"corrections": [], "overall_feedback": ""}

        user_corrections[user]["corrections"].append(data)

    for feedback in feedback_rows:
        user = feedback.user

        if user not in user_corrections:
            user_corrections[user] = {"corrections": [], "overall_feedback": ""}

        user_corrections[user]["overall_feedback"] = feedback.comment

    sorted_corrections = order_user_corrections_by_post_row(user_corrections)

    return sorted_corrections
