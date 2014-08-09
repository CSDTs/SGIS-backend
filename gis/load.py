import os, decimal
from django.contrib.gis.utils import LayerMapping
from models import MapPolygon, Dataset
from datetime import datetime
from django.utils.timezone import utc

def run(verbose=True):
    ds = Dataset(name = '2010 Census Tracts',
        cached = datetime.utcnow().replace(tzinfo=utc),
        cache_max_age = 1000,
        remote_id_field = 'GEOID10',
        name_field = 'NAMELSAD10',
        lat_field = 'INTPTLAT10',
        lon_field = 'INTPTLON10',
        field1_en = 'Land Area',
        field1_name = 'ALAND10',
        field2_en = 'Water Area',
        field2_name = 'AWATER10')
    ds.save()


    tract_mapping = {
        'remote_id' : ds.remote_id_field,
        'name' : ds.name_field,
        'lat' : ds.lat_field,
        'lon' : ds.lon_field,
        'field1' : ds.field1_name,
        'field2' : ds.field2_name,
        'mpoly' : 'MULTIPOLYGON',
    }

    tract_shp = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/tl_2010_36_tract10.shp'))

    lm = LayerMapping(MapPolygon, tract_shp, tract_mapping, transform=False, encoding='iso-8859-1')

    lm.save(strict=True, verbose=verbose)
    for mp in MapPolygon.objects.filter(dataset_id = None):
        mp.dataset = ds
        lat = decimal.Decimal(mp.field1)
        lon = decimal.Decimal(mp.field2)
        mp.field1 = str(mp.lat)
        mp.field2 = str(mp.lon)
        mp.lat= lat
        mp.lon = lon
        mp.save()

