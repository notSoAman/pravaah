from django.contrib import admin, messages
from django.utils.html import format_html

from .models import Event, EventImage, HeroSlide, Journal, JournalImport, Member, Movie
from .services.importer import process_journal_import


def render_thumbnail(file_field, width=50, height=50):
    if file_field and hasattr(file_field, "url") and file_field.name:
        try:
            return format_html(
                '<img src="{}" style="width: {}px; height: {}px; object-fit: cover; border-radius: 4px; border: 1px solid #333;" />',
                file_field.url,
                width,
                height,
            )
        except Exception:
            pass
    return format_html('<span style="color: #666; font-size: 11px;">No Image</span>')


def render_preview(file_field, max_width=300):
    if file_field and hasattr(file_field, "url") and file_field.name:
        try:
            return format_html(
                '<div style="margin-top: 5px;"><img src="{}" style="max-width: {}px; max-height: 250px; object-fit: contain; border-radius: 6px; border: 1px solid #444;" /></div>',
                file_field.url,
                max_width,
            )
        except Exception:
            pass
    return format_html('<span style="color: #888;">No image available</span>')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "name", "position", "slug")
    list_display_links = ("thumbnail", "name")
    search_fields = ("name", "position", "bio")
    list_filter = ("position",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)

    @admin.display(description="Photo")
    def thumbnail(self, obj):
        return render_thumbnail(obj.photo)

    @admin.display(description="Photo Preview")
    def image_preview(self, obj):
        return render_preview(obj.photo)


class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1
    fields = ("image", "image_preview", "caption", "order")
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj):
        return render_thumbnail(obj.image, width=80, height=60)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "date", "created_at")
    list_display_links = ("thumbnail", "title")
    search_fields = ("title", "description")
    list_filter = ("date",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    inlines = [EventImageInline]

    @admin.display(description="Cover")
    def thumbnail(self, obj):
        return render_thumbnail(obj.cover_image, width=70, height=45)

    @admin.display(description="Cover Preview")
    def image_preview(self, obj):
        return render_preview(obj.cover_image)


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "event", "caption", "order")
    list_filter = ("event",)
    search_fields = ("caption", "event__title")
    readonly_fields = ("image_preview",)

    @admin.display(description="Image")
    def thumbnail(self, obj):
        return render_thumbnail(obj.image, width=70, height=50)

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        return render_preview(obj.image)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "release_date", "youtube_url")
    list_display_links = ("thumbnail", "title")
    search_fields = ("title", "description")
    list_filter = ("release_date",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview",)

    @admin.display(description="Poster")
    def thumbnail(self, obj):
        return render_thumbnail(obj.poster_image, width=45, height=65)

    @admin.display(description="Poster Preview")
    def image_preview(self, obj):
        return render_preview(obj.poster_image)


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "author", "published_at", "created_at")
    list_display_links = ("thumbnail", "title")
    search_fields = ("title", "content")
    list_filter = ("author", "published_at")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")

    @admin.display(description="Cover")
    def thumbnail(self, obj):
        return render_thumbnail(obj.cover_image, width=70, height=45)

    @admin.display(description="Cover Preview")
    def image_preview(self, obj):
        return render_preview(obj.cover_image)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "message", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("message",)
    readonly_fields = ("image_preview",)

    @admin.display(description="Slide Image")
    def thumbnail(self, obj):
        return render_thumbnail(obj.image, width=80, height=45)

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        return render_preview(obj.image)


@admin.register(JournalImport)
class JournalImportAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "title", "author", "status", "published_at", "created_at")
    list_filter = ("status", "author")
    search_fields = ("title", "error_message")
    readonly_fields = ("image_preview", "status", "error_message", "journal", "created_at", "updated_at")

    @admin.display(description="Cover")
    def thumbnail(self, obj):
        return render_thumbnail(obj.cover_image, width=60, height=40)

    @admin.display(description="Cover Preview")
    def image_preview(self, obj):
        return render_preview(obj.cover_image)

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