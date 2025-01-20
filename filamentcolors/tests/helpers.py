from io import BytesIO
from random import randrange

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image

from filamentcolors.models import (
    FilamentType,
    GenericFilamentType,
    Manufacturer,
    PurchaseLocation,
    Retailer,
    Swatch,
)
from filamentcolors.tests.constants import TestColors


def test_image(name="test.jpg", size=(4056, 3040)):
    # https://stackoverflow.com/q/69141293
    # the size is the swatchrig photo size
    solidcolor = (randrange(0, 255), randrange(0, 255), randrange(0, 255))

    img = Image.new("RGB", size, solidcolor)
    output = BytesIO()
    img.save(output, format="JPEG", quality=60)
    output.seek(0)
    return InMemoryUploadedFile(
        output, "ImageField", "test.jpg", "image/jpeg", len(output.read()), None
    )


BASE_MANUFACTURER_DATA = {
    "name": "Tester Materials",
    "website": "",
    "swap_purchase_buttons": False,
    "affiliate_portal": "https://test.test/affiliate",
    "affiliate_url_param": "&foo=bar",
}
BASE_RETAILER_DATA = {"name": "Tester Plastics Retail", "website": "http://example.com"}
BASE_SWATCH_DATA = {
    "manufacturer": None,  # needs to be replaced
    "filament_type": None,  # needs to be replaced
    "hex_color": TestColors.WHITE1,
    "color_name": Swatch.WHITE,
    "color_parent": Swatch.WHITE,
    "image_front": test_image(),
    "image_back": test_image(),
    "image_other": test_image(),
    "image_opengraph": test_image(),
}
BASE_FILAMENT_TYPE_DATA = {"name": "Test", "parent_type": None}
BASE_GENERIC_FILAMENT_TYPE_DATA = {"name": "TestBase"}
BASE_PURCHASE_LOCATION_DATA = {
    "retailer": None,
    "url": "https://example.com/shop/stuff",
    "swatch": None,
}


def get_generic_filament_type(**kwargs) -> GenericFilamentType:
    info = {
        **BASE_GENERIC_FILAMENT_TYPE_DATA,
        **{key: kwargs[key] for key in kwargs if key in dir(GenericFilamentType)},
    }

    obj, _ = GenericFilamentType.objects.get_or_create(**info)
    return obj


def get_filament_type(**kwargs) -> FilamentType:
    info = {
        **BASE_FILAMENT_TYPE_DATA,
        **{key: kwargs[key] for key in kwargs if key in dir(FilamentType)},
    }

    if not info.get("parent_type"):
        info["parent_type"] = get_generic_filament_type()

    obj, _ = FilamentType.objects.get_or_create(**info)
    return obj


def get_swatch(**kwargs) -> Swatch:
    info = {
        **BASE_SWATCH_DATA,
        **{key: kwargs[key] for key in kwargs if key in dir(Swatch)},
    }
    if not info.get("manufacturer"):
        info["manufacturer"] = get_manufacturer()
    if not info.get("filament_type"):
        info["filament_type"] = get_filament_type()
    obj, _ = Swatch.objects.get_or_create(**info)
    if not obj.lab_l:
        obj._set_rgb_from_hex()
        obj._set_lab_from_rgb()
        obj.save()
    return obj


def get_manufacturer(**kwargs) -> Manufacturer:
    info = {
        **BASE_MANUFACTURER_DATA,
        **{key: kwargs[key] for key in kwargs if key in dir(Manufacturer)},
    }
    obj, _ = Manufacturer.objects.get_or_create(**info)
    return obj


def get_retailer(**kwargs) -> Manufacturer:
    info = {
        **BASE_RETAILER_DATA,
        **{key: kwargs[key] for key in kwargs if key in dir(Retailer)},
    }
    obj, _ = Retailer.objects.get_or_create(**info)
    return obj


def get_purchase_location(**kwargs) -> PurchaseLocation:
    info = {
        **BASE_PURCHASE_LOCATION_DATA,
        **{key: kwargs[key] for key in kwargs if key in dir(PurchaseLocation)},
    }
    if not kwargs.get("swatch"):
        info["swatch"] = get_swatch()
    if not kwargs.get("retailer"):
        info["retailer"] = get_retailer()
    obj, _ = PurchaseLocation.objects.get_or_create(**info)
    return obj
