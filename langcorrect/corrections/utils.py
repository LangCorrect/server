# ruff: noqa: TRY300,BLE001
import csv
import logging
import tempfile
from io import StringIO
from pathlib import Path

from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from config.settings.base import SITE_BASE_URL
from langcorrect.posts.models import PostRow

logger = logging.getLogger(__name__)

CSV_HEADERS = [
    "Original Sentence",
    "Corrected Sentence",
    "Correction Feedback",
    "Corrector",
]
EXCLUDE_TITLE_ROW = 0


class ExportCorrections:
    def __init__(self, post) -> None:
        self.post = post
        self.post_rows = (
            PostRow.available_objects.filter(post=post)
            .exclude(order=EXCLUDE_TITLE_ROW)
            .order_by("created")
        )

    def export_csv(self) -> HttpResponse:
        """Export the post sentences and their corrections to a CSV file."""
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(CSV_HEADERS)

        for post_row in self.post_rows:
            for correction in post_row.correctedrow_set.all():
                writer.writerow(
                    [
                        post_row.sentence,
                        correction.correction,
                        correction.note,
                        correction.user.username,
                    ],
                )

        output.seek(0)

        yyyy_mm_dd = self.post.created.strftime("%Y-%m-%d")

        response = HttpResponse(output.read(), content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={yyyy_mm_dd}.csv"
        return response

    def export_pdf(self) -> HttpResponse:
        try:
            html_string = render_to_string(
                "corrections/export_corrections_pdf.html",
                {"post": self.post, "post_rows": self.post_rows},
            )

            html = HTML(string=html_string, encoding="utf-8", base_url=SITE_BASE_URL)
            result = html.write_pdf()

            yyyy_mm_dd = self.post.created.strftime("%Y-%m-%d")

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = f"attachment; filename={yyyy_mm_dd}.pdf"

            with tempfile.NamedTemporaryFile(delete=True) as output:
                output.write(result)
                output.flush()

                temp_path = Path(output.name)
                with temp_path.open("rb") as f:
                    response.write(f.read())
            return response
        except Exception:
            logger.exception("Failed to export corrections as a PDF.")
            return HttpResponse(
                "An error occurred while generating the PDF.",
                status=500,
            )

    def export_json(self) -> HttpResponse:
        try:
            post_rows = [
                {
                    "original_sentence": post_row.sentence,
                    "corrections": [
                        {
                            "corrected_sentence": correction.correction,
                            "correction_feedback": correction.note,
                            "corrector": correction.user.username,
                        }
                        for correction in post_row.correctedrow_set.all()
                    ],
                }
                for post_row in self.post_rows
            ]

            yyyy_mm_dd = self.post.created.strftime("%Y-%m-%d")

            response = HttpResponse(content_type="application/json")
            response["Content-Disposition"] = f"attachment; filename={yyyy_mm_dd}.json"
            response.write(post_rows)
            return response
        except Exception:
            logger.exception("Failed to export corrections as a JSON.")
            return HttpResponse(
                "An error occurred while generating the JSON.",
                status=500,
            )
