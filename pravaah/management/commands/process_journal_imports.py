from django.core.management.base import BaseCommand
from pravaah.services.importer import process_all_journal_imports


class Command(BaseCommand):
    help = (
        "Iterates over all queued JournalImport objects, converts them into "
        "published Journal model objects, and automatically deletes each "
        "JournalImport object upon successful conversion."
    )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting Notion Journal import conversion loop..."))
        stats = process_all_journal_imports()
        self.stdout.write(
            self.style.SUCCESS(
                f"Conversion completed! Successfully converted & deleted: {stats['successful']} import(s). "
                f"Failed: {stats['failed']} import(s)."
            )
        )
