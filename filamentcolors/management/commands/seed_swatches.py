from datetime import datetime, timezone
import random

from django.core.management import call_command
from django.core.management.base import BaseCommand

from filamentcolors.models import (
    Swatch,
    Manufacturer,
    FilamentType,
    GenericFilamentType,
)
from filamentcolors.constants import (
    NAMED_COLORS,
    HUMAN_READABLE_NAMES,
    COLOR_FAMILY_ASSOCIATIONS,
)

JITTER_VALUE = 5


MFR_NAMES: list[str] = [
    # I'm making these up. If any of these exist, that's an oopsie and they
    # should be removed
    "Matrix Materials",
    "Filament Factory",
    "Filament Co.",
    "3DIndustries",
    "Innovative",
    "ABC Filament",
    "3DPrints",
    "99RedPLAs",
    "Castle3D",
    "Filament Depot",
    "Warehouse 3D",
    "PeachPrints",
    "Freshly Minted",
    "Questionable Research",
    "Protractor Labs",
    "Premium Adhesives",
    "Global Industries",
    "Bucket O' Fishament",
    "Oddly Specific",
    "Widget Central",
    "LicensedToPrint",
    "eBooks Are Reading Too",
    "FilamentColors.xyz",
    "OldCameraFilm Studios",
    "EwwGrossWhatIsThat",
    "SingularHeadphone",
    "Pet Rock",
    "MaybePurple Filament",
    "TwistyStand",
    "Slightly Used",
    "3D3D3D",
    "PlasticYarn",
    "Wimdy's",
    "Omelette du Fromage",
]

FILAMENT_TYPES: dict[str, list[str]] = {
    "PLA": [
        "PLA",
        "PLA+",
        "PLA++",
        "PLA Pro",
        "PLA Premium",
        "PLA Ultra",
        "PLA Extreme",
        "PLA Max",
        "PLA Super",
        "CF PLA",
        "Silk PLA",
        "Metallic PLA",
        "Glow-in-the-Dark PLA",
        "High Speed PLA",
    ],
    "PETG": [
        "PETG",
        "PETG+",
        "PETG++",
        "PETG Pro",
        "PETG Premium",
        "PETG Ultra",
        "PETG Extreme",
        "PETG Max",
        "PETG Super",
        "CF PETG",
        "Metallic PETG",
    ],
    "ABS": [
        "ABS",
        "ABS+",
        "ABS++",
        "ABS Pro",
        "ABS Premium",
        "ABS Ultra",
        "ABS Extreme",
        "ABS Max",
        "ABS Super",
        "CF ABS",
        "GF ABS",
        "Silk ABS",
        "Metallic ABS",
        "ASA",
        "ASA+",
        "High Speed ASA",
    ],
    "TPU / TPE": [
        "TPU",
        "TPU Pro",
        "TPU Premium",
        "TPE",
        "TPE Pro",
        "TPE Premium",
    ],
    "Exotics": [
        "Nylon",
        "PP",
        "PC",
        "PVA",
        "HIPS",
        "???",
        "WTF",
        "OMFG",
        "ROFL",
        "BBQ",
        "Unicorn Tears",
        "Dragon Scales",
        "Magic Dust",
        "Mystery Meat",
    ],
}


def jitter_hex(hex_color: str) -> str:
    hex_color = hex_color if "#" in hex_color else f"#{hex_color}"
    r, g, b = hex_color[1:3], hex_color[3:5], hex_color[5:]
    r = max(0, min(int(r, 16) + random.randint(-JITTER_VALUE, JITTER_VALUE), 0xFF))
    g = max(0, min(int(g, 16) + random.randint(-JITTER_VALUE, JITTER_VALUE), 0xFF))
    b = max(0, min(int(b, 16) + random.randint(-JITTER_VALUE, JITTER_VALUE), 0xFF))
    return f"#{r:02X}{g:02X}{b:02X}"


class Command(BaseCommand):
    help = "Create fake swatches for testing."

    def handle(self, *args, **options):
        call_command("migrate")
        call_command("createsuperuser")
        call_command("bootstrap_generic_types")
        call_command("import_pantone_ral")

        self.stdout.write(self.style.SUCCESS("Seeding manufacturers..."))
        for mfr_name in MFR_NAMES:
            # create the slow way so that slugs get built
            Manufacturer.objects.create(name=mfr_name)

        self.stdout.write(self.style.SUCCESS("Seeding filament types..."))
        filament_types_to_create = []
        for filament_type, subtypes in FILAMENT_TYPES.items():
            parent_type = GenericFilamentType.objects.get(name=filament_type)
            for subtype in subtypes:
                filament_types_to_create.append(
                    FilamentType(name=subtype, parent_type=parent_type)
                )
        FilamentType.objects.bulk_create(filament_types_to_create)

        self.stdout.write(self.style.SUCCESS("Seeding swatches. This may take a bit."))

        for i in range(400):
            self.stdout.write(".", ending="")
            self.stdout.flush()
            random_color_key = random.choice(list(NAMED_COLORS.keys()))
            random_hex = NAMED_COLORS[random_color_key]
            random_color_name = HUMAN_READABLE_NAMES[random_color_key]
            random_color_families = COLOR_FAMILY_ASSOCIATIONS[random_color_key]
            jittered = jitter_hex(random_hex)
            swatch = Swatch(
                manufacturer=random.choice(Manufacturer.objects.all()),
                filament_type=random.choice(FilamentType.objects.all()),
                hex_color=jittered[1:],
                color_name=random_color_name,
                published=False,
                color_parent=random_color_families[0],
                alt_color_parent=random_color_families[1],
                date_published=datetime.now(tz=timezone.utc),
                amazon_purchase_link=(
                    "https://example.com" if random.random() < 0.7 else None
                ),
                mfr_purchase_link=(
                    "https://example.com" if random.random() < 0.7 else None
                ),
                td=round(random.randint(1, 100) + random.random(), 1),
            )
            swatch.rgb_r, swatch.rgb_g, swatch.rgb_b = swatch.get_rgb(swatch.hex_color)
            lab = swatch.get_lab_from_self()
            swatch.lab_l = lab.lab_l
            swatch.lab_a = lab.lab_a
            swatch.lab_b = lab.lab_b
            swatch.save()
            swatch.set_slug()
            swatch.create_local_dev_images()
            swatch.published = True
            swatch.save()

        self.stdout.write(self.style.SUCCESS("Done!"))
        call_command("import_pantone_ral")
        call_command("force_library_rebuild")
