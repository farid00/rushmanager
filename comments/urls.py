from django.conf.urls import patterns, url
from comments import views

urlpatterns = patterns('', 
    url(r'^(?P<pk>\d+)/$', views.CommentListView.as_view(), name='comments'), 
)