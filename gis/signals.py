from django.dispatch import receiver
from django.db.models.signals import post_save
from gis.models import Dataset, MapPoint #, Tag

def update_mappoints(sender, **kwargs):
	dataset = kwargs.get('instance')
	if dataset.should_update():
		dataset.update_cache()
	elif dataset.needs_geocoding:
		for point in MapPoint.objects.filter(dataset_id = dataset.pk).order_by('remote_id'):
			if not point.geocoded:
				r = point.geocode()
				print point, point.geocoded, r
				if r['status'] == 'OVER_QUERY_LIMIT':
					return # ENDS FUNCTION
				point.save()
		dataset.needs_geocoding = False
		dataset.save()
post_save.connect(update_mappoints, sender=Dataset)