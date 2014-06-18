from django.shortcuts import render
from gis.models import Dataset, MapPoint
#from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from gis.serializers import DatasetSerializer, MapPointSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class MapPointViewSet(viewsets.ModelViewSet):
    serializer_class = MapPointSerializer

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
    				r = float(result)
    				#for tolerance
	    			minr = r - 0.0005
	    			maxr = r + 0.0005 
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
	    	elif p in ['zipcode','zip','zip_code']:
	    		queryset = queryset.filter(zipcode__iexact = result)
        return queryset