from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    S3Boto3Storage backend configured for Cloudflare R2 media assets.
    Stores uploaded media under the 'media/' prefix in the R2 bucket.
    """
    location = "media"
    file_overwrite = False
