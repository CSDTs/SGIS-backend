from time import sleep
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from gis_csdt.models import Location, GeoCoordinates, DatasetNameField, Dataset, MapPoint, MapElement, Sensor, DataPoint, PhoneNumber, MapPolygon, DataElement, DataField
from gis_csdt.views import DataToGSM7
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, TestSerializer, MapPolygonSerializer, CountPointsSerializer, AnalyzeAreaSerializer, AnalyzeAreaNoValuesSerializer, DataPointSerializer, SensorSerializer

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from rest_framework.request import Request
import urllib

User = get_user_model()

class TestDatasetSerializer(TestCase):
	def test_dataset_serializer(self):
		ds = Dataset(name="RPI")
		ds.save()
		data = {'name': 'RPI'}
		serializer = DatasetSerializer(data=data)
		self.assertTrue(serializer.is_valid())
		self.assertEqual(serializer.get_count(ds), 0)
		me = MapElement(dataset=ds)
		me.save()
		self.assertEqual(serializer.get_count(ds), 1)

class TestTestSerializer(TestCase):
	fixtures = ['test_data.json']

	def test_can_create_serializer(self):
		mp = MapPoint.objects.get(pk=1)
		ds = Dataset.objects.get(pk=1)
		me = MapElement(dataset=ds, mappoint=mp)
		me.save()
		df = DataField(dataset=ds, field_type='I', field_name='int_data', field_en='test')
		df.save()
		element = DataElement(mapelement=me, datafield=df, int_data=23)
		element.save()
		request = RequestFactory().put('/?data=all')
		self.user = User.objects.get(username='test')
		request.user = self.user
		# convert the HTTP Request object to a REST framework Request object
		self.request = APIView().initialize_request(request) 
		serializer = TestSerializer(context={'request': self.request})
		expected_address = {"street": "", "city": "Troy", "state": "NY", "zipcode": "", "county": ""}
		self.assertEqual(serializer.get_address(me), expected_address)
		self.assertEqual(serializer.get_data(me), {'test': 23})

class TestCountPointsSerializer(TestCase):
	fixtures = ['test_data.json']

	def test_can_create_serializer(self):
		ds = Dataset.objects.get(pk=1)		
		polygon = MapPolygon(lat='42.7302', lon=73.6788)
		me = MapElement(dataset=ds, mappolygon=polygon)
		me.save()
		serializer = CountPointsSerializer()
