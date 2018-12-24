from django.db import models
from django.contrib.auth.models import User


class Printer(models.Model):
    name = models.CharField(max_length=50)
    notes = models.TextField(max_length=4000, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.owner.username} - {self.name}"


class Swatch(models.Model):
    manufacturer = models.CharField(max_length=160)
    color_name = models.CharField(max_length=240)
    hex_color = models.CharField(max_length=6)
    # PLA, PETG, etc.
    filament_type = models.CharField(max_length=10, default='PLA')
    hot_end_temp = models.IntegerField(default=205)
    bed_temp = models.IntegerField(default=60)
    image_back = models.ImageField(null=True, blank=True)
    image_front = models.ImageField(null=True, blank=True)
    image_side = models.ImageField(null=True, blank=True)
    printed_on = models.ForeignKey(Printer, on_delete=models.CASCADE)
    maker = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now=True)
    notes = models.TextField(max_length=4000, null=True, blank=True)


    def __str__(self):
        return f"{self.manufacturer} - {self.color_name}"
