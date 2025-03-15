import os
import random
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Union
from urllib.parse import urlsplit, urlunparse

import pytz
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colormath.color_objects import LabColor, sRGBColor
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.query import QuerySet
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from PIL import Image as Img
from taggit.managers import TaggableManager

from filamentcolors.colors import clamp, Color
from filamentcolors.exceptions import UnknownSlugOrID
from filamentcolors.constants import OBSERVER_ANGLE, ILLUMINANT


class DistanceMixin:
    def get_distance_to(self, rgb: tuple[str]) -> float:
        target_color = convert_color(sRGBColor(*rgb, is_upscaled=True), LabColor)
        self_color = convert_color(sRGBColor.new_from_rgb_hex(self.hex_color), LabColor)
        return delta_e_cie2000(target_color, self_color)


class Manufacturer(models.Model):
    name = models.CharField(max_length=160)
    website = models.URLField(null=True, blank=True, max_length=2000)
    swap_purchase_buttons = models.BooleanField(
        default=False,
        help_text="List the manufacturer purchase link above the Amazon button.",
    )
    affiliate_portal = models.CharField(max_length=2000, null=True, blank=True)
    affiliate_url_param = models.CharField(max_length=150, null=True, blank=True)
    parent_company_name = models.CharField(
        max_length=160, null=True, blank=True, help_text="Used for purchase buttons."
    )
    slug = models.SlugField(max_length=160, null=True, blank=True)

    @property
    def get_possessive_apostrophe(self):
        return "'" if self.name.endswith("s") else "'s"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                self.parent_company_name if self.parent_company_name else self.name
            )
        super(Manufacturer, self).save(*args, **kwargs)

    def get_slug_from_id_or_slug(self, slug_or_id: str | int) -> str:
        mfr_id = False
        if isinstance(slug_or_id, int) or slug_or_id.isdigit():
            mfr_id = True

        if mfr_id:
            return Manufacturer.objects.get(id=slug_or_id).slug

        # we must have a slug left. May not be valid... but we'll try it later.
        return slug_or_id

    def get_display_name(self):
        return self.parent_company_name if self.parent_company_name else self.name

    def __str__(self):
        return self.name


class DeadLink(models.Model):
    LINK_TYPE_CHOICES = [
        ("mfr", "Manufacturer"),
        ("amazon", "Amazon"),
        ("retailer", "Retailer"),
    ]
    # need to finish flow for retailer support
    current_url = models.URLField(max_length=2000)
    suggested_url = models.URLField(max_length=2000, null=True, blank=True)
    link_type = models.CharField(max_length=10, choices=LINK_TYPE_CHOICES)
    swatch = models.ForeignKey("Swatch", on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (
            f"{self.swatch.manufacturer.name} {self.swatch.color_name}"
            f" {self.swatch.filament_type.name} - {self.current_url}"
        )

    def resolve(self):
        self.resolved = True
        self.date_resolved = timezone.now()
        self.save()


class Retailer(models.Model):
    """A retailer is where filament can be purchased as an alternate to direct from
    manufacturer or Amazon."""

    name = models.CharField(max_length=160)
    website = models.URLField(null=True, blank=True, max_length=2000)
    affiliate_url_param = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.name


class PurchaseLocation(models.Model):
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE)
    url = models.URLField(null=True, blank=True, max_length=2000)
    swatch = models.ForeignKey("Swatch", on_delete=models.CASCADE)

    def __str__(self):
        return (
            f"{self.retailer.name} - {self.swatch.manufacturer.name}"
            f" {self.swatch.color_name} {self.swatch.filament_type.name}"
        )


class GenericFilamentType(models.Model):
    """
    This is to keep track of the basics: PLA, ABS, etc. Searching by type is
    performed off of these generic types.
    """

    name = models.CharField(max_length=24, default="PLA")
    slug = models.SlugField(max_length=24, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(GenericFilamentType, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class FilamentType(models.Model):
    """
    This is for the specialty subtypes: PLA2, HTPLA, etc. Both of those are
    still PLAs, so we want them to be included when searching by PLA.
    """

    name = models.CharField(max_length=24, default="PLA")
    hot_end_temp = models.IntegerField(default=205)
    bed_temp = models.IntegerField(default=60)
    parent_type = models.ForeignKey(
        GenericFilamentType, blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name


class GenericFile(models.Model):
    """
    Used for storing files like PDFs so that I can link to them from
    other parts of the site. This is mostly used to power the welcome
    experience images.
    """

    name = models.CharField(max_length=30, null=True, blank=True)
    file = models.FileField()
    alt_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.file.name}" if self.name else self.file.name


class Pantone(models.Model, DistanceMixin):
    CATEGORIES = [
        "Fashion and Interior Designers",
        "Industrial Designers",
        "Graphic Designers",
    ]

    code = models.CharField(max_length=48)
    name = models.CharField(max_length=250, null=True, blank=True)
    rgb_r = models.IntegerField()
    rgb_g = models.IntegerField()
    rgb_b = models.IntegerField()
    hex_color = models.CharField(max_length=6, null=True, blank=True)
    category = models.CharField(max_length=30)

    def __str__(self):
        return self.code


class PantonePMS(models.Model, DistanceMixin):
    """Shortened version of the most common graphic designers colors.

    These are the colors that are likely to appear in Photoshop, for example.
    """

    code = models.CharField(max_length=48)
    rgb_r = models.IntegerField()
    rgb_g = models.IntegerField()
    rgb_b = models.IntegerField()
    hex_color = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.code


class RAL(models.Model, DistanceMixin):
    CATEGORIES = ["RAL Classic", "RAL Effect", "RAL Design System+"]

    code = models.CharField(max_length=48)
    name = models.CharField(max_length=250, null=True, blank=True)
    rgb_r = models.IntegerField()
    rgb_g = models.IntegerField()
    rgb_b = models.IntegerField()
    hex_color = models.CharField(max_length=6, null=True, blank=True)
    category = models.CharField(max_length=30)

    def __str__(self):
        return self.code


class UserSubmittedTD(models.Model):
    swatch = models.ForeignKey("Swatch", on_delete=models.CASCADE)
    td = models.FloatField()
    # todo: if the same ip address submits again for the same swatch,
    #  update the previously stored value instead of storing another one.
    ip = models.GenericIPAddressField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{str(self.swatch)} - {self.td}"


class Swatch(models.Model, DistanceMixin):
    """
    The swatch model is used to keep track of two states of swatch;
    if the swatch is unpublished, then it's treated as a swatch that's
    in inventory, probably not printed yet, but ready to add.

    If it's published, then it's ready to go and visible on the homepage.
    """

    WHITE = "WHT"
    BLACK = "BLK"
    RED = "RED"
    GREEN = "GRN"
    YELLOW = "YLW"
    BLUE = "BLU"
    BROWN = "BRN"
    PURPLE = "PPL"
    PINK = "PNK"
    ORANGE = "RNG"
    GREY = "GRY"
    TRANSLUCENT = "TRN"

    BASE_COLOR_OPTIONS = [
        (WHITE, "White"),
        (BLACK, "Black"),
        (RED, "Red"),
        (GREEN, "Green"),
        (YELLOW, "Yellow"),
        (BLUE, "Blue"),
        (BROWN, "Brown"),
        (PURPLE, "Purple"),
        (PINK, "Pink"),
        (ORANGE, "Orange"),
        (GREY, "Grey"),
        (TRANSLUCENT, "Translucent"),
    ]

    BASE_COLOR_IDS = [i[0] for i in BASE_COLOR_OPTIONS]
    BASE_COLOR_SLUGS = [slugify(i[1]).lower() for i in BASE_COLOR_OPTIONS]

    STEP_OPTIONS = [16, 32, 48, 64, 80, 96, 112, 128]

    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, null=True, blank=True
    )
    color_name = models.CharField(max_length=240)

    # PLA, PETG, etc.
    filament_type = models.ForeignKey(
        FilamentType, on_delete=models.CASCADE, null=True, blank=True
    )

    color_parent = models.CharField(
        max_length=3,
        choices=BASE_COLOR_OPTIONS,
        null=True,
        blank=True,
        default=WHITE,
    )

    alt_color_parent = models.CharField(
        max_length=3,
        choices=BASE_COLOR_OPTIONS,
        null=True,
        blank=True,
    )

    # full size images
    image_front = models.ImageField(null=True, blank=True)
    image_back = models.ImageField(null=True, blank=True)
    image_other = models.ImageField(null=True, blank=True)
    image_opengraph = models.ImageField(null=True, blank=True)

    rebuild_long_way = models.BooleanField(
        default=False,
        help_text=(
            "Regenerate the color information using the long way for increased"
            " accuracy."
        ),
    )
    regenerate_info = models.BooleanField(
        default=False, help_text="Rebuild all the information related to this swatch."
    )

    published = models.BooleanField(
        default=True, help_text="Is the swatch visible on the homepage?"
    )
    donated_by = models.CharField(max_length=240, null=True, blank=True)

    date_added = models.DateTimeField(default=timezone.now)
    date_published = models.DateTimeField(null=True, blank=True)
    last_cache_update = models.DateTimeField(
        default=pytz.timezone("UTC").localize(
            timezone.datetime(year=1969, month=1, day=1)
        )
    )
    notes = models.TextField(max_length=4000, null=True, blank=True)
    amazon_purchase_link = models.URLField(null=True, blank=True, max_length=2000)
    mfr_purchase_link = models.URLField(null=True, blank=True, max_length=2000)
    slug = models.SlugField(max_length=400, null=True, blank=True)
    td = models.FloatField(null=True, blank=True)

    complement = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="complement_swatch",
    )
    analogous_1 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="analogous_one_swatch",
    )
    analogous_2 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="analogous_two_swatch",
    )

    triadic_1 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="triadic_one_swatch",
    )
    triadic_2 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="triadic_two_swatch",
    )

    split_complement_1 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="split_complement_one_swatch",
    )
    split_complement_2 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="split_complement_two_swatch",
    )

    tetradic_1 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tetradic_one_swatch",
    )
    tetradic_2 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tetradic_two_swatch",
    )
    tetradic_3 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tetradic_three_swatch",
    )

    square_1 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="square_one_swatch",
    )
    square_2 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="square_two_swatch",
    )
    square_3 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="square_three_swatch",
    )
    closest_1 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="closest_one_swatch",
    )
    closest_2 = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="closest_two_swatch",
    )
    hex_color = models.CharField(
        max_length=6, blank=True, verbose_name="Measured hex value"
    )
    lab_l = models.FloatField(null=True, blank=True)
    lab_a = models.FloatField(null=True, blank=True)
    lab_b = models.FloatField(null=True, blank=True)

    # !!!!!!!!!!!!!!!!!!!!!!!!
    # DO NOT PUT ANYTHING IN THESE FIELDS!
    # They are computed and added automatically!

    # This is treated as a flag to mark whether this is a converted
    # value from RGB or if this is something we've measured ourselves.
    # TODO: once we've measured everything, we can remove this field.
    computed_lab = models.BooleanField(default=False)

    card_img_jpeg = models.ImageField(
        upload_to="card_img",
        blank=True,
        null=True,
        verbose_name="DO NOT ADD! Computed card original",
    )
    card_img = models.ImageField(
        blank=True, verbose_name="DO NOT ADD! Computed Card Image"
    )

    rgb_r = models.IntegerField(null=True, blank=True)
    rgb_g = models.IntegerField(null=True, blank=True)
    rgb_b = models.IntegerField(null=True, blank=True)

    closest_pantone_1 = models.ForeignKey(
        Pantone,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pantone_1",
        verbose_name="Computed Pantone 'Fashion and Interior Designers' color",
    )
    closest_pantone_2 = models.ForeignKey(
        Pantone,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pantone_2",
        verbose_name="Computed Pantone 'Industrial Designers' color",
    )
    closest_pantone_3 = models.ForeignKey(
        Pantone,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pantone_3",
        verbose_name="Computed Pantone 'Graphic Designers' color",
    )
    closest_ral_1 = models.ForeignKey(
        RAL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ral_1",
        verbose_name="Computed RAL Classic color",
    )
    closest_ral_2 = models.ForeignKey(
        RAL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ral_2",
        verbose_name="Computed RAL Effect color",
    )
    closest_ral_3 = models.ForeignKey(
        RAL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ral_3",
        verbose_name="Computed RAL Design System+ color",
    )
    closest_pms_1 = models.ForeignKey(
        PantonePMS,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pms_1",
        verbose_name="Computed Pantone PMS color 1",
    )
    closest_pms_2 = models.ForeignKey(
        PantonePMS,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pms_2",
        verbose_name="Computed Pantone PMS color 2",
    )
    closest_pms_3 = models.ForeignKey(
        PantonePMS,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pms_3",
        verbose_name="Computed Pantone PMS color 3",
    )

    tags = TaggableManager(blank=True)
    # have this been uploaded as a new swatch and been posted yet?
    posted_to_social_media = models.BooleanField(default=False)

    # !!!!!!!!!!!!!!!!!!!!!!!!

    @property
    def human_readable_date(self) -> str:
        format = "%b %d, %Y"
        if self.date_published:
            return self.date_published.strftime(format)
        else:
            return self.date_added.strftime(format)

    def get_td(self) -> float | None:
        if self.usersubmittedtd_set.all():
            tds: list[float] = list(
                self.usersubmittedtd_set.all().values_list("td", flat=True)
            )
            if self.td:
                tds.append(self.td)
            if len(tds) >= 3:
                tds = sorted(tds)
                tds = tds[1:-1]
            return sum([i for i in tds]) / len(tds)
        if self.td:
            return self.td
        return None

    def get_lab_str(self):
        if self.lab_l and self.lab_a and self.lab_b and not self.computed_lab:
            return (
                f"L* {round(self.lab_l, 2)},"
                f" a* {round(self.lab_a, 2)},"
                f" b* {round(self.lab_b, 2)}"
            )

    def get_td_range(self) -> tuple[float, float] | None:
        tds: list[float] = list(
            self.usersubmittedtd_set.all().values_list("td", flat=True)
        )
        if not tds:
            tds = []
        if self.td:
            tds.append(self.td)
        if len(tds) == 0:
            return None
        elif len(tds) == 1:
            return tds[0], tds[0]
        elif len(tds) == 2:
            tds = sorted(tds)
            return min(tds), max(tds)

        tds = sorted(tds)
        tds = tds[1:-1]
        if len(tds) > 1:
            return min(tds), max(tds)
        return tds[0], tds[0]

    def get_rgb(self, hex: str) -> Tuple[int, ...]:
        return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))

    def get_hex(self, rgb: tuple) -> str:
        return "{R}{G}{B}".format(
            R="%0.2X" % int(rgb[0]), G="%0.2X" % int(rgb[1]), B="%0.2X" % int(rgb[2])
        )

    def get_lab_from_self(self):
        # intermediate step while we transition to full measured LAB color
        if not self.lab_a:
            return convert_color(
                sRGBColor(*self.get_rgb(self.hex_color), is_upscaled=True), LabColor
            )
        return LabColor(self.lab_l, self.lab_a, self.lab_b, OBSERVER_ANGLE, ILLUMINANT)

    def rgb_hilo(self, a: int, b: int, c: int) -> int:
        # courtesy of https://stackoverflow.com/a/40234924
        if c < b:
            b, c = c, b
        if b < a:
            a, b = b, a
        if c < b:
            b, c = c, b
        return a + c

    def _save_image(self, i, image_type: str) -> str:
        # https://stackoverflow.com/a/24380132
        output = BytesIO()
        i.save(output, format="JPEG", quality=75)
        output.seek(0)
        filename = default_storage.save(
            f"{self.slug}-{image_type}.jpg", ContentFile(output.read())
        )
        return filename

    def crop_and_save_images(self) -> None:
        try:
            # first let's see if we even need to work on it
            this = Swatch.objects.get(id=self.id)
            if this.image_front != self.image_front:
                this.image_front.delete(save=False)
        except:
            pass

        # Process:
        #
        # Take the front image and crop it twice. The first time for the card image,
        # the second time for the regular front image.
        #
        # Take the card image file, create a thumbnail, save the thumbnail to disk,
        # then add that file to the self.card_img attribute.

        # card image
        # x = y * 3.218
        card_image_x = 2613
        card_image_y = 812

        # regular front/back image
        # x = y * 1.3333
        main_image_x = 2740
        main_image_y = 2056

        image = Img.open(self.image_front)
        back_image = Img.open(self.image_back)
        card_image_x_offset = -30  # px
        card_image_y_offset = -50  # px
        img_card = image.crop(
            (
                int((image.width - card_image_x) / 2 + card_image_x_offset),
                int((image.height - card_image_y) / 2 + card_image_y_offset),
                int(
                    card_image_x
                    + (image.width - card_image_x) / 2
                    + card_image_x_offset
                ),
                int(
                    card_image_y
                    + (image.height - card_image_y) / 2
                    + card_image_y_offset
                ),
            )
        )
        main_image_x_offset = -40
        main_image_y_offset = 0

        main_image_crop_dimensions = (
            int((image.width - main_image_x) / 2 + main_image_x_offset),
            int((image.height - main_image_y) / 2 + main_image_y_offset),
            int(main_image_x + (image.width - main_image_x) / 2 + main_image_x_offset),
            int(main_image_y + (image.height - main_image_y) / 2 + main_image_y_offset),
        )
        img_front = image.crop(main_image_crop_dimensions)
        img_back = back_image.crop(main_image_crop_dimensions)

        filename_card = self._save_image(img_card, "card")
        filename_front = self._save_image(img_front, "front")
        filename_back = self._save_image(img_back, "back")

        path = os.path.join(settings.MEDIA_ROOT, filename_card)
        self.card_img_jpeg = ImageFile(open(path, "rb"))
        self.card_img_jpeg.name = filename_card

        path = os.path.join(settings.MEDIA_ROOT, filename_front)
        self.image_front = ImageFile(open(path, "rb"))
        self.image_front.name = filename_front

        path = os.path.join(settings.MEDIA_ROOT, filename_back)
        self.image_back = ImageFile(open(path, "rb"))
        self.image_back.name = filename_back

        image = Img.open(self.card_img_jpeg)
        image.thumbnail((288, 288), Img.Resampling.LANCZOS)

        filename = self._save_image(image, "thumb")

        path = os.path.join(settings.MEDIA_ROOT, filename)
        self.card_img = ImageFile(open(path, "rb"))
        self.card_img.name = filename

    def create_local_dev_images(self):
        front_masks = [
            "swatch_front_mask.png",
            "swatch_front_mask_2.png",
            "swatch_front_mask_3.png",
        ]
        back_masks = [
            "swatch_back_mask.png",
            "swatch_back_mask_2.png",
            "swatch_back_mask_3.png",
        ]
        mask_path = settings.BASE_DIR / Path("..") / Path("extras")

        front_mask = Img.open(os.path.join(mask_path, random.choice(front_masks)))
        front_img = Img.new("RGBA", front_mask.size, f"#{self.hex_color}")
        front_img.paste(front_mask, (0, 0), front_mask)
        front_img = front_img.convert("RGB")
        front_img_filename = self._save_image(front_img, "front")
        path = os.path.join(settings.MEDIA_ROOT, front_img_filename)
        self.image_front = ImageFile(open(path, "rb"))
        self.image_front.name = front_img_filename

        back_mask = Img.open(os.path.join(mask_path, random.choice(back_masks)))
        back_img = Img.new("RGBA", back_mask.size, f"#{self.hex_color}")
        back_img.paste(back_mask, (0, 0), back_mask)
        back_img = back_img.convert("RGB")
        back_img_filename = self._save_image(back_img, "back")
        path = os.path.join(settings.MEDIA_ROOT, back_img_filename)
        self.image_back = ImageFile(open(path, "rb"))
        self.image_back.name = back_img_filename

        self.crop_and_save_images()

    def create_opengraph_image(self, close_django_file_too=False):
        opengraph_size = (1370, 1028)

        def do_update(img_obj):
            img_obj.thumbnail(opengraph_size, Img.Resampling.LANCZOS)
            filename_opengraph = self._save_image(img_obj, "opengraph")

            path = os.path.join(settings.MEDIA_ROOT, filename_opengraph)
            self.image_opengraph = ImageFile(open(path, "rb"))
            self.image_opengraph.name = filename_opengraph

        if close_django_file_too:
            # There is an issue in Pillow where the file is not closed properly.
            # There is no proper workaround except to close the django file handler
            # and the pillow file handler at the same time; however, this breaks
            # normal operation of Django. This workaround is only for large batches
            # of images.
            # https://github.com/python-pillow/Pillow/issues/5132#issuecomment-750918772
            with self.image_front.file, Img.open(self.image_front) as image_opengraph:
                do_update(image_opengraph)
        else:
            with Img.open(self.image_front) as image_opengraph:
                do_update(image_opengraph)

    def get_opengraph_image(self):
        # this is only to tide us over until we create all the proper images
        if self.image_opengraph:
            return self.image_opengraph.url
        # The object that we're currently working with may have been modified
        # due to the custom library rendering, so it's not safe to save it.
        # Reload the object from disk and then generate the opengraph image,
        # then save that version.
        this = Swatch.objects.get(id=self.id)
        this.create_opengraph_image()
        this.save()
        return this.image_opengraph.url

    def get_closest_color_swatch(self, library: Union[QuerySet, List], rgb: tuple):
        """Get a swatch that fits with progressively less-strict clamps."""
        for step_option in self.STEP_OPTIONS:
            if result := self._get_closest_color(library, rgb=rgb, step=step_option):
                return result

    def get_closest_third_party_color(self, model, category=None, queryset=None):
        """Get a swatch that fits with progressively less-strict clamps."""
        self_color = self.get_rgb(self.hex_color)
        queryset = queryset if queryset else model.objects.all()
        extra_args = {"category": category} if category else None

        for step_option in self.STEP_OPTIONS:
            if result := self._get_closest_color(
                queryset,
                rgb=self_color,
                step=step_option,
                extra_args=extra_args,
            ):
                return result

    def _get_closest_color(
        self, queryset, step: int, rgb: tuple = None, extra_args: dict = None
    ):
        """Takes in either Pantone or RAL, then returns the matching element."""
        distance_dict = {}

        if not extra_args:
            extra_args = {}

        if not rgb:
            rgb = self.get_rgb(self.hex_color)

        target_color = convert_color(sRGBColor(*rgb, is_upscaled=True), LabColor)

        options = queryset.filter(
            **extra_args,
            rgb_r__gt=max(rgb[0] - step, 0),
            rgb_r__lt=min(rgb[0] + step, 255),
            rgb_g__gt=max(rgb[1] - step, 0),
            rgb_g__lt=min(rgb[1] + step, 255),
            rgb_b__gt=max(rgb[2] - step, 0),
            rgb_b__lt=min(rgb[2] + step, 255),
        )
        for option in options:
            possible_color = convert_color(
                sRGBColor.new_from_rgb_hex(option.hex_color), LabColor
            )
            distance = delta_e_cie2000(target_color, possible_color)
            distance_dict.update({option: distance})

        distance_dict = {
            i: distance_dict[i] for i in distance_dict if distance_dict[i] is not None
        }
        sorted_distance_list = sorted(distance_dict.items(), key=lambda kv: kv[1])
        try:
            return sorted_distance_list[0][0]
        except IndexError:
            return None

    def generate_closest_pantone(self):
        fields = ["closest_pantone_1", "closest_pantone_2", "closest_pantone_3"]
        for index, category in enumerate(Pantone.CATEGORIES):
            setattr(
                self,
                fields[index],
                self.get_closest_third_party_color(Pantone, category),
            )

    def generate_closest_ral(self):
        fields = ["closest_ral_1", "closest_ral_2", "closest_ral_3"]
        for index, category in enumerate(RAL.CATEGORIES):
            setattr(
                self, fields[index], self.get_closest_third_party_color(RAL, category)
            )

    def generate_closest_pms(self):
        fields = ["closest_pms_1", "closest_pms_2", "closest_pms_3"]
        qs = PantonePMS.objects.all()

        for index in range(3):
            result = self.get_closest_third_party_color(PantonePMS, queryset=qs)
            qs = qs.exclude(id=result.id)
            setattr(self, fields[index], result)

    def update_complement_swatch(self, l):
        complement = Color(self.hex_color).complementary()[1]
        complement = sRGBColor.new_from_rgb_hex(str(complement))

        self.complement = self.get_closest_color_swatch(
            l, complement.get_upscaled_value_tuple()
        )

    def update_analogous_swatches(self, l):
        analogous = Color(self.hex_color).analagous()
        a_1 = sRGBColor.new_from_rgb_hex(str(analogous[1]))
        a_2 = sRGBColor.new_from_rgb_hex(str(analogous[2]))

        self.analogous_1 = self.get_closest_color_swatch(
            l, a_1.get_upscaled_value_tuple()
        )
        self.analogous_2 = self.get_closest_color_swatch(
            l, a_2.get_upscaled_value_tuple()
        )

    def update_triadic_swatches(self, l):
        triadic = Color(self.hex_color).triadic()
        t_1 = sRGBColor.new_from_rgb_hex(str(triadic[1]))
        t_2 = sRGBColor.new_from_rgb_hex(str(triadic[2]))

        self.triadic_1 = self.get_closest_color_swatch(
            l, t_1.get_upscaled_value_tuple()
        )
        self.triadic_2 = self.get_closest_color_swatch(
            l, t_2.get_upscaled_value_tuple()
        )

    def update_split_complement_swatches(self, l):
        split_c = Color(self.hex_color).split_complementary()
        s_1 = sRGBColor.new_from_rgb_hex(str(split_c[1]))
        s_2 = sRGBColor.new_from_rgb_hex(str(split_c[2]))

        self.split_complement_1 = self.get_closest_color_swatch(
            l, s_1.get_upscaled_value_tuple()
        )
        self.split_complement_2 = self.get_closest_color_swatch(
            l, s_2.get_upscaled_value_tuple()
        )

    def update_tetradic_swatches(self, l):
        tetradic = Color(self.hex_color).tetradic()
        t_1 = sRGBColor.new_from_rgb_hex(str(tetradic[1]))
        t_2 = sRGBColor.new_from_rgb_hex(str(tetradic[2]))
        t_3 = sRGBColor.new_from_rgb_hex(str(tetradic[3]))

        self.tetradic_1 = self.get_closest_color_swatch(
            l, t_1.get_upscaled_value_tuple()
        )
        self.tetradic_2 = self.get_closest_color_swatch(
            l, t_2.get_upscaled_value_tuple()
        )
        self.tetradic_3 = self.get_closest_color_swatch(
            l, t_3.get_upscaled_value_tuple()
        )

    def update_square_swatches(self, l):
        square = Color(self.hex_color).square()
        s_1 = sRGBColor.new_from_rgb_hex(str(square[1]))
        s_2 = sRGBColor.new_from_rgb_hex(str(square[2]))
        s_3 = sRGBColor.new_from_rgb_hex(str(square[3]))

        self.square_1 = self.get_closest_color_swatch(l, s_1.get_upscaled_value_tuple())
        self.square_2 = self.get_closest_color_swatch(l, s_2.get_upscaled_value_tuple())
        self.square_3 = self.get_closest_color_swatch(l, s_3.get_upscaled_value_tuple())

    def update_closest_swatches(self, l):
        own_color = sRGBColor.new_from_rgb_hex(
            self.hex_color
        ).get_upscaled_value_tuple()
        l = l.exclude(pk=self.pk)

        self.closest_1 = self.get_closest_color_swatch(l, own_color)
        if not self.closest_1:
            # correct for an empty library during testing and dev work
            self.closest_1 = self

        l = l.exclude(pk=self.closest_1.pk)
        self.closest_2 = self.get_closest_color_swatch(l, own_color)
        if not self.closest_2:
            self.closest_2 = self

    def refresh_cache_if_needed(self) -> None:
        """
        Because we're caching all the color swatches on every entry in the db,
        we need to know if we should refresh these from time to time. We can
        check by seeing the last time we added a swatch to the library; if the
        cache hasn't been updated since we've added a new swatch, go ahead and
        update all the entries.

        These will only be used if the user has the default settings on the
        front end.
        """
        latest_swatch = Swatch.objects.filter(published=True).latest("date_published")
        if latest_swatch.date_published > self.last_cache_update:
            library = Swatch.objects.filter(published=True)
            self.update_all_color_matches(library)
            self.last_cache_update = timezone.now()
            self.save()

    def update_all_color_matches(
        self, library: QuerySet, include_third_party=False
    ) -> None:
        # NOTE: This does not save to the database!!! This is deliberate -
        # we only want to save it if we're updating the defaults. Otherwise,
        # this allows us to modify the defaults out of any given library, built
        # from the settings that the end user has requested.
        self.update_complement_swatch(library)
        self.update_analogous_swatches(library)
        self.update_triadic_swatches(library)
        self.update_split_complement_swatches(library)
        self.update_tetradic_swatches(library)
        self.update_square_swatches(library)
        self.update_closest_swatches(library)
        if include_third_party:
            self.generate_closest_ral()
            self.generate_closest_pantone()
            self.generate_closest_pms()

    def is_available(self):
        return any([self.amazon_purchase_link, self.mfr_purchase_link])

    def get_closest_swatch_from_hex(self, hex: str):
        # This is a helper function designed to be called from the command line.
        # Should return the closest element to a given hex string.
        color_to_match = convert_color(sRGBColor.new_from_rgb_hex(hex), LabColor)
        l = Swatch.objects.filter(published=True)
        return self.get_closest_color_swatch(l, color_to_match)

    def regenerate_all(self, library: QuerySet = None):
        if library:
            # this should only run when we pass a queryset in, otherwise
            # just handle the things that we can directly access easily
            self.update_all_color_matches(library)
        self.set_rgb_from_lab()
        self.generate_closest_ral()
        self.generate_closest_pantone()
        self.generate_closest_pms()

    def update_affiliate_links(self):
        """
        Forcibly update the urls attached to a swatch with aff info.

        There's one confusing piece in here; python's urllib marks 'params' as
        something that looks like it's related to filesystems. Either way, it's
        not a syntax I'm familiar with, and none of the examples in the docs
        actually show it used. In the Manufacturer model, we use 'param' to refer
        to the query string parameter, which is known as the `query` object from
        urllib. Fun times for everyone.
        """
        # all of our short links start with `amzn.to`, so that's an easy check
        if amazonlink := self.amazon_purchase_link:
            if "amzn.to" not in amazonlink and len(amazonlink) > 26:
                if "tag=fil" not in amazonlink:
                    scheme, netloc, path, query, fragment = urlsplit(amazonlink)
                    if query:
                        query = query.split("&")
                        query.append("tag=filamentcol0c-20")
                        query = "&".join(query)
                    else:
                        query = "tag=filamentcol0c-20"
                    # we have no 'params' in this url, so pass an empty string
                    self.amazon_purchase_link = urlunparse(
                        (scheme, netloc, path, "", query, fragment)
                    )
        if param := self.manufacturer.affiliate_url_param:
            if mfr_url := self.mfr_purchase_link:
                param = param.strip("&")
                param = param.split("=")
                if param[0] not in mfr_url and param[1] not in mfr_url:
                    scheme, netloc, path, query, fragment = urlsplit(mfr_url)
                    if query:
                        query = query.split("&")
                        query.append(f"{param[0]}={param[1]}")
                        query = "&".join(query)
                    else:
                        query = f"{param[0]}={param[1]}"
                    self.mfr_purchase_link = urlunparse(
                        (scheme, netloc, path, "", query, fragment)
                    )
        for location in self.purchaselocation_set.all():
            if location.url is None or location.url == "":
                continue
            if param := location.retailer.affiliate_url_param:
                param = param.strip("&").split("=")
                if param[0] not in location.url and param[1] not in location.url:
                    scheme, netloc, path, query, fragment = urlsplit(location.url)
                    if query:
                        query = query.split("&")
                        query.append(f"{param[0]}={param[1]}")
                        query = "&".join(query)
                    else:
                        query = f"{param[0]}={param[1]}"
                    location.url = urlunparse(
                        (scheme, netloc, path, "", query, fragment)
                    )
                location.save()

    def get_color_id_from_slug_or_id(self, slug_or_id: str) -> str:
        slug_or_id = slug_or_id.upper()
        if slug_or_id in self.BASE_COLOR_IDS:
            return slug_or_id

        slug_or_id = slug_or_id.lower()
        if slug_or_id in self.BASE_COLOR_SLUGS:
            return self.BASE_COLOR_IDS[self.BASE_COLOR_SLUGS.index(slug_or_id)]

        raise UnknownSlugOrID

    def set_slug(self):
        # just clobber what was there before. We need to fix the broken urls
        # that end in `-none`
        self.slug = slugify(
            f"{self.manufacturer.slug} {self.color_name} {self.filament_type.name} {self.id}"
        )

    def _set_rgb_from_hex(self):
        # for testing only
        rgb = self.get_rgb(self.hex_color)
        self.rgb_r = rgb[0]
        self.rgb_g = rgb[1]
        self.rgb_b = rgb[2]

    def _set_lab_from_rgb(self):
        # for testing only
        color = convert_color(
            sRGBColor(self.rgb_r, self.rgb_g, self.rgb_b, is_upscaled=True), LabColor
        )
        color.set_illuminant(ILLUMINANT)
        color.set_observer(OBSERVER_ANGLE)
        self.lab_l = color.lab_l
        self.lab_a = color.lab_a
        self.lab_b = color.lab_b

    def set_rgb_from_lab(self):
        # Not everything has lab yet, but if lab exists, use it.
        if not self.lab_l or not self.lab_a or not self.lab_b:
            # old-style swatches start with a hex color, so we can safely
            # assume that it exists
            rgb = self.get_rgb(self.hex_color)
            self.rgb_r = rgb[0]
            self.rgb_g = rgb[1]
            self.rgb_b = rgb[2]
        else:
            color = convert_color(
                LabColor(
                    self.lab_l, self.lab_a, self.lab_b, OBSERVER_ANGLE, ILLUMINANT
                ),
                sRGBColor,
            )
            rgb: tuple = color.get_upscaled_value_tuple()
            # When converting measured LAB into sRGB, it can rarely result in
            # invalid RGB colors that are too intense to display properly.
            # In this case, we should clamp each of the values to ensure that
            # we will always end up with a valid hex color.
            clamped_rgb: tuple[int] = (
                int(clamp(rgb[0], 0, 255)),
                int(clamp(rgb[1], 0, 255)),
                int(clamp(rgb[2], 0, 255))
            )
            self.hex_color = self.get_hex(clamped_rgb)
            self.rgb_r = clamped_rgb[0]
            self.rgb_g = clamped_rgb[1]
            self.rgb_b = clamped_rgb[2]

    def save(self, *args, **kwargs):
        rebuild_matches = False

        if self.regenerate_info:
            # the joys of using flags on the models themselves. Because
            # this is only triggered from the admin panel, we treat it
            # like a button. If it's pushed, we do stuff. We have to reset
            # regenerate_info back to false before we save the model,
            # otherwise it will get stuck like that and the tweet will
            # never fire.
            if not self.card_img:
                self.crop_and_save_images()
                self.create_opengraph_image()
            self.regenerate_all()
            self.regenerate_info = False
            rebuild_matches = True

        if self.rebuild_long_way:
            self.regenerate_all()
            self.rebuild_long_way = False
            rebuild_matches = True

        if rebuild_matches:
            self.update_all_color_matches(Swatch.objects.filter(published=True))

        if self.card_img or not self.published:
            # we already have a card image, so just save everything and abort.

            # this will create a malformed url for inventory swatches, but it
            # will get corrected when the swatch is published. See #142 for
            # more information.
            self.set_slug()
            super(Swatch, self).save(*args, **kwargs)
            return
        else:
            self.crop_and_save_images()
            self.create_opengraph_image()
            self.regenerate_all()

            super(Swatch, self).save(*args, **kwargs)

            self.update_affiliate_links()
            self.set_slug()

            if kwargs.get("force_insert"):
                # In normal operation, this will never trigger. However,
                # in tests, the `force_insert` flag is set to True, which
                # will trigger the double save operation here to try and
                # create two items with the same ID.
                del kwargs["force_insert"]

            super(Swatch, self).save(*args, **kwargs)

    def __str__(self):
        try:
            mfr = self.manufacturer.name
        except:
            mfr = "NOT ADDED"

        try:
            ft = self.filament_type.name
        except:
            ft = "NOT ADDED"
        return f"{mfr} - {self.color_name} {ft}"

    def get_absolute_url(self):
        return reverse("swatchdetail", args=(self.slug,))

    class Meta:
        verbose_name_plural = "swatches"
