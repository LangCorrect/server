# ruff: noqa: E501
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.translation import gettext_lazy as _

from langcorrect.utils.generics import get_file_extension

VALID_IMAGE_EXTENSIONS = ["jpg", "jpeg"]


def validate_jpeg_extension(image: UploadedFile) -> None:
    """Ensures that the image extension is valid.

    Args:
        image (UploadedFile)

    Raises:
        ValidationError: If the file extension is not in the valid extensions list (e.g., not "jpg" or "jpeg").
    """

    ext = get_file_extension(image)
    if ext.lower() not in VALID_IMAGE_EXTENSIONS:
        raise ValidationError(
            _("Unsupported file extension. Only .jpg and .jpeg are allowed."),
        )


def validate_image_size(image: UploadedFile, max_size_mb: int = 5) -> None:
    """Ensures that the image size does not exceed the specified maximum size.

    Args:
        image (UploadedFile)
        max_size_mb (int, optional): The maximum allowed size for the image in MB. Defaults to 5.

    Raises:
        ValidationError: If the image size exceeds the specified maximum size.
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    if image.size > max_size_bytes:
        raise ValidationError(
            _("Image size should not be more than %sMB.") % max_size_mb,
        )
