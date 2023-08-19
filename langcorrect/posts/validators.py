from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from langcorrect.utils.storages import S3MediaStorageUtility


def validate_jpeg_extension(value):
    """Ensure the provided file has either a .jpg or .jpeg extension."""

    ext = S3MediaStorageUtility.get_file_extension(value)
    valid_extensions = ["jpg", "jpeg"]

    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Unsupported file extension. Only .jpg and .jpeg are allowed."))


def validate_image_size(image, max_size_mb=5):
    """Ensure the image is less than the specified size."""
    max_size_bytes = max_size_mb * 1024 * 1024

    if image.size > max_size_bytes:
        raise ValidationError(_(f"Image size should not be more than {max_size_mb}MB."))
