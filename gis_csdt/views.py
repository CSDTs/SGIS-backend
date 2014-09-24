#from django.db.models import Count
from django.contrib.gis.db.models import Count
from django.shortcuts import render
#from django.contrib.auth.models import User, Group
from rest_framework import views, viewsets, permissions, response
from django.contrib.gis.geos import Polygon, Point

from gis_csdt.models import Dataset, MapPoint, Tag, MapPolygon, TagIndiv, DataField, DataElement
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, TagSerializer, NewTagSerializer, MapPolygonSerializer #, CountPointsInPolygonSerializer
from django.core.paginator import Paginator


class TagViewSet(viewsets.ModelViewSet):
    queryset = TagIndiv.objects.filter(tag__approved=True).distinct('tag')
    serializer_class = TagSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = (permissions.AllowAny,)#(permissions.IsAuthenticatedOrReadOnly)

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
            elif p in ['max_lat','min_lat','lat','max_lon','min_lon','lon']:
                try:
                    r = Decimal(result)
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
                queryset = queryset.filter(street__iexact = result)
            elif p == 'state':
                queryset = queryset.filter(state__iexact = result)
            elif p == 'county':
                queryset = queryset.filter(county__iexact = result)
            elif p in ['zipcode','zip','zip_code']:
                queryset = queryset.filter(zipcode__iexact = result)

        if 'max_lat' in bb and 'min_lat' in bb and 'max_lon' in bb and 'min_lon' in bb:
            mid_lat = (bb['max_lat'] + bb['min_lat']) / 2
            mid_lon = (bb['max_lon'] + bb['min_lon']) / 2
            geom = Point(mid_lat, mid_lon)
            #print geom
            queryset = queryset.filter(mpoly__bboverlaps=geom)
            #print queryset.query
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
        
        bb = {}
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
        polygons = polygons.distinct()
        count = []
        mult_tags = len(tags) > 1

        for poly in polygons:
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
                    d[tag + " count"] = temp.filter(point__contained = poly.mpoly).count()
                if mult_tags:
                    d[all_tags + " count (match any)"] = points.filter(point__contained = poly.mpoly).count()
            if mult_tags:
                d[all_tags + " count (match all)"] = all_tag_filter.filter(point__contained = poly.mpoly).count()

            #get other data
            for df in datafields:
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

                d[df.field_en] = data
            count.append(d)
        paginator = Paginator(count,5)
        return response.Response(count)


import csv
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseNotAllowed

def AnalyzeAreaAroundPointView(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    dataset_list = request.GET.getlist('dataset')
    if len(dataset_list) != 1:
        return HttpResponseBadRequest(reason_phrase = 'Exactly one dataset must be specified')
    id_list = request.GET.getlist('id')
    distances = request.GET.getlist('distance')
    unit = request.GET.getlist('unit')
    years = request.GET.getlist('year')
    if len(unit) > 1:
        return HttpResponseBadRequest(reason_phrase = 'No more than one unit may be specified')
    elif len(unit) == 0:
        unit = 'mi'

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
            pass
    points = MapPoint.filter(dataset__id__exact = d)
    if len(id_list) > 0:
        points = points.in_bulk(ids).all()
    else:
        points.points.all()

    counties = {}
    for point in points:
        others = MapPoint.filter(dataset__id__exact = d).exclude(id__exact=point.id)
        max_dist_between = distances[-1] * 2
        #others  = others. 
        #point.point


    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response
##doesn't belong in views
def findCensusTracts():
    pass