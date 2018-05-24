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

class SMSCreateData(LiveServerTestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test',
                                                  email='test@test.test',
                                                  password='test')
        self.assertTrue(self.client.login(username='test', password='test'))

    def test_SMS(self):       
        set = Dataset.objects.create(name='test')
        set.save()
        point = MapPoint.objects.create(lat=0,lon=0)
        point.save()
        sensor = Sensor.objects.create(name='test')
        sensor.save()
        phNum = PhoneNumber.objects.create(phone_number=11111111111,user=self.user)
        phNum.save()
        data = [1,1,0,128,129,300,10001]
        data[1] = point.id # get the correct point id
        string = DataToGSM7(data)
        postData = {'Body': string.encode('utf-8'), 'From': phNum.phone_number}
        response = self.client.post('/api-SMS/', urllib.urlencode(postData), content_type='application/x-www-form-urlencoded')
        self.assertEqual(DataPoint.objects.get(pk=5).value, 10001)

class TestMapPoint(TestCase):
    def test_can_create_new_mappoint(self):
        original_count = MapPoint.objects.all().count()       
        point = MapPoint(lat=43.0831, lon=73.7846)
        point.save()
        sleep(1)
        self.assertEqual(MapPoint.objects.all().count(), original_count + 1)
        self.assertEqual(point.lat, Decimal(43.0831))


class TestAddMapPointAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test',
                                                  email='test@test.test',
                                                  password='test')
        self.assertTrue(self.client.login(username='test', password='test'))        

    def test_api_can_add_mappoint(self):
        original_count = MapPoint.objects.all().count()
        self.mp_data = {'lat': 31.7, 'lon': 68.9}
        self.response = self.client.post('/api-addmp/', self.mp_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MapPoint.objects.all().count(), original_count + 1)

class TestAddDatasetAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(username='test',
                                                  email='test@test.test',
                                                  password='test')
        self.assertTrue(self.client.login(username='test', password='test'))        

    def test_api_can_add_dataset(self):
        original_count = Dataset.objects.all().count()
        location = Location.objects.create(state_field='NY')
        location.save()
        self.ds_data = {'name': 'Catskill', 'location_id': location.id}
        self.response = self.client.post('/api-addds/', self.ds_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dataset.objects.all().count(), original_count + 1)
