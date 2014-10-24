#from django.db.models import Count
from django.contrib.gis.db.models import Count
from django.shortcuts import render
#from django.contrib.auth.models import User, Group
from rest_framework import views, viewsets, permissions, response, pagination
from django.contrib.gis.geos import Polygon, Point
from gis_csdt.models import Dataset, MapElement, MapPoint, Tag, MapPolygon, TagIndiv, DataField, DataElement
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, MapPolygonSerializer, CountPointsSerializer
from gis_csdt.filter_tools import filter_request
from django.core.paginator import Paginator
from django.contrib.gis.measure import Distance, Area


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
        return filter_request(self.request.QUERY_PARAMS, 'mappoint')

class MapPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MapPolygonSerializer
    model = MapPolygon

    def get_queryset(self):
        return filter_request(self.request.QUERY_PARAMS, 'mappolygon')

class CountPointsInPolygonView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CountPointsSerializer
    model = MapPolygon
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self, format=None):
        use_csv = format and format == 'csv'

        #split params by which it applies to
        mappolygon_params = {}
        for (param, result) in self.request.QUERY_PARAMS.items():
            if param in ['max_lat','min_lat','max_lon','min_lon']:
                mappolygon_params[param] = result
            elif param == 'poly_dataset':
                mappolygon_params['dataset'] = result
            '''elif param in ['dataset','tag','tags','match']:
                mappoint_params[param] = result'''
        #now get the querysets
        polygons = filter_request(mappolygon_params,'mappolygon')
        if 'state' in self.request.QUERY_PARAMS:
            polygons = polygons.filter(remote_id__startswith=self.request.QUERY_PARAMS['state'])
        return polygons

        '''points = filter_request(mappoint_params,'mappoint')
                                if len(dataset_ids) == 0:
                                    dataset_ids = [d.id for d in Dataset.objects.all()]
                        
                        
                                datafields = DataField.objects.all()
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
                                            element = DataElement.objects.filter(datafield = df).filter(mapelement=poly)
                                            if element:
                                                data = element[0].int_data
                                        elif df.field_type == DataField.FLOAT:
                                            element = DataElement.objects.filter(datafield = df).filter(mapelement=poly)
                                            if element:
                                                data = element[0].float_data
                                        else:
                                            element = DataElement.objects.filter(datafield = df).filter(mapelement=poly)
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
                                return response.Response(count)'''


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
                            de = DataElement.objects.filter(datafield_id__exact=field.id).filter(mapelement_id__exact=poly.id)
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





from gis_csdt.serializers import TestSerializer
class TestView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestSerializer
    model = MapPoint

    def get_queryset(self):\
        return filter_request(self.request.QUERY_PARAMS, 'mappoint')