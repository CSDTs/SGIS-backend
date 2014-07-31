from django.dispatch import receiver
from django.db.models.signals import post_save
from gis.models import Dataset, MapPoint, Tag, TagIndiv

def update_mappoints(sender, **kwargs):
	dataset = kwargs.get('instance')
	dataset.update_mappoints()
	
#post_save.connect(update_mappoints, sender=Dataset)

def update_tag_count(sender, **kwargs):
	if kwargs.get('created'): #if this is a new TagIndiv
		#increment the count and save
		print '!'
		kwargs.get('instance').tag.increment_count(save=True)

post_save.connect(update_tag_count, sender=TagIndiv)