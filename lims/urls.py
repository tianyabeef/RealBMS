from django.conf.urls import url

from .views import ProjectListView,SampleInfoFormListView


urlpatterns = [
    url(r'project/', ProjectListView.as_view(), name='project-list'),
    url(r'sampleinfoform/', SampleInfoFormListView.as_view(), name='sampleinfoform-list'),
]



