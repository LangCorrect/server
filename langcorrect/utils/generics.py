import uuid

from django.core.files.uploadedfile import UploadedFile


def get_file_extension(file_obj: UploadedFile) -> str:
    """
    Extracts the extension from the given file object.

    Args:
        file_obj (UploadedFile)

    Returns:
        str: "jpeg"
    """
    return file_obj.name.split(".")[-1]


def generate_unique_filename(extension: str) -> str:
    """
    Generate a unique filename using UUID.

    Args:
        extension (str): ".jpeg"

    Returns:
        str: "2f79fb98-93c9-4fe1-a6e2-6d1289bcbc32.jpeg"
    """
    return f"{uuid.uuid4()}.{extension}"
