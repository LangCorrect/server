import logging
from io import BytesIO

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from langcorrect.utils.generics import generate_unique_filename, get_file_extension

logger = logging.getLogger(__name__)


class BaseMediaStorage:
    @staticmethod
    def compress_image(file_obj: UploadedFile, quality=40) -> File:
        """
        Compresses an image to the specified quality.

        Args:
            file_obj (UploadedFile)
            quality (int, optional): How much to compress the image to. Defaults to 40.

        Returns:
            File: Compressed image
        """
        image = Image.open(file_obj)
        output = BytesIO()

        ext = get_file_extension(file_obj)
        image_format = "JPEG" if ext.lower() in ["jpg", "jpeg"] else ext.upper()

        image.save(output, format=image_format, quality=quality, optimize=True)
        output.seek(0)

        return File(output, name=file_obj.name)


class LocalMediaStorage(BaseMediaStorage):
    @staticmethod
    def save(file_obj: UploadedFile, compress=True) -> str:
        """
        Saves a file to local media storage.

        Args:
            file_obj (UploadedFile)

        Returns:
            str: The stored file's unique key including the extension (ex: "2f79fb98-93c9-4fe1-a6e2-6d1289bcbc32.jpeg")

        """
        media_storage = FileSystemStorage()
        ext = get_file_extension(file_obj)
        new_name = generate_unique_filename(ext)

        if compress and file_obj.content_type.startswith("image/"):
            file_obj = LocalMediaStorage.compress_image(file_obj)

        media_storage.save(new_name, file_obj)
        return new_name

    @staticmethod
    def delete(file_key: str) -> None:
        """
        Deletes a file from local media storage

        Args:
            file_key (str)

        Returns:
            None
        """
        media_storage = FileSystemStorage()
        if media_storage.exists(file_key):
            try:
                media_storage.delete(file_key)
            except Exception as e:
                logger.error(f"Failed to delete file with key ({file_key}) from local storage. Error: {e}")


def get_storage_backend():
    return LocalMediaStorage()
