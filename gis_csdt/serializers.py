from gis_csdt.models import Dataset, MapElement, MapPoint, Tag, TagIndiv, MapPolygon, DataField, DataElement, Observation, ObservationValue, Sensor
from gis_csdt.filter_tools import filter_request, neighboring_points, unite_radius_bubbles
from gis_csdt.geometry_tools import circle_as_polygon
from gis_csdt.settings import CENSUS_API_KEY
from rest_framework import serializers, exceptions
from rest_framework_gis import serializers as gis_serializers
from django.contrib.gis.measure import Distance, Area
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Count
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseNotAllowed
import copy, json, urllib

CIRCLE_EDGES = 12 #number of edges on polygon estimation of a circle

'''class TagSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(TagSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = TagIndiv
        fields = ('mappoint','mappolygon','tag')'''

class MapElementIdField(serializers.WritableField):
    def __init__(self, *args,**kwargs):
        self.field = kwargs.pop('field')
        super(MapElementIdField, self).__init__(*args, **kwargs)
    def to_native(self, obj):
        try:
            r = getattr(obj,self.field)
            return r.id
        except ObjectDoesNotExist:
            return None
    def from_native(self, data):
        try:
            return MapElement.objects.get(id=int(data))
        except (ObjectDoesNotExist, ValueError):
            return None

class NewTagSerializer(serializers.ModelSerializer):
    #mappolygon = MapElementIdField(required=False, source='mapelement_id', field='mappolygon')
    mappoint = serializers.IntegerField(source='mapelement_id')
    tag = serializers.CharField()


    class Meta:
        model = TagIndiv
        fields = ('mappoint','tag')

    def restore_object(self, attrs, instance=None):
        #find the mappoint
        try:
            mp = MapElement.objects.get(id=attrs['mapelement_id'])
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
        return TagIndiv(mapelement=mp, tag=tag)

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
        fields = ('dataset','id','name','street','city','state','zipcode','county','field1','field2','field3','tags')

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

    class Meta:
        model = MapPolygon
        fields = ('polygon_id','count')

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

class AnalyzeAreaSerializer(serializers.ModelSerializer):
    street = serializers.CharField(source = 'mappoint.street')
    city = serializers.CharField(source = 'mappoint.city')
    state = serializers.CharField(source = 'mappoint.state')
    zipcode = serializers.CharField(source = 'mappoint.zipcode')
    county = serializers.CharField(source = 'mappoint.county')
    field1 = serializers.CharField(source = 'mappoint.field1')
    field2 = serializers.CharField(source = 'mappoint.field2')
    field3 = serializers.CharField(source = 'mappoint.field3')

    tags = serializers.SerializerMethodField('get_tags')
    areaAroundPoint = serializers.SerializerMethodField('area_around_point')

    class Meta:
        model = MapPoint 
        fields = ('street','city','state','zipcode','county','field1','field2','field3','tags','areaAroundPoint')

    def get_tags(self, mappoint):
        #build nested distinct list
        return Tag.objects.filter(approved=True, tagindiv__mapelement=mappoint).distinct('tag').values('tag')
    
    def area_around_point(self, mappoint):
        request = self.context.get('request', None)

        years = request.GET.getlist('year')
        datasets = Dataset.objects.filter(name__icontains='census')
        if len(years) > 0:
            d = Dataset.objects.none()
            for y in years:
                d = d | datasets.filter(name__contains=y.strip())
            datasets = d
        if len(datasets) == 0:
            return {}
        else:
            dataset_id = datasets[0].id

        ### DISTANCES
        distances = request.GET.getlist('distance')
        unit = request.GET.getlist('unit')
        if len(unit) > 1:
            return HttpResponseBadRequest('No more than one unit may be specified.')
        elif len(unit) == 0:
            unit = 'mi'
        elif unit[0] in ['m','km','mi']:
            unit = unit[0]
        else:
            return HttpResponseBadRequest('Accepted units: m, km, mi')
        if len(distances) == 0:
            distances = [1,3,5]
            unit = 'km'
        else:
            distances.sort()

        dist_objs = []
        for dist in distances:
            kwargs = {unit: dist}
            dist_objs.append(Distance(**kwargs))

        all_points = neighboring_points(mappoint, MapPoint.objects.filter(dataset_id=mappoint.dataset_id), dist_objs[-1])

        data_sums = {'point id(s)':'', 'view url(s)':[]}
        for p in all_points:
            data_sums['point id(s)'] = data_sums['point id(s)'] + ',' + str(p.id)
            data_sums['view url(s)'].append('/around-point/%d/' %(p.id))
        data_sums['view url(s)'] = str(data_sums['view url(s)'])
        data_sums['point id(s)'] = data_sums['point id(s)'].strip(',')
        already_accounted = set()
        boundary = unite_radius_bubbles(all_points,dist_objs)
        for dist in dist_objs:
            if unit == 'm':
                dist_str = '%f m' %(dist.m)
            elif unit == 'km':
                dist_str = '%f km' %(dist.km)
            elif unit == 'mi':
                dist_str = '%f mi' %(dist.mi)
            poly = set(MapPolygon.objects.filter(dataset_id__exact=dataset_id).filter(mpoly__covers=boundary[dist]).exclude(remote_id__in=already_accounted).values_list('remote_id',flat=True))
            maybe_polys = MapPolygon.objects.filter(dataset_id__exact=dataset_id).exclude(mpoly__covers=boundary[dist]).exclude(remote_id__in=already_accounted).filter(mpoly__intersects=boundary[dist])
            for polygon in maybe_polys:
                if polygon.mpoly.intersection(boundary[dist]).area > .5 * polygon.mpoly.area:
                    poly.add(polygon.remote_id)
            already_accounted = already_accounted | poly
            data_sums[dist_str] = {}
            data_sums[dist_str]['polygon count'] = len(poly)
            data_sums[dist_str]['land area (m2)'] = sum([int(i) for i in MapPolygon.objects.filter(dataset_id__exact=dataset_id,remote_id__in=poly).values_list('field1',flat=True)])
            if data_sums[dist_str]['polygon count'] > 0:
                data_sums[dist_str]['polygons'] = str(list(poly))
                datafields = DataField.objects.filter(dataset_id__exact=dataset_id).exclude(field_type__exact=DataField.STRING)
                for field in datafields:
                    if field.field_longname not in data_sums[dist_str]:
                        data_sums[dist_str][field.field_longname] = {}
                    if field.field_type == DataField.INTEGER:
                        data = DataElement.objects.filter(datafield_id=field.id,mapelement__remote_id__in=poly).aggregate(sum=Sum('int_data'),dsum=Sum('denominator__int_data'))
                        #print data['sum'], data['dsum']
                    elif field.field_type == DataField.FLOAT:
                        data = DataElement.objects.filter(datafield_id=field.id,mapelement__remote_id__in=poly).aggregate(sum=Sum('float_data'),dsum=Sum('denominator__float_data'))
                    else:
                        continue
                    data_sums[dist_str][field.field_longname][field.field_en] = data['sum']
                    data_sums[dist_str][field.field_longname]['total']= data['dsum']

        return data_sums

    def area_around_point2(self, mappoint):
        request = self.context.get('request', None)

        years = request.GET.getlist('year')
        year = years[0]
        datasets = Dataset.objects.filter(name__icontains='census')
        if len(years) > 0:
            d = Dataset.objects.none()
            for y in years:
                d = d | datasets.filter(name__contains=y.strip())
            datasets = d
        if len(datasets) == 0:
            return {}
        else:
            dataset_id = datasets[0].id

        ### DISTANCES
        distances = request.GET.getlist('distance')
        unit = request.GET.getlist('unit')
        if len(unit) > 1:
            return HttpResponseBadRequest('No more than one unit may be specified.')
        elif len(unit) == 0:
            unit = 'mi'
        elif unit[0] in ['m','km','mi']:
            unit = unit[0]
        else:
            return HttpResponseBadRequest('Accepted units: m, km, mi')
        if len(distances) == 0:
            distances = [1,3,5]
            unit = 'km'
        else:
            distances.sort()

        dist_objs = []
        for dist in distances:
            kwargs = {unit: dist}
            dist_objs.append(Distance(**kwargs))

        all_points = neighboring_points(mappoint, MapPoint.objects.filter(dataset=mappoint.dataset_id), dist_objs[-1])
        print all_points

        #variables = ['Total Population','Area (km2)','Total (Race)', 'White Only', 'African American', 'Hispanic','Asian/Pacific Islander', 'Native American','Total (Poverty)','below 1.00', 'weighted mean of median household income','Mean Housing Value']
        #variables = {'B02001_001E':{},'B02001_002E':{},'B02009_001E':{},'B03001_001E':{},'B03001_003E':{},'B02011_001E':{}, 'B02012_001E':{},'B02010_001E':{},'B05010_001E':{},'B05010_002E':{},'B19061_001E':{},'B25105_001E':{},'B25077_001E':{},'B25077_001E':{}}
        variables = {'B00001_001E':{},'B02001_001E':{},'B02001_002E':{},'B02001_003E':{},'B02001_004E':{},'B02001_005E':{},'B02001_006E':{},'B02001_007E':{},'B02001_008E':{},'B03001_001E':{},'B03001_003E':{},'C17002_001E':{},'C17002_002E':{},'C17002_003E':{}}
        for v in variables:
            request = 'http://api.census.gov/data/2010/acs5/variables/%s.json?key=%s' %(v,CENSUS_API_KEY)
            try:
                data = json.loads(urllib.urlopen(request).read())
            except Exception as e:
                print 'variable info for %s failed to load: %s'%(v,request)
                print e
                continue
            variables[v] = data


        data_sums = {'point id(s)':'', 'view url(s)':[]}
        for p in all_points:
            data_sums['point id(s)'] = data_sums['point id(s)'] + ',' + str(p.id)
            data_sums['view url(s)'].append('/around-point/%d/' %(p.id))
        data_sums['point id(s)'] = data_sums['point id(s)'].strip(',')
        already_accounted = set()

        boundary = unite_radius_bubbles(all_points,dist_objs)
        for dist in dist_objs:
            if unit == 'm':
                dist_str = '%f m' %(dist.m)
            elif unit == 'km':
                dist_str = '%f km' %(dist.km)
            elif unit == 'mi':
                dist_str = '%f mi' %(dist.mi)
            poly = set(MapPolygon.objects.filter(dataset_id__exact=dataset_id).filter(mpoly__covers=boundary[dist]).exclude(remote_id__in=already_accounted).values_list('remote_id',flat=True))
            maybe_polys = MapPolygon.objects.filter(dataset_id__exact=dataset_id).exclude(mpoly__covers=boundary[dist]).exclude(remote_id__in=already_accounted).filter(mpoly__intersects=boundary[dist])
            for polygon in maybe_polys:
                if polygon.mpoly.intersection(boundary[dist]).area > .5 * polygon.mpoly.area:
                    poly.add(polygon.remote_id)
            already_accounted = already_accounted | poly
            data_sums[dist_str] = {}
            data_sums[dist_str]['polygon count'] = len(poly)
            data_sums[dist_str]['land area (m2)'] = sum([int(i) for i in MapPolygon.objects.filter(dataset_id__exact=dataset_id,remote_id__in=poly).values_list('field1',flat=True)])
            if data_sums[dist_str]['polygon count'] > 0:
                data_sums[dist_str]['polygons'] = str(list(poly))
                if year == '2010':
                    get = ''
                    for e in variables:
                        get = get + ',' + e
                    get = get.strip(',')
                    tracts = {}
                    for e in poly:
                        if e[:2] not in tracts:
                            tracts[e[:2]] = {}
                        if e[2:5] not in tracts[e[:2]]:
                            tracts[e[:2]][e[2:5]]=''
                        tracts[e[:2]][e[2:5]] = tracts[e[:2]][e[2:5]] + ',' + e[-6:]
                    for state in tracts:
                        for county in tracts[state]:
                            request = 'http://api.census.gov/data/2010/acs5?key=%s&get=%s,NAME&for=tract:%s&in=state:%s,county:%s' %(CENSUS_API_KEY,get,tracts[state][county].strip(','),state,county)
                            try:
                                url = urllib.urlopen(request).read()
                                data = json.loads(url)
                            except Exception as e:
                                print e
                                print url
                                print request
                                continue
                            line = data[0]
                            locations = {}
                            for i in range(len(line)):
                                locations[line[i]] = i
                                if line[i] not in data_sums[dist_str] and line[i] in variables:
                                    data_sums[dist_str][line[i]] = copy.deepcopy(variables[line[i]])
                                    data_sums[dist_str][line[i]]['sum'] = 0

                            for line in data[1:]:
                                #get area
                                for v in variables:
                                    try:
                                        data_sums[dist_str][v]['sum'] = data_sums[dist_str][v]['sum'] + int(line[locations[v]])
                                    except:
                                        continue

        return data_sum

class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('name','sensor_type')
    def restore_object(self, attrs, instance=None):
        try:
            return Sensor.objects.get(name__iexact=attrs['name'].strip(),sensor_type__iexact=attrs['sensor_type'].strip())
        except:
            return Sensor(name=attrs['name'].strip(),sensor_type=attrs['sensor_type'].strip())
class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = ('mapelement','time','accuracy')
    def restore_object(self, attrs, instance=None):
        try:
            return Observation.objects.get(mapelement_id=attrs['mapelement_id'],time=attrs['time'],accuracy=attrs['accuracy'])
        except:
            return Observation(mapelement_id=attrs['mapelement_id'],time=attrs['time'],accuracy=attrs['accuracy'])
class SensedDataSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='observation__sensor__name')
    sensor_type = serializers.CharField()
    mapelement = serializers.IntegerField()
    time = serializers.DateTimeField()
    accuracy = serializers.FloatField(required=False)
    value_name = serializers.CharField(source='name')
    value = serializers.FloatField(source='value')

    class Meta:
        model = ObservationValue
        fields = ('sensor_name','sensor_type','mapelement','time','accuracy','value_name','value')

    def restore_object(self, attrs, instance=None):
        #check that we have enough info
        #if not set('sensor_name','sensor_type','mapelement','time','value_name','value').issubset(set(attrs.keys())):
        #    raise exceptions.ParseError()
        #find the mappoint
        try:
            mp = MapElement.objects.get(id=attrs['mapelement'])
        except:
            raise exceptions.ParseError()
        #find or create the sensor
        sensor = Sensor.objects.filter(name__iexact=attrs['observation__sensor__name'].strip(),sensor_type__iexact=attrs['sensor_type'].strip())
        if len(sensor)==0:
            sensor = Sensor(name=attrs['observation__sensor__name'].strip(),sensor_type=attrs['sensor_type'].strip())
            sensor.save()
        else:
            sensor = sensor[0]
        #find or create the observation
        observation = Observation.objects.filter(mapelement_id=mp.id,sensor_id=sensor.id,time__exact=attrs['time'],accuracy__exact=attrs['accuracy'])
        if len(observation)==0:
            observation = Observation(mapelement=mp,sensor=sensor,time=attrs['time'],accuracy=attrs['accuracy'])
            observation.save()
        else:
            observation = observation[0]
        #create the value
        return ObservationValue(observation=observation,name=attrs['name'].strip(),value=attrs['value'])
