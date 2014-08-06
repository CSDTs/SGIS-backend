from gis.models import Dataset, MapPoint, Tag, TagIndiv, MapPolygon
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

class NestedTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag 
        fields = ['tag']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagIndiv
        fields = ('mappoint','tag')

class NewTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagIndiv
        fields = ('mappoint','tag')

    def restore_object(self, attrs, instance=None):
        #only react to a post
        if not instance:
            #find the mappoint
            mp = MapPoint.objects.get(id=attrs['mappoint']) 
            if len(mp) == 0:
                return None
            mp = mp[0]
            #create a new tag
            new_tag = Tag(dataset = mp.dataset, tag = attrs['tag'])
            new_tag.save()
            attrs['tag'] = new_tag.id
            instance = super().restore_object(attrs, instance)

        return instance

class TagCountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag 
        fields = ['dataset','tag','count']

class DatasetSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField('get_tags')
    def get_tags(self, dataset):
        #build nested distinct list
        return Tag.objects.filter(approved=True, dataset=dataset).order_by('-count').values('id','tag')

    class Meta:
        model = Dataset
        fields = ('id','name','cached','field1_en','field2_en','field3_en', 'tags')

class MapPointSerializer(serializers.HyperlinkedModelSerializer):
    latitude = serializers.DecimalField(source = 'lat')
    longitude = serializers.DecimalField(source = 'lon')

    tags = serializers.SerializerMethodField('get_tags')
    def get_tags(self, mappoint):
        #build nested distinct list
        return Tag.objects.filter(approved=True, tagindiv__mappoint=mappoint).distinct('id','tag').values('id','tag')

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
