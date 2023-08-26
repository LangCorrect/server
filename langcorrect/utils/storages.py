from io import BytesIO

from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from storages.backends.s3boto3 import S3Boto3Storage

from langcorrect.utils.generics import generate_unique_filename, get_file_extension


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = False


class S3MediaStorage:
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

    @staticmethod
    def save(file_obj: UploadedFile, compress=True) -> str:
        """
        Saves a file to S3 media storage. If the file is an image and compress is True, the image will be compressed.

        Args:
            file_obj (UploadedFile)
            compress (bool, optional): Whether or not to compress the file. Defaults to True.

        Returns:
            str: The stored file's unique key including the extension (ex: "2f79fb98-93c9-4fe1-a6e2-6d1289bcbc32.jpeg")
        """
        media_storage = MediaRootS3Boto3Storage()
        ext = get_file_extension(file_obj)
        new_name = generate_unique_filename(ext)

        if compress and file_obj.content_type.startswith("image/"):
            file_obj = S3MediaStorage.compress_image(file_obj)

        media_storage.save(new_name, file_obj)
        return new_name
