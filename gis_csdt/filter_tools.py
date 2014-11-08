from django.contrib.gis.geos import Polygon, Point
from gis_csdt.models import Dataset, MapElement, MapPoint, Tag, MapPolygon, TagIndiv, DataField, DataElement
from django.contrib.gis.measure import Distance

def filter_request(parameters, model_type):

    if 'tag' in parameters:
        tags = parameters['tag']
    elif 'tags' in parameters:
        tags = parameters['tags']
    else:
        tags = False

    if 'match' in parameters:
        matchall = parameters['match'] == 'all'
    else:
        matchall = False

    
    queryset = MapElement.objects.none()
    if tags:
        tags = tags.split(',')
        if type(tags) is not list:
            tags = [tags]
        if matchall:
            queryset = MapElement.objects
            for tag in tags:
                try:
                    num = int(tag)
                    queryset = queryset.filter(tagindiv__tag=num)
                except:
                    queryset = queryset.filter(tagindiv__tag__tag=tag)
        else:
            for tag in tags:
                try:
                    num = int(tag)
                    queryset = queryset | MapElement.objects.filter(tagindiv__tag=num)
                except:
                    queryset = queryset | MapElement.objects.filter(tagindiv__tag__tag=tag)
        queryset = queryset.filter(tagindiv__tag__approved=True)
    else:
        queryset = MapElement.objects

    if 'dataset' in parameters:
        dataset_list = parameters['dataset'].strip().split(',')
        if type(dataset_list) is not list:
            dataset_list = [dataset_list]
        for dataset in dataset_list:
            try:
                r = int(dataset)
                queryset = queryset.filter(dataset__id__exact = r)
            except:
                queryset = queryset.filter(dataset__name__icontains = dataset)

    #make it just one type now
    kwargs = {model_type:None}
    queryset = queryset.exclude(**kwargs)

    if model_type == 'mappoint':
        if 'street' in parameters:
            queryset = queryset.filter(mappoint__street__iexact = parameters[model_type+'street'])
        if 'city' in parameters:
            queryset = queryset.filter(mappoint__city__iexact = parameters[model_type+'city'])
        if 'state' in parameters:
            queryset = queryset.filter(mappoint__state__iexact = parameters[model_type+'state'])
        if 'county' in parameters:
            queryset = queryset.filter(mappoint__county__iexact = parameters[model_type+'county'])
        for key in ['zipcode','zip','zip_code']:
            if key in parameters:
                queryset = queryset.filter(mappoint__zipcode__iexact = parameters[model_type+key])

    bb = {}
    for key in ['max_lat','min_lat','max_lon','min_lon']:
        if key in parameters:
            try:
                r = float(parameters[key])
            except:
                return HttpResponseBadRequest('Invalid radius. Only integers accepted.' )
                continue
            bb[key] = r

    if 'max_lat' in bb and 'min_lat' in bb and 'max_lon' in bb and 'min_lon' in bb:
        geom = Polygon.from_bbox((bb['min_lon'],bb['min_lat'],bb['max_lon'],bb['max_lat']))
        if model_type == 'mappoint':
            queryset = queryset.filter(point__within=geom)
        elif model_type == 'mappolygon':
            queryset = queryset.filter(mappolygon__mpoly__bboverlaps=geom)

    if 'radius' in parameters and 'center' in parameters:
        try:
            radius = int(parameters['radius'])
        except:
            return HttpResponseBadRequest('Invalid radius. Only integers accepted.')
        temp = parameters.split(',')
        try:
            if len(temp) != 2:
                raise 
            temp[0] = float(temp[0])
            temp[1] = float(temp[1])
            center = Point(temp[0],temp[1])
        except:
            return HttpResponseBadRequest('Invalid center. Format is: center=lon,lat' )
        queryset = queryset.filter(point__distance_lte = (center,Distance(mi=radius)))
    elif 'radius' in parameters or 'center' in parameters:
        return HttpResponseBadRequest('If a center or radius is specified, the other must also be specified.')

    return queryset.distinct()
