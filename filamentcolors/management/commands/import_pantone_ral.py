import os
import sqlite3

from colormath.color_conversions import convert_color
from colormath.color_objects import LabColor, sRGBColor
from django.conf import settings
from django.core.management.base import BaseCommand

from filamentcolors.colors import hex_to_rgb
from filamentcolors.models import RAL, Pantone, PantonePMS, Swatch


class Command(BaseCommand):
    help = "Import information from pantone.db"

    def rgb_to_lab(self, r: int, g: int, b: int):
        color = convert_color(sRGBColor(r, g, b, is_upscaled=True), LabColor)
        color.set_illuminant("d65")
        color.set_observer("10")
        return float(color.lab_l), float(color.lab_a), float(color.lab_b)

    def handle(self, *args, **options):
        if not os.path.exists(os.path.join(settings.BASE_DIR, "pantone.db")):
            self.stdout.write(self.style.ERROR("Cannot find pantone.db."))
            return

        con = sqlite3.connect(os.path.join(settings.BASE_DIR, "pantone.db"))
        cur = con.cursor()

        if Pantone.objects.count() == 0:
            to_write = []
            for obj in cur.execute("select * from pantone").fetchall():
                L, a, b = self.rgb_to_lab(obj[1], obj[2], obj[3])
                to_write.append(
                    Pantone(
                        code=obj[0],
                        rgb_r=obj[1],
                        rgb_g=obj[2],
                        rgb_b=obj[3],
                        lab_l=L,
                        lab_a=a,
                        lab_b=b,
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
                L, a, b = self.rgb_to_lab(obj[1], obj[2], obj[3])
                to_write.append(
                    RAL(
                        code=obj[0],
                        rgb_r=obj[1],
                        rgb_g=obj[2],
                        rgb_b=obj[3],
                        lab_l=L,
                        lab_a=a,
                        lab_b=b,
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
                L, a, b = self.rgb_to_lab(r, g, b)
                to_write.append(
                    PantonePMS(
                        code=code,
                        rgb_r=r,
                        rgb_g=g,
                        rgb_b=b,
                        lab_l=L,
                        lab_a=a,
                        lab_b=b,
                        hex_color=hex_code,
                    )
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
