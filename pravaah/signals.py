from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.files.uploadedfile import UploadedFile

from .models import Event, EventImage, HeroSlide, Journal, JournalImport, Member, Movie
from .utils.image_processing import (
    optimize_cover_image,
    optimize_gallery_image,
    optimize_team_photo,
)


def _process_image_upload(instance, field_name, optimizer_fn):
    field_file = getattr(instance, field_name, None)
    if not field_file or getattr(field_file, "_optimized", False):
        return

    # Check if a new file object is attached to the model instance (e.g. on upload)
    if hasattr(field_file, "_file") and field_file._file is not None:
        optimized_content = optimizer_fn(field_file._file)
        if optimized_content:
            setattr(instance, field_name, optimized_content)
            new_field_file = getattr(instance, field_name)
            setattr(new_field_file, "_optimized", True)


@receiver(pre_save, sender=Event)
def handle_event_cover_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "cover_image", optimize_cover_image)


@receiver(pre_save, sender=Journal)
def handle_journal_cover_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "cover_image", optimize_cover_image)


@receiver(pre_save, sender=JournalImport)
def handle_journal_import_cover_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "cover_image", optimize_cover_image)


@receiver(pre_save, sender=Movie)
def handle_movie_poster_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "poster_image", optimize_cover_image)


@receiver(pre_save, sender=EventImage)
def handle_event_image_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "image", optimize_gallery_image)


@receiver(pre_save, sender=HeroSlide)
def handle_hero_slide_image_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "image", optimize_gallery_image)


@receiver(pre_save, sender=Member)
def handle_member_photo_upload(sender, instance, **kwargs):
    _process_image_upload(instance, "photo", optimize_team_photo)
