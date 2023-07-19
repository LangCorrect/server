from django.db import models  # noqa: F401
from django.utils.text import slugify
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Challenge(TimeStampedModel, SoftDeletableModel):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    slug = models.SlugField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title, allow_unicode=True)
            count = 0
            while Challenge.objects.filter(slug=slug).exists():
                count = count + 1
                slug = f"{slug}-{count}"
            self.slug = slug
        super().save(*args, **kwargs)
