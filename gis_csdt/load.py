##This file includes functions to load basic information
##should be used from the shell

import os, decimal, json, urllib
from django.contrib.gis.utils import LayerMapping
from models import MapPolygon, MapPoint, Dataset, DataField, DataElement, Tag, TagIndiv
from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.contrib.gis.geos import Polygon, Point

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

    ds.save()

    MapPolygon.objects.filter(dataset = None).update(dataset = ds)
    
'''def temp_switch():
    for poly in MapPolygon.objects.all():
        lat = poly.field1
        lon = poly.field2
        poly.field1 = poly.lat
        poly.field2 = poly.lon
        poly.lat = lat
        poly.lon = lon
        poly.save()'''

def recount():
    all_tags = Tag.objects.all()
    for tag in all_tags:
        tag.recount(save=True)

def get_income():
    key = settings.CENSUS_API_KEY
    state = '36'

    ds = Dataset.objects.filter(name__icontains='census').filter(name__contains='2010').all()
    if len(ds) == 0:
        print 'No Census dataset exists. Aborting'
        return
    elif len(ds) > 1:
        print 'More than one 2010 Census dataset exists. Using ID %d' %(d[0].id)

    #http://www.census.gov/data/developers/data-sets/acs-survey-5-year-data.html
    #http://api.census.gov/data/2010/acs5/variables.html
    #              median household income                                     Total population
    to_process = [{'variable':'B19013_001E', 'variable_type':DataField.INTEGER}, {'variable':'B01003_001E', 'variable_type':DataField.INTEGER}]
    dfs = []
    get = ''
    for item in to_process:
        request = 'http://api.census.gov/data/2010/acs5/variables/%s.json' %(item['variable'])
        data = json.loads(urllib.urlopen(request).read())
        dfs.append(DataField(dataset = ds[0], field_en = data['concept'][7:].strip(), field_longname = data['label'], field_name = item['variable'], field_type = item['variable_type']))
        dfs[-1].save()
        get = get + ',' + item['variable']
    get = get.strip(', ')

    #get the data
    request = 'http://api.census.gov/data/2010/acs5?key=%s&get=%s,NAME&for=tract:*&in=state:%s' %(key,get,state)
    data = json.loads(urllib.urlopen(request).read())
    converted = {}
    #locations of basic data in each list
    #format like:
    #[["B19013_001E","B01003_001E","NAME","state","county","tract"],
    #["32333","2308","Census Tract 1, Albany County, New York","36","001","000100"],
    #...]
    for col in range(len(data[0])):
        if data[0][col] == 'NAME':
            n = col
        elif data[0][col] == 'state':
            s = col
        elif data[0][col] == 'county':
            c = col
        elif data[0][col] == 'tract':
            t = col
    for d in data[1:]:
        census_tract = d[s] + d[c] + d[t]
        converted[census_tract] = {}
        for num in range(n):
            if d[num] is not None:
                converted[census_tract][data[0][num]] = d[num].strip()
    #converted now looks like
    # {"36001000100": {"B19013_001E": "32333","B01003_001E": "2308"},
    #  "36001000200": {"B19013_001E": "25354","B01003_001E": "5506"},...}
    for poly in MapPolygon.objects.filter(dataset = ds[0]):
        if poly.remote_id in converted:
            for df in dfs:
                if df.field_name in converted[poly.remote_id]:
                    de = DataElement(datafield = df,mappolygon = poly)
                    if df.field_type == DataField.INTEGER:
                        try:
                            de.int_data = int(converted[poly.remote_id][df.field_name])
                        except:
                            print 'integer conversion failed for census tract %s, field %s' %(poly.remote_id, df.field_name)
                            print 'value:', converted[poly.remote_id][df.field_name]
                    elif df.field_type == DataField.FLOAT:
                        try:
                            de.float_data = float(converted[poly.remote_id][df.field_name])
                        except:
                            print 'float conversion failed for census tract %s, field %s' %(poly.remote_id, df.field_name)
                    elif df.field_type == DataField.STRING:
                        if len(converted[poly.remote_id][df.field_name]) > 200:
                            print 'string overload - string truncated as shown:'
                            print '%s[%s]' %(converted[poly.remote_id][df.field_name][:200],converted[poly.remote_id][df.field_name][200:])
                            de.char_data = converted[poly.remote_id][df.field_name][:200]
                        else:
                            de.char_data = converted[poly.remote_id][df.field_name]
                    de.save()
        else:
            print 'ERROR: Tract #%s is not in the dataset' %(poly.remote_id)
            
def del_all():
    DataField.objects.all().delete()

import re, string
def tag_by_name(filename='fastfood.json', name_field='Company', dataset=2, tag='fast food'):
    data = json.loads(open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'data/'+filename))).read())
    data = data['data']

    print data

    mps = MapPoint.objects.filter(dataset_id=dataset)
    tags = Tag.objects.filter(dataset_id=dataset).filter(tag=tag)
    if tags.count() > 1:
        appr_tags = tags.filter(approved=True)
        if appr_tags.count() > 0:
            tags = appr_tags
        tag = tags[0]
    elif tags.count() == 0:
        tag = Tag(dataset_id = dataset, tag = tag, approved = True)
        tag.save()
    else:
        tag = tags[0]

    regex = re.compile('[%s]' % re.escape(string.punctuation))
    for item in data:
        name = regex.sub(r'[\'\'\.-]*', item[name_field])
        print name
        for mp in mps.filter(name__iregex=name):
            print mp.name
            t = TagIndiv(tag = tag, mappoint = mp)
            t.save()
            

def add_point_to_mp():
    mps = MapPoint.objects.filter(point__isnull=True).exclude(lat__isnull=True).exclude(lon__isnull=True)
    for mp in mps:
        try:
            mp.point = Point(float(mp.lon),float(mp.lat))
            mp.save()
        except:
            pass