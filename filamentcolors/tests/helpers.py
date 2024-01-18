from io import BytesIO
from random import randrange

from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


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
