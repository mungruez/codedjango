from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('new_search', views.new_search, name='new_search'),
    path('jobs', views.jobs, name='jobs'),
    path('job_search', views.job_search, name='job_search'),
    path('cartoon', views.cartoon, name='cartoon'),

    path('success', views.success, name='success'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
