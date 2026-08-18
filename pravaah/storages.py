import json
import mimetypes
import os
import urllib.request
import boto3
from botocore.config import Config
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseStorage(Storage):
    """
    Storage backend for Supabase Storage using boto3 and Supabase REST API.
    Environment-variable driven via USE_SUPABASE_STORAGE, SUPABASE_PROJECT_URL,
    SUPABASE_SECRET_KEY, and SUPABASE_BUCKET.
    """

    def __init__(self, project_url=None, secret_key=None, bucket_name=None):
        self.project_url = (
            project_url
            or getattr(settings, "SUPABASE_PROJECT_URL", "")
            or os.environ.get("SUPABASE_PROJECT_URL", "")
        ).rstrip("/")
        self.secret_key = (
            secret_key
            or getattr(settings, "SUPABASE_SECRET_KEY", "")
            or os.environ.get("SUPABASE_SECRET_KEY", "")
        )
        self.bucket_name = (
            bucket_name
            or getattr(settings, "SUPABASE_BUCKET", "")
            or os.environ.get("SUPABASE_BUCKET", "media-pravaah")
        )

        project_ref = (
            self.project_url.split("://")[-1].split(".")[0]
            if "://" in self.project_url
            else ""
        )
        s3_endpoint = (
            f"{self.project_url}/storage/v1/s3" if self.project_url else ""
        )

        if s3_endpoint and project_ref and self.secret_key:
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=s3_endpoint,
                aws_access_key_id=project_ref,
                aws_secret_access_key=self.secret_key,
                region_name="global",
                config=Config(
                    s3={"addressing_style": "path"}, signature_version="s3v4"
                ),
            )
        else:
            self.s3_client = None

    def _get_headers(self, content_type=None, upsert=True):
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "apikey": self.secret_key,
        }
        if upsert:
            headers["x-upsert"] = "true"
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _save(self, name, content):
        clean_name = name.lstrip("/")
        upload_url = f"{self.project_url}/storage/v1/object/{self.bucket_name}/{clean_name}"

        if hasattr(content, "chunks"):
            file_bytes = b"".join(chunk for chunk in content.chunks())
        else:
            file_bytes = content.read()

        content_type = getattr(content, "content_type", None)
        if not content_type:
            content_type, _ = mimetypes.guess_type(clean_name)
        if not content_type:
            content_type = "application/octet-stream"

        headers = self._get_headers(content_type=content_type, upsert=True)
        req = urllib.request.Request(
            upload_url, data=file_bytes, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            pass
        return clean_name

    def _open(self, name, mode="rb"):
        clean_name = name.lstrip("/")
        public_url = self.url(clean_name)
        req = urllib.request.Request(public_url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return ContentFile(resp.read(), name=clean_name)

    def exists(self, name):
        clean_name = name.lstrip("/")
        info_url = f"{self.project_url}/storage/v1/object/info/public/{self.bucket_name}/{clean_name}"
        headers = self._get_headers(upsert=False)
        req = urllib.request.Request(info_url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                return resp.status == 200
        except Exception:
            return False

    def delete(self, name):
        clean_name = name.lstrip("/")
        delete_url = f"{self.project_url}/storage/v1/object/{self.bucket_name}"
        headers = self._get_headers(content_type="application/json", upsert=False)
        data = json.dumps({"prefixes": [clean_name]}).encode("utf-8")
        req = urllib.request.Request(
            delete_url, data=data, headers=headers, method="DELETE"
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                pass
        except Exception:
            pass


    def url(self, name):
        clean_name = name.lstrip("/")
        return f"{self.project_url}/storage/v1/object/public/{self.bucket_name}/{clean_name}"


MediaStorage = SupabaseStorage
