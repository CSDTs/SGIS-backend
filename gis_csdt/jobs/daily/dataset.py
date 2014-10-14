from django_extensions.management.jobs import DailyJob
from gis_csdt.models import Dataset

class Job(DailyJob):
    help = 'Daily dataset updater'
    def execute(self):
        datasets = Dataset.objects.all()
        for dataset in datasets:
            print 'Update dataset:', dataset
            try:
                dataset.update_mappoints()
            except Exception as inst:
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst           # __str__ allows args to be printed directly