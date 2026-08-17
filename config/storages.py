from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Custom S3/R2 storage backend for media files (films, events, journal assets, team photos).
    """
    location = "media"
    file_overwrite = False
    default_acl = None
