from rest_framework import views, viewsets, permissions, response, pagination
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import CSVRenderer
from django.contrib.gis.db.models import Count
from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import Distance, Area
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render
from gis_csdt.filter_tools import filter_request
from gis_csdt.models import Dataset, MapElement, MapPoint, Tag, MapPolygon, TagIndiv, DataField, DataElement
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, MapPolygonSerializer, CountPointsSerializer, AnalyzeAreaSerializer
#import csv
from gis_csdt.serializers import TestSerializer
class TestView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestSerializer
    model = MapPoint

    def get_queryset(self):\
        return filter_request(self.request.QUERY_PARAMS, 'mappoint')

class PaginatedCSVRenderer (CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super(PaginatedCSVRenderer, self).render(data, media_type, renderer_context)

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
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer]
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
        #now get the querysets
        polygons = filter_request(mappolygon_params,'mappolygon')
        if 'state' in self.request.QUERY_PARAMS:
            polygons = polygons.filter(remote_id__startswith=self.request.QUERY_PARAMS['state'])
        return polygons

        if False:
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
                row = [poly.remote_id, poly.field1, poly.field2]

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
                        row.append(temp.filter(point__intersects = poly.mpoly).count())
                    print points.filter(point__intersects = poly.mpoly).query
                    if mult_tags:
                        row.append(points.filter(point__intersects = poly.mpoly).count())
                if mult_tags:
                    row.append(all_tag_filter.filter(point__intersects = poly.mpoly).count())

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
                    if data:
                        row.append(data)
                    else:
                        row.append('')
                writer.writerow(row)
            return csv_response

class AnalyzeAreaAroundPointView(viewsets.ReadOnlyModelViewSet):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer]
    serializer_class = AnalyzeAreaSerializer
    model = MapPoint
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self, format=None):
        #split params by which it applies to
        mappoint_params = {}
        for (param, result) in self.request.QUERY_PARAMS.items():
            if param in ['max_lat','min_lat','max_lon','min_lon','dataset','tags','tag']:
                mappoint_params[param] = result
        #now get the queryset
        points = filter_request(mappoint_params,'mappoint')
        return points