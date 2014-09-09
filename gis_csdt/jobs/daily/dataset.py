from django_extensions.management.jobs import DailyJob
from gis_csdt.models import Dataset

class Job(DailyJob):
    help = 'Daily dataset updater'
    def execute(self):
    	datasets = Dataset.objects.all()
    	for dataset in datasets:
    		dataset.update_mappoints()