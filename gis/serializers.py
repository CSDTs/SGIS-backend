from gis.models import Dataset, MapPoint, Tag, MapPolygon
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

class NestedTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag 
        fields = ['tags']

class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag 
        fields = ['dataset','mappoint','tag']

class TagCountSerializer(serializers.HyperlinkedModelSerializer):
    num_tags = serializers.Field(
        source='tags.num_tags')
    class Meta:
        model = Tag 
        fields = ['dataset','tag','num_tags']

class DatasetSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField('get_tags')
    def get_tags(self, dataset):
        #build nested distinct list
        return Tag.objects.filter(approved=True, dataset=dataset).distinct('tag').values_list('tag', flat=True)

    class Meta:
        model = Dataset
        fields = ('id','name','cached','field1_en','field2_en','field3_en', 'tags')

class MapPointSerializer(serializers.HyperlinkedModelSerializer):
    latitude = serializers.DecimalField(source = 'lat')
    longitude = serializers.DecimalField(source = 'lon')

    tags = serializers.SerializerMethodField('get_tags')
    def get_tags(self, mappoint):
        #build nested distinct list
        return Tag.objects.filter(approved=True, mappoint=mappoint).distinct('tag').values_list('tag', flat=True)

    class Meta:
        model = MapPoint 
        fields = ('dataset','id','name','latitude','longitude','street','city','state','zipcode','county','field1','field2','field3','tags')

class MapPolygonSerializer(serializers.HyperlinkedModelSerializer):
    latitude = serializers.DecimalField(source = 'lat')
    longitude = serializers.DecimalField(source = 'lon')
    tags = serializers.RelatedField(required = False, many = True, read_only = True)

    class Meta:
        model = MapPolygon 
        fields = ('dataset','remote_id','name','latitude','longitude','field1','field2','mpoly','tags')

#class MapElementSerializer(gis_serializers.GeoModelSerializer):
