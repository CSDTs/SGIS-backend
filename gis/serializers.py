from gis.models import Dataset, MapPoint, Tag
from rest_framework import serializers

class TagSerializer(serializers.HyperlinkedModelSerializer):
	num_tags = serializers.IntegerField(
    	source='tag_set.count', 
    	read_only=True)
	class Meta:
		model = Tag 
		fields = ['tag']

class DatasetSerializer(serializers.HyperlinkedModelSerializer):
	tags = TagSerializer(source = 'tag')
	class Meta:
		model = Dataset
		fields = ('id','name','url','cached','cache_max_age','remote_id_field','name_field','field1_name','field2_name','field3_name')
class MapPointSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = MapPoint 
		fields = ('dataset','remote_id','name','lat','lon','street','city','state','zipcode','county','field1','field2','field3')