from django.contrib import admin

from .models import *

from django.contrib import messages
from .services.importer import process_journal_import

admin.site.register(Member)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(Movie)
admin.site.register(Journal)
admin.site.register(HeroSlide)


@admin.register(JournalImport)
class JournalImportAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "published_at", "created_at")
    list_filter = ("status", "author")
    search_fields = ("title", "error_message")
    readonly_fields = ("status", "error_message", "journal", "created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        article_title = obj.title
        journal, success = process_journal_import(obj)
        if success:
            self.message_user(
                request,
                f"Notion article '{article_title}' converted into published Journal and import record auto-deleted!",
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                f"Import conversion failed for '{article_title}': {obj.error_message}",
                level=messages.ERROR,
            )