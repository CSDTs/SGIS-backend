from django.conf.urls import patterns, include, url
from rest_framework import routers
from gis import views

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'api-ds', views.DatasetViewSet)
router.register(r'api-mp', views.MapPointViewSet, base_name = 'mappoint')
router.register(r'api-newtag', views.NewTagViewSet)
router.register(r'api-poly', views.MapPolygonViewSet, base_name = 'mappolygon')
router.register(r'api-tag', views.TagViewSet)
#router.register(r'api-tag/count', views.TagCountViewSet, base_name = 'tag')

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
