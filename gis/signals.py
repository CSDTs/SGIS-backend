from django.dispatch import receiver
from django.db.models.signals import post_save
from gis.models import Dataset, MapPoint #, Tag

def update_mappoints(sender, **kwargs):
	dataset = kwargs.get('instance')
	dataset.update_mappoints()
	
post_save.connect(update_mappoints, sender=Dataset)