from gis.models import Dataset, MapPoint
from rest_framework import serializers


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Dataset
        fields = ('id','name','url','cached','cache_max_age','remote_id_field','name_field','field1_name','field2_name','field3_name')
class MapPointSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = MapPoint 
		fields = ('dataset','remote_id','name','lat','lon','street','city','state','zipcode','county','field1','field2','field3')