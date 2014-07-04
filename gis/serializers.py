from gis.models import Dataset, MapPoint, Tag
from rest_framework import serializers

class TagSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Tag 
		fields = ('dataset','mappoint','tag')

class TagCountSerializer(serializers.HyperlinkedModelSerializer):
	num_tags = serializers.IntegerField(
    	source='tag_set.count', 
    	read_only=True)
	class Meta:
		model = Tag 
		fields = ['dataset','tag','num_tags']

class DatasetSerializer(serializers.HyperlinkedModelSerializer):
	#tags = TagSerializer(source = 'tag')
	class Meta:
		model = Dataset
		fields = ('id','name','cached','field1_en','field2_en','field3_en')
class MapPointSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = MapPoint 
		fields = ('dataset','id','name','lat','lon','street','city','state','zipcode','county','field1','field2','field3')