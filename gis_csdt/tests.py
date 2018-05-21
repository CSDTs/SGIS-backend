from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.core.urlresolvers import reverse
from gis_csdt.models import Dataset, MapPoint, Sensor, DataPoint, PhoneNumber
from gis_csdt.views import DataToGSM7
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
import urllib
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

class SMSCreateData(LiveServerTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test',
                                                  email='test@test.test',
                                                  password='test')
        self.assertTrue(self.client.login(username='test', password='test'))

    def test_SMS(self):
        data = [1,1,0,128,129,300,10001]
        string = DataToGSM7(data)
        set = Dataset.objects.create(name='test')
        set.save()
        point = MapPoint.objects.create(lat=0,lon=0)
        point.save()
        sensor = Sensor.objects.create(name='test')
        sensor.save()
        phNum = PhoneNumber.objects.create(phone_number=11111111111,user=self.user)
        phNum.save()
        postData = {'Body': string.encode('utf-8'), 'From': phNum.phone_number}
        response = self.client.post('/api-SMS/', urllib.urlencode(postData), content_type='application/x-www-form-urlencoded')
        self.assertEqual(DataPoint.objects.get(pk=5).value, 10001)
