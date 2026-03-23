import pytest
from django.urls import reverse
from filamentcolors.models import Manufacturer, Swatch
from filamentcolors.tests.helpers import get_swatch, get_manufacturer

@pytest.mark.django_db
def test_manufacturer_filter_hides_blacklisted_mfr(client):
    # Setup two manufacturers with published swatches
    m1 = get_manufacturer(name="Manufacturer 1")
    m2 = get_manufacturer(name="Manufacturer 2")
    get_swatch(manufacturer=m1, color_name="Blue", published=True)
    get_swatch(manufacturer=m2, color_name="Red", published=True)
    
    # Verify both are in the initial view
    response = client.get(reverse('library'))
    content = response.content.decode()
    assert f'data-mfr-slug="{m1.slug}"' in content
    assert f'data-mfr-slug="{m2.slug}"' in content
    assert "Some manufacturers have been hidden based on your current settings." not in content

    # Blacklist Manufacturer 1
    # The cookie format is IDs separated by hyphen, ending with hyphen
    client.cookies['mfr-blacklist'] = f"{m1.id}-"
    
    response = client.get(reverse('library'))
    content = response.content.decode()
    
    # AFTER FIX BEHAVIOR: Manufacturer 1 should be hidden
    # and the notice should be present.
    assert f'data-mfr-slug="{m2.slug}"' in content
    assert f'data-mfr-slug="{m1.slug}"' not in content
    assert "Some manufacturers have been hidden based on your current settings." in content

@pytest.mark.django_db
def test_manufacturer_filter_no_notice_if_blacklisted_mfr_has_no_swatches(client):
    # Setup two manufacturers, but only one has swatches
    m1 = get_manufacturer(name="Manufacturer 1")
    m2 = get_manufacturer(name="Manufacturer 2")
    get_swatch(manufacturer=m2, color_name="Red", published=True)
    
    # Blacklist Manufacturer 1 (which has no swatches anyway)
    client.cookies['mfr-blacklist'] = f"{m1.id}-"
    
    response = client.get(reverse('library'))
    content = response.content.decode()
    
    # Manufacturer 1 shouldn't be in the list anyway
    assert f'data-mfr-slug="{m1.slug}"' not in content
    assert f'data-mfr-slug="{m2.slug}"' in content
    # The notice should NOT be present because hiding m1 didn't change the list
    assert "Some manufacturers have been hidden based on your current settings." not in content
