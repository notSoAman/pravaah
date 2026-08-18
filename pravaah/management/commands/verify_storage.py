import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.conf import settings
from pravaah.models import Member, Event, EventImage, Movie, Journal, HeroSlide


class Command(BaseCommand):
    help = "Inspects all models with media fields and verifies that referenced files exist in storage."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Starting Storage Verification ==="))
        self.stdout.write(f"Active Storage Backend: {settings.STORAGES['default']['BACKEND']}")
        self.stdout.write(f"USE_SUPABASE_STORAGE: {getattr(settings, 'USE_SUPABASE_STORAGE', False)}")
        sys.stdout.flush()

        media_targets = [
            (Member, "photo"),
            (Event, "cover_image"),
            (EventImage, "image"),
            (Movie, "poster_image"),
            (Journal, "cover_image"),
            (HeroSlide, "image"),
        ]

        total_checked = 0
        total_found = 0
        total_missing = 0
        missing_records = []

        def check_file(model_name, pk, field_name, file_field):
            file_path = file_field.name
            try:
                exists = file_field.storage.exists(file_path)
            except Exception:
                exists = False
            return (model_name, pk, field_name, file_path, exists)

        tasks = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for model_cls, field_name in media_targets:
                model_name = model_cls.__name__
                queryset = model_cls.objects.all()
                for obj in queryset:
                    file_field = getattr(obj, field_name, None)
                    if file_field and file_field.name:
                        tasks.append(
                            executor.submit(
                                check_file, model_name, obj.pk, field_name, file_field
                            )
                        )

            for future in as_completed(tasks):
                total_checked += 1
                model_name, pk, field_name, file_path, exists = future.result()
                if exists:
                    total_found += 1
                    self.stdout.write(self.style.SUCCESS(f"  [OK] {model_name} ID={pk} [{field_name}]: {file_path}"))
                else:
                    total_missing += 1
                    missing_records.append((model_name, pk, field_name, file_path))
                    self.stdout.write(self.style.ERROR(f"  [MISSING] {model_name} ID={pk} [{field_name}]: {file_path}"))
                sys.stdout.flush()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Verification Summary ==="))
        self.stdout.write(f"Total media files checked : {total_checked}")
        self.stdout.write(self.style.SUCCESS(f"Total files found         : {total_found}"))

        if total_missing == 0:
            self.stdout.write(self.style.SUCCESS("All referenced media files exist in storage! No missing files detected."))
        else:
            self.stdout.write(self.style.ERROR(f"Total missing files       : {total_missing}"))
            self.stdout.write(self.style.WARNING("\nMissing File Details:"))
            for model_name, pk, field_name, file_path in missing_records:
                self.stdout.write(f" - {model_name} (ID={pk}) [{field_name}]: {file_path}")
        sys.stdout.flush()
