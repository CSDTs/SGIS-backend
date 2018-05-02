from django.conf.urls import include, url
from rest_framework import routers
from gis_csdt import views, templates
from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'api-ds', views.DatasetViewSet)
router.register(r'api-mp', views.MapPointViewSet, base_name = 'mappoint')
router.register(r'api-poly', views.MapPolygonViewSet, base_name = 'mappolygon')
router.register(r'api-tag', views.NewTagViewSet)
router.register(r'api-count', views.CountPointsInPolygonView, base_name = 'count_points')
router.register(r'api-dist', views.AnalyzeAreaAroundPointView, base_name = 'area')
router.register(r'api-dist2', views.AnalyzeAreaAroundPointNoValuesView, base_name = 'area2')
router.register(r'api-newsensor', views.NewSensorView)
router.register(r'api-datapoint', views.SubmitDataPointView, base_name = 'datapoint')
router.register(r'api-fields', views.FieldViewSet, base_name = 'fields')
router.register(r'api-fieldorder', views.FieldOrderViewSet, base_name = 'fieldOrder')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api-count/', views.CountPointsInPolygonView.as_view(), name='count'),
    #url(r'^api-dist/', views.AnalyzeAreaAroundPointView, name='distance'),
    url(r'^around-point/(?P<mappoint_id>[0-9]+)/$', templates.AroundPointView),
    url(r'^around-point/$', templates.AroundPointView),
]
