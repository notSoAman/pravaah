from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile


def optimize_image(
    file_obj,
    max_width: int,
    quality: int = 80,
    force_jpeg: bool = False,
) -> ContentFile | None:
    """
    Optimizes an image file object using Pillow:
    - Resizes to max_width preserving aspect ratio if width exceeds max_width
    - Respects EXIF orientation tags
    - Converts RGBA/P modes to RGB for JPEG encoding
    - Compresses with requested quality setting

    Returns a ContentFile object containing optimized bytes, or None if file_obj is invalid.
    """
    if not file_obj:
        return None

    try:
        if hasattr(file_obj, "open"):
            file_obj.open("rb")
        file_obj.seek(0)
        img_bytes = file_obj.read()
        if not img_bytes:
            return None
        img = Image.open(BytesIO(img_bytes))
    except Exception:
        return None

    # Handle EXIF orientation automatically
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    orig_format = (img.format or "JPEG").upper()
    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )

    # Resize image if width exceeds max_width
    width, height = img.size
    if width > max_width:
        new_width = max_width
        new_height = max(1, int(height * (max_width / width)))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    output_buffer = BytesIO()

    if force_jpeg or not has_alpha or orig_format in ("JPEG", "JPG"):
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(output_buffer, format="JPEG", quality=quality, optimize=True)
        filename = getattr(file_obj, "name", "image.jpg")
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        new_filename = f"{base_name}.jpg"
    else:
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if has_alpha else "RGB")
        img.save(output_buffer, format="PNG", optimize=True)
        new_filename = getattr(file_obj, "name", "image.png")

    output_buffer.seek(0)
    return ContentFile(output_buffer.read(), name=new_filename)


def optimize_cover_image(file_obj) -> ContentFile | None:
    """Cover Images: max width 1600px, JPEG quality 82."""
    return optimize_image(file_obj, max_width=1600, quality=82)


def optimize_gallery_image(file_obj) -> ContentFile | None:
    """Gallery Images: max width 1920px, JPEG quality 80."""
    return optimize_image(file_obj, max_width=1920, quality=80)


def optimize_team_photo(file_obj) -> ContentFile | None:
    """Team Photos: max width 800px, JPEG quality 80."""
    return optimize_image(file_obj, max_width=800, quality=80)
