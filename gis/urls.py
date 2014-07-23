from django.conf.urls import patterns, include, url
from rest_framework import routers
from gis import views

from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'api-ds', views.DatasetViewSet)
router.register(r'api-mp', views.MapPointViewSet, base_name = 'mappoint')
router.register(r'api-poly', views.MapPolygonViewSet, base_name = 'mappolygon')
router.register(r'api-tag/count', views.TagCountViewSet, base_name = 'tag')
router.register(r'api-tag', views.TagViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gis_site.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
