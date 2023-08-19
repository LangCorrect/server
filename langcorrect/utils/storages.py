import uuid
from io import BytesIO

from django.core.files import File
from django.core.files.uploadedfile import UploadedFile
from PIL import Image
from storages.backends.s3boto3 import S3Boto3Storage


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = False


class S3MediaStorageUtility:
    @staticmethod
    def generate_unique_filename(extension: str) -> str:
        """Generate a unique filename using UUID."""
        return f"{uuid.uuid4()}.{extension}"

    @staticmethod
    def get_file_extension(file_obj: UploadedFile) -> str:
        return file_obj.name.split(".")[-1]

    @staticmethod
    def compress_image(file_obj: UploadedFile, quality=40) -> UploadedFile:
        """Compress an image to the specified quality and return the compressed image."""
        ext = S3MediaStorageUtility.get_file_extension(file_obj)
        new_name = S3MediaStorageUtility.generate_unique_filename(ext)

        image = Image.open(file_obj)
        output = BytesIO()

        image_format = "JPEG" if ext.lower() in ["jpg", "jpeg"] else ext.upper()
        image.save(output, format=image_format, quality=quality, optimize=True)

        output.seek(0)
        new_image = File(output, name=new_name)
        return new_image

    @staticmethod
    def save_to_s3_media_storage(filename: str, file_obj: UploadedFile) -> str:
        """Saves a file to the S3 media storage and returns the stored file's key."""
        media_storage = MediaRootS3Boto3Storage()
        media_storage.save(filename, file_obj)
        return filename
