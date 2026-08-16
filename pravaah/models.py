from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Member(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    photo = models.ImageField(upload_to="members/")
    position = models.CharField(max_length=150)
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    date = models.DateField()
    cover_image = models.ImageField(upload_to="events/covers/")
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class EventImage(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="gallery",
    )
    image = models.ImageField(upload_to="events/gallery/")
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.event.title} - Image {self.order}"


class Movie(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    poster_image = models.ImageField(upload_to="movies/posters/")
    youtube_url = models.URLField()
    release_date = models.DateField()

    class Meta:
        ordering = ["-release_date"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Journal(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    author = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="journal_articles",
    )
    cover_image = models.ImageField(upload_to="journal/covers/")
    content = models.TextField(
        help_text="Sanitized HTML content imported from Notion."
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    @property
    def is_published(self):
        return (
            self.published_at is not None
            and self.published_at <= timezone.now()
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class JournalImport(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    title = models.CharField(max_length=250)
    author = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name="journal_imports",
    )
    cover_image = models.ImageField(upload_to="journal/import_covers/")
    published_at = models.DateTimeField(null=True, blank=True)
    source_zip = models.FileField(upload_to="journal/imports/")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_message = models.TextField(blank=True)
    journal = models.OneToOneField(
        Journal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="import_record",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class HeroSlide(models.Model):
    image = models.ImageField(upload_to="hero/")
    message = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.message