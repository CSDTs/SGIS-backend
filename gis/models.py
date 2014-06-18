from django.db import models
#from django.contrib.gis.db import models
from datetime import datetime
from django.utils.timezone import utc

import simplejson as json
import urllib
import re

class Dataset(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=300)
    cached = models.DateTimeField()
    cache_max_age = models.IntegerField('age when cache should be replaced in days',default=1)
    #field names
    remote_id_field = models.CharField('column name of key field on the remote server', max_length=50)
    name_field = models.CharField(max_length=50)

    field1_name = models.CharField(blank=True,max_length=50)
    field2_name = models.CharField(blank=True,max_length=50)
    field3_name = models.CharField(blank=True,max_length=50)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name

    def update_cache(self):
    	since = datetime.utcnow().replace(tzinfo=utc) - self.cached
    	if since.days < self.cache_max_age:
    		return
    	points = MapPoint.objects.filter(dataset_id = self.pk).order_by('remote_id')
        #using SODA API?
        json_in = json.loads(urllib.urlopen(self.url + '?$order=' + self.remote_id_field).read())

        rec_read = len(json_in)
        while len(json_in) > 0:
            i = 0
            for item in json_in:
                if i < len(points):
                    if points[i].remote_id == str(item[self.remote_id_field]):
                        i += 1
                        continue
                    elif points[i].remote_id < str(item[self.remote_id_field]):
                        points[i].delete()
                        continue
                new_point = MapPoint(dataset = self, 
                    remote_id = str(item[self.remote_id_field]).strip(),
                    name = item[self.name_field].strip())
                if 'lat' in item.keys() and 'lon' in item.keys():
                    new_point.lat = item['lat']
                    new_point.lon = item['lon']
                elif 'latitude' in item.keys() and 'longitude' in item.keys():
                    new_point.lat = item['latitude']
                    new_point.lon = item['longitude']
                elif 'location' in item.keys() and 'latitude' in item['location'].keys() and 'longitude' in item['location'].keys():
                    new_point.lat = item['location']['latitude']
                    new_point.lon = item['location']['longitude']
                if 'street' in item.keys():
                    new_point.street = item['street']
                elif 'street_name' in item.keys():
                    new_point.street = item['street_name']
                if 'street_number' in item.keys():
                    new_point.street = item['street_number'] + ' ' + new_point.street
                new_point.city = item['city']
                new_point.state = item['state'][0:2]
                new_point.zipcode = item['zip_code'][0:5]
                new_point.county = item['county']
                
                if self.field1_name != '':
                    new_point.field1 = item[self.field1_name]
                    if self.field2_name != '':
                        new_point.field2 = item[self.field2_name],
                        if self.field3_name != '':
                            new_point.field3 = item[self.field3_name]
                new_point.save() 
            json_in = json.loads(urllib.urlopen(self.url + '?$order=' + self.remote_id_field + '&$offset=' + str(rec_read)).read())
            rec_read += len(json_in)
        self.cached = datetime.utcnow().replace(tzinfo=utc)


    def save(self, *args, **kwargs):
        super(Dataset, self).save(*args, **kwargs)
        self.update_cache()
        

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