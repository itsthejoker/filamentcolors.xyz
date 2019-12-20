import os
from io import BytesIO
from typing import Tuple

import pytz
from PIL import Image as Img
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cmc
from colormath.color_objects import LabColor
from colormath.color_objects import sRGBColor
from colorthief import ColorThief
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from taggit.managers import TaggableManager

from filamentcolors.colors import Color
from filamentcolors.twitter_helpers import send_tweet


class Printer(models.Model):
    name = models.CharField(max_length=50)
    notes = models.TextField(max_length=4000, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner.username} - {self.name}"


class Manufacturer(models.Model):
    name = models.CharField(max_length=160)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class GenericFilamentType(models.Model):
    name = models.CharField(max_length=24, default="PLA")

    def __str__(self):
        return self.name


class FilamentType(models.Model):
    name = models.CharField(max_length=24, default="PLA")
    hot_end_temp = models.IntegerField(default=205)
    bed_temp = models.IntegerField(default=60)
    parent_type = models.ForeignKey(
        GenericFilamentType, blank=True, null=True, on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return self.name


class GenericFile(models.Model):
    # used for storing files like PDFs so that I can link to them
    # from other parts of the site

    file = models.FileField()

    def __str__(self):
        return self.file.name


class Swatch(models.Model):
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
    TRANSPARENT = "TRN"

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
        (TRANSPARENT, "Transparent")
    ]

    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, null=True, blank=True
    )
    color_name = models.CharField(max_length=240)

    # PLA, PETG, etc.
    filament_type = models.ForeignKey(
        FilamentType, on_delete=models.CASCADE, null=True, blank=True
    )

    color_parent = models.CharField(
        max_length=3, choices=BASE_COLOR_OPTIONS, null=True, blank=True, default=WHITE
    )

    # full size images
    image_front = models.ImageField(null=True, blank=True)
    image_back = models.ImageField(null=True, blank=True)
    image_other = models.ImageField(null=True, blank=True)

    regenerate_info = models.BooleanField(default=False)

    date_added = models.DateTimeField(default=timezone.now)
    last_cache_update = models.DateTimeField(
        default=pytz.timezone('UTC').localize(
            timezone.datetime(year=1969, month=1, day=1)
        )
    )
    notes = models.TextField(max_length=4000, null=True, blank=True)
    amazon_purchase_link = models.URLField(null=True, blank=True)
    mfr_purchase_link = models.URLField(null=True, blank=True)

    complement = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="complement_swatch"
    )

    analogous_1 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="analogous_one_swatch"
    )
    analogous_2 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="analogous_two_swatch"
    )

    triadic_1 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="triadic_one_swatch"
    )
    triadic_2 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="triadic_two_swatch"
    )

    split_complement_1 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="split_complement_one_swatch"
    )
    split_complement_2 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="split_complement_two_swatch"
    )

    tetradic_1 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="tetradic_one_swatch"
    )
    tetradic_2 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="tetradic_two_swatch"
    )
    tetradic_3 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="tetradic_three_swatch"
    )

    square_1 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="square_one_swatch"
    )
    square_2 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="square_two_swatch"
    )
    square_3 = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.DO_NOTHING,
        related_name="square_three_swatch"
    )

    tags = TaggableManager(blank=True)

    # !!!!!!!!!!!!!!!!!!!!!!!!
    # DO NOT PUT ANYTHING IN THESE FIELDS!
    # They are computed and added automatically!
    card_img_jpeg = models.ImageField(
        upload_to="card_img", blank=True, null=True,
        verbose_name="DO NOT ADD! Computed card original"
    )
    card_img = models.ImageField(
        blank=True, verbose_name="DO NOT ADD! Computed Card Image"
    )
    hex_color = models.CharField(
        max_length=6, blank=True, verbose_name="DO NOT ADD! Computed Hex Color"
    )
    complement_hex = models.CharField(
        max_length=6, blank=True, verbose_name="DO NOT ADD! Computed Complement Hex"
    )

    # !!!!!!!!!!!!!!!!!!!!!!!!

    @property
    def date_added_date(self) -> str:
        return self.date_added.strftime("%b %d, %Y")

    def get_rgb(self, hex: str) -> Tuple[int, ...]:
        return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

    def get_hex(self, rgb: tuple) -> str:
        return (
            "{R}{G}{B}".format(
                R="%0.2X" % int(rgb[0]),
                G="%0.2X" % int(rgb[1]),
                B="%0.2X" % int(rgb[2])
            )
        )

    def rgb_hilo(self, a: int, b: int, c: int) -> int:
        # courtesy of https://stackoverflow.com/a/40234924
        if c < b:
            b, c = c, b
        if b < a:
            a, b = b, a
        if c < b:
            b, c = c, b
        return a + c

    def get_complement(self, hex: str) -> str:
        r, g, b = self.get_rgb(hex)
        # courtesy of https://stackoverflow.com/a/40234924
        k = self.rgb_hilo(r, g, b)
        return self.get_hex(tuple(k - u for u in (r, g, b)))

    def _save_image(self, i, image_type: str) -> str:
        # https://stackoverflow.com/a/24380132

        # do we even need to do it this way? Need to learn more about byte streams
        # and verify that this is actually a valid way to handle this.
        output = BytesIO()
        i.save(output, format='JPEG', quality=75)
        output.seek(0)
        # remove the file type so that we can modify the filename
        filename_str = self.image_front.name[:self.image_front.name.rindex('.')]
        filename = default_storage.save(
            f'{filename_str}-{image_type}.jpg', ContentFile(output.read())
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
        cs_x = 1783
        cs_y = 554

        # regular front image
        cs_two_x = 1865
        cs_two_y = 1399

        image = Img.open(self.image_front)
        back_image = Img.open(self.image_back)
        img_card = image.crop(
            (
                (image.width - cs_x) / 2,
                (image.height - cs_y) / 2,
                cs_x + (image.width - cs_x) / 2,
                cs_y + (image.height - cs_y) / 2
            )
        )
        img_front = image.crop(
            (
                (image.width - cs_two_x) / 2,
                (image.height - cs_two_y) / 2,
                cs_two_x + (image.width - cs_two_x) / 2,
                cs_two_y + (image.height - cs_two_y) / 2
            )
        )
        img_back = back_image.crop(
            (
                (back_image.width - cs_two_x) / 2,
                (back_image.height - cs_two_y) / 2,
                cs_two_x + (back_image.width - cs_two_x) / 2,
                cs_two_y + (back_image.height - cs_two_y) / 2
            )
        )

        filename_card = self._save_image(img_card, 'card')
        filename_front = self._save_image(img_front, 'front')
        filename_back = self._save_image(img_back, 'back')

        path = os.path.join(settings.MEDIA_ROOT, filename_card)
        self.card_img_jpeg = ImageFile(open(path, 'rb'))
        self.card_img_jpeg.name = filename_card

        path = os.path.join(settings.MEDIA_ROOT, filename_front)
        self.image_front = ImageFile(open(path, 'rb'))
        self.image_front.name = filename_front

        path = os.path.join(settings.MEDIA_ROOT, filename_back)
        self.image_back = ImageFile(open(path, 'rb'))
        self.image_back.name = filename_back

        image = Img.open(self.card_img_jpeg)
        image.thumbnail((200, 200), Img.ANTIALIAS)

        filename = self._save_image(image, 'thumb')

        path = os.path.join(settings.MEDIA_ROOT, filename)
        self.card_img = ImageFile(open(path, 'rb'))
        self.card_img.name = filename

    def generate_hex_info(self) -> None:
        ct_image = ColorThief(self.card_img.path)
        self.hex_color = self.get_hex(ct_image.get_color(quality=1))
        self.complement_hex = self.get_complement(self.hex_color)

    def _get_closest_color_swatch(self, library: QuerySet, color_to_match: LabColor):
        distance_dict = dict()

        for item in library:
            possible_color = convert_color(
                sRGBColor.new_from_rgb_hex(item.hex_color), LabColor
            )

            distance = delta_e_cmc(color_to_match, possible_color)

            distance_dict.update({item: distance})

        distance_dict = {
            i: distance_dict[i] for i in distance_dict
            if distance_dict[i] is not None
        }

        sorted_distance_list = sorted(distance_dict.items(), key=lambda kv: kv[1])

        try:
            return sorted_distance_list[0][0]
        except IndexError:
            return None

    def update_complement_swatch(self, l):
        complement = Color(self.hex_color).complementary()[1]
        complement = convert_color(
            sRGBColor.new_from_rgb_hex(str(complement)), LabColor
        )

        self.complement = self._get_closest_color_swatch(l, complement)

    def update_analogous_swatches(self, l):
        analogous = Color(self.hex_color).analagous()
        a_1 = convert_color(
            sRGBColor.new_from_rgb_hex(str(analogous[1])), LabColor
        )
        a_2 = convert_color(
            sRGBColor.new_from_rgb_hex(str(analogous[2])), LabColor
        )

        self.analogous_1 = self._get_closest_color_swatch(l, a_1)
        self.analogous_2 = self._get_closest_color_swatch(l, a_2)

    def update_triadic_swatches(self, l):
        triadic = Color(self.hex_color).triadic()
        t_1 = convert_color(
            sRGBColor.new_from_rgb_hex(str(triadic[1])), LabColor
        )
        t_2 = convert_color(
            sRGBColor.new_from_rgb_hex(str(triadic[2])), LabColor
        )

        self.triadic_1 = self._get_closest_color_swatch(l, t_1)
        self.triadic_2 = self._get_closest_color_swatch(l, t_2)

    def update_split_complement_swatches(self, l):
        split_c = Color(self.hex_color).split_complementary()
        s_1 = convert_color(
            sRGBColor.new_from_rgb_hex(str(split_c[1])), LabColor
        )
        s_2 = convert_color(
            sRGBColor.new_from_rgb_hex(str(split_c[2])), LabColor
        )

        self.split_complement_1 = self._get_closest_color_swatch(l, s_1)
        self.split_complement_2 = self._get_closest_color_swatch(l, s_2)

    def update_tetradic_swatches(self, l):
        tetradic = Color(self.hex_color).tetradic()
        t_1 = convert_color(
            sRGBColor.new_from_rgb_hex(str(tetradic[1])), LabColor
        )
        t_2 = convert_color(
            sRGBColor.new_from_rgb_hex(str(tetradic[2])), LabColor
        )
        t_3 = convert_color(
            sRGBColor.new_from_rgb_hex(str(tetradic[3])), LabColor
        )

        self.tetradic_1 = self._get_closest_color_swatch(l, t_1)
        self.tetradic_2 = self._get_closest_color_swatch(l, t_2)
        self.tetradic_3 = self._get_closest_color_swatch(l, t_3)

    def update_square_swatches(self, l):
        square = Color(self.hex_color).square()
        s_1 = convert_color(
            sRGBColor.new_from_rgb_hex(str(square[1])), LabColor
        )
        s_2 = convert_color(
            sRGBColor.new_from_rgb_hex(str(square[2])), LabColor
        )
        s_3 = convert_color(
            sRGBColor.new_from_rgb_hex(str(square[3])), LabColor
        )

        self.square_1 = self._get_closest_color_swatch(l, s_1)
        self.square_2 = self._get_closest_color_swatch(l, s_2)
        self.square_3 = self._get_closest_color_swatch(l, s_3)

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
        latest_swatch = Swatch.objects.latest('date_added')
        if latest_swatch.date_added > self.last_cache_update:
            library = Swatch.objects.all()
            self.update_all_color_matches(library)
            self.last_cache_update = timezone.now()
            self.save()

    def update_all_color_matches(self, library: QuerySet) -> None:
        # NOTE: This does not save to the database!!! This is deliberate -
        # we only want to save it if we're updating the defaults. Otherwise
        # this allows us to modify the defaults out of any given library, built
        # from the settings that the end user has requested.
        self.update_complement_swatch(library)
        self.update_analogous_swatches(library)
        self.update_triadic_swatches(library)
        self.update_split_complement_swatches(library)
        self.update_tetradic_swatches(library)
        self.update_square_swatches(library)

    def save(self, *args, **kwargs):
        post_tweet = False

        # and now, the fun begins
        if self.regenerate_info:
            self.card_img = None

        if self.card_img:
            # we already have a card image, so just save everything and abort.
            super(Swatch, self).save(*args, **kwargs)
            return

        if self.image_front:
            self.crop_and_save_images()

        # sanity check
        if self.card_img:
            post_tweet = True
            # lovingly ripped from https://stackoverflow.com/a/43111221
            self.generate_hex_info()

        if self.regenerate_info:
            # the joys of using flags on the models themselves. Because
            # this is only triggered from the admin panel, we treat it
            # like a button. If it's pushed, we do stuff. We have to reset
            # regenerate_info back to false before we save the model,
            # otherwise it will get stuck like that and the tweet will
            # never fire.
            self.regenerate_info = False
            regenerate_info_tweet_bypass = True
        else:
            regenerate_info_tweet_bypass = False

        super(Swatch, self).save(*args, **kwargs)

        if post_tweet and not settings.DEBUG and not regenerate_info_tweet_bypass:
            # have to save the model before we can send the tweet, otherwise
            # we won't have a swatch ID.
            send_tweet(self)

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

    class Meta:
        verbose_name_plural = "swatches"
