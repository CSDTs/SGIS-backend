from django.contrib import admin
from gis.models import Dataset, MapPoint, Tag

class DatasetAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name','url','cache_max_age']}),
        ('Field Mapping',	{'fields': ['remote_id_field','name_field','lat_field','lon_field',
        							'street_field','city_field','state_field','zipcode_field',
        							'county_field','field1_name','field2_name','field3_name']})]

admin.site.register(Dataset, DatasetAdmin)
#for testing
admin.site.register(MapPoint)
admin.site.register(Tag)