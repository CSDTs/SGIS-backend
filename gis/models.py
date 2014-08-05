from django.contrib.gis.db import models
#from django.contrib.gis.db import models #may need to switch to this later
from datetime import datetime
from django.utils.timezone import utc
from django.conf import settings
from django.db.models import Q#, Count

import json, urllib, pycurl, decimal

BATCH_SIZE = 5000

class Dataset(models.Model):
	name = models.CharField(max_length=200)
	url = models.URLField(blank=True,max_length=300)
	cached = models.DateTimeField(null=True,blank=True)
	cache_max_age = models.IntegerField('age when cache should be replaced in days',default=1)
	#field names
	remote_id_field = models.CharField('column name of key field on the remote server',blank=True, max_length=50, default='id')
	name_field = models.CharField(max_length=50,default='name')
	lat_field = models.CharField(max_length=50,default='latitude')
	lon_field = models.CharField(max_length=50,default='longitude')
	street_field = models.CharField(max_length=50,default='street')
	city_field = models.CharField(max_length=50,default='city')
	state_field = models.CharField(max_length=50,default='state')
	zipcode_field = models.CharField(max_length=50,default='zip')
	county_field = models.CharField(max_length=50,default='county')
	field1_en = models.CharField(blank=True,max_length=150)
	field1_name = models.CharField(blank=True,max_length=50)
	field2_en = models.CharField(blank=True,max_length=150)
	field2_name = models.CharField(blank=True,max_length=50)
	field3_en = models.CharField(blank=True,max_length=150)
	field3_name = models.CharField(blank=True,max_length=50)
	needs_geocoding = models.BooleanField(default = False)

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

	def update_mappoints(self):
		if self.url == '': #this can only be done through manual updates
			return
		if self.should_update():
			self.loop_thru_cache()
		elif self.needs_geocoding:
			for point in MapPoint.objects.filter(dataset_id = self.pk).order_by('remote_id'):
				if not point.geocoded:
					r = point.geocode()
					if r['status'] == 'OVER_QUERY_LIMIT':
						return # ENDS FUNCTION
					point.save()
			self.needs_geocoding = False
			self.save()

	def loop_thru_cache(self):
		added = 0
		geocoded = 0

		points = MapPoint.objects.filter(dataset_id = self.pk).order_by('remote_id')
		if self.remote_id_field == '':
			plus = ''
		else:
			plus = '?$order=' + self.remote_id_field
		json_in = json.loads(urllib.urlopen(self.url + plus).read())
		if plus == '':
			plus = '?'
		else:
			plus += '&'
		#if json_in['error']:

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

		
		try_geocoding = self.needs_geocoding
		rec_read = len(json_in)
		i = 0
		while len(json_in) > 0:
			for item in json_in:
				if i < len(points) and self.remote_id_field != '':
					if points[i].remote_id == str(item[self.remote_id_field]):
						if try_geocoding and not points[i].geocoded:
							r = points[i].geocode()
							if r['status'] == 'OVER_QUERY_LIMIT':
								try_geocoding = False
								print '--%d geocoded--' %(geocoded)
							else:
								geocoded += 1
						i += 1
						continue
					elif points[i].remote_id < str(item[self.remote_id_field]):
						print 'Deleting point:', points[i]
						points[i].delete()

						continue
				new_point = MapPoint(dataset = self)
				for field in fields:
					temp = self.reach_field(item, fields[field]).strip()
					if field in ['lat','lon']:
						l = len(temp)
						if l > 19 and temp[0] == '-':
							temp = temp[:19]
						elif l > 18:
							temp = temp[:18]
						try:
							temp = decimal.Decimal(temp)
						except:
							continue
					elif len(temp) > MapPoint._meta.get_field(field).max_length:
						temp = temp[0:MapPoint._meta.get_field(field).max_length]
					setattr(new_point, field, temp)
				if try_geocoding:
					r = new_point.geocode()
					if r['status'] == 'OVER_QUERY_LIMIT':
						try_geocoding = False
					else:
						geocoded += 1
				try:
					new_point.save()
				except:
					new_point.lat = decimal.Decimal("0")
					new_point.lon = decimal.Decimal("0")
					new_point.save()
				added += 1
				if added >= BATCH_SIZE:
					if try_geocoding:
						print '--%d added, %d geocoded--' %(added, geocoded)
					else:
						print '--%d added--' %(added)
					return
			json_in = json.loads(urllib.urlopen(self.url + plus + '$offset=' + str(rec_read)).read())
			rec_read += len(json_in)
		self.cached = datetime.utcnow().replace(tzinfo=utc)
		if try_geocoding: #if still able to geocode, must have completed set
			self.needs_geocoding = False
		print '--%d added, %d geocoded--' %(added,geocoded)
		self.save()

	def should_update(self):
		if self.cached is None or self.cached == '':
			return True
		since = datetime.utcnow().replace(tzinfo=utc) - self.cached
		if since.days < self.cache_max_age or since.seconds < 60:
			return False
		return True

class MapElement(models.Model):
	dataset = models.ForeignKey(Dataset)
	remote_id = models.CharField(max_length=50)
	name = models.CharField(max_length=150)
	lat = models.DecimalField(max_digits=17, decimal_places=15)
	lon = models.DecimalField(max_digits=17, decimal_places=15)
	field1 = models.CharField(blank=True,max_length=200)
	field2 = models.CharField(blank=True,max_length=200)
	field3 = models.CharField(blank=True,max_length=200)

	objects = models.GeoManager()

	def __unicode__(self):
		return self.name

	class Meta:
		abstract = True


class MapPoint(MapElement):
	street = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=2)
	zipcode = models.CharField(max_length=5)
	county = models.CharField(max_length=75)
	geocoded = models.BooleanField(default = False)

	def geocode(self, unknown_count = 0):
		key = settings.GOOGLE_API_KEY
		location = urllib.quote_plus(self.street + ', ' + self.city + ', ' + self.state + ', ' + self.zipcode)
		request = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s&sensor=false' % (location, key)
		j = json.loads(urllib.urlopen(request).read())
		if j['status'] == 'OK':
			try:
				self.lat = decimal.Decimal(j['results'][0]['geometry']['location']['lat'])
				self.lon = decimal.Decimal(j['results'][0]['geometry']['location']['lng'])
				self.geocoded = True
			except:
				return  {'status':'conversion_error','request': request}
		elif j['status'] == 'UNKNOWN_ERROR' and unknown_count < 5: #this error type means the request can be retried
			return self.geocode(unknown_count + 1)

		assert j['status'] == 'OK' or j['status'] == 'OVER_QUERY_LIMIT' or j['status'] == 'ZERO_RESULTS' #want to debug other errors
		if j['status'] == 'OVER_QUERY_LIMIT':
			print 'Hit Google Maps API daily query limit'
		return {'status': j['status'], 'request': request}

class MapPolygon(MapElement):
	mpoly = models.MultiPolygonField()

class Tag(models.Model):
	dataset = models.ForeignKey(Dataset, related_name = 'tags')
	tag = models.CharField(max_length = 100)
	approved = models.BooleanField(default=False)
	count = models.IntegerField(default=0)
	
	def __unicode__(self):
		return self.tag

	def increment_count(self, save=True): #not necessary, but would rather have the code centralized
		self.count += 1
		if save:
			self.save()

	def recount(self, save=True):
		self.count = TagIndiv.objects.filter(Q(tag=self), Q(mappoint__dataset_id=self.dataset_id) | Q(mappoint__dataset_id=self.dataset_id)).count()
		if save:
			self.save()

class TagIndiv(models.Model):
	tag = models.ForeignKey(Tag)
	mappoint = models.ForeignKey(MapPoint, null = True, blank = True)
	mappolygon = models.ForeignKey(MapPolygon, null = True, blank = True)

	def __unicode__(self):
		return self.mappoint.name + ' tagged as "' + self.tag.tag + '"'