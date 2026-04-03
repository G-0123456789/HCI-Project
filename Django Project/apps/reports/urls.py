from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('report/location/', views.LocationView.as_view(), name='location'),
    path('report/submit/', views.ReportSubmitView.as_view(), name='submit'),
    path('report/done/<str:ref_id>/', views.ReportDoneView.as_view(), name='done'),
    path('map/', views.IssueMapView.as_view(), name='map'),
]
