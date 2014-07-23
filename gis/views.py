from django.db.models import Count
from django.shortcuts import render
#from django.contrib.auth.models import User, Group
from rest_framework import viewsets

from gis.models import Dataset, MapPoint, Tag, MapPolygon
from gis.serializers import TagCountSerializer, DatasetSerializer, MapPointSerializer, TagSerializer, MapPolygonSerializer
'''from tutorial
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def tag_list(request):
    """
    List all snippets, or create a new snippet.
    """
    if request.method == 'GET':
        tags = Tag.objects.all()
        serializer = SnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SnippetSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.filter(approved=True)
    serializer_class = TagSerializer

class TagCountViewSet(viewsets.ModelViewSet):
    serializer_class = TagCountSerializer
    model = Tag

    def get_queryset(self):
    	queryset = Tag.objects.filter(approved = True).values('tag').annotate(num_tags = Count('id')).order_by()
    	return Tag.objects.all()

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class MapPointViewSet(viewsets.ModelViewSet):
    serializer_class = MapPointSerializer
    model = MapPoint

    def get_queryset(self):
    	queryset = MapPoint.objects.all()
    	for param, result in self.request.QUERY_PARAMS.items():
    		p = param.lower()
    		if p == 'dataset':
    			try:
    				r = int(result)
    				queryset = queryset.filter(dataset__id__exact = r)
    			except:
    				queryset = queryset.filter(dataset__name__icontains = result)
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
        return queryset

class MapPolygonViewSet(viewsets.ModelViewSet):
    serializer_class = MapPolygonSerializer
    model = MapPolygon

    def get_queryset(self):
        queryset = MapPolygon.objects.all()
        for param, result in self.request.QUERY_PARAMS.items():
            p = param.lower()
            if p == 'dataset':
                try:
                    r = int(result)
                    queryset = queryset.filter(dataset__id__exact = r)
                except:
                    queryset = queryset.filter(dataset__name__icontains = result)
            elif p in ['max_lat','min_lat','lat','max_lon','min_lon','lon']:
                try:
                    r = Decimal(result)
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
            '''elif p == 'street':
                queryset = queryset.filter(street__iexact = result)
            elif p == 'city':
                queryset = queryset.filter(street__iexact = result)
            elif p == 'state':
                queryset = queryset.filter(state__iexact = result)
            elif p == 'county':
                queryset = queryset.filter(county__iexact = result)
            elif p in ['zipcode','zip','zip_code']:
                queryset = queryset.filter(zipcode__iexact = result)'''
        return queryset
