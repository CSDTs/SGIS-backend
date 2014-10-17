#from django.db.models import Count
from django.contrib.gis.db.models import Count
from django.shortcuts import render
#from django.contrib.auth.models import User, Group
from rest_framework import views, viewsets, permissions, response, pagination
from django.contrib.gis.geos import Polygon, Point
from gis_csdt.models import Dataset, MapPoint, Tag, MapPolygon, TagIndiv, DataField, DataElement
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, MapPolygonSerializer #, CountPointsInPolygonSerializer
from django.core.paginator import Paginator
from django.contrib.gis.measure import Distance, Area


'''class TagViewSet(viewsets.ModelViewSet):
    queryset = TagIndiv.objects.filter(tag__approved=True).distinct('tag')
    serializer_class = TagSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = (permissions.AllowAny,)#(permissions.IsAuthenticatedOrReadOnly)'''

class NewTagViewSet(viewsets.ModelViewSet):
    queryset = TagIndiv.objects.filter(tag__approved=True).distinct('tag')
    serializer_class = NewTagSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = (permissions.AllowAny,)#(permissions.IsAuthenticatedOrReadOnly)

class TagCountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagCountSerializer
    model = Tag

    def get_queryset(self):
        return Tag.objects.filter(approved = True).values('dataset','tag').annotate(num_tags = Count('id'))

class DatasetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class MapPointViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MapPointSerializer
    model = MapPoint

    def get_queryset(self):
        t = False
        radius = False
        center = False
        matchall = False
        queryset = MapPoint.objects.none()

        for (param, result) in self.request.QUERY_PARAMS.items():
            if param in ['tag','tags']:
                t = result
            elif param == 'match' and result == 'all':
                matchall = True
        if t:
            t = t.split(',')
            if type(t) is not list:
                t = [t]
            if matchall:
                queryset = MapPoint.objects
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset.filter(tagindiv__tag__tag=tag)
            else:
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag__tag=tag)
            queryset = queryset.filter(tagindiv__tag__approved=True)
        else:
            queryset = MapPoint.objects
        bb = {}
        for param, result in self.request.QUERY_PARAMS.items():
            p = param.lower()
            if p == 'dataset':
                try:
                    r = int(result)
                    queryset = queryset.filter(dataset__id__exact = r)
                except:
                    queryset = queryset.filter(dataset__name__icontains = result.strip())
            elif p in ['max_lat','min_lat','max_lon','min_lon']:
                try:
                    r = float(result)
                    #for tolerance
                    minr = r - 0.0000005
                    maxr = r + 0.0000005 
                except:
                    continue
                if p == 'max_lat' or p == 'lat':
                    queryset = queryset.filter(lat__lte = maxr)
                    bb['max_lat'] = maxr
                if p == 'min_lat' or p == 'lat':
                    queryset = queryset.filter(lat__gte = minr)
                    bb['min_lat'] = minr
                    continue
                if p == 'max_lon' or p == 'lon':
                    queryset = queryset.filter(lon__lte = maxr)
                    bb['max_lon'] = maxr
                if p == 'min_lon' or p == 'lon':
                    queryset = queryset.filter(lon__gte = minr)
                    bb['min_lon'] = minr
            elif p == 'street':
                queryset = queryset.filter(street__iexact = result)
            elif p == 'city':
                print result
                queryset = queryset.filter(city__iexact = result)
            elif p == 'state':
                queryset = queryset.filter(state__iexact = result)
            elif p == 'county':
                queryset = queryset.filter(county__iexact = result)
            elif p in ['zipcode','zip','zip_code']:
                queryset = queryset.filter(zipcode__iexact = result)
            elif param == 'radius':
                try:
                    radius = int(result)
                except:
                    return HttpResponseBadRequest('Invalid radius. Only integers accepted.' )
            elif param == 'center':
                temp = result.split(',')
                try:
                    if len(temp) != 2:
                        raise 
                    temp[0] = float(temp[0])
                    temp[1] = float(temp[1])
                    center = Point(temp[0],temp[1])
                except:
                    return HttpResponseBadRequest('Invalid center. Format is: center=lon,lat' )


        if 'max_lat' in bb and 'min_lat' in bb and 'max_lon' in bb and 'min_lon' in bb:
            geom = Polygon.from_bbox((bb['min_lon'],bb['min_lat'],bb['max_lon'],bb['max_lat']))
            queryset = queryset.filter(point__within=geom)

        if radius and center:
            queryset = queryset.filter(point__distance_lte = (center,Distance(mi=radius)))
        return queryset.distinct().all()

class MapPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MapPolygonSerializer
    model = MapPolygon

    def get_queryset(self):
        t = False
        matchall = False
        queryset = MapPolygon.objects.none()

        for (param, result) in self.request.QUERY_PARAMS.items():
            if param in ['tag','tags']:
                t = result
            elif param == 'match' and result == 'all':
                matchall = True
        if t:
            t = t.split(',')
            if type(t) is not list:
                t = [t]
            if matchall:
                queryset = MapPolygon.objects
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset.filter(tagindiv__tag__tag=tag)
            else:
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset | MapPolygon.objects.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset | MapPolygon.objects.filter(tagindiv__tag__tag=tag)
            queryset = queryset.filter(tagindiv__tag__approved=True)
        else:
            queryset = MapPolygon.objects
        
        bb = {}
        for param, result in self.request.QUERY_PARAMS.items():
            p = param.lower()
            if p == 'dataset':
                try:
                    r = int(result)
                    queryset = queryset.filter(dataset__id__exact = r)
                except:
                    queryset = queryset.filter(dataset__name__icontains = result)
            elif p in ['max_lat','min_lat','max_lon','min_lon']:
                try:
                    r = float(result)
                    bb[p] = r
                except:
                    continue
        #define bounding box
        if 'max_lat' in bb and 'min_lat' in bb and 'max_lon' in bb and 'min_lon' in bb:
            geom = Polygon.from_bbox((bb['min_lon'],bb['min_lat'],bb['max_lon'],bb['max_lat']))
            #print geom
            queryset = queryset.filter(mpoly__bboverlaps=geom)
            #print queryset.query
        return queryset.distinct().all()

class CountPointsInPolygonView(views.APIView):
    #serializer_class = MapPolygonSerializer
    #model = MapPolygon
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        #serializer = CountPointsInPolygonSerializer
        #get polygons
        all_tags = ''
        matchall = False
        polygons = MapPolygon.objects
        dataset_ids = []
        state = ''

        bb = {}
        use_csv = False
        for param, result in request.QUERY_PARAMS.items():
            p = param.lower()
            if p == 'dataset':
                for res in result.split(','):
                    try:
                        r = int(result)
                        dataset_ids.append(r)
                    except:
                        for d in Dataset.objects.filter(name__icontains = result):
                            dataset_ids.append(d.id)
                polygons = polygons.filter(dataset__id__in = dataset_ids)

            elif p in ['max_lat','min_lat','max_lon','min_lon']:
                try:
                    r = float(result)
                    bb[p] = r
                except:
                    continue
            elif p == 'file' and result.lower() == 'csv':
                use_csv = True
            elif p =='state':
                state = result
            print p, result, use_csv
        #define bounding box
        if 'max_lat' in bb and 'min_lat' in bb and 'max_lon' in bb and 'min_lon' in bb:
            geom = Polygon.from_bbox((bb['min_lon'],bb['min_lat'],bb['max_lon'],bb['max_lat']))
            #print geom
            polygons = polygons.filter(mpoly__bboverlaps=geom)
            #print polygons.query
        
        if len(dataset_ids) == 0:
            dataset_ids = [d.id for d in Dataset.objects.all()]

        points = MapPoint.objects.none()

        for (param, result) in request.QUERY_PARAMS.items():
            if param in ['tag','tags']:
                all_tags = all_tags + result + ','
            elif param == 'match' and result == 'all':
                matchall = True
        if all_tags == '':
            for t in Tag.objects.filter(dataset__in = dataset_ids):
                all_tags = all_tags + t.tag + ','
            tags = all_tags.strip(' ,').split(',')
            points = MapPoint.objects
        else:
            tags = all_tags.strip(' ,').split(',')
            if type(tags) is not list:
                tags = [tags]
            if matchall:
                points = MapPoint.objects
                for tag in tags:
                    try:
                        num = int(tag)
                        points = points.filter(tagindiv__tag=num)
                    except:
                        points = points.filter(tagindiv__tag__tag=tag)
            else:
                for tag in tags:
                    try:
                        num = int(tag)
                        points = points | MapPoint.objects.filter(tagindiv__tag=num)
                    except:
                        points = points | MapPoint.objects.filter(tagindiv__tag__tag=tag)
            points = points.filter(tagindiv__tag__approved=True)

        
        datafields = DataField.objects.all()
        points = points.distinct()
        if state != '':
            polygons = polygons.filter(remote_id__startswith=state)
        polygons = polygons.distinct()
        count = []
        mult_tags = len(tags) > 1

        if use_csv:
            csv_response = HttpResponse(content_type='text/csv')
            filename = 'census_tract_stats'
            for t in tags:
                filename = filename + '_' + t
            csv_response['Content-Disposition'] = 'attachment; filename="' + filename + '.csv"'
            writer = csv.writer(csv_response)

            firstrow = ['polygon_id', polygons[0].dataset.field1_en, polygons[0].dataset.field2_en]
            for tag in tags:
                try:
                    num = int(tag)
                    t = Tag.objects.get(pk = num)
                    t = t.tag
                except:
                    t = tag
                firstrow.append(t + " count")
            if mult_tags:
                if not matchall:
                    firstrow.append(all_tags + " count (match any)")
                firstrow.append(all_tags + " count (match all)")
            for df in datafields:
                firstrow.append(df.field_en)
            writer.writerow(firstrow)

        for poly in polygons:
            if use_csv:
                row = [poly.remote_id, poly.field1, poly.field2]
            else:
                d = {"polygon_id": poly.remote_id, poly.dataset.field1_en : poly.field1, poly.dataset.field2_en : poly.field2}

            #counts in polygons
            all_tag_filter = points
            if not matchall:
                for tag in tags:
                    try:
                        num = int(tag)
                        temp = points.filter(tagindiv__tag=num)
                        all_tag_filter = points.filter(tagindiv__tag=num)
                    except:
                        temp = points.filter(tagindiv__tag__tag=tag)
                        all_tag_filter = points.filter(tagindiv__tag__tag=tag)
                    if use_csv:
                        row.append(temp.filter(point__intersects = poly.mpoly).count())
                    else:
                        d[tag + " count"] = temp.filter(point__intersects = poly.mpoly).count()
                print points.filter(point__intersects = poly.mpoly).query
                if mult_tags:
                    if use_csv:
                        row.append(points.filter(point__intersects = poly.mpoly).count())
                    else:
                        d[all_tags + " count (match any)"] = points.filter(point__intersects = poly.mpoly).count()
            if mult_tags:
                if use_csv:
                    row.append(all_tag_filter.filter(point__intersects = poly.mpoly).count())
                else:
                    d[all_tags + " count (match all)"] = all_tag_filter.filter(point__intersects = poly.mpoly).count()

            #get other data
            for df in datafields:
                data = None
                if df.field_type == DataField.INTEGER:
                    element = DataElement.objects.filter(datafield = df).filter(mappolygon=poly)
                    if element:
                        data = element[0].int_data
                elif df.field_type == DataField.FLOAT:
                    element = DataElement.objects.filter(datafield = df).filter(mappolygon=poly)
                    if element:
                        data = element[0].float_data
                else:
                    element = DataElement.objects.filter(datafield = df).filter(mappolygon=poly)
                    if element:
                        data = element[0].char_data
                if use_csv:
                    if data:
                        row.append(data)
                    else:
                        row.append('')
                else:
                    d[df.field_en] = data
            if use_csv:
                writer.writerow(row)
            else:
                count.append(d)
        if use_csv:
            return csv_response
        #paginator = Paginator(count,5)
        #serializer = pagination.PaginationSerializer(instance = paginator)
        return response.Response(count)


import csv
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseNotAllowed

def AnalyzeAreaAroundPointView(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    dataset_list = request.GET.getlist('dataset')
    if len(dataset_list) != 1:
        print dataset_list
        print request.QUERY_PARAMS.items()
        return HttpResponseBadRequest('Exactly one dataset must be specified')


    id_list = request.GET.getlist('id')
    distances = request.GET.getlist('distance')
    unit = request.GET.getlist('unit')
    years = request.GET.getlist('year')
    level = request.GET.getlist('level')

    
    if len(unit) > 1:
        return HttpResponseBadRequest('No more than one unit may be specified')
    elif len(unit) == 0:
        unit = 'mi'
    elif unit[0] in ['m','km','mi']:
        unit = unit[0]
    else:
        return HttpResponseBadRequest('Accepted units: m, km, mi')
    if len(level) == 1 and level[0] == 'point':
        by_point = True
    elif len(level) == 0:
        by_point = False
    else:
        return HttpResponseBadRequest('Please specify level as "point" or not at all' )


    if len(distances) == 0:
        distances = [1,3,5]
        unit = 'km'
    else:
        distances.sort()

    ids = []
    for i in id_list:
        try:
            n = int(i)
            ids.append(n)
        except:
            return HttpResponseBadRequest('Please use MapPoint ids (integers) only')
    try:
        dataset_id = int(dataset_ids[0])
    except:
        return HttpResponseBadRequest('Dataset must be given as an id (integer)')

    all_points = MapPoint.filter(dataset__id__exact = dataset_id)

    if len(id_list) > 0:
        points = all_points.in_bulk(ids).all()
    else:
        points = all_points.all()

    firstrow = ['Year','Region']
    firstrow.append('Field Name')
    #distances must have at least one element by this point
    last = distances[0]
    firstrow.append('Within '+str(last)+' '+unit)
    for d in distances[1:]:
        firstrow.append('Between '+str(last)+' '+unit+' and '+str(d)+' '+unit)
        last = d
    firstrow.append('Beyond '+str(last)+' '+unit)


    filename = 'distance_report'
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+filename+'.csv"'
    writer = csv.writer(response)
    writer.writerow(firstrow)

    max_dist_between = distances[-1] * 2
    kwargs = {unit: max_dist_between}
    max_dist_between =  Distance(**kwargs)#exec('Distance('unit+'=max_dist_between)')
    kwargs = {unit: distance}
    distances = Distance(**kwargs) #[exec('Distance('+unit+'=distance)') for distance in distances]

    
    for year in years:
        totals = []
        poly_dataset = Dataset.objects.filter(name__icontains='census').filter(name__icontains=year.strip())
        if len(poly_dataset) < 1:
            return HttpResponseBadRequest('Census year data does not exist for the year '+year)
        poly_dataset = poly_dataset[0]
        datafields = DataField.objects.filter(dataset_id__exact=poly_dataset.id).exclude(field_type__exact=DataField.STRING)
        data_sums_total = {}
        data_sums = {}
        for point in points:
            if by_point:
                point_name = point.name
            nearby = all_points.exclude(id__exact=point.id).filter(point__distance_lte=(point.point, max_dist_between))
            for n in nearby:
                if by_point:
                    point_name = point_name + ',' + n.name
                points = points.exclude(id__exact=n.id)

            last = Distance(ft=0)
            for dist in distances:
                polys = MapPolygon.objects.filter(dataset_id__exact=poly_dataset.id).filter(poly__dwithin=(point.point,dist)).exclude(poly__dwithin=(point.point,last))
                for n in nearby:
                    polys = polys | MapPolygon.objects.filter(dataset_id__exact=poly_dataset.id).filter(poly__dwithin=(n.point,dist)).exclude(poly__dwithin=(n.point,last))
                
                for poly in polys:
                    for field in datafields:
                        if field not in data_sums:
                            data_sums[field] = {}
                        if dist not in data_sums[field]:
                            data_sums[field][dist] = 0
                        try:
                            de = DataElement.objects.filter(datafield_id__exact=field.id).filter(mappolygon_id__exact=poly.id)
                        except DataElement.DoesNotExist:
                            continue
                        if field.type == DataField.INTEGER:
                            data_sums[field][dist] = data_sums[field][dist] + de.int_data
                        elif field.type == DataField.FLOAT:
                            data_sums[field][dist] = data_sums[field][dist] + de.float_data

                last = dist
            if by_point:
                for field in data_sums:
                    row = [year,point_name,field]
                    for dist in distances:
                        if field not in data_sums_total:
                            data_sums_total[field] = {}
                        if dist not in data_sums_total[field]:
                            data_sums_total[field][dist] = 0
                        row.append(data_sums[field][dist])
                        data_sums_total[field][dist] = data_sums_total[field][dist] + data_sums[field][dist]
                    writer.writerow(row)
                data_sums = {}
        if not by_point:
            data_sums_total = data_sums
        for field in data_sums:
            row = [year,point_name,field]
            for dist in distances:
                if field not in data_sums_total:
                    data_sums_total[field] = {}
                if dist not in data_sums_total[field]:
                    data_sums_total[field][dist] = 0
                row.append(data_sums[field][dist])
                data_sums_total[field][dist] = data_sums_total[field][dist] + data_sums[field][dist]
            writer.writerow(row)

    return response
##doesn't belong in views
def findCensusTracts():
    pass





from gis_csdt.serializers import TestSerializer
class TestView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestSerializer
    model = MapPoint

    def get_queryset(self):
        t = False
        radius = False
        center = False
        matchall = False
        queryset = MapPoint.objects.none()

        for (param, result) in self.request.QUERY_PARAMS.items():
            if param in ['tag','tags']:
                t = result
            elif param == 'match' and result == 'all':
                matchall = True
        if t:
            t = t.split(',')
            if type(t) is not list:
                t = [t]
            if matchall:
                queryset = MapPoint.objects
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset.filter(tagindiv__tag__tag=tag)
            else:
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag__tag=tag)
            queryset = queryset.filter(tagindiv__tag__approved=True)
        else:
            queryset = MapPoint.objects
        bb = {}
        for param, result in self.request.QUERY_PARAMS.items():
            p = param.lower()
            if p == 'dataset':
                try:
                    r = int(result)
                    queryset = queryset.filter(dataset__id__exact = r)
                except:
                    queryset = queryset.filter(dataset__name__icontains = result.strip())
            elif p in ['max_lat','min_lat','max_lon','min_lon']:
                try:
                    r = float(result)
                    #for tolerance
                    minr = r - 0.0000005
                    maxr = r + 0.0000005 
                except:
                    continue
                if p == 'max_lat' or p == 'lat':
                    queryset = queryset.filter(lat__lte = maxr)
                    bb['max_lat'] = maxr
                if p == 'min_lat' or p == 'lat':
                    queryset = queryset.filter(lat__gte = minr)
                    bb['min_lat'] = minr
                    continue
                if p == 'max_lon' or p == 'lon':
                    queryset = queryset.filter(lon__lte = maxr)
                    bb['max_lon'] = maxr
                if p == 'min_lon' or p == 'lon':
                    queryset = queryset.filter(lon__gte = minr)
                    bb['min_lon'] = minr
            elif p == 'street':
                queryset = queryset.filter(street__iexact = result)
            elif p == 'city':
                print result
                queryset = queryset.filter(city__iexact = result)
            elif p == 'state':
                queryset = queryset.filter(state__iexact = result)
            elif p == 'county':
                queryset = queryset.filter(county__iexact = result)
            elif p in ['zipcode','zip','zip_code']:
                queryset = queryset.filter(zipcode__iexact = result)
            elif param == 'radius':
                try:
                    radius = int(result)
                except:
                    return HttpResponseBadRequest('Invalid radius. Only integers accepted.' )
            elif param == 'center':
                temp = result.split(',')
                try:
                    if len(temp) != 2:
                        raise 
                    temp[0] = float(temp[0])
                    temp[1] = float(temp[1])
                    center = Point(temp[0],temp[1])
                except:
                    return HttpResponseBadRequest('Invalid center. Format is: center=lon,lat' )


        if 'max_lat' in bb and 'min_lat' in bb and 'max_lon' in bb and 'min_lon' in bb:
            geom = Polygon.from_bbox((bb['min_lon'],bb['min_lat'],bb['max_lon'],bb['max_lat']))
            queryset = queryset.filter(point__within=geom)

        if radius and center:
            queryset = queryset.filter(point__distance_lte = (center,Distance(mi=radius)))
        return queryset.distinct().all()