def _sort_key(correction_dict):
    return correction_dict["ordering"]


def order_user_corrections_by_post_row(user_corrections):
    for user, _ in user_corrections.items():
        user_corrections[user]["corrections"].sort(key=_sort_key)
    return user_corrections


def populate_user_corrections(perfect_rows, corrected_rows, feedback_rows, postreply_rows):
    user_corrections = {}

    for row in perfect_rows:
        data = row.serialize
        user = row.user

        if user not in user_corrections:
            user_corrections[user] = {"corrections": [], "overall_feedback": "", "replies": []}
        user_corrections[user]["corrections"].append(data)

    for row in corrected_rows:
        data = row.serialize
        user = row.user

        if user not in user_corrections:
            user_corrections[user] = {"corrections": [], "overall_feedback": "", "replies": []}
        user_corrections[user]["corrections"].append(data)

    for feedback in feedback_rows:
        user = feedback.user

        if user not in user_corrections:
            user_corrections[user] = {"corrections": [], "overall_feedback": "", "replies": []}
        user_corrections[user]["overall_feedback"] = feedback.comment

    for reply in postreply_rows:
        recipient = reply.recipient

        if user not in user_corrections:
            user_corrections[recipient] = {"corrections": [], "overall_feedback": "", "replies": []}
        user_corrections[recipient]["replies"].append(reply)

    sorted_corrections = order_user_corrections_by_post_row(user_corrections)
    return sorted_corrections


def check_can_make_corrections(current_user, post):
    if post.user == current_user:
        return False

    if post.language not in current_user.native_languages:
        return False

    return True
