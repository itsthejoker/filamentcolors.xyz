from django.db import models


class Printer(models.Model):
    name = models.CharField(max_length=50)
    notes = models.TextField(max_length=4000, null=True, blank=True)


class Swatch(models.Model):
    manufacturer = models.CharField(max_length=160)
    color_name = models.CharField(max_length=240)
    # PLA, PETG, etc.
    filament_type = models.CharField(max_length=10, default='PLA')
    hot_end_temp = models.IntegerField(default=205)
    bed_temp = models.IntegerField(default=60)
    image_one = models.ImageField(null=True, blank=True)
    image_two = models.ImageField(null=True, blank=True)
    printed_on = models.ForeignKey(Printer, on_delete=models.CASCADE)
