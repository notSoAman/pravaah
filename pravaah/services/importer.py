import io
import os
import re
import urllib.parse
import zipfile
import bleach
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import slugify
from ..models import Journal, JournalImport


def extract_all_files_from_zip(zip_source, virtual_prefix="") -> dict[str, bytes]:
    """
    Recursively extracts all files from a ZIP archive (handling nested .zip files
    like Notion's multi-part ExportBlock-xxx-Part-1.zip archives).
    Returns a dictionary mapping virtual relative filepaths to file bytes.
    """
    extracted_files = {}

    if isinstance(zip_source, (str, os.PathLike)):
        if not os.path.exists(zip_source):
            return extracted_files
        try:
            with open(zip_source, "rb") as f:
                zip_bytes = f.read()
        except Exception:
            return extracted_files
    elif isinstance(zip_source, bytes):
        zip_bytes = zip_source
    elif hasattr(zip_source, "read"):
        zip_bytes = zip_source.read()
    else:
        return extracted_files

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for item in zf.infolist():
                if item.is_dir() or item.filename.startswith("__MACOSX/"):
                    continue

                clean_name = item.filename
                vpath = (
                    f"{virtual_prefix}/{clean_name}"
                    if virtual_prefix
                    else clean_name
                )
                file_bytes = zf.read(item.filename)

                # If the nested item is itself a ZIP file, extract it recursively!
                if clean_name.lower().endswith(".zip"):
                    nested_dict = extract_all_files_from_zip(
                        file_bytes, virtual_prefix=vpath
                    )
                    extracted_files.update(nested_dict)
                else:
                    extracted_files[vpath] = file_bytes
    except zipfile.BadZipFile:
        pass

    return extracted_files


def process_journal_import(import_obj: JournalImport) -> tuple[Journal | None, bool]:
    """
    Processes a Notion HTML export uploaded via JournalImport model.
    Handles recursive nested ZIP archives, deep folder structures, multi-part HTML exports,
    local asset extraction, YouTube/Vimeo embeds, HTML sanitization, Journal creation,
    and automatic deletion of the JournalImport object upon successful conversion.
    """
    import_obj.status = JournalImport.Status.PROCESSING
    import_obj.error_message = ""
    import_obj.save(update_fields=["status", "error_message"])

    if not import_obj.source_zip:
        import_obj.status = JournalImport.Status.FAILED
        import_obj.error_message = "No ZIP file provided."
        import_obj.save(update_fields=["status", "error_message"])
        return None, False

    zip_path = import_obj.source_zip.path
    if not os.path.exists(zip_path):
        import_obj.status = JournalImport.Status.FAILED
        import_obj.error_message = "Source ZIP file does not exist on storage."
        import_obj.save(update_fields=["status", "error_message"])
        return None, False

    # Extract all files recursively (including nested ZIPs & deep folders)
    all_files = extract_all_files_from_zip(zip_path)
    if not all_files:
        import_obj.status = JournalImport.Status.FAILED
        import_obj.error_message = "Corrupted or invalid ZIP file archive."
        import_obj.save(update_fields=["status", "error_message"])
        return None, False

    # Locate all HTML files in extracted file tree (excluding macOS hidden files)
    html_entries = [
        path
        for path in all_files.keys()
        if (path.lower().endswith(".html") or path.lower().endswith(".htm"))
        and not os.path.basename(path).startswith(".")
    ]

    if not html_entries:
        import_obj.status = JournalImport.Status.FAILED
        import_obj.error_message = "No HTML file found inside ZIP archive."
        import_obj.save(update_fields=["status", "error_message"])
        return None, False

    # Sort HTML files cleanly (main root-most files first, then parts in sequence)
    html_entries.sort(key=lambda x: (x.count("/"), len(x), x))

    article_slug = slugify(import_obj.title)
    if not article_slug:
        article_slug = f"journal-article-{import_obj.id}"

    combined_body_htmls = []

    for html_path in html_entries:
        raw_html = all_files[html_path].decode("utf-8", errors="replace")
        soup = BeautifulSoup(raw_html, "html.parser")

        body = (
            soup.find(class_="page-body")
            or soup.find("article")
            or soup.find("body")
            or soup
        )

        # Strip Notion header and properties table
        for header in body.find_all("header"):
            header.decompose()
        for meta_table in body.find_all("table", class_="properties"):
            meta_table.decompose()

        # Process local & external images
        html_dir = os.path.dirname(html_path)

        for img in body.find_all("img"):
            src = img.get("src", "")
            if not src or src.startswith(("http://", "https://", "//", "data:")):
                continue

            decoded_src = urllib.parse.unquote(src)
            file_basename = os.path.basename(decoded_src)

            # Try exact relative path resolution
            target_vpath = (
                os.path.normpath(os.path.join(html_dir, decoded_src))
                if html_dir
                else decoded_src
            )

            matched_vpath = None
            if target_vpath in all_files:
                matched_vpath = target_vpath
            else:
                # Fuzzy fallback lookup by basename or path ending across extracted tree
                for key in all_files.keys():
                    if (
                        key.lower().endswith(decoded_src.lower())
                        or os.path.basename(key).lower() == file_basename.lower()
                    ):
                        matched_vpath = key
                        break

            if matched_vpath and matched_vpath in all_files:
                image_bytes = all_files[matched_vpath]
                dest_relative_path = f"journal/{article_slug}/{file_basename}"

                if default_storage.exists(dest_relative_path):
                    default_storage.delete(dest_relative_path)
                saved_path = default_storage.save(
                    dest_relative_path, ContentFile(image_bytes)
                )
                img["src"] = default_storage.url(saved_path)

        # Process Video Embeds (YouTube / Vimeo)
        for element in list(body.find_all(["iframe", "a", "figure"])):
            target_url = ""
            if element.name == "iframe":
                target_url = element.get("src", "")
            elif element.name == "a":
                target_url = element.get("href", "")
            elif element.name == "figure":
                child = element.find(["iframe", "a"])
                if child:
                    target_url = child.get("src") or child.get("href") or ""

            if not target_url:
                continue

            yt_match = re.search(
                r'(?:v=|\/embed\/|\/1.1\/|\/v\/|https:\/\/youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})',
                target_url,
            )
            if yt_match:
                video_id = yt_match.group(1)
                embed_html = (
                    f'<div class="aspect-video w-full overflow-hidden bg-[#0a0a0a] my-8 border border-[#111] relative">'
                    f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}?rel=0&modestbranding=1" '
                    f'class="w-full h-full border-0" '
                    f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                    f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
                )
                embed_soup = BeautifulSoup(embed_html, "html.parser")
                element.replace_with(embed_soup)
                continue

            vimeo_match = re.search(r'vimeo\.com\/(?:video\/)?([0-9]+)', target_url)
            if vimeo_match:
                video_id = vimeo_match.group(1)
                embed_html = (
                    f'<div class="aspect-video w-full overflow-hidden bg-[#0a0a0a] my-8 border border-[#111] relative">'
                    f'<iframe src="https://player.vimeo.com/video/{video_id}" '
                    f'class="w-full h-full border-0" '
                    f'allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe></div>'
                )
                embed_soup = BeautifulSoup(embed_html, "html.parser")
                element.replace_with(embed_soup)
                continue

            if element.name in ["video", "embed", "object"]:
                element.decompose()

        part_html = "".join(str(c) for c in body.contents)
        if part_html.strip():
            combined_body_htmls.append(part_html)

    full_extracted_html = "\n\n".join(combined_body_htmls)

    # Sanitize HTML using bleach
    allowed_tags = [
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'strong', 'em', 'b', 'i', 'u', 'a', 'blockquote',
        'ul', 'ol', 'li', 'hr', 'br', 'span', 'div',
        'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
        'img', 'iframe', 'figure', 'figcaption'
    ]
    allowed_attributes = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height', 'class', 'loading'],
        'iframe': [
            'src', 'title', 'width', 'height', 'allow',
            'allowfullscreen', 'referrerpolicy', 'class', 'frameborder'
        ],
        '*': ['class']
    }
    allowed_protocols = ['http', 'https', 'mailto']

    sanitized_html = bleach.clean(
        full_extracted_html,
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=True,
    )

    # Create or update Journal instance with unique slug resolution
    journal = import_obj.journal or Journal.objects.filter(slug=article_slug).first()
    if not journal:
        base_slug = article_slug
        counter = 1
        while Journal.objects.filter(slug=article_slug).exists():
            article_slug = f"{base_slug}-{counter}"
            counter += 1

        journal = Journal(
            title=import_obj.title,
            slug=article_slug,
            author=import_obj.author,
            cover_image=import_obj.cover_image,
            content=sanitized_html,
            published_at=import_obj.published_at or timezone.now(),
        )
        journal.save()
    else:
        journal.title = import_obj.title
        journal.author = import_obj.author
        journal.cover_image = import_obj.cover_image
        journal.content = sanitized_html
        if import_obj.published_at:
            journal.published_at = import_obj.published_at
        journal.save()

    # Clean up uploaded zip file from disk if present
    if import_obj.source_zip and os.path.exists(import_obj.source_zip.path):
        try:
            os.remove(import_obj.source_zip.path)
        except OSError:
            pass

    # Automatically delete the JournalImport object upon successful conversion
    import_obj.delete()
    return journal, True


def process_all_journal_imports():
    """
    Processes all pending or queued JournalImport objects continuously
    until every object in JournalImport is converted to a Journal and auto-deleted.
    Returns stats dict with counts of successful and failed imports.
    """
    successful_count = 0
    failed_count = 0
    failed_ids = set()

    while True:
        import_obj = (
            JournalImport.objects.exclude(id__in=failed_ids)
            .order_by("created_at")
            .first()
        )
        if not import_obj:
            break

        journal, success = process_journal_import(import_obj)
        if success:
            successful_count += 1
        else:
            failed_count += 1
            failed_ids.add(import_obj.id)

    return {"successful": successful_count, "failed": failed_count}
