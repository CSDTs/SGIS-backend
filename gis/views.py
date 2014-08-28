from django.db.models import Count
from django.contrib.gis.db.models import Count
from django.shortcuts import render
#from django.contrib.auth.models import User, Group
from rest_framework import viewsets, permissions
from django.contrib.gis.geos import Polygon

from gis.models import Dataset, MapPoint, Tag, MapPolygon, TagIndiv
from gis.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, NewTagSerializer, TagSerializer, NewTagSerializer, MapPolygonSerializer


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
        tags = [result for (param, result) in self.request.QUERY_PARAMS.items() if param in ['tag','tags']]
        queryset = MapPoint.objects.none()
        if len(tags) > 0:
            for t in tags:
                t = t.split(',')
                if type(t) is not list:
                    t = [t]
                print t
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag__tag=tag)
            queryset = queryset.filter(tagindiv__tag__approved=True)
        else:
            queryset = MapPoint.objects
        #print queryset.query
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
	    		if p == 'min_lat' or p == 'lat':
	    			queryset = queryset.filter(lat__gte = minr)
	    			continue
	    		if p == 'max_lon' or p == 'lon':
	    			queryset = queryset.filter(lon__lte = maxr)
	    		if p == 'min_lon' or p == 'lon':
	    			queryset = queryset.filter(lon__gte = minr)
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
            

        return queryset.all()

class MapPolygonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MapPolygonSerializer
    model = MapPolygon

    def get_queryset(self):
               tags = [result for (param, result) in self.request.QUERY_PARAMS.items() if param in ['tag','tags']]
        queryset = MapPoint.objects.none()
        if len(tags) > 0:
            for t in tags:
                t = t.split(',')
                if type(t) is not list:
                    t = [t]
                print t
                for tag in t:
                    try:
                        num = int(tag)
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag=num)
                    except:
                        queryset = queryset | MapPoint.objects.filter(tagindiv__tag__tag=tag)
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
        return queryset.all()

