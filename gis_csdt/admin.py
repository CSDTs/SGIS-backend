from django.contrib import admin
from gis_csdt.models import Dataset, MapPoint, PhoneNumber, Tag, MapPolygon, TagIndiv, DataField, DataElement, Sensor, DataPoint

class DatasetAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name','url','cache_max_age']}),
        ('Field Mapping',	{'fields': ['remote_id_field','name_field','lat_field','lon_field',
        							'street_field','city_field','state_field','zipcode_field',
        							'county_field']}),
        ('Custom Fields',	{'fields': ['field1_en','field1_name','field2_en','field2_name','field3_en','field3_name']}),
        ('Geocoding',		{'fields': ['needs_geocoding']})]

admin.site.register(Dataset, DatasetAdmin)
#for testing
admin.site.register(MapPoint)
admin.site.register(Tag)
admin.site.register(MapPolygon)
admin.site.register(TagIndiv)
admin.site.register(DataField)
admin.site.register(DataElement)
admin.site.register(Sensor)
admin.site.register(DataPoint)
admin.site.register(PhoneNumber)
