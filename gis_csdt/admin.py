from django.contrib import admin
from gis_csdt.models import Field, FieldOrder, Dataset, MapPoint, MapElement, Tag, MapPolygon, TagIndiv, Sensor, DataPoint

class FieldOrderInline(admin.TabularInline):
    model = FieldOrder
    extra = 1

class DatasetAdmin(admin.ModelAdmin):
    inlines = (FieldOrderInline,)



admin.site.register(Dataset, DatasetAdmin)
admin.site.register(DataPoint)
#for testing
admin.site.register(Field)
admin.site.register(MapElement)
admin.site.register(MapPoint)
admin.site.register(MapPolygon)
admin.site.register(Sensor)
admin.site.register(Tag)
admin.site.register(TagIndiv)
