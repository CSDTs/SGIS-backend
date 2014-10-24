from gis_csdt.models import Dataset, MapPoint, Tag, TagIndiv, MapPolygon, DataField, DataElement
from gis_csdt.filter_tools import filter_request
from rest_framework import serializers, exceptions 
from rest_framework_gis import serializers as gis_serializers
import copy


'''class TagSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(TagSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = TagIndiv
        fields = ('mappoint','mappolygon','tag')'''

class NewTagSerializer(serializers.ModelSerializer):
    mappoint = serializers.IntegerField(required=False)
    mappolygon = serializers.IntegerField(required=False)
    tag = serializers.CharField()

    class Meta:
        model = TagIndiv
        fields = ('mappoint','mappolygon','tag')

    def restore_object(self, attrs, instance=None):
        #only react to a post
        if not instance:
            #find the mappoint
            mappoint = 'mappoint' in attrs.keys() and attrs['mappoint']!='' and attrs['mappoint'] is not None
            mappolygon = 'mappolygon' in attrs.keys() and attrs['mappolygon']!='' and attrs['mappolygon'] is not None
            if mappoint and mappolygon:
                #ambiguous - not allowed
                print attrs
                raise exceptions.ParseError()
            try:
                if mappoint:
                    mp = MapPoint.objects.get(id=attrs['mappoint'])
                else:
                    mp = MapPolygon.objects.get(id=attrs['mappolygon']) 
            except:
                raise exceptions.ParseError()
            if ',' in attrs['tag']:
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
        return TagIndiv(mapelement = mp, tag = tag)

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
    latitude = serializers.DecimalField(source = 'mappoint.lat')
    longitude = serializers.DecimalField(source = 'mappoint.lon')
    street = serializers.CharField(source = 'mappoint.street')
    city = serializers.CharField(source = 'mappoint.city')
    state = serializers.CharField(source = 'mappoint.state')
    zipcode = serializers.CharField(source = 'mappoint.zipcode')
    county = serializers.CharField(source = 'mappoint.county')
    field1 = serializers.CharField(source = 'mappoint.field1')
    field2 = serializers.CharField(source = 'mappoint.field2')
    field3 = serializers.CharField(source = 'mappoint.field3')

    tags = serializers.SerializerMethodField('get_tags')
    def get_tags(self, mappoint):
        #build nested distinct list
        return Tag.objects.filter(approved=True, tagindiv__mapelement=mappoint).distinct('id','tag').values('id','tag')

    class Meta:
        #id_field = False
        #geo_field = 'point'
        model = MapPoint 
        fields = ('dataset','id','name','latitude','longitude','street','city','state','zipcode','county','field1','field2','field3','tags')

class TestSerializer(gis_serializers.GeoFeatureModelSerializer):
    latitude = serializers.DecimalField(source = 'mappoint.lat')
    longitude = serializers.DecimalField(source = 'mappoint.lon')
    street = serializers.CharField(source = 'mappoint.street')
    city = serializers.CharField(source = 'mappoint.city')
    state = serializers.CharField(source = 'mappoint.state')
    zipcode = serializers.CharField(source = 'mappoint.zipcode')
    county = serializers.CharField(source = 'mappoint.county')
    field1 = serializers.CharField(source = 'mappoint.field1')
    field2 = serializers.CharField(source = 'mappoint.field2')
    field3 = serializers.CharField(source = 'mappoint.field3')

    tags = serializers.SerializerMethodField('get_tags')
    def get_tags(self, mappoint):
        #build nested distinct list
        return Tag.objects.filter(approved=True, tagindiv__mapelement=mappoint).distinct('id','tag').values('id','tag')

    class Meta:
        id_field = False
        geo_field = 'point'
        model = MapPoint 
        fields = ('dataset','id','name','latitude','longitude','street','city','state','zipcode','county','field1','field2','field3','tags')

class MapPolygonSerializer(gis_serializers.GeoFeatureModelSerializer):
    latitude = serializers.DecimalField(source = 'mappolygon.lat')
    longitude = serializers.DecimalField(source = 'mappolygon.lon')
    field1 = serializers.CharField(source = 'mappolygon.field1')
    field2 = serializers.CharField(source = 'mappolygon.field2')
    
    mpoly = gis_serializers.GeometryField(source = 'mappolygon.mpoly')

    tags = serializers.SerializerMethodField('get_tags')

    def get_tags(self, mappolygon):
        #build nested distinct list
        return Tag.objects.filter(approved=True, tagindiv__mapelement=mappolygon).distinct('id','tag').values('id','tag')

    class Meta:
        id_field = False
        geo_field = 'mpoly'
        model = MapPolygon 
        fields = ('id','dataset','remote_id','name','latitude','longitude','field1','field2','tags')

class CountPointsSerializer(serializers.ModelSerializer):
    polygon_id = serializers.IntegerField(source = 'remote_id')
    count = serializers.SerializerMethodField('count_points')

    def count_points(self, mappolygon):
        request = self.context.get('request', None)
        params = copy.deepcopy(request.QUERY_PARAMS)
        for key in ['max_lat','min_lat','max_lon','min_lon','state']:
            try:
                del params[key]
            except:
                pass #no big deal

        c = {mappolygon.dataset.field1_en : mappolygon.mappolygon.field1, mappolygon.dataset.field2_en : mappolygon.mappolygon.field2}

        datafields = DataField.objects.filter(dataset=mappolygon.dataset)
        #get other data
        for df in datafields:
            data = None
            if df.field_type == DataField.INTEGER:
                element = DataElement.objects.filter(datafield = df).filter(mapelement=mappolygon)
                if element:
                    data = element[0].int_data
            elif df.field_type == DataField.FLOAT:
                element = DataElement.objects.filter(datafield = df).filter(mapelement=mappolygon)
                if element:
                    data = element[0].float_data
            else:
                element = DataElement.objects.filter(datafield = df).filter(mapelement=mappolygon)
                if element:
                    data = element[0].char_data
            if data:
                c[df.field_en] = data


        
        points = filter_request(params,'mappoint').filter(point__intersects=mappolygon.mappolygon.mpoly)
        all_tags = None
        if 'tag' in params:
            all_tags = params['tag']
        elif 'tags' in params:
            all_tags = params['tags']
        if all_tags:
            tags = all_tags.split(',')
            if type(tags) is not list:
                tags = [tags]
            all_tags = all_tags.replace(',',', ')
        else:
            tags = []

        #counts in polygons
        if 'match' not in params or params['match'] != 'all':
            all_tag_filter = points
            for tag in tags:
                try:
                    num = int(tag)
                    tag_obj = Tag.objects.get(num)
                    all_tag_filter = all_tag_filter.filter(tagindiv__tag=tag_obj)
                    c[tag_obj.tag + " count"] = points.filter(tagindiv__tag=tag_obj).count()
                except:
                    all_tag_filter = all_tag_filter.filter(tagindiv__tag__tag=tag)
                    c[tag + " count"] = points.filter(tagindiv__tag__tag=tag).count()
            if len(tags) > 1:
                c[all_tags + " count (match any)"] = points.count()
                c[all_tags + " count (match all)"] = points.count()
        if len(tags) > 1:
            c[all_tags + " count (match all)"] = points.count()

        return c
    
    class Meta:
        model = MapPolygon
        fields = ('polygon_id','count')