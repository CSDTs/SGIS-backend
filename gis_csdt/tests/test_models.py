from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.core.urlresolvers import reverse

from time import sleep
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from gis_csdt.models import Location, GeoCoordinates, DatasetNameField, Dataset, MapPoint, Sensor, DataPoint, PhoneNumber
from gis_csdt.views import DataToGSM7
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
import urllib
from decimal import Decimal
from datetime import datetime
User = get_user_model()

class AllViewTestsNoData(APITestCase):
    def test_no_datasets(self):
        response = self.client.get('/api-ds/')
        self.assertEqual(response.status_code, 200)
    def test_no_mappoints(self):
        response = self.client.get('/api-mp/')
        self.assertEqual(response.status_code, 200)
    def test_no_newtags(self):
        response = self.client.get('/api-newtag/')
        self.assertEqual(response.status_code, 200)
    def test_no_polygons(self):
        response = self.client.get('/api-poly/')
        self.assertEqual(response.status_code, 200)
    def test_no_mappoints_geojson(self):
        response = self.client.get('/api-test/')
        self.assertEqual(response.status_code, 200)
    def test_no_mappolygons_count_of_points(self):
        response = self.client.get('/api-count/')
        self.assertEqual(response.status_code, 200)
    def test_no_mappolygons_analysis_around_point(self):
        response = self.client.get('/api-dist/')
        self.assertEqual(response.status_code, 400)

class TestDataset(TestCase):
    fixtures = ['test_data.json']

    def test_can_create_new_dataset(self):
        original_count = Dataset.objects.all().count()       
        geo1 = GeoCoordinates(lat_field="43.0831", lon_field="73.7846")
        geo1.save()
        dataset1 = Dataset(name="Saratoga Spring", cached="2017-10-12T12:46:00.258Z", coordinates=geo1)
        dataset1.save()
        sleep(1)
        self.assertEqual(Dataset.objects.all().count(), original_count + 1)
        self.assertEqual(dataset1.coordinates.lat_field, "43.0831")
        original_count += 1

        loc2 = Location(city_field="Troy", state_field="NY")
        loc2.save()
        dataset2 = Dataset(name="RPI", location=loc2)
        dataset2.save()
        self.assertEqual(Dataset.objects.all().count(), original_count + 1)
        self.assertEqual(dataset2.location.city_field, "Troy")
        self.assertEqual(dataset2.coordinates, None)
        self.assertEqual(str(dataset2), "RPI")

    def test_reach_field(self):
        ds = Dataset.objects.get(pk=1)
        result = ds.reach_field({'field2':'test2', 'field3':'test3'}, [['field1', 'field2', 'field3']])
        self.assertEqual(result, 'test2 test3')

        result = ds.reach_field({'field2':{'field4': 'test4'}}, [['field1', 'field2', 'field3'], ['field4', 'field5']])
        self.assertEqual(result, 'test4')

class TestMapPoint(TestCase):
    def test_can_create_new_mappoint(self):
        original_count = MapPoint.objects.all().count()       
        point = MapPoint(lat=43.0831, lon=73.7846)
        point.save()
        sleep(1)
        self.assertEqual(MapPoint.objects.all().count(), original_count + 1)
        self.assertEqual(point.lat, Decimal(43.0831))

class TestDataPoint(TestCase):

    def test_can_create_datapoint(self):
        user = User.objects.create_superuser(username='test',
                                             email='test@test.test',
                                             password='test')
        mappoint = MapPoint(lat=43.0831, lon=73.7846)
        mappoint.save()   
        sensor = Sensor.objects.create(name='test', user=user, mappoint=mappoint)
        sensor.save()
        dp1 = DataPoint(value=25)
        dp1.save()
        sensor.datapoints.add(dp1)
        dp2 = DataPoint(value=20)
        dp2.save()
        sensor.datapoints.add(dp2)
        self.assertEqual(sensor.mappoint.lat, 43.0831)
        self.assertEqual(sensor.datapoints.filter(value=20).count(), 1)
