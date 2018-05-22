from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse
from time import sleep
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from gis_csdt.models import Location, GeoCoordinates, Dataset

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
        geo1 = GeoCoordinates(lat_field="43.0831N", lon_field="73.7846W")
        geo1.save()
        dataset1 = Dataset(name="Saratoga Spring", cached="2017-10-12T12:46:00.258Z", coordinates=geo1)
        dataset1.save()
        sleep(1)
        self.assertEqual(Dataset.objects.all().count(), original_count + 1)
        self.assertEqual(dataset1.coordinates.lat_field, "43.0831N")
        original_count += 1

        loc2 = Location(city_field="Troy", state_field="NY")
        loc2.save()
        dataset2 = Dataset(name="RPI", location=loc2)
        dataset2.save()
        self.assertEqual(Dataset.objects.all().count(), original_count + 1)
        self.assertEqual(dataset2.location.city_field, "Troy")
        self.assertEqual(dataset2.coordinates, None)

