import os
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand

from filamentcolors.colors import hex_to_rgb
from filamentcolors.models import RAL, Pantone, PantonePMS, Swatch


class Command(BaseCommand):
    help = "Import information from pantone.db"

    def handle(self, *args, **options):
        if not os.path.exists(os.path.join(settings.BASE_DIR, "pantone.db")):
            self.stdout.write(self.style.ERROR("Cannot find pantone.db."))
            return

        con = sqlite3.connect(os.path.join(settings.BASE_DIR, "pantone.db"))
        cur = con.cursor()

        if Pantone.objects.count() == 0:
            to_write = []
            for obj in cur.execute("select * from pantone").fetchall():
                to_write.append(
                    Pantone(
                        code=obj[0],
                        rgb_r=obj[1],
                        rgb_g=obj[2],
                        rgb_b=obj[3],
                        hex_color=obj[4][1:],
                        name=obj[5],
                        category=obj[6],
                    )
                )
            Pantone.objects.bulk_create(to_write)
            self.stdout.write(
                self.style.SUCCESS(f"Created {Pantone.objects.count()} objects!")
            )
        else:
            self.stdout.write(
                self.style.ERROR("There are already Pantone objects present. Skipping.")
            )

        if RAL.objects.count() == 0:
            to_write = []
            for obj in cur.execute("select * from ral").fetchall():
                to_write.append(
                    RAL(
                        code=obj[0],
                        rgb_r=obj[1],
                        rgb_g=obj[2],
                        rgb_b=obj[3],
                        hex_color=obj[4][1:],
                        name=obj[5],
                        category=obj[6],
                    )
                )
            RAL.objects.bulk_create(to_write)
            self.stdout.write(
                self.style.SUCCESS(f"Created {RAL.objects.count()} objects!")
            )
        else:
            self.stdout.write(
                self.style.ERROR("There are already RAL objects present. Skipping.")
            )

        if PantonePMS.objects.count() == 0:
            to_write = []
            for obj in cur.execute("select * from pms").fetchall():
                code, hex_code = obj
                r, g, b = hex_to_rgb(hex_code)
                to_write.append(
                    PantonePMS(code=code, rgb_r=r, rgb_g=g, rgb_b=b, hex_color=hex_code)
                )
            PantonePMS.objects.bulk_create(to_write)
            self.stdout.write(
                self.style.SUCCESS(f"Created {PantonePMS.objects.count()} objects!")
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    "There are already PantonePMS objects present. Skipping."
                )
            )

        # self.stdout.write(self.style.SUCCESS("Loading data..."))
        # count = 0
        # for s in Swatch.objects.filter(published=True):
        #     # s.regenerate_all(Swatch.objects.filter(published=True))
        #     s.generate_closest_pms()
        #     s.save()
        #     count += 1
        #     if count % 50 == 0:
        #         self.stdout.write(f"Rebuilt {count}...")
        self.stdout.write(self.style.SUCCESS("Rebuild complete!"))
