from django.db import models
#from django.contrib.gis.db import models #may need to switch to this later
from datetime import datetime
from django.utils.timezone import utc

import simplejson as json
import urllib

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    cached = models.DateTimeField()
    cache_max_age = models.IntegerField('age when cache should be replaced in days',default=1)
    #field names
    remote_id_field = models.CharField('column name of key field on the remote server', max_length=50)
    name_field = models.CharField(max_length=50)
    lat_field = models.CharField(max_length=50)
    lon_field = models.CharField(max_length=50)
    street_field = models.CharField(max_length=50)
    city_field = models.CharField(max_length=50)
    state_field = models.CharField(max_length=50)
    zipcode_field = models.CharField(max_length=50)
    county_field = models.CharField(max_length=50)
    field1_name = models.CharField(blank=True,max_length=50)
    field2_name = models.CharField(blank=True,max_length=50)
    field3_name = models.CharField(blank=True,max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    #recurses through structure of fields and the json
    # , = level
    # + = concatenation of 2 or more fields.
    def reach_field(self, json_item, location):
        result = ''
        if len(location) > 1:
            for field in location[0]:
                if field in json_item:
                    result += self.reach_field(json_item[field], location[1:]) + ' '
        elif len(location) == 1:
            for field in location[0]:
                if field in json_item:
                    result += json_item[field].strip() + ' '
        return result.strip()

    def update_cache(self):
    	since = datetime.utcnow().replace(tzinfo=utc) - self.cached
    	if since.days < self.cache_max_age:
    		return
    	points = MapPoint.objects.filter(dataset_id = self.pk).order_by('remote_id')
        json_in = json.loads(urllib.urlopen(self.url + '?$order=' + self.remote_id_field).read())

        #dictionary to hold structure of data in remote dataset
        fields = {}
        fields['remote_id'] = [x.split('+') for x in self.remote_id_field.split(',')]
        fields['name'] = [x.split('+') for x in self.name_field.split(',')]
        fields['lat'] = [x.split('+') for x in self.lat_field.split(',')]
        fields['lon'] = [x.split('+') for x in self.lon_field.split(',')] 
        fields['street'] = [x.split('+') for x in self.street_field.split(',')] 
        fields['city'] = [x.split('+') for x in self.city_field.split(',')]
        fields['state'] = [x.split('+') for x in self.state_field.split(',')] 
        fields['zipcode'] = [x.split('+') for x in self.zipcode_field.split(',')] 
        fields['county'] = [x.split('+') for x in self.county_field.split(',')]
        fields['field1'] = [x.split('+') for x in self.field1_name.split(',')]
        fields['field2'] = [x.split('+') for x in self.field2_name.split(',')]
        fields['field3'] = [x.split('+') for x in self.field3_name.split(',')]

        rec_read = len(json_in)
        i = 0
        while len(json_in) > 0:
            for item in json_in:
                if i < len(points):
                    if points[i].remote_id == str(item[self.remote_id_field]):
                        i += 1
                        continue
                    elif points[i].remote_id < str(item[self.remote_id_field]):
                        points[i].delete()
                        continue
                new_point = MapPoint(dataset = self)
                for field in fields:
                    temp = self.reach_field(item, fields[field])
                    if field in ['lat','lon']:
                        try:
                            temp = float(temp)
                        except:
                            continue
                    setattr(new_point, field, temp)
                new_point.save() 
            json_in = json.loads(urllib.urlopen(self.url + '?$order=' + self.remote_id_field + '&$offset=' + str(rec_read)).read())
            rec_read += len(json_in)
        self.cached = datetime.utcnow().replace(tzinfo=utc)

    def save(self, *args, **kwargs):
        self.update_cache()
        super(Dataset, self).save(*args, **kwargs)
        

class MapPoint(models.Model):
	dataset = models.ForeignKey(Dataset)
	remote_id = models.CharField(max_length=50)
	name = models.CharField(max_length=150)
	lat = models.FloatField()
	lon = models.FloatField()
	street = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=2)
	zipcode = models.CharField(max_length=5)
	county = models.CharField(max_length=75)
	field1 = models.CharField(blank=True,max_length=200)
	field2 = models.CharField(blank=True,max_length=200)
	field3 = models.CharField(blank=True,max_length=200)

	def __unicode__(self):
		return self.name
