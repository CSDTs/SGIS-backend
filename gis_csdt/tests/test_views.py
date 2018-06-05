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
        mappoint = MapPoint.objects.create(lat=0,lon=0)
        mappoint.save()
        sensor = Sensor.objects.create(name='test', mappoint=mappoint, user=self.user)
        sensor.save()
        phNum = PhoneNumber.objects.create(phone_number=11111111111,user=self.user)
        phNum.save()
        data = [1,1,0,128,129,300,10001]
        data[1] = mappoint.id # get the correct point id
        data[0] = sensor.id
        string = DataToGSM7(data)
        postData = {'Body': string.encode('utf-8'), 'From': phNum.phone_number}
        response = self.client.post('/api-SMS/', urllib.urlencode(postData), content_type='application/x-www-form-urlencoded')
        self.assertEqual(DataPoint.objects.get(pk=7).value, 10001)

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
        self.assertEqual(Dataset.objects.get(pk=5).name, 'Catskill')
        self.assertEqual(Dataset.objects.get(pk=5).location.state_field, 'NY')