import time
from datetime import datetime, timezone
import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Pings the /health/ endpoint of SITE_URL to verify server availability and prevent cold starts."

    def handle(self, *args, **options):
        site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000").rstrip("/")
        health_url = f"{site_url}/health/"
        now_iso = datetime.now(timezone.utc).isoformat()

        self.stdout.write(f"[{now_iso}] Pinging health endpoint: {health_url}")

        start_time = time.time()
        try:
            response = requests.get(health_url, timeout=10)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{now_iso}] OK - Status: {response.status_code} | Latency: {elapsed_ms}ms"
                    )
                )
            else:
                self.stderr.write(
                    self.style.WARNING(
                        f"[{now_iso}] HEALTH CHECK FAILED - Status: {response.status_code} | Latency: {elapsed_ms}ms"
                    )
                )
        except requests.RequestException as exc:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            self.stderr.write(
                self.style.ERROR(
                    f"[{now_iso}] CONNECTION ERROR - Failed to ping {health_url}: {exc} | Latency: {elapsed_ms}ms"
                )
            )
