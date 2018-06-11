from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.core.urlresolvers import reverse

from time import sleep
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon, MultiPolygon, Point

from gis_csdt.models import Location, GeoCoordinates, DatasetNameField, Dataset, MapPoint, MapElement, Sensor, DataPoint, PhoneNumber, MapPolygon
from gis_csdt.views import DataToGSM7
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, MapPolygonSerializer, CountPointsSerializer, AnalyzeAreaSerializer, AnalyzeAreaNoValuesSerializer, DataPointSerializer, SensorSerializer

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
import urllib
from decimal import Decimal
from datetime import datetime
import pytz
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
        cached = datetime(year=2017, month=10, day=12, hour=12, minute=46, tzinfo=pytz.UTC)
        dataset1 = Dataset(name="Saratoga Spring", cached=cached, coordinates=geo1)
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
        self.assertEqual(dataset1.should_update(), True)

    def test_reach_field(self):
        ds = Dataset.objects.get(pk=1)
        result = ds.reach_field({'field2':'test2', 'field3':'test3'}, [['field1', 'field2', 'field3']])
        self.assertEqual(result, 'test2 test3')

        result = ds.reach_field({'field2':{'field4': 'test4'}}, [['field1', 'field2', 'field3'], ['field4', 'field5']])
        self.assertEqual(result, 'test4')

class TestMapPoint(TestCase):
    def test_can_create_new_mappoint(self):
        original_count = MapPoint.objects.all().count()       
        point = MapPoint(lat=42.7302, lon=73.6788, city='Troy', state='NY')
        point.save()
        sleep(1)
        self.assertEqual(MapPoint.objects.all().count(), original_count + 1)
        self.assertEqual(point.lat, Decimal(42.7302))
        status = point.geocode()['status']
        self.assertTrue(status == 'OK' or status == 'OVER_QUERY_LIMIT' or status == 'ZERO_RESULTS')

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

class TestMapElement(TestCase):
    fixtures = ['test_data.json']

    def test_can_create_mapelement(self):
        ds = Dataset.objects.get(pk=1)
        p1 = Polygon( ((0, 0), (0, 1), (1, 1), (0, 0)) )
        p2 = Polygon( ((1, 1), (1, 2), (2, 2), (1, 1)) )
        mpoly = MultiPolygon(p1, p2)
        polygon = MapPolygon(lat='42.7302', lon='73.6788', field1=1.0, field2=2.0, mpoly=mpoly, dataset=ds)
        polygon.save()  
        mp = MapPoint.objects.get(pk=1)
        original_count = MapElement.objects.all().count()
        me = MapElement(dataset=ds, remote_id='123', name='element', mappolygon=polygon, mappoint=mp)
        me.save()
        self.assertEqual(MapElement.objects.all().count(), original_count + 1)
        self.assertEqual(me.name, 'element')
        self.assertEqual(me.polygon_id(), me.id)
        self.assertEqual(me.point_id(), me.id)