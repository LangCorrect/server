import csv
from io import StringIO

from django.http import HttpResponse

from langcorrect.posts.models import PostRow


class ExportCorrections:
    def __init__(self, post) -> None:
        self.post = post
        self.post_rows = PostRow.available_objects.filter(post=post).exclude(order=0).order_by("created")

    def export_csv(self) -> HttpResponse:
        """Export the post sentences and their corrections to a CSV file."""
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(["Original Sentence", "Corrected Sentence", "Correction Feedback", "Corrector"])

        for post_row in self.post_rows:
            for correction in post_row.correctedrow_set.all():
                writer.writerow([post_row.sentence, correction.correction, correction.note, correction.user.username])

        output.seek(0)

        yyyy_mm_dd = self.post.created.strftime("%Y-%m-%d")

        response = HttpResponse(output.read(), content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={yyyy_mm_dd}-{self.post.title}.csv"
        return response
