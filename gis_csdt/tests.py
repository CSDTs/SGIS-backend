from rest_framework import status
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse


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
