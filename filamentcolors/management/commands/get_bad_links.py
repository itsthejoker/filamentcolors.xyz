import csv
import time

import httpx
from django.core.management.base import BaseCommand
from django.db.models import Q

from filamentcolors.models import Swatch


class Command(BaseCommand):
    help = "Check for links that return weird errors."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting check..."))
        for s in Swatch.objects.filter(
            Q(mfr_purchase_link__isnull=False) | Q(amazon_purchase_link__isnull=False),
            published=True,
        ):
            for link in [s.mfr_purchase_link, s.amazon_purchase_link]:
                if link:
                    try:
                        r = httpx.get(link)
                        if r.status_code != 200:
                            self.stdout.write(f"Got a {r.status_code}...")
                            with open("bad_links.csv", "a") as f:
                                writer = csv.writer(f)
                                writer.writerow(
                                    [
                                        "https://filamentcolors.xyz"
                                        + s.get_absolute_url(),
                                        link,
                                        r.status_code,
                                    ]
                                )
                    except (httpx.HTTPError, TimeoutError):
                        self.stdout.write("Connection error...")
                        with open("bad_links.csv", "a") as f:
                            writer = csv.writer(f)
                            writer.writerow(
                                [
                                    "https://filamentcolors.xyz" + s.get_absolute_url(),
                                    link,
                                    "Connection Error",
                                ]
                            )
                    time.sleep(1)

        self.stdout.write(self.style.SUCCESS("All done!"))
