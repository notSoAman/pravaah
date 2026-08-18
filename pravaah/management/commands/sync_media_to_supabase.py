import os
import sys
import mimetypes
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = "Uploads all local media files from media/ directory to Supabase Storage concurrently."

    def add_arguments(self, parser):
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help="Overwrite files in Supabase Storage even if they already exist.",
        )

    def handle(self, *args, **options):
        overwrite = options.get("overwrite", False)
        media_dir = Path(settings.BASE_DIR) / "media"

        if not media_dir.exists():
            self.stdout.write(self.style.ERROR(f"Local media directory '{media_dir}' does not exist."))
            return

        self.stdout.write(self.style.MIGRATE_HEADING("=== Uploading Local Media to Supabase Storage ==="))
        self.stdout.write(f"Media Directory: {media_dir}")
        self.stdout.write(f"Supabase Bucket: {getattr(settings, 'SUPABASE_BUCKET', 'media-pravaah')}\n")
        sys.stdout.flush()

        files_to_process = []
        for root, _, files in os.walk(media_dir):
            for file_name in files:
                full_path = Path(root) / file_name
                rel_path = full_path.relative_to(media_dir).as_posix()
                if not file_name.startswith(".") and "__MACOSX" not in rel_path:
                    files_to_process.append((full_path, rel_path, file_name))

        def upload_file(full_path, rel_path, file_name):
            try:
                if not overwrite and default_storage.exists(rel_path):
                    return ("SKIPPED", rel_path, "Already exists")

                with open(full_path, "rb") as f:
                    file_bytes = f.read()

                content_type, _ = mimetypes.guess_type(file_name)
                if not content_type:
                    content_type = "application/octet-stream"

                if hasattr(default_storage, "_get_headers"):
                    upload_url = f"{default_storage.project_url}/storage/v1/object/{default_storage.bucket_name}/{rel_path}"
                    headers = default_storage._get_headers(content_type=content_type, upsert=True)
                    req = urllib.request.Request(upload_url, data=file_bytes, headers=headers, method="POST")
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        pass
                else:
                    from django.core.files.base import ContentFile
                    default_storage.save(rel_path, ContentFile(file_bytes))

                return ("SUCCESS", rel_path, None)
            except Exception as exc:
                return ("FAILED", rel_path, str(exc))

        uploaded_count = 0
        skipped_count = 0
        failed_count = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(upload_file, full_path, rel_path, file_name)
                for full_path, rel_path, file_name in files_to_process
            ]
            for future in as_completed(futures):
                status, rel_path, err = future.result()
                if status == "SUCCESS":
                    uploaded_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  [OK] {rel_path}"))
                elif status == "SKIPPED":
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f"  [SKIPPED] {rel_path}"))
                else:
                    failed_count += 1
                    self.stdout.write(self.style.ERROR(f"  [FAILED] {rel_path}: {err}"))
                sys.stdout.flush()

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Upload Summary ==="))
        self.stdout.write(self.style.SUCCESS(f"Uploaded : {uploaded_count} files"))
        self.stdout.write(self.style.WARNING(f"Skipped  : {skipped_count} files"))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f"Failed   : {failed_count} files"))
        else:
            self.stdout.write(self.style.SUCCESS("Failed   : 0 files"))
        sys.stdout.flush()
