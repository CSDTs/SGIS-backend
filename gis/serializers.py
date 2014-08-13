from gis.models import Dataset, MapPoint, Tag, TagIndiv, MapPolygon
from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

class TagSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(TagSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = TagIndiv
        fields = ('mappoint','tag')

class NewTagSerializer(serializers.ModelSerializer):
    mappoint = serializers.IntegerField()
    tag = serializers.CharField()

    class Meta:
        model = TagIndiv
        fields = ('mappoint','tag')

    def restore_object(self, attrs, instance=None):
        #only react to a post
        if not instance:
            #find the mappoint
            try:
                mp = MapPoint.objects.get(id=attrs['mappoint']) 
            except:
                return None
            attrs['tag'] = attrs['tag'].strip().lower()
            tags = Tag.objects.filter(dataset = mp.dataset, tag = attrs['tag'])
            len_tags = len(tags)
            if len_tags == 0:
                tag = Tag(dataset = mp.dataset, tag = attrs['tag'])
                tag.save()
            elif len_tags == 1:
                tag = tags[0]
            else:
                approved_tags = tags.filter(approved = True)
                if len(approved_tags) > 0:
                    tag = approved_tags[0]
                else:
                    tag = tags[0]
            instance = TagIndiv(mappoint = mp, tag = tag)  
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

class MapPolygonSerializer(gis_serializers.GeoFeatureModelSerializer):
    latitude = serializers.DecimalField(source = 'lat')
    longitude = serializers.DecimalField(source = 'lon')
    
    tags = serializers.SerializerMethodField('get_tags')
   # geometry = serializers.SerializerMethodField('get_mpoly')

    def get_tags(self, mappolygon):
        #build nested distinct list
        return Tag.objects.filter(approved=True, tagindiv__mappolygon=mappolygon).distinct('id','tag').values('id','tag')

    def get_mpoly(self, mappolygon):
        return mappolygon.mpoly

    class Meta:
        id_field = False
        geo_field = 'mpoly'
        model = MapPolygon 
        fields = ('id','dataset','remote_id','name','latitude','longitude','field1','field2','tags')

#class MapElementSerializer(gis_serializers.GeoModelSerializer):
