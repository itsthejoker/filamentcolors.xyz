import os
from io import BytesIO

import cv2
import numpy as np
from PIL import Image as Img
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.db import models
from django.utils import timezone
from skimage import io

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


class FilamentType(models.Model):
    name = models.CharField(max_length=24, default="PLA")
    hot_end_temp = models.IntegerField(default=205)
    bed_temp = models.IntegerField(default=60)

    def __str__(self):
        return self.name


class Swatch(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.CASCADE, null=True, blank=True
    )
    color_name = models.CharField(max_length=240)

    # PLA, PETG, etc.
    filament_type = models.ForeignKey(
        FilamentType, on_delete=models.CASCADE, null=True, blank=True
    )
    card_img_jpeg = models.ImageField(upload_to="card_img", blank=True)
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # DO NOT PUT ANYTHING IN THESE FIELDS!
    # They are computed and added automatically!
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

    # full size images
    image_back = models.ImageField(null=True, blank=True)
    image_front = models.ImageField(null=True, blank=True)
    image_other = models.ImageField(null=True, blank=True)

    printed_on = models.ForeignKey(Printer, on_delete=models.CASCADE)
    maker = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)
    notes = models.TextField(max_length=4000, null=True, blank=True)
    amazon_purchase_link = models.URLField(null=True, blank=True)
    mfr_purchase_link = models.URLField(null=True, blank=True)

    @property
    def date_added_date(self):
        return self.date_added.strftime("%b %d, %Y")

    def save(self, *args, **kwargs):

        def get_rgb(hex: str) -> tuple:
            return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))

        def get_hex(rgb: tuple) -> str:
            return (
                "{R}{G}{B}".format(
                R = "%0.2X" % int(rgb[0]),
                G = "%0.2X" % int(rgb[1]),
                B = "%0.2X" % int(rgb[2])
                )
            )

        def rgb_hilo(a, b, c):
            # courtesy of https://stackoverflow.com/a/40234924
            if c < b: b, c = c, b
            if b < a: a, b = b, a
            if c < b: b, c = c, b
            return a + c

        def get_complement(hex):
            r, g, b = get_rgb(hex)
            # courtesy of https://stackoverflow.com/a/40234924
            k = rgb_hilo(r, g, b)
            return get_hex(tuple(k - u for u in (r, g, b)))

        post_tweet = False

        if self.card_img:
            # we already have a card image, so just save everything and abort.
            super(Swatch, self).save(*args, **kwargs)
            return

        # https://stackoverflow.com/a/24380132
        if self.card_img_jpeg:
            try:
                # first let's see if we even need to work on it
                this = Swatch.objects.get(id=self.id)
                if this.card_img_jpeg != self.card_img_jpeg:
                    this.card_img_jpeg.delete(save=False)
            except:
                pass

            # Process:
            #
            # Take the image file, create a thumbnail, save the thumbnail to disk,
            # then add that file to the self.card_img attribute.

            image = Img.open(self.card_img_jpeg)
            image.thumbnail((200, 200), Img.ANTIALIAS)
            # do we even need to do it this way? Need to learn more about byte streams
            # and verify that this is actually a valid way to handle this.
            output = BytesIO()
            image.save(output, format='JPEG', quality=75)
            output.seek(0)
            # remove the file type so that we can modify the filename
            filename_str = self.card_img_jpeg.name[:self.card_img_jpeg.name.rindex('.')]
            filename = default_storage.save(
                f'{filename_str}-thumb.jpg', ContentFile(output.read())
            )

            path = os.path.join(settings.MEDIA_ROOT, filename)
            self.card_img = ImageFile(open(path, 'rb'))
            self.card_img.name = filename

        # sanity check
        if self.card_img:
            post_tweet = True
            # lovingly ripped from https://stackoverflow.com/a/43111221
            self.card_img.file.seek(0)
            img = io.imread(self.card_img.file)

            pixels = np.float32(img.reshape(-1, 3))

            n_colors = 5
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
            flags = cv2.KMEANS_RANDOM_CENTERS

            # this line is super painful in computation time. We kind of get
            # around that by only having it parse the resized small card image;
            # if it runs on the full-size image, it could take a minute or two
            # to complete.
            _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
            _, counts = np.unique(labels, return_counts=True)
            dominant = palette[np.argmax(counts)]

            self.hex_color = get_hex(dominant)
            self.complement_hex = get_complement(self.hex_color)


        super(Swatch, self).save(*args, **kwargs)

        if post_tweet:
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
