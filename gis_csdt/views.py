# -*- coding: utf8 -*-
import sys
import binascii
from rest_framework import views, viewsets, permissions, response, pagination
from rest_framework.settings import api_settings
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.exceptions import ParseError #, APIException
from django.contrib.gis.db.models import Count
from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import Distance, Area
from django.views.generic.edit import CreateView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpRequest,  HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render
from gis_csdt.filter_tools import filter_request, neighboring_points
from gis_csdt.models import Dataset, MapElement, MapPoint, Tag, MapPolygon, TagIndiv, DataField, DataElement, Observation, ObservationValue, Sensor, DataPoint, PhoneNumber
from gis_csdt.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, MapPolygonSerializer, CountPointsSerializer, AnalyzeAreaSerializer, AnalyzeAreaNoValuesSerializer, SensedDataSerializer, DataPointSerializer, SensorSerializer
#import csv
from gis_csdt.serializers import TestSerializer
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse

###constants for pagination
PAGINATE_BY_CONST = 100
PAGINATE_BY_PARAM_CONST = 'page_size'
MAX_PAGINATE_BY_CONST = 500
GSM_CHAR_SET = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
               "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà").decode("utf8")
###classes for pagination
class PaginatedModelViewSet(viewsets.ModelViewSet):
    paginate_by = PAGINATE_BY_CONST
    paginate_by_param = PAGINATE_BY_PARAM_CONST
    max_paginate_by = MAX_PAGINATE_BY_CONST
class PaginatedReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    paginate_by = PAGINATE_BY_CONST
    paginate_by_param = PAGINATE_BY_PARAM_CONST
    max_paginate_by = MAX_PAGINATE_BY_CONST
########


class SensedDataViewSet(PaginatedModelViewSet):
    paginate_by = PAGINATE_BY_CONST
    paginate_by_param = PAGINATE_BY_PARAM_CONST
    max_paginate_by = MAX_PAGINATE_BY_CONST
    queryset = ObservationValue.objects.filter()
    serializer_class = SensedDataSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = [permissions.IsAuthenticated]#(permissions.IsAuthenticatedOrReadOnly)

class NewSensorView(PaginatedModelViewSet):
    paginate_by = PAGINATE_BY_CONST
    paginate_by_param = PAGINATE_BY_PARAM_CONST
    max_paginate_by = MAX_PAGINATE_BY_CONST
    queryset = Sensor.objects.filter()
    serializer_class = SensorSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = [permissions.IsAuthenticated]#(permissions.IsAuthenticatedOrReadOnly)

class SubmitDataPointView(PaginatedModelViewSet):
    paginate_by = PAGINATE_BY_CONST
    paginate_by_param = PAGINATE_BY_PARAM_CONST
    max_paginate_by = MAX_PAGINATE_BY_CONST
    queryset = DataPoint.objects.all()
    serializer_class = DataPointSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = [permissions.IsAuthenticated]#(permissions.IsAuthenticatedOrReadOnly)


def GSM7ToInt(string):
    pow = 0
    BASE = 128  # GSM-7 code base
    val = 0
    for char in string:
        val += GSM_CHAR_SET.find(char) * (BASE ** pow)
        pow += 1
    return val

def IntToGSM7(value):
    string = ''
    BASE = 128  # GSM-7 code base
    while value >= BASE:
        string += GSM_CHAR_SET[value%BASE]
        value = int(value/BASE)
    string += GSM_CHAR_SET[value%BASE]
    return string

def DataToGSM7(values):
    string = ''
    BASE = 128  # GSM-7 code base
    MAXSIZE = BASE**2  # 2 bytes of GSM7
    string += IntToGSM7(values.pop(0))
    string += IntToGSM7(values.pop(0))
    for value in values:
        if value > MAXSIZE:
            raise
        if value < BASE:
            string+=IntToGSM7(value)+'@'
        else:
            string+=IntToGSM7(value)
    return string

@csrf_exempt
def SMSSubmitDataPointView(request):
    DATASIZE = 2  # 2 GSM-7 chars
    try:
        data = request.POST.get('Body')
        phNum = int(request.POST.get('From'))
        user = PhoneNumber.objects.get(phone_number=phNum).user
        data = [data[i:i+DATASIZE] for i in range (0, len(data), DATASIZE)]
        source = data.pop(0)
        sensor = Sensor.objects.get(pk=GSM7ToInt(source[0]))
        mapPoint = MapPoint.objects.get(pk=GSM7ToInt(source[1]))
        for dataValue in data:
            newData = DataPoint.objects.create(value=GSM7ToInt(dataValue), point=mapPoint, sensor=sensor, user=user)
            newData.save()
    except:
        raise ParseError('Bad format.')
    return HttpResponse(status=204)


class TestView(PaginatedReadOnlyModelViewSet):
    serializer_class = TestSerializer
    model = MapElement

    def get_queryset(self):
        return filter_request(self.request.query_params, 'mapelement')

class PaginatedCSVRenderer (CSVRenderer):
    results_field = 'results'

    def render(self, data, media_type=None, renderer_context=None):
        if not isinstance(data, list):
            data = data.get(self.results_field, [])
        return super(PaginatedCSVRenderer, self).render(data, media_type, renderer_context)

class NewTagViewSet(PaginatedModelViewSet):
    queryset = TagIndiv.objects.filter(tag__approved=True).distinct('tag')
    serializer_class = NewTagSerializer

    #http://www.django-rest-framework.org/api-guide/permissions
    permission_classes = [permissions.AllowAny]#(permissions.IsAuthenticatedOrReadOnly)

class TagCountViewSet(PaginatedReadOnlyModelViewSet):
    serializer_class = TagCountSerializer
    model = Tag

    def get_queryset(self):
        return Tag.objects.filter(approved = True).values('dataset','tag').annotate(num_tags = Count('id'))

class DatasetViewSet(PaginatedReadOnlyModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class MapPointViewSet(PaginatedReadOnlyModelViewSet):
    serializer_class = MapPointSerializer
    model = MapPoint

    def get_queryset(self):
        return filter_request(self.request.query_params, 'mappoint')

class MapPolygonViewSet(PaginatedReadOnlyModelViewSet):
    serializer_class = MapPolygonSerializer
    model = MapPolygon

    def get_queryset(self):
        return filter_request(self.request.query_params, 'mappolygon')

class CountPointsInPolygonView(PaginatedReadOnlyModelViewSet):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer]
    serializer_class = CountPointsSerializer
    model = MapPolygon
    permission_classes = [permissions.AllowAny]#(permissions.IsAuthenticatedOrReadOnly)

    def get_queryset(self, format=None):
        use_csv = format and format == 'csv'

        #split params by which it applies to
        mappolygon_params = {}
        for (param, result) in self.request.query_params.items():
            if param in ['max_lat','min_lat','max_lon','min_lon']:
                mappolygon_params[param] = result
            elif param == 'poly_dataset':
                mappolygon_params['dataset'] = result
        #now get the querysets
        polygons = filter_request(mappolygon_params,'mappolygon')
        if 'state' in self.request.query_params:
            polygons = polygons.filter(remote_id__startswith=self.request.query_params['state'])
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

class AnalyzeAreaAroundPointView(PaginatedReadOnlyModelViewSet):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES + [PaginatedCSVRenderer]
    serializer_class = AnalyzeAreaSerializer
    model = MapPoint
    permission_classes = [permissions.AllowAny]#(permissions.IsAuthenticatedOrReadOnly)

    def get_queryset(self, format=None):
        #split params by which it applies to
        mappoint_params = {}
        for (param, result) in self.request.query_params.items():
            if param in ['max_lat','min_lat','max_lon','min_lon','dataset','tags','tag']:
                mappoint_params[param] = result
        #if none of this is specified, this is just too much
        if len(mappoint_params) == 0:
            raise ParseError('Too many results. Please restrict the mappoints.')
        #now get the queryset
        points = filter_request(mappoint_params,'mappoint')
        distances = self.request.GET.getlist('distance')
        unit = self.request.GET.getlist('unit')
        if len(unit) > 1:
            raise ParseError('No more than one unit may be specified.')
        elif len(unit) == 0:
            unit = 'mi'
        elif unit[0] in ['m','km','mi']:
            unit = unit[0]
        else:
            raise ParseError('Accepted units: m, km, mi')
        if len(distances) == 0:
            distances = [1,3,5]
            unit = 'km'
        else:
            distances.sort()
        kwargs = {unit:distances[-1]}
        take_out = []
        for point in points:
            if point.id in take_out:
                continue
            take_out.extend(neighboring_points(point, points, Distance(**kwargs)).exclude(id=point.id).values_list('id',flat=True))
        return points.exclude(id__in=take_out)

class AnalyzeAreaAroundPointNoValuesView(PaginatedReadOnlyModelViewSet):
    serializer_class = AnalyzeAreaNoValuesSerializer
    model = MapPoint
    permission_classes = [permissions.IsAuthenticated]#(permissions.IsAuthenticatedOrReadOnly)

    def get_queryset(self):
        #split params by which it applies to
        mappoint_params = {}
        for (param, result) in self.request.query_params.items():
            if param in ['max_lat','min_lat','max_lon','min_lon','dataset','tags','tag','state','zipcode']:
                mappoint_params[param] = result
        #if none of this is specified, this is just too much
        if len(mappoint_params) == 0:
            raise ParseError('Too many results. Please restrict the mappoints.')
        #now get the queryset
        points = filter_request(mappoint_params,'mappoint')
        distances = self.request.GET.getlist('distance')
        unit = self.request.GET.getlist('unit')
        if len(unit) > 1:
            raise ParseError('No more than one unit may be specified.')
        elif len(unit) == 0:
            unit = 'mi'
        elif unit[0] in ['m','km','mi']:
            unit = unit[0]
        else:
            raise ParseError('Accepted units: m, km, mi')
        if len(distances) == 0:
            distances = [1,3,5]
            unit = 'km'
        else:
            print distances
            distances.sort()
        kwargs = {unit:distances[-1]}
        take_out = []
        for point in points:
            if point.id in take_out:
                continue
            take_out.extend(neighboring_points(point, points, Distance(**kwargs)).exclude(id=point.id).values_list('id',flat=True))
        return points.exclude(id__in=take_out).distinct()
