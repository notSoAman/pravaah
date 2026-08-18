from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Event, EventImage, HeroSlide, Journal, JournalImport, Member, Movie
from .utils.image_processing import (
    optimize_cover_image,
    optimize_gallery_image,
    optimize_team_photo,
)


def _is_file_referenced_elsewhere(model_cls, field_name, file_name, exclude_pk=None):
    if not file_name:
        return False
    qs = model_cls.objects.filter(**{field_name: file_name})
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    return qs.exists()


def _cleanup_old_file_on_update(instance, field_name):
    """Deletes old file from storage when an image field is replaced."""
    if not instance.pk:
        return

    try:
        old_instance = instance.__class__.objects.get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return

    old_file = getattr(old_instance, field_name, None)
    new_file = getattr(instance, field_name, None)

    if old_file and old_file.name and (not new_file or old_file.name != getattr(new_file, "name", None)):
        if not _is_file_referenced_elsewhere(
            instance.__class__, field_name, old_file.name, exclude_pk=instance.pk
        ):
            try:
                old_file.delete(save=False)
            except Exception:
                pass


def _delete_file_on_record_delete(instance, field_name):
    """Deletes associated file from storage when a record is deleted."""
    file_field = getattr(instance, field_name, None)
    if file_field and file_field.name:
        if not _is_file_referenced_elsewhere(
            instance.__class__, field_name, file_field.name, exclude_pk=instance.pk
        ):
            try:
                file_field.delete(save=False)
            except Exception:
                pass


def _process_image_upload(instance, field_name, optimizer_fn):
    field_file = getattr(instance, field_name, None)
    if not field_file or getattr(field_file, "_optimized", False):
        return

    if hasattr(field_file, "_file") and field_file._file is not None:
        optimized_content = optimizer_fn(field_file._file)
        if optimized_content:
            setattr(instance, field_name, optimized_content)
            new_field_file = getattr(instance, field_name)
            setattr(new_field_file, "_optimized", True)


@receiver(pre_save, sender=Event)
def handle_event_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "cover_image")
    _process_image_upload(instance, "cover_image", optimize_cover_image)


@receiver(post_delete, sender=Event)
def handle_event_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "cover_image")


@receiver(pre_save, sender=EventImage)
def handle_event_image_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "image")
    _process_image_upload(instance, "image", optimize_gallery_image)


@receiver(post_delete, sender=EventImage)
def handle_event_image_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "image")


@receiver(pre_save, sender=Member)
def handle_member_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "photo")
    _process_image_upload(instance, "photo", optimize_team_photo)


@receiver(post_delete, sender=Member)
def handle_member_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "photo")


@receiver(pre_save, sender=Movie)
def handle_movie_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "poster_image")
    _process_image_upload(instance, "poster_image", optimize_cover_image)


@receiver(post_delete, sender=Movie)
def handle_movie_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "poster_image")


@receiver(pre_save, sender=Journal)
def handle_journal_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "cover_image")
    _process_image_upload(instance, "cover_image", optimize_cover_image)


@receiver(post_delete, sender=Journal)
def handle_journal_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "cover_image")


@receiver(pre_save, sender=JournalImport)
def handle_journal_import_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "cover_image")
    _cleanup_old_file_on_update(instance, "source_zip")
    _process_image_upload(instance, "cover_image", optimize_cover_image)


@receiver(post_delete, sender=JournalImport)
def handle_journal_import_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "cover_image")
    _delete_file_on_record_delete(instance, "source_zip")


@receiver(pre_save, sender=HeroSlide)
def handle_hero_slide_pre_save(sender, instance, **kwargs):
    _cleanup_old_file_on_update(instance, "image")
    _process_image_upload(instance, "image", optimize_gallery_image)


@receiver(post_delete, sender=HeroSlide)
def handle_hero_slide_post_delete(sender, instance, **kwargs):
    _delete_file_on_record_delete(instance, "image")
